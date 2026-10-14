# -*- coding: utf-8 -*-
"""Detecta tomas de clips que parecen carteles/intertitulos (fondo plano oscuro + texto claro) entre las usadas."""
import json, subprocess, numpy as np, sys
from concurrent.futures import ThreadPoolExecutor
rows=json.load(open('_montaje/plan_final.json',encoding='utf-8'))
cl=[r for r in rows if r['tipo']=='clip']
def chk(r):
    out=[]
    for k in (0.2,0.5,0.8):
        t=r['start']+min(r['sdur'],6)*k
        b=subprocess.run(['ffmpeg','-v','error','-ss',f"{t:.2f}",'-i','video/lo/'+r['file'],'-frames:v','1','-vf','scale=160:90','-pix_fmt','gray','-f','rawvideo','-'],capture_output=True).stdout
        if len(b)!=160*90: continue
        a=np.frombuffer(b,dtype=np.uint8)
        dark=(a<40).mean(); bright=(a>200).mean(); mid=((a>=40)&(a<=200)).mean()
        flat=a.std()
        out.append((dark,bright,mid,flat))
    return out
with ThreadPoolExecutor(8) as ex: res=list(ex.map(chk,cl))
bad=[]
for r,o in zip(cl,res):
    sus=[x for x in o if (x[0]>0.7 and 0.015<x[1]<0.3) or (x[1]>0.7 and x[0]>0.015 and x[2]<0.15)]
    if sus: bad.append((round(r['t0']),r['file'],r['start'],r['pool']))
print(len(bad)); 
for b in bad: print(b)
json.dump(bad,open('qa/bad_titles.json','w'))
