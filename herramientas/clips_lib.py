# -*- coding: utf-8 -*-
"""Divide cada clip en tomas (cortes de escena) y descarta las muy oscuras/blancas/cortas."""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
LO="video/lo"
def dur(f):
    o=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f],capture_output=True,text=True).stdout.strip()
    return float(o) if o else 0
def analizar(fn):
    f=os.path.join(LO,fn); d=dur(f)
    r=subprocess.run(["ffmpeg","-nostats","-i",f,"-vf","fps=4,scale=160:-1,select='gt(scene,0.30)+eq(n,0)',showinfo","-an","-f","null","-"],capture_output=True,text=True)
    cuts=sorted(set([0.0]+[float(x) for x in re.findall(r"pts_time:([0-9.]+)",r.stderr)]))
    # brillo cada 0.5 s
    r2=subprocess.run(["ffmpeg","-nostats","-i",f,"-vf","fps=2,scale=160:-1,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-","-an","-f","null","-"],capture_output=True,text=True)
    yv=[float(x) for x in re.findall(r"YAVG=([0-9.]+)",r2.stdout)]
    shots=[]
    for a,b in zip(cuts,cuts[1:]+[d]):
        if b-a<2.2: continue
        i0=int(a*2); i1=max(i0+1,int(b*2)); seg=yv[i0:i1] or [128]
        m=sum(seg)/len(seg)
        if m<28 or m>225: continue
        # partir tomas largas en tramos de <=7 s
        t=a
        while b-t>=2.2:
            l=min(7.0,b-t)
            if b-(t+l)<2.0: l=b-t
            shots.append(dict(file=fn,start=round(t,2),dur=round(l,2),y=round(m)))
            t+=l
    return fn,d,shots
files=sorted(f for f in os.listdir(LO) if f.endswith(".mp4"))
out={}
with ThreadPoolExecutor(4) as ex:
    for fn,d,s in ex.map(analizar,files):
        out[fn]=dict(dur=d,shots=s); print(fn,round(d),"s ->",len(s),"tomas",flush=True)
json.dump(out,open("media/clips_tomas.json","w"),indent=0)
print("TOTAL",sum(len(v["shots"]) for v in out.values()))
