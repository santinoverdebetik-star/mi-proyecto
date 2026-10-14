# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, json, time, sys
UA={"User-Agent":"CanalWW2-docbuilder/1.0 (contact: contacto@example.com)"}
def g(u):
    for k in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read()
        except Exception as e: time.sleep(2+2*k)
Q=["V-2 rocket","Peenemunde","Wernher von Braun","German rocket scientists 1945","Operation Paperclip","German scientists captured 1945","Nuremberg trial","Hitler 1944","Berlin ruins 1945","Germany 1945 surrender","Silesia Poland 1945","Poland 1945","Red Army 1945","Russian front Germans 1944","German tunnels underground factory","Nordhausen Mittelwerk","German jet aircraft Me 262","Nazi Germany newsreel","Heinrich Himmler","SS troops","German atomic bomb","Alsos mission","Heisenberg","Wunderwaffe","Allied bombing Germany 1944","Wroclaw Breslau 1945","Prague May 1945","Czechoslovakia 1945","uranium atomic energy 1945","laboratory scientist 1940s"]
res=[]; seen=set()
for q in Q:
    api="https://archive.org/advancedsearch.php?q="+urllib.parse.quote(f'({q}) AND mediatype:movies')+"&fl[]=identifier&fl[]=title&fl[]=year&fl[]=licenseurl&fl[]=downloads&fl[]=collection&fl[]=runtime&rows=10&output=json&sort[]=downloads+desc"
    raw=g(api)
    if not raw: print("sin respuesta",q); continue
    try: docs=json.loads(raw)["response"]["docs"]
    except Exception: continue
    for d in docs:
        if d["identifier"] in seen: continue
        seen.add(d["identifier"]); d["q"]=q; res.append(d)
    time.sleep(0.5)
json.dump(res,open("media/ia_candidatos_g.json","w",encoding="utf8"),ensure_ascii=False,indent=1)
print(len(res))
for d in res: print(d["identifier"][:38],"|",d.get("year"),"|",str(d.get("title"))[:55],"|",str(d.get("licenseurl","-"))[-18:],"|",str(d.get("collection"))[:34],"|",d["q"][:16])
