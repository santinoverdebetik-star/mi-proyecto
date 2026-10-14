import json, sys, time
from faster_whisper import WhisperModel
t0=time.time()
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, info = m.transcribe("narracion/narracion.mp3", language="es", word_timestamps=True, vad_filter=False, beam_size=1)
words=[]
for s in segs:
    for w in s.words: words.append([w.word.strip(), round(w.start,2), round(w.end,2)])
    print(f"{s.end:7.1f}s / {info.duration:.0f}s", flush=True)
json.dump({"duration": info.duration, "words": words}, open("narracion/palabras.json","w",encoding="utf-8"), ensure_ascii=False)
print("listo", len(words), "palabras", round(time.time()-t0), "s")
