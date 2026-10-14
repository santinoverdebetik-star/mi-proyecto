# -*- coding: utf-8 -*-
"""Descarga RAPIDA de fotos reales de Wikimedia Commons, sin hojas de miniaturas.
Uso (desde la carpeta del video):
    python ..\\fast_assets.py assets.json
assets.json = {"pools": {"etiqueta": {"q": ["consulta", ...], "cats": ["Categoria", ...], "max": 12, "min_w": 1100, "dest": "lugares"}}}
- Busca por consulta y por categoria EN PARALELO, filtra por licencia libre / tamano / palabras prohibidas,
  quita duplicados (misma 'serie' de titulo y casi-duplicados por hash), baja las mejores 'max' por etiqueta y
  escribe media/<dest>/<etiqueta>_NNNN.jpg + creditos_fotos_auto.txt.  Luego solo se revisa 1 storyboard.
"""
import json, os, re, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
UA = {"User-Agent": "CrimenEnLaSombra-docbuilder/1.0 (contact: contacto@example.com)"}
API = "https://commons.wikimedia.org/w/api.php"
LIC_OK = re.compile(r"public domain|pd|cc0|cc by|cc-by|no restrictions|attribution", re.I)
LIC_NO = re.compile(r"nc|nd|fair use|copyrighted", re.I)
BAD = re.compile(r"logo|flag|coat of arms|diagram|map of|\bmap\b|chart|icon|symbol|svg|nude|nsfw|sex|porn|bikini|graph|poster|screenshot|banner|stamp|coin|painting|drawing|cartoon|statue|toy|lego|model", re.I)
SEM = None


def get(u, tries=5):
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(4 + 6 * k)
            else:
                time.sleep(1 + k)
        except Exception:
            time.sleep(1 + k)
    return None


def q_search(q):
    u = (API + "?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=25&prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=1920&gsrsearch=" + urllib.parse.quote(q + " filetype:bitmap"))
    return _parse(get(u))


def q_cat(c):
    u = (API + "?action=query&format=json&generator=categorymembers&gcmtitle=" + urllib.parse.quote("Category:" + c) + "&gcmtype=file&gcmlimit=50&prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=1920")
    return _parse(get(u))


def _parse(raw):
    out = []
    if not raw:
        return out
    try:
        pages = json.loads(raw).get("query", {}).get("pages", {}).values()
    except Exception:
        return out
    for p in sorted(pages, key=lambda x: x.get("index", 99)):
        ii = (p.get("imageinfo") or [{}])[0]
        url = ii.get("thumburl") or ii.get("url")
        if not url or not re.search(r"\.(jpe?g|png|webp)$", p["title"], re.I):
            continue
        m = ii.get("extmetadata", {})
        out.append(dict(title=p["title"], url=url, w=ii.get("width", 0), h=ii.get("height", 0),
                        lic=m.get("LicenseShortName", {}).get("value", "?"),
                        aut=re.sub("<[^>]+>", "", m.get("Artist", {}).get("value", "?"))[:70]))
    return out


def serie(t):
    t = re.sub(r"^File:", "", t); t = re.sub(r"\.(jpe?g|png|webp)$", "", t, flags=re.I)
    t = re.sub(r"[\(\[].*", "", t); t = re.sub(r"[\s\-_]*\d+[\s\-_]*\w{0,3}$", "", t).strip(); t = re.sub(r"\d+", "#", t)
    return t[:28].lower()


def run(spec_path):
    spec = json.load(open(spec_path, encoding="utf-8"))["pools"]
    here = os.getcwd()
    cred = []
    from PIL import Image
    import numpy as np
    hashes = []

    def ahash(path):
        im = Image.open(path).convert("L").resize((16, 16)); a = np.asarray(im, dtype=float); return (a > a.mean()).flatten()

    # 1) todas las consultas/categorias en paralelo
    jobs = []
    for tag, cfg in spec.items():
        for q in cfg.get("q", []): jobs.append((tag, "q", q))
        for c in cfg.get("cats", []): jobs.append((tag, "c", c))
    with ThreadPoolExecutor(5) as ex:
        res = list(ex.map(lambda j: (j[0], q_search(j[2]) if j[1] == "q" else q_cat(j[2])), jobs))
    cand = {}
    for tag, lst in res:
        cand.setdefault(tag, []).extend(lst)
    # 2) filtrar + dedup + descargar
    usados = set()
    for tag, cfg in spec.items():
        mx = cfg.get("max", 10); mw = cfg.get("min_w", 1100); dest = cfg.get("dest", "lugares")
        os.makedirs(os.path.join(here, "media", dest), exist_ok=True)
        elegidas, series = [], set()
        for r in cand.get(tag, []):
            if r["title"] in usados or BAD.search(r["title"]):
                continue
            if r["w"] < mw or r["h"] < 650 or not LIC_OK.search(r["lic"]) or LIC_NO.search(r["lic"]):
                continue
            s = serie(r["title"])
            if s in series:
                continue
            series.add(s); elegidas.append(r)
            if len(elegidas) >= mx + 4:
                break
        got = 0
        def dl(a):
            n, r = a
            fn = os.path.join(here, "media", dest, f"{tag}_{n:04d}.jpg")
            if os.path.exists(fn):
                return fn, r
            b = get(r["url"])
            if not b:
                return None, r
            open(fn, "wb").write(b); return fn, r
        with ThreadPoolExecutor(5) as ex:
            files = list(ex.map(dl, list(enumerate(elegidas, 1))))
        for fn, r in files:
            if not fn or got >= mx:
                if fn and os.path.exists(fn): os.remove(fn)
                continue
            try:
                h = ahash(fn)
            except Exception:
                os.remove(fn); continue
            if any(int((h != o).sum()) <= 14 for o in hashes):
                os.remove(fn); continue                      # casi-duplicado
            hashes.append(h); usados.add(r["title"]); got += 1
            cred.append(f"{os.path.basename(fn)} | {r['title'][5:]} | {r['aut']} | {r['lic']} | Wikimedia Commons")
        print(f"{tag}: {got}/{mx}", flush=True)
    open(os.path.join(here, "creditos_fotos_auto.txt"), "w", encoding="utf-8").write("\n".join(cred))
    print("total", len(cred))


if __name__ == "__main__":
    run(sys.argv[1])
