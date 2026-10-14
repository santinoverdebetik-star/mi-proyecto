# -*- coding: utf-8 -*-
import json, collections, os
rows=json.load(open("_montaje/plan_final.json"))
M=json.load(open("media/ia_meta_g.json",encoding="utf8"))
used=collections.OrderedDict()
for r in rows:
    if r["tipo"]=="clip":
        k=r["file"][:-4]; used.setdefault(k,0); used[k]+=1
with open("creditos_clips.txt","w",encoding="utf8") as f:
    f.write("Clips de video (dominio publico / CC0 / Public Domain Mark) - Internet Archive\n")
    for k,c in used.items():
        m=M.get(k,{}); f.write(f"{k} | {m.get('title','')} | {m.get('lic','') or ''} | {c} tomas | https://archive.org/details/{k}\n")
photos={os.path.basename(("media/fotos/%s_%04d.jpg"%tuple([r['ref'].rsplit('_',1)[0],int(r['ref'].rsplit('_',1)[1])]))) for r in rows if r["tipo"]=="foto"}
lines=[l for l in open("creditos_fotos_all.txt",encoding="utf8").read().splitlines() if l.split(" | ")[0] in photos]
open("creditos_fotos.txt","w",encoding="utf8").write("\n".join(lines))
print(len(used),"fuentes de clips;",len(photos),"fotos;",len(lines),"creditos de fotos")
