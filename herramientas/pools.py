# -*- coding: utf-8 -*-
"""Pools de clips (dominio publico NARA / US Army / Prelinger). Ventanas [t0,t1] en segundos sobre cada archivo."""
import json, os
HERE=os.path.dirname(os.path.abspath(__file__))
HSW="HitlersSecretWeapons.mp4"; WOCHE="gov.archives.arc.44362.mp4"; CAP="gov.archives.arc.64760.mp4"
POOLS={
 "v2_test":[("ADC-10039.mp4",0,235)],
 "cientificos":[("ADC-10039.mp4",252,328),("ADC-10039.mp4",385,444)],
 "hsw_v2":[(HSW,215,330),(HSW,425,600)],
 "hsw_jets":[(HSW,2240,2540),(HSW,2800,3215)],
 "wochenschau":[(WOCHE,28,590),(WOCHE,625,1290)],
 "nazi_cap":[(CAP,840,1280),(CAP,2145,2480)],
 "luft_cap":[(CAP,1380,1600),(CAP,0,230)],
 "wehrmacht":[("gov.archives.arc.43528.2.mp4",5,390),("gov.archives.arc.43553.mp4",15,420)],
 "oss":[("gov.archives.arc.43528.1.mp4",34,340)],
 "berlin47":[("PostwarG.mp4",535,800)],
 "vonbraun":[("gov.archives.arc.2569665.mp4",1085,1500),("gov.archives.arc.2569665.mp4",400,480),("gov.archives.arc.2569665.mp4",1520,1610)],
 "redstone":[("redstone_years.mp4",150,330),("redstone_years.mp4",345,400)],
 "nuremberg":[("1946-10-08_21_Nazi_Chiefs_Guilty.mp4",14,285)],
 "hitler_arch":[("1942-01-07_Gen_Adolph_Takes_Over.mp4",8,110)],
}
_T=None
def tomas():
    global _T
    if _T is None: _T=json.load(open(os.path.join(HERE,"media","clips_tomas.json")))
    return _T
def shots(pool):
    out=[]
    T=tomas()
    for f,a,b in POOLS[pool]:
        for s in T.get(f,{}).get("shots",[]):
            if s["start"]>=a and s["start"]+min(s["dur"],3)<=b: out.append(dict(s,pool=pool))
    out.sort(key=lambda s:(s["file"],s["start"]))
    return out
