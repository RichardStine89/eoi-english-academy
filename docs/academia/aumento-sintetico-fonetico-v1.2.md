# Piloto de aumento sintético por contraste

Reanudación desde `17fb8527e2b0056f2b08695de9029f50c51dbca7`. Se probaron dos contrastes en CPU Windows y sin servicios de síntesis remotos. El mínimo definitivo sigue siendo sensibilidad efectiva ≥80 %, precisión ≥95 % y cobertura ≥90 %, con casos suficientes, voces y guiones independientes y controles de variantes británicas. Ningún resultado del piloto habilita correcciones automáticas. [Protocolo definitivo](validacion-fonetica-v1.2.md)

## Método y control de la síntesis

Masson y Carson‑Berndsen estudiaron cómo responde el ASR a variantes sintéticas en inglés con influencia del español. Usaron 4.401 tomas de cuatro voces de L2‑ARCTIC, Azure TTS y Wav2Vec2. En la revisión humana de 100 muestras de su ensayo de epéntesis, solo el 56 % de las inserciones solicitadas se oyó en la síntesis y el ASR señaló epéntesis en el 21 % de las muestras. El trabajo aporta un método para estudiar confusiones de ASR. El efecto sobre clasificadores MDD por contraste exige medir transferencia a voces humanas. La licencia del manuscrito no establece permiso para reutilizar sus audios sintéticos. [Estudio, secciones 4 y 5.2](https://doi.org/10.21437/SynData4GenAI.2024-17)

| Motor | Uso y alcance |
|---|---|
| SAPI y Microsoft Zira Desktop | Generó en local 48 WAV con una voz estadounidense ya instalada. Cada pareja conserva palabra, frase y velocidad y solicita un único cambio mediante SSML IPA. Los audios se conservaron en local. [SAPI](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ee431815(v=vs.85)) |
| Kokoro ONNX INT8 | Generó 12 WAV dentales con `bf_emma`, voz británica según la ficha. Se usó un paquete Apache‑2.0 fijado, de 92.361.116 bytes, con ONNX Runtime CPU y fonemas explícitos. La voz sintética sirve para desarrollar el método. La comprobación de variantes válidas requiere controles humanos. [Paquete fijado](https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/tree/a70f0e45c1cc0df9abdfbfa0f6dee9073579ee99) |
| eSpeak NG y Piper | eSpeak NG ofrece fonemas explícitos y una distribución Windows GPL‑3.0 o posterior. Piper admite IPA y exige comprobar la licencia de cada voz. La revisión original de Cori documenta el corpus de dominio público. Queda por confirmar el alcance de la licencia sobre ese peso concreto. Ambas rutas quedan como alternativas de investigación. [eSpeak NG](https://github.com/espeak-ng/espeak-ng) · [Piper y licencias de voces](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/LICENSING.md) |

Se comprobaron las huellas y la diferencia de las señales PCM de cada pareja. Ambos reconocedores, IF‑MDD y HuBERT, decodificaron el audio libremente y sus salidas se cotejaron con el mismo guion. Se conservó la pareja solo si ambos reconocían la categoría solicitada en las dos tomas y la medición acústica era compatible con el cambio. El filtro vocálico pedía una reducción de al menos 15 Hz en F1. El dental buscaba indicios de cierre o liberación más marcados o menor fricación sostenida. Son reglas exploratorias sobre ventanas estimadas. Se registraron los resultados discordantes y se excluyeron del entrenamiento.

| Contraste y voz | Pares | Ambos reconocedores coinciden | Medición acústica compatible | Pares retenidos para el ensayo |
|---|---:|---:|---:|---:|
| /ð/ → /d/ · Zira | 12 | 2 | 6 | 0 |
| /ɪ/ → /iː/ · Zira | 12 | 7 | 12 | 7 |
| /ð/ → /d/ · Kokoro | 6 | 2 | 3 | 1 |

En la vocal, las diferencias medianas en las ventanas medibles fueron −94 Hz en F1, +754 Hz en F2 y +15 ms de duración. No hay dictámenes humanos. Se prepararon dos fichas ciegas por lote, con los 60 audios seudonimizados y la clave fuera de las carpetas de revisión. La confirmación perceptiva requiere identificar el sonido tras *Say* por separado y dejar inciertos los casos dudosos. El entrenamiento de abajo usa solo la comprobación automática y tiene alcance exploratorio.

## Transferencia a las mismas grabaciones humanas

Se reutilizaron las observaciones congeladas de L2‑ARCTIC, se reconstruyeron los rasgos y se comprobó que el clasificador con voz humana reproduce los recuentos anteriores. EBVS y ERMS se usaron para el ajuste, MBMPS para la calibración y NJS para el cotejo retrospectivo. Los sintéticos entraron solo en el ajuste con un peso acumulado equivalente al 25 % del peso humano, aproximadamente el 20 % del peso combinado. Las pruebas no usaron el audio, guion ni voz de la reserva final. El corte fijo 0,50 es el punto de comparación histórico. Ninguna variante aumentada encontró en MBMPS un corte que cumpliera 80/95/90.

| Dirección y método | Aciertos NJS | Falsos avisos sobre controles | Precisión | Sensibilidad efectiva | Cobertura |
|---|---:|---:|---:|---:|---:|
| /ɪ/ → /iː/ · ZIPA operativo | 0/1 | 0/24 | Sin avisos | 0 % | 76 % |
| /ɪ/ → /iː/ · acústico, ajuste humano | 1/1 | 3/24 | 25 % | 100 % | 92 % |
| /ɪ/ → /iː/ · más siete pares Zira | 1/1 | 6/24 | 14,3 % | 100 % | 92 % |
| /ð/ → /d/ · ZIPA operativo | 0/5 | 0/9 | Sin avisos | 0 % | 50 % |
| /ð/ → /d/ · acústico, ajuste humano | 3/5 | 3/9 | 50 % | 60 % | 100 % |
| /ð/ → /d/ · más un par Kokoro | 2/5 | 1/9 | 66,7 % | 40 % | 100 % |

El clasificador acústico y neuronal de la vocal mantuvo 0/1 aciertos y tres falsos avisos. El híbrido dental mantuvo 2/5 aciertos y pasó de dos a tres falsos avisos. El aumento sintético ensayado se descarta para uso operativo. La prioridad es reunir etiquetas humanas independientes y probar si una síntesis con más voces, posiciones y realizaciones validadas aporta una mejora que conserve sensibilidad, precisión y cobertura. Un único caso positivo vocálico y cinco dentales en NJS impiden estimar la generalización.

## Acceso a muestras humanas

- **MRPL2 v1.1** declara CC BY 4.0 con los archivos restringidos. Solicita desde tu cuenta de Zenodo el subconjunto de español L1 a 16 kHz, los TextGrid, las secuencias esperadas y realizadas, y los identificadores seudonimizados de voz y guion. Su origen en CMU ARCTIC exige deduplicar frases frente a los ensayos anteriores. [Registro](https://zenodo.org/records/22690685) · [Procedimiento](https://help.zenodo.org/docs/share/access-requests/request-access/)
- **EpaDB** ofrece acceso de investigación bajo CC BY‑NC‑ND 4.0 según el repositorio de los autores. Pide el canal actual, la versión, las tomas con doble anotación y el manifiesto de las 20 voces reservadas descritas en 2021. La primera versión tuvo un segundo anotador en 200 tomas. Sus referencias estadounidenses requieren controles británicos separados. Las dos solicitudes están preparadas localmente. [Contacto y condiciones](https://github.com/JazminVidal/gop-dnn-epadb#introduction) · [Anotaciones](https://www.isca-archive.org/interspeech_2019/vidal19_interspeech.pdf#page=2) · [Partición](https://www.isca-archive.org/interspeech_2021/vidal21_interspeech.pdf#page=3)

## Reanudación local

- Generadores comprobados en [PowerShell 7 con SAPI](../../modules/pronunciation-lab/tests/generate_synthetic_contrasts.ps1) y [Python con ONNX Runtime](../../modules/pronunciation-lab/tests/generate_kokoro_dental.py). Escriben en un directorio nuevo fuera del repositorio. El segundo comprueba las huellas del bundle antes de inferir.
- En `%TEMP%/eoi-mdd-phase5/` constan `tts/`, `kokoro/`, sus manifiestos, el bundle fijado y las salidas `synthetic-augmentation-results.json`, `kokoro-dental-augmentation-results.json` y `zipa-njs-current.json`. Los paquetes de revisión están en `escucha-sintetica-v1/` y `escucha-kokoro-v1/`. El análisis reutiliza `modules/pronunciation-lab/.cache/synthetic_augmentation.py`, las observaciones históricas y el Python de laboratorio. Se conservaron los audios y predicciones en local.
- Para volver a cotejar sin sintetizar ni ejecutar IF‑MDD de nuevo, ejecuta ese script con `--source tts` o `--source kokoro` y un `--output` nuevo fuera del repositorio. El programa reutiliza las emisiones congeladas y vuelve a calcular el cotejo HuBERT y las medidas acústicas.
- Pasaron las 21 pruebas de regresión del laboratorio. Se comprobaron los enlaces, los recuentos, las huellas de los lotes y que las dos reservas finales conservaban sus huellas previas.
- Los borradores editables están en `modules/pronunciation-lab/.cache/acceso-corpus-foneticos.md`. El laboratorio operativo sigue disponible. La investigación permanece abierta.
