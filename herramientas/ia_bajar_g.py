# -*- coding: utf-8 -*-
import json, os, sys, urllib.request, urllib.parse, time
from concurrent.futures import ThreadPoolExecutor
UA={"User-Agent":"CanalWW2-docbuilder/1.0 (contact: contacto@example.com)"}
M=json.load(open("media/ia_meta_g.json",encoding="utf8"))
def pick(i):
    f=M[i]["files"]
    # prefer 512kb mp4, else h.264 mp4 (smallest)
    c=[x for x in f if x[0].endswith("_512kb.mp4")] or sorted([x for x in f if x[0].endswith(".mp4")],key=lambda x:x[1])
    return c[0][0] if c else None
ids=["ADC-10039","HitlersSecretWeapons","gov.archives.arc.64760","gov.archives.arc.44362","gov.archives.arc.43528.1","gov.archives.arc.43528.2","gov.archives.arc.43553","PostwarG","PostwarG_2","PostwarG_3","PostwarG_4","HERE_IS_GERMANY","gov.archives.arc.2569665","CS-2937","redstone_years","1946-10-08_21_Nazi_Chiefs_Guilty","1942-01-07_Gen_Adolph_Takes_Over","TheNazisStrike","gov.archives.arc.35957.b"]
ids=[i for i in ids if i in M]
def dl(i):
    n=pick(i)
    if not n: return i,"sin mp4"
    dst=os.path.join("video","lo",i.replace("/","_")+".mp4")
    if os.path.exists(dst) and os.path.getsize(dst)>1000: return i,"ya"
    url="https://archive.org/download/"+i+"/"+urllib.parse.quote(n)
    for k in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=120) as r, open(dst+".part","wb") as o:
                while True:
                    b=r.read(1<<20)
                    if not b: break
                    o.write(b)
            os.replace(dst+".part",dst); return i,"ok %d MB"%(os.path.getsize(dst)//1048576)
        except Exception as e: time.sleep(3)
    return i,"FALLO"
with ThreadPoolExecutor(3) as ex:
    for r in ex.map(dl,ids): print(*r,flush=True)
