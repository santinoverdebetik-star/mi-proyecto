# Estilo visual de los 2 videos de referencia del usuario

Archivos analizados (D:\back up\descargas\):
- `video_final.mp4` — 34:04, es el video de la familia Stauffenberg (mismo contenido que el guion).
- `juventude shitlerianas.mp4` — 33:26, video sobre las Juventudes Hitlerianas.
Los dos tienen exactamente el mismo acabado (misma "plantilla"), así que este es el estilo del canal.

## Técnica del export
- 1920x1080, 30 fps, H.264, AAC 48 kHz mono.
- Sonido normalizado a **-14,5 LUFS**, LRA ~1,7 LU (muy parejo: voz + música baja constante).
- Bitrate: ~2,0 Mb/s (video_final) y ~3,7 Mb/s (juventud).

## Ritmo
- ~360 cortes en ~34 min ⇒ **~10-11 cortes por minuto**.
- Duración de plano: **mediana 5,5 s**, media 5,7 s, mínimo ~1,4 s, máximo ~14 s.
- Cortes secos (hard cut) entre planos; no hay transiciones vistosas.
- Cada imagen se mueve lento (zoom/paneo tipo Ken Burns): al muestrear a 3 s, el mismo plano aparece 2 veces con ligero cambio de encuadre.

## Look
- **Monocromo sepia** en TODO (incluso fotos modernas de lugares y objetos se pasan a sepia/marrón verdoso). Contraste moderado-alto, negros profundos.
- **Viñeta oscura** + **grano** + **motas de polvo/rayas** (muy visibles en planos fijos).
- Las imágenes que no son 16:9 (retratos verticales, fotos 4:3) se centran con **bordes que son una copia ampliada, oscurecida y desenfocada de la misma imagen** (no barras negras lisas).
- Los retratos de personas van centrados y con el rostro como foco del zoom.

## Tipo de material (mezcla)
1. Fotografías de archivo reales (Bundesarchiv, Wikimedia Commons): retratos, desfiles, ruinas, salas de juicio, soldados.
2. Fotos actuales de lugares/monumentos/placas (memoriales, edificios, calles, carteles de calle, ciudad en panorámica) con sello sepia.
3. Documentos y objetos: escaneos de manuscritos, carteles/leyes (p. ej. Leyes de Núremberg), mapas/planos de campo, portadas de libros, carpetas de archivo, micrófono de radio, sobre y pluma.
4. Fragmentos de **película de archivo** real (multitudes, camiones, discursos).
5. **Imágenes generadas por IA** de recreación histórica (niños con maletas, retrato de un niño, aviadora, camión de noche, interiores). OJO: choca con la regla "material real primero"; en los videos nuevos usarlas solo como último recurso.
6. Tomas de "relleno" metafórico: estantería de libros, cielo/valle, vía de tren, manzana sobre libro, ropa tendida.

## Tarjetas de texto (únicas gráficas)
- **Tarjeta de cita**: fondo marrón casi negro, texto en **serif** (tipo Georgia/Times) blanco hueso, centrado, con la cita entre comillas «…» y debajo el autor en pequeño (ej. «La familia Stauffenberg será exterminada hasta el último miembro.» — Heinrich Himmler). Se usa ~1 min dentro del video.
- **Tarjeta de suscripción** (~min 2:00): misma estética; texto **"Historias que empiezan donde terminan los libros"** y botón marrón rojizo **"SUSCRÍBETE"**.
- **Tarjeta final sobre negro**: pregunta de cierre en serif (ej. "¿Se puede culpar a un niño de catorce años por lo que le enseñaron a creer?") + línea pequeña subrayada **"Te leo en los comentarios"**. Sirve de llamada a comentar.
- No hay lower-thirds, ni rótulos de fechas/lugares, ni números de capítulo, ni rótulos con nombres sobre las fotos.

## Hook (primeros 60 s)
Planos lentos: paisaje con niebla → niños de espaldas con maletas → casa del hogar → documento manuscrito → ruinas de la sala de la bomba → retrato de Stauffenberg → camión de noche → biblioteca → memorial. Un plano ≈ 6 s, de a pares con ligero cambio de encuadre.
Juventud: ruinas de la Cancillería → edificio monumental → niño soldado con Cruz de Hierro → Hitler → Goebbels condecorando a un niño → multitud con Panzerfaust → prisioneros adolescentes.

## Qué falta por revisar (cuando termine la transcripción)
Voz del narrador, música de fondo y estructura narrativa del video de las Juventudes Hitlerianas. Transcripciones en `analisis/` (se generan con `analisis/transcribir.py`).
