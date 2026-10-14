# -*- coding: utf-8 -*-
"""Monta el video de La Campana Nazi (clips + fotos reales + transiciones xfade).
  python montar.py                      -> salida.mp4 (completo)
  python montar.py --desde 0 --hasta 150 --salida prueba.mp4
Prioridad de material: clips -> fotos reales -> (IA solo si falta; ninguna por ahora)."""
import argparse, json, math, os, random, re, subprocess, sys, textwrap, wave
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
import pools, plan_data
from alinear import paragraphs

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
W, H, FPS = 1920, 1080, 30
LO = os.path.join(HERE, "video", "lo")
MPEG = r"D:\YOUTUBE STUFF\Segunda Guerra Mundial\_fuente_mariscales\mpeg"
SEG = os.path.join(HERE, "_montaje", "seg"); FIT = os.path.join(HERE, "_montaje", "fit"); CARD = os.path.join(HERE, "_montaje", "cards")
for d in (SEG, FIT, CARD): os.makedirs(d, exist_ok=True)
MUSICA = r"D:\YOUTUBE STUFF\COMUNES\musica_tension2.wav"
CARD_DUR = {"subscribe": 7.0, "quote_madej": 6.5, "final": 9.0}
BG = (23, 18, 13); FG = (226, 214, 196); ACC = (126, 84, 62)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        sys.exit("FFmpeg fallo:\n" + " ".join(cmd[:24]) + "\n" + r.stderr[-1500:])


# ------------------------------------------------------------------ linea de tiempo
_Q = None
QMIN_STD, QMIN_MEAN, QMAX_MEAN, QMIN_LAP = 20, 40, 215, 2.0
def good_shot(s):
    """Descarta tomas en blanco, casi negras o borrosas (medidas en qshots.py)."""
    global _Q
    if _Q is None: _Q = json.load(open("media/shots_q.json")) if os.path.exists("media/shots_q.json") else {}
    q = _Q.get(f"{s['file']}|{s['start']}")
    return q is None or (q[0] >= QMIN_STD and QMIN_MEAN <= q[1] <= QMAX_MEAN and q[2] >= QMIN_LAP)

ALIAS = json.load(open("media/alias.json")) if os.path.exists("media/alias.json") else {}
_rp = {}
def repl_pool(i):
    lst = plan_data.REPL.get(i) or plan_data.REPL_DEFAULT
    k = _rp.get(i, 0); _rp[i] = k + 1
    return lst[k % len(lst)]

def photo_path(ref):
    tag, n = ref.rsplit("_", 1)
    return f"media/fotos/{tag}_{int(n):04d}.jpg"


BAD = set(json.load(open("media/bad_shots.json"))) if os.path.exists("media/bad_shots.json") else set()
def postfix(rows):
    """Quita tomas con carteles/negras y tomas casi iguales (mismo archivo a <12 s de otra ya usada)."""
    pool = {k: pools.shots(k) for k in pools.POOLS}
    used = [(r["file"], r["start"]) for r in rows if r["tipo"] == "clip"]
    taken = {}
    nfix = 0
    for r in rows:
        if r["tipo"] != "clip": continue
        key = f"{r['file']}|{r['start']}"
        near = [s for (f, s) in taken.get(r["file"], []) if abs(s - r["start"]) < 12]
        if key in BAD or near:
            need = r["d"]
            cands = [s for s in pool[r["pool"]] if f"{s['file']}|{s['start']}" not in BAD and good_shot(s)
                     and (s["file"], s["start"]) not in used
                     and all(abs(s["start"] - t) >= 12 for (f, t) in taken.get(s["file"], []) + [(f2, t2) for (f2, t2) in used if f2 == s["file"]] if f == s["file"])]
            if cands:
                cands.sort(key=lambda s: (s["dur"] < need - 0.6, abs(s["dur"] - need)))
                s = cands[0]; used.append((s["file"], s["start"]))
                r.update(file=s["file"], start=s["start"], sdur=s["dur"]); nfix += 1
        taken.setdefault(r["file"], []).append((r["file"], r["start"]))
    return nfix

def build_rows():
    P = paragraphs(); al = json.load(open("narracion/parrafos.json")); st, en = al["starts"], al["ends"]
    pool = {k: pools.shots(k) for k in pools.POOLS}
    used_shot = set(); seen_photo = set()
    rows = []; warn = []
    FALL = plan_data.REPL_DEFAULT

    def take_clip(name, need):
        cand = [s for s in pool[name] if (s["file"], s["start"]) not in used_shot and good_shot(s)]
        if not cand: return None
        good = [s for s in cand if s["dur"] >= need - 0.6]
        s = (good or sorted(cand, key=lambda x: -x["dur"]))[0]
        used_shot.add((s["file"], s["start"])); return s

    for i, p in enumerate(P):
        t0, t1 = st[i], en[i]; dur = t1 - t0
        specs = plan_data.P[i].split()
        cards = [s for s in specs if s.startswith("card:")]
        fixed = sum(CARD_DUR[c[5:]] for c in cards)
        rem = max(dur - fixed, 2.0 if not cards else 0.0)
        items = []
        for s in specs:
            if s.startswith("card:"): items.append(("card", s[5:])); continue
            if s.startswith("f:"):
                ref = s[2:]
                if not os.path.exists(photo_path(ref)): warn.append(f"p{i}: foto {ref} no existe"); items.append(("c", repl_pool(i))); continue
                cn = ALIAS.get(ref, ref)
                if cn in seen_photo: warn.append(f"p{i}: foto {ref} repetida -> clip"); items.append(("c", repl_pool(i))); continue
                seen_photo.add(cn); items.append(("f", ref))
            else: items.append(("c", s[2:]))
        nb = len([x for x in items if x[0] != "card"])
        if nb == 0: nb = 1; items = [("c", FALL[i % len(FALL)])] + items
        avg = rem / nb if nb else rem
        while avg > 7.5:
            items.insert(len(items) - (1 if items and items[-1][0] == "card" else 0), ("c", repl_pool(i))); nb += 1; avg = rem / nb
        while nb > 1 and avg < 3.0:
            cand = [k for k, x in enumerate(items) if x[0] == "f"] or [k for k, x in enumerate(items) if x[0] != "card"]
            items.pop(max(cand)); nb -= 1; avg = rem / nb
        step = rem / nb if nb else 0
        cur = t0
        for kind, ref in items:
            if kind == "card":
                d = CARD_DUR[ref]; rows.append(dict(t0=cur, d=d, tipo="card", ref=ref, p=i)); cur += d; continue
            d = step
            if kind == "f":
                rows.append(dict(t0=cur, d=d, tipo="foto", ref=ref, p=i))
            else:
                s = take_clip(ref, d)
                if s is None:
                    for fb in FALL:
                        s = take_clip(fb, d)
                        if s: warn.append(f"p{i}: pool {ref} agotado -> {fb}"); break
                rows.append(dict(t0=cur, d=d, tipo="clip", file=s["file"], start=s["start"], sdur=s["dur"], pool=s["pool"], p=i))
            cur += d
    total = al["ends"][-1]
    for r in rows: r["f0"] = round(r["t0"] * FPS)
    for a, b in zip(rows, rows[1:] + [None]):
        a["n"] = (b["f0"] if b else round(total * FPS)) - a["f0"]
    return rows, warn


# ------------------------------------------------------------------ tarjetas
def fnt(name, size):
    for base in (r"C:\Windows\Fonts\%s" % name,):
        if os.path.exists(base): return ImageFont.truetype(base, size)
    return ImageFont.load_default()


def center(d, y, text, f, fill):
    w = d.textlength(text, font=f); d.text(((W - w) / 2, y), text, font=f, fill=fill)


def make_card(kind, path):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    v = Image.new("L", (W, H), 0); ImageDraw.Draw(v).ellipse((-300, -200, W + 300, H + 200), fill=255)
    img.paste(Image.new("RGB", (W, H), (34, 27, 20)), mask=v.filter(ImageFilter.GaussianBlur(260)))
    d = ImageDraw.Draw(img)
    if kind == "subscribe":
        f = fnt("georgia.ttf", 54); center(d, 420, "Historias que empiezan donde terminan los libros", f, FG)
        b = fnt("georgiab.ttf", 34); w = d.textlength("SUSCRÍBETE", font=b); x0 = (W - w) / 2 - 46
        d.rounded_rectangle((x0, 545, x0 + w + 92, 620), radius=8, fill=ACC); d.text((x0 + 46, 557), "SUSCRÍBETE", font=b, fill=(240, 232, 220))
    elif kind == "quote_madej":
        q = "«Equivocarse es humano, pero obstinarse es de necios.»"
        f = fnt("georgia.ttf", 58); y = 400
        for ln in textwrap.wrap(q, 40): center(d, y, ln, f, FG); y += 80
        center(d, y + 40, "Janusz Madej, geofísico de la Universidad AGH de Cracovia · 15 de diciembre de 2015 (traducido)", fnt("georgia.ttf", 26), (160, 148, 130))
    elif kind == "final":
        f = fnt("georgia.ttf", 50); y = 380
        for ln in textwrap.wrap("¿Fue la Campana un arma secreta, un engaño o una historia que necesitábamos creer?", 36): center(d, y, ln, f, FG); y += 70
        s = fnt("georgia.ttf", 30); center(d, y + 56, "Te leo en los comentarios", s, (170, 158, 140))
        w = d.textlength("Te leo en los comentarios", font=s); d.line(((W - w) / 2, y + 100, (W + w) / 2, y + 100), fill=ACC, width=2)
    img.save(path)
    return path


# ------------------------------------------------------------------ fotos
def fit_photo(n):
    out = os.path.join(FIT, f"{n}.jpg")
    if os.path.exists(out): return out
    im = Image.open(photo_path(n)).convert("RGB"); w, h = im.size
    CW, CH = 2880, 1620
    if 1.72 <= w / h <= 1.84:
        im.resize((CW, CH), Image.LANCZOS).save(out, quality=93); return out
    s = max(CW / w, CH / h)
    bg = im.resize((int(w * s) + 1, int(h * s) + 1)); l, t = (bg.width - CW) // 2, (bg.height - CH) // 2
    bg = ImageEnhance.Brightness(bg.crop((l, t, l + CW, t + CH)).filter(ImageFilter.GaussianBlur(45))).enhance(0.40)
    s2 = min(CW * 0.97 / w, CH * 0.97 / h)
    fg = im.resize((max(int(w * s2), 1), max(int(h * s2), 1)), Image.LANCZOS)
    bg.paste(fg, ((CW - fg.width) // 2, (CH - fg.height) // 2)); bg.save(out, quality=93)
    return out


CAMS = ["zin", "zin2", "zout", "panlr", "panrl"]


def zoompan(cam, n):
    if cam == "zin": return f"z='1+0.09*on/{n}':x='iw/2-(iw/zoom/2)':y='ih*0.40-(ih/zoom*0.40)'"
    if cam == "zin2": return f"z='1+0.065*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    if cam == "zout": return f"z='1.08-0.08*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    if cam == "panlr": return f"z='1.07':x='(iw-iw/zoom)*on/{n}':y='ih/2-(ih/zoom/2)'"
    if cam == "panrl": return f"z='1.07':x='(iw-iw/zoom)*(1-on/{n})':y='ih/2-(ih/zoom/2)'"
    return f"z='1+0.02*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"


# sepia + grano + vineta (look del canal)
GRADE = ("eq=saturation=0:contrast=1.10:brightness=-0.035,"
         "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0,"
         "vignette=PI/3.2,noise=alls=7:allf=t+u")


def src_for(f):
    return os.path.join(LO, f), False


def render(row, idx):
    ext = row.get("ext", 0); fin = row.get("fin", True)
    out = os.path.join(SEG, f"{idx:04d}.mp4")
    tag = json.dumps({k: row[k] for k in row if k in ("tipo", "ref", "file", "start", "n")}) + f"|x{ext}|f{int(fin)}"
    mark = out + ".tag"
    if os.path.exists(out) and os.path.exists(mark) and open(mark).read() == tag: return out
    n = row["n"] + ext; dur = n / FPS
    fade = (",fade=t=in:st=0:d=0.10" if fin else "")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-threads", "2"]
    if row["tipo"] == "foto":
        src = fit_photo(row["ref"]); cam = CAMS[idx % len(CAMS)]
        chain = f"scale=2880:1620,setsar=1,zoompan={zoompan(cam, n)}:d={n}:s={W}x{H}:fps={FPS},{GRADE}"
        cmd += ["-i", src, "-vf", chain + fade + ",format=yuv420p"]
    elif row["tipo"] == "card":
        src = os.path.join(CARD, row["ref"] + ".png"); make_card(row["ref"], src)
        chain = f"scale=2400:1350,setsar=1,zoompan=z='1+0.03*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},fade=t=in:st=0:d=0.5,fade=t=out:st={max(dur-0.5,0):.2f}:d=0.5,noise=alls=4:allf=t"
        cmd += ["-i", src, "-vf", chain + ",format=yuv420p"]
    else:
        src, hi = src_for(row["file"]); d_src = min(row["sdur"], dur); stretch = max(dur / d_src, 1.0) if d_src > 0 else 1.0
        chain = (f"fps={FPS},setpts={stretch:.4f}*PTS,split[ca][cb];"
                 f"[ca]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:4,eq=brightness=-0.24[cbg];"
                 f"[cb]scale=-2:{H}:force_original_aspect_ratio=decrease,setsar=1[cfg];[cbg][cfg]overlay=(W-w)/2:(H-h)/2,setsar=1,"
                 f"{GRADE},eq=brightness='-0.005+0.012*sin(13*t)':eval=frame" + fade)
        cmd += ["-ss", f"{row['start']:.2f}", "-t", f"{d_src + 0.3:.2f}", "-i", src, "-vf", chain + ",format=yuv420p"]
    tmp = out + ".part.mp4"
    cmd += ["-frames:v", str(n), "-r", str(FPS), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-maxrate", "8M", "-bufsize", "16M", tmp]
    run(cmd); os.replace(tmp, out); open(mark, "w").write(tag)
    return out


# ------------------------------------------------------------------ transiciones (xfade)
XT = {"fade": 0.50, "dissolve": 0.40, "fadegrays": 0.50, "smoothleft": 0.35, "smoothright": 0.35, "hblur": 0.30, "zoomin": 0.35,
      "slideleft": 0.30, "fadeblack": 0.45, "circleopen": 0.40}
CALM = ["fade", "dissolve", "fade", "fadegrays"]
MOV = ["smoothleft", "hblur", "zoomin", "smoothright", "slideleft"]
XACC = ["fadeblack", "circleopen"]


def plan_transitions(rows, share=0.62):
    rng = random.Random(7); last = None; since = 0; cm = mv = ac = 0
    for r in rows: r["xt"] = None; r["ext"] = 0; r["fin"] = True
    for i in range(len(rows) - 1):
        a, b = rows[i], rows[i + 1]
        if a["t0"] < 18 or a["tipo"] == "card" or b["tipo"] == "card" or a["n"] < 36 or b["n"] < 36: continue
        p = share if last is None else (0.45 if last else share + 0.12)
        hit = rng.random() < p; last = hit
        if not hit: continue
        since += 1
        if since >= 8 and rng.random() < 0.6: kind = XACC[ac % len(XACC)]; ac += 1; since = 0
        elif rng.random() < 0.6: kind = CALM[cm % len(CALM)]; cm += 1
        else: kind = MOV[mv % len(MOV)]; mv += 1
        ov = min(int(round(XT[kind] * FPS)), a["n"] - 12, b["n"] - 12)
        if ov < 6: continue
        a["xt"] = (kind, ov); a["ext"] = ov + 1; b["fin"] = False


def assemble(rows, files, work):
    segs = []; cur = [0]
    for k in range(1, len(rows)):
        if rows[k - 1].get("xt"): cur.append(k)
        else: segs.append(cur); cur = [k]
    segs.append(cur)
    out_files = []; todo = []
    for si, sg in enumerate(segs):
        if len(sg) == 1: out_files.append(files[sg[0]]); continue
        outp = os.path.join(work, f"seg{si:04d}.mp4"); out_files.append(outp)
        sig = "|".join(f"{files[k]}:{os.path.getmtime(files[k])}:{rows[k].get('xt')}" for k in sg)
        tg = outp + ".tag"
        if os.path.exists(outp) and os.path.exists(tg) and open(tg).read() == sig: continue
        todo.append((sg, outp, sig))

    def mk(args):
        sg, outp, sig = args
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-threads", "2"]
        for k in sg: cmd += ["-i", files[k]]
        parts = []; cum = 0; prev = "0:v"
        for j in range(len(sg) - 1):
            kind, ov = rows[sg[j]]["xt"]; cum += rows[sg[j]]["n"]
            parts.append(f"[{prev}][{j + 1}:v]xfade=transition={kind}:duration={ov / FPS:.3f}:offset={cum / FPS:.3f}[v{j}]"); prev = f"v{j}"
        total = sum(rows[k]["n"] for k in sg)
        parts.append(f"[{prev}]fps={FPS},tpad=stop_mode=clone:stop_duration=1,format=yuv420p[vout]")
        cmd += ["-filter_complex", ";".join(parts), "-map", "[vout]", "-frames:v", str(total), "-r", str(FPS), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-maxrate", "9M", "-bufsize", "18M", outp + ".part.mp4"]
        run(cmd); os.replace(outp + ".part.mp4", outp); open(outp + ".tag", "w").write(sig)
    with ThreadPoolExecutor(6) as ex: list(ex.map(mk, todo))
    return out_files


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--salida", default="salida_video.mp4"); ap.add_argument("--workers", type=int, default=10); a = ap.parse_args()
    rows, warn = build_rows()
    print(postfix(rows), "tomas sustituidas (carteles/casi iguales)", flush=True)
    for w in warn[:5]: print("AVISO", w)
    nc = sum(1 for r in rows if r["tipo"] == "clip"); nf = sum(1 for r in rows if r["tipo"] == "foto"); nk = sum(1 for r in rows if r["tipo"] == "card")
    print(f"planos: {len(rows)} ({nc} clips = {100*nc//len(rows)}%, {nf} fotos, {nk} tarjetas, 0 IA)", flush=True)
    if os.environ.get("NOTRANS") == "1":
        for r in rows: r["xt"] = None; r["ext"] = 0; r["fin"] = True
    else: plan_transitions(rows)
    print(sum(1 for r in rows if r.get("xt")), "transiciones xfade", flush=True)
    json.dump(rows, open("_montaje/plan_final.json", "w"), indent=0)
    with ThreadPoolExecutor(a.workers) as ex:
        files = list(ex.map(lambda ir: render(ir[1], ir[0]), enumerate(rows)))
    work = os.path.join(HERE, "_montaje"); out_files = assemble(rows, files, work)
    lst = os.path.join(work, "lista.txt")
    with open(lst, "w") as f:
        for p in out_files: f.write("file '" + p.replace("\\", "/") + "'\n")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", a.salida])
    print("LISTO", a.salida, round(sum(r["n"] for r in rows) / FPS), "s")


if __name__ == "__main__":
    main()
