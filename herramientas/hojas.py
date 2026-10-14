# -*- coding: utf-8 -*-
"""Hojas de contacto etiquetadas por tiempo: python hojas.py <archivo> <paso_s> <salida_prefijo> [cols] [filas]"""
import os, subprocess, sys, tempfile, glob
from PIL import Image, ImageDraw, ImageFont
f, step, pref = sys.argv[1], float(sys.argv[2]), sys.argv[3]
cols=int(sys.argv[4]) if len(sys.argv)>4 else 6; rows=int(sys.argv[5]) if len(sys.argv)>5 else 5
W=320
tmp=tempfile.mkdtemp()
subprocess.run(["ffmpeg","-y","-v","error","-i",f,"-vf",f"fps=1/{step},scale={W}:-2","-q:v","4",os.path.join(tmp,"f_%04d.jpg")],check=True)
fr=sorted(glob.glob(os.path.join(tmp,"f_*.jpg")))
try: ft=ImageFont.truetype("arialbd.ttf",18)
except Exception: ft=ImageFont.load_default()
per=cols*rows
for si in range(0,len(fr),per):
    chunk=fr[si:si+per]; ims=[Image.open(c) for c in chunk]; H=max(i.height for i in ims)
    sheet=Image.new("RGB",(cols*W,rows*H),(0,0,0)); d=ImageDraw.Draw(sheet)
    for k,im in enumerate(ims):
        x=(k%cols)*W; y=(k//cols)*H; sheet.paste(im,(x,y))
        t=(si+k)*step; lab="%d:%02d"%(t//60,t%60)
        d.rectangle([x,y,x+58,y+22],fill=(0,0,0)); d.text((x+3,y+1),lab,fill=(255,255,0),font=ft)
    out=f"{pref}_{si//per:02d}.jpg"; sheet.save(out,quality=70); print(out)
