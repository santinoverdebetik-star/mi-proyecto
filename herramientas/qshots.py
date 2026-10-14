# -*- coding: utf-8 -*-
"""Calidad de cada toma (nitidez/contraste/brillo) para descartar tomas en blanco, negras o borrosas."""
import json, os, subprocess, numpy as np
from concurrent.futures import ThreadPoolExecutor
import pools
LO = os.path.join(pools.HERE, "video", "lo")
def frame(f, t):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", os.path.join(LO, f), "-frames:v", "1", "-vf", "crop=iw:ih*0.77:0:0,scale=96:54", "-pix_fmt", "gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(b, dtype=np.uint8).astype(float) if len(b) == 96 * 54 else None
def score(s):
    d = min(s["dur"], 6); res = []
    for k in (0.2, 0.5, 0.8):
        a = frame(s["file"], s["start"] + d * k)
        if a is None: continue
        g = a.reshape(54, 96); lap = np.abs(np.diff(g, axis=1)).mean()      # detalle horizontal
        res.append((a.std(), a.mean(), lap))
    if not res: return [0, 0, 0]
    return [float(np.median([r[0] for r in res])), float(np.median([r[1] for r in res])), float(np.median([r[2] for r in res]))]
if __name__ == "__main__":
    allsh = {}
    for p in pools.POOLS:
        for s in pools.shots(p): allsh[f"{s['file']}|{s['start']}"] = s
    keys = list(allsh)
    with ThreadPoolExecutor(6) as ex: out = list(ex.map(lambda k: score(allsh[k]), keys))
    json.dump(dict(zip(keys, out)), open("media/shots_q.json", "w"))
    print(len(keys), "tomas")
