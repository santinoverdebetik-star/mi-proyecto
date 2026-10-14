# -*- coding: utf-8 -*-
"""Remezcla solo el audio (musica mas presente) y copia el video de salida_video.mp4.
python remix.py <salida> [ss] [t]   (ss/t solo para pruebas de audio)"""
import subprocess, sys, os
M = r"D:\YOUTUBE STUFF\COMUNES\musica_tension2.wav"
out = sys.argv[1]; ss = float(sys.argv[2]) if len(sys.argv) > 2 else 0; t = float(sys.argv[3]) if len(sys.argv) > 3 else 1804.33
DRY, WET = "volume=0.60", "volume=24dB,asoftclip=type=tanh,highpass=f=160,lowpass=f=2500,volume=-24dB"
af = (f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,asplit=2[d][w];[d]{DRY}[d2];[w]{WET}[w2];[d2][w2]amix=inputs=2:normalize=0[m];"
      "[0:a]aformat=sample_rates=44100:channel_layouts=stereo,highpass=f=80,equalizer=f=200:t=q:w=1:g=1.5,equalizer=f=3200:t=q:w=1:g=2,acompressor=threshold=-18dB:ratio=2.5:attack=20:release=250[v];"
      "[v]asplit[v1][v2];[m][v1]sidechaincompress=threshold=0.03:ratio=3:attack=30:release=600[md];"
      "[v2][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14.5:TP=-1.5:LRA=8[a]")
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{ss}", "-t", f"{t}", "-i", "narracion/narracion.mp3",
       "-stream_loop", "-1", "-t", f"{t}", "-i", M, "-filter_complex", af]
if out.endswith(".wav"):
    cmd += ["-map", "[a]", out]
else:
    cmd = cmd[:cmd.index("-filter_complex")] + ["-i", os.environ.get("VIDEO", "salida_video.mp4"), "-filter_complex", af, "-map", "2:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{t}", "-movflags", "+faststart", out]
subprocess.run(cmd, check=True)
