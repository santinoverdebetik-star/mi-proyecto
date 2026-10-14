# -*- coding: utf-8 -*-
import urllib.request, json, time, sys
UA={"User-Agent":"CanalWW2-docbuilder/1.0 (contact: contacto@example.com)"}
IDS=['ADC-10039', '1946-05-13_1st_Pictures_Nazi_Rocket_Bomb_i', 'HitlersSecretWeapons', 'gov.archives.arc.64760', 'gov.archives.arc.44362', 'gov.archives.arc.43528.1', 'gov.archives.arc.43528.2', 'gov.archives.arc.43553', 'PostwarG', 'PostwarG_2', 'PostwarG_3', 'PostwarG_4', 'HERE_IS_GERMANY', 'gov.archives.arc.2569665', 'CS-2937', 'redstone_years', '1946-10-08_21_Nazi_Chiefs_Guilty', 'polish-army-seals-alleged-site-of-undergro', 'polish-authorities-believe-they-have-locat', '1942-01-07_Gen_Adolph_Takes_Over', 'TheNazisStrike', 'TheOccultHistoryOfTheThirdReich-Part1TheEn', 'gov.archives.arc.35957.b', '1944-07-02_Cherbourg_Gateway_to_Victory']
out={}
for i in IDS:
    for k in range(3):
        try:
            d=json.loads(urllib.request.urlopen(urllib.request.Request("https://archive.org/metadata/"+i,headers=UA),timeout=60).read()); break
        except Exception as e: d=None; time.sleep(2)
    if not d or "files" not in d: print("ERR",i); continue
    m=d.get("metadata",{})
    vids=[(f["name"],int(f.get("size",0))//1048576,f.get("format","")) for f in d["files"] if f["name"].lower().endswith((".mp4",".mpeg",".mpg",".ogv",".mov",".avi")) and int(f.get("size",0))>0]
    out[i]={"title":m.get("title"),"lic":m.get("licenseurl"),"coll":m.get("collection"),"dur":m.get("runtime") or "", "files":vids,"desc":str(m.get("description",""))[:200]}
    print(i,"|",str(m.get("title"))[:45],"|",m.get("runtime",""),"|",(m.get("licenseurl") or "-")[-22:])
    for v in vids[:4]: print("    ",v)
    time.sleep(0.3)
json.dump(out,open("media/ia_meta_g.json","w",encoding="utf8"),ensure_ascii=False,indent=1)
