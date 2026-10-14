# -*- coding: utf-8 -*-
import difflib, json, re, unicodedata
def norm(w):
    w=unicodedata.normalize("NFD",w.lower()); return re.sub(r"[^a-z0-9]","","".join(c for c in w if unicodedata.category(c)!="Mn"))
def paragraphs(): return [p.strip() for p in open("guion.txt",encoding="utf-8").read().strip().split("\n\n")]
def align(paras,words,total):
    ww=[(norm(w[0]),w[1],w[2]) for w in words if norm(w[0])]
    n_g=[len([x for x in p.split() if norm(x)]) for p in paras]
    exp,acc=[],0
    for n in n_g: exp.append(acc); acc+=n
    scale=len(ww)/max(acc,1); starts,prev=[],-1
    for i,p in enumerate(paras):
        g=[norm(x) for x in p.split() if norm(x)][:5]; e=int(exp[i]*scale)
        best,bi=-1,min(max(e,prev+1),len(ww)-1)
        for j in range(max(prev+1,e-80),min(len(ww)-1,e+80)):
            cand=[x[0] for x in ww[j:j+len(g)]]
            sc=difflib.SequenceMatcher(None," ".join(g)," ".join(cand)).ratio()-abs(j-e)*0.002
            if sc>best: best,bi=sc,j
        prev=bi; starts.append(ww[bi][1])
    starts[0]=0.0
    return starts, starts[1:]+[total]
if __name__=="__main__":
    d=json.load(open("narracion/palabras.json",encoding="utf8"))
    P=paragraphs(); s,e=align(P,d["words"],d["duration"])
    json.dump(dict(starts=s,ends=e),open("narracion/parrafos.json","w"))
    for i,(p,a,b) in enumerate(zip(P,s,e)):
        print(f"{i:3d} {int(a//60):02d}:{int(a%60):02d} {b-a:5.1f}s | {p[:95]}")
