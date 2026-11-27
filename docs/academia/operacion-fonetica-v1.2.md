# Evaluación de IF‑MDD en EOI Pronunciation Lab

Resultados del 27 de noviembre de 2026. Se conserva el laboratorio de la [candidata v1.2](https://github.com/RichardStine89/eoi-english-academy/commit/175c86a9069c9b08d610255e5ac485ef3751b52d). IF‑MDD detecta más errores anotados que ZIPA en las muestras cotejadas. La precisión del diagnóstico cae al 28,2 % en la voz hispanohablante reservada para prueba por los autores. Los filtros ensayados quedan por debajo de los mínimos para integrar el modelo o habilitar una corrección automática.

## Muestras y métricas

Se reutilizaron las 48 tomas de español L1 de L2‑ARCTIC con los mismos 144 errores y 869 controles del benchmark de ZIPA. El artículo original reserva NJS para prueba. Las otras tres voces se incluyen en entrenamiento o validación, sin manifiestos que permitan distinguir la partición exacta de cada grabación. El ajuste de los filtros usó solo esas tres voces y se aplicó a NJS sin cambiar los umbrales. El diagnóstico inicial ya incluía NJS. La evaluación de los filtros es retrospectiva y aporta una sola voz reservada por el estudio. SpeechOcean762 aporta una comprobación entre corpus, con voces de mandarín L1 y referencia estadounidense. [Particiones de IF‑MDD](https://secondtonumb.github.io/ICASSP2026.pdf#page=3) · [L2‑ARCTIC](https://psi.engr.tamu.edu/l2-arctic-corpus/) · [SpeechOcean762](https://www.openslr.org/101/)

El cotejo reduce las etiquetas al inventario fonético común y alinea por distancia de edición, sin usar los intervalos de la anotación para seleccionar la salida del modelo. Un diagnóstico exacto exige acertar el fonema sustituto o la omisión. Una etiqueta equivocada sobre un error cuenta como aviso incorrecto y como error sin diagnosticar. La sensibilidad efectiva incluye las abstenciones. La especificidad se calcula sobre controles evaluados y se acompaña de cobertura. Con abstenciones, el valor sobre todos los controles es menor.

| Corpus y motor | Diagnósticos exactos | Precisión | Sensibilidad efectiva | Especificidad | F1 | Cobertura |
|---|---:|---:|---:|---:|---:|---:|
| L2‑ARCTIC · ZIPA vigente | 0/144 | Sin avisos | 0 % | 100 % | 0 % | 79,8 % |
| L2‑ARCTIC · ZIPA con indicios libres | 1/144 | 25,0 % | 0,7 % | 99,6 % | 1,4 % | 79,8 % |
| L2‑ARCTIC · IF‑MDD | 111/144 | 60,0 % | 77,1 % | 92,4 % | 67,5 % | 100 % |
| SpeechOcean762 · ZIPA vigente | 1/50 | 100 % de un aviso | 2,0 % | 100 % | 3,9 % | 33,9 % |
| SpeechOcean762 · IF‑MDD | 12/50 | 22,6 % | 24,0 % | 75,0 % | 23,3 % | 100 % |

En L2‑ARCTIC, IF‑MDD obtuvo 803 negativos correctos, 66 avisos falsos en controles, 8 diagnósticos equivocados y 25 errores sin aviso. Acertó 93/117 sustituciones y 18/27 omisiones. La alineación indicó 9 inserciones y acertó 6 de las 9 anotadas en posición y fonema. Las inserciones se contabilizan aparte. En SpeechOcean762 hubo 9 negativos correctos, 3 falsos avisos en controles y 38 etiquetas equivocadas en posiciones con errores. El 100 % de cobertura indica que el cotejo procesó todos los puntos seleccionados. La referencia y la alineación pueden producir diferencias en segmentos distintos al objetivo. El resultado de detección binaria de 50/50 en esa muestra tiene escaso valor para decidir qué corregir.

| Voz L2‑ARCTIC | Aciertos | Falsos avisos en controles | Diagnósticos equivocados | Precisión | Sensibilidad |
|---|---:|---:|---:|---:|---:|
| EBVS · ajuste | 36/43 | 14/208 | 2 | 69,2 % | 83,7 % |
| ERMS · ajuste | 33/37 | 18/209 | 2 | 62,3 % | 89,2 % |
| MBMPS · ajuste | 31/37 | 8/218 | 2 | 75,6 % | 83,8 % |
| NJS · evaluación | 11/27 | 26/234 | 2 | 28,2 % | 40,7 % |

| Dirección | Aciertos totales | Controles del fonema esperado | Precisión total | Aciertos en NJS | Decisión |
|---|---:|---:|---:|---:|---|
| /z/ → /s/ | 37/40 | 17 | 94,9 % | 7/9 | Prioridad para un nuevo conjunto independiente. Faltan controles y voces de evaluación. |
| /ð/ → /d/ | 21/25 | 28 | 60,0 % | 3/5 | Bloqueada por precisión y falta de voces. |
| /ɪ/ → /iː/ | 20/24 | 84 | 62,5 % | 0/1 | Bloqueada por precisión y falta de positivos en prueba. |
| /θ/ → /t/ | 4/4 | 8 | 80,0 % | Muestra insuficiente | Bloqueada por precisión y tamaño. |
| /ʊ/ → /uː/, /æ/ → /ʌ/, /b/ → /v/, omisiones y demás direcciones | Menos de 20 errores por dirección | Variable | Muestra insuficiente | Muestra insuficiente | Solo práctica y escucha. |

## Reducción de falsos avisos

Se probaron la probabilidad en la marca del decodificador, el máximo del fonema predicho en ±2 cuadros y la diferencia entre este máximo y el del fonema esperado en esa ventana. Para elegir cada corte se exigió al menos 90 % de precisión, 75 % de cobertura y diez avisos en las tres voces de ajuste. Entre los cortes admisibles se maximizó la sensibilidad efectiva. Las omisiones carecen de un fonema predicho en ese punto. Estos filtros se abstienen ante ellas. Sus probabilidades son señales de emisión acústica.

| Filtro | Precisión y sensibilidad en ajuste | Aciertos en NJS | Falsos avisos en controles NJS | Precisión en NJS | Sensibilidad efectiva | Cobertura NJS |
|---|---:|---:|---:|---:|---:|---:|
| Sin filtro adicional | 68,5 % · 85,5 % | 11/27 | 26 | 28,2 % | 40,7 % | 100 % |
| Probabilidad en la marca | 81,8 % · 7,7 % en el corte 0,50 | Sin corte admisible | — | — | — | — |
| Máximo local ≥0,90 | 96,1 % · 41,9 % | 6/27 | 3 | 66,7 % | 22,2 % | 88,5 % |
| Margen local ≥0,75 | 90,3 % · 47,9 % | 6/27 | 3 | 66,7 % | 22,2 % | 88,5 % |
| Coincidencia con la secuencia libre ZIPA | 76,5 % · 11,1 % | 0/27 | 8 | 0 % | 0 % | 88,5 % |
| Coincidencia con indicios del laboratorio ZIPA | 100 % de un aviso · 0,9 % | 0/27 | 1 | 0 % | 0 % | 85,4 % |

Ambos cortes locales elevaron la especificidad en controles evaluados de NJS del 88,9 % al 98,6 %, con 23 controles y 7 errores anotados derivados a revisión. Sobre los 234 controles originales hubo 208 negativos correctos antes y después. El F1 se mantuvo en 33,3 %. La mejora de precisión implicó perder cinco aciertos. Los 11 aciertos del modelo sin filtrar fijan un techo del 40,7 % para una regla que se limite a retirar avisos en NJS.

Se ensayó un filtro léxico de palabra completa para las variantes admitidas de *with*, *either*, *neither* y *route*. Pasó las pruebas con secuencias controladas y ningún aviso de la muestra coincidió con esas variantes. Queda pendiente medir grabaciones británicas anotadas. El inglés regional admite diferencias como la distribución de FOOT–STRUT. La etiqueta del corpus y las variantes del léxico estadounidense sirven para este cotejo. Para evaluar al alumno, deben contrastarse con la palabra, la variedad y la inteligibilidad en contexto. [IPA y enlace de /r/](https://dictionary.cambridge.org/help/phonetics.html) · [Atlas dialectal británico](https://doi.org/10.1017/jlg.2022.2)

## Ejecución y decisión

- IF‑MDD CTC `de46aaf5778c5759c003ffa17657176fee772e77`, código `cca150ec4ff00e01d61a613092d1d178e661dfb2`. Código y paquete CTC con licencia Apache‑2.0. Se cargó el encoder completo del paquete CTC y se usó la configuración de WavLM Large `c1423ed94bb01d80a3f5ce5bc39f6026a0f4828c`. L2‑ARCTIC se usó para investigación conforme a su licencia CC BY‑NC 4.0. Los pesos, los corpus y los informes de tomas permanecen en cachés locales. [Código y alcance de la licencia](https://github.com/Secondtonumb/IF-MDD#license) · [Paquete CTC](https://huggingface.co/Haopeng/CTC_for_IF-MDD/tree/de46aaf5778c5759c003ffa17657176fee772e77) · [WavLM Large](https://huggingface.co/microsoft/wavlm-large/tree/c1423ed94bb01d80a3f5ce5bc39f6026a0f4828c)
- Windows 11 x64, Ryzen 9 7900X, seis hilos CPU y Python 3.12 aislado. El ensayo usó PyTorch y TorchAudio 2.7.1 CPU, Transformers 4.57.0, Flashlight Text 0.0.7, NumPy 2.4.4 y SoundFile 0.14.0. La versión específica de Transformers estaba retirada en PyPI y se limita a este entorno de investigación. El encoder ocupa 1.262.009.603 bytes y el cabezal 2.239.857. Carga aproximada de 3,1 s, pico de 2.729 MiB y medianas de 0,44 s en L2‑ARCTIC y 0,52 s en SpeechOcean762. Estas mediciones incluyen decodificación y lectura local, con los dos lotes ejecutados en paralelo.
- Se ejecutó una reproducción revisada del grafo y el decodificador por haz del ejemplo, con los pesos fijados y sin importación remota dinámica. El WAV distribuido produjo 45 etiquetas y 241 cuadros con marcas ordenadas. La salida comentada por los autores contiene 43 etiquetas y 221 cuadros. PyAV y TorchAudio conservaron la duración de 4,826 s tras remuestrear. La correspondencia exacta con el ejemplo publicado sigue pendiente. Las marcas son centros aproximados de emisión CTC, con paso de 20 ms. No delimitan por sí solas el principio y el final de un fonema. [Ejemplo revisado](https://github.com/Secondtonumb/IF-MDD/blob/cca150ec4ff00e01d61a613092d1d178e661dfb2/inference.py)
- El ensayo se completó con los pesos locales. El silencio y la toma de 125 ms quedaron sin señal suficiente. El ruido blanco devolvió únicamente etiquetas de silencio. En once tomas NJS, la mediana de distancia de edición por fonema canónico fue 14,7 % con el guion correspondiente y 89,7 % al intercambiarlo por otro. Estas pruebas apoyan revisar primero la lectura y la señal. La detección automática de errores de lectura sigue sin validación. Las 12 pruebas unitarias existentes pasaron. Los informes y la ruta acústica de respaldo conservan el esquema de la candidata.
- Pronunciada 1.1.0 original con ZIPA int8 obtuvo 0/144 diagnósticos exactos en L2‑ARCTIC y 4/50 en SpeechOcean762. Cambiar su política de alineación aumentó cobertura y mantuvo 0/144. CROTTC‑IF y MDD‑LLM carecen de licencia explícita para los pesos publicados y quedan sin ejecutar. En MPL‑MDD se localizó código MIT y recetas que requieren un directorio de pesos, sin un paquete de inferencia listo verificado. El benchmark de Burgos y colaboradores aporta metodología para separar evaluaciones por hablante y lengua materna. [Pronunciada 1.1.0](https://github.com/moglearn/pronunciada/blob/v1.1.0/docs/LICENSING.md) · [MPL‑MDD](https://github.com/Mu-Y/mpl-mdd) · [Pronunciation Scoring Benchmark](https://github.com/fjburgosf/pronunciation-scoring-benchmark)

En Windows se utiliza el [lanzador del laboratorio existente](../../modules/pronunciation-lab/Abrir.cmd) y la [guía de escucha y repetición](pronunciacion.md). Revisa el guion, escucha el fragmento, contrástalo con una referencia británica y repite en condiciones parecidas. Si el audio falta o la comparación sigue ambigua, deja el contraste pendiente. Mantén sin calificación automática las hipótesis, la inteligibilidad, el ritmo, la acentuación y la entonación. Los cortes de esta fase pertenecen al ensayo histórico. La aceptación corresponde a Dirección Académica y se rige por el [criterio definitivo](validacion-fonetica-v1.2.md).

## Reanudación local

Los scripts de ensayo quedan en `modules/pronunciation-lab/.cache/`, excluidos de Git. `ifmdd_probe.py` ejecuta el decodificador con `--beam` y puede extraer el perfil local con `--confidence-profiles`. `ifmdd_compare.py` coteja las predicciones congeladas y `ifmdd_calibrate.py` reconstruye la partición por voz, los cortes y el cotejo con ZIPA. En `%TEMP%/eoi-ifmdd-audit/` se conservan el entorno, las predicciones, `metrics-es.json`, `metrics-so.json` y `calibration-es.json`. Reutiliza estos resultados para continuar la evaluación. Los siguientes ensayos requieren ejemplos nuevos, separados por hablante, con doble revisión y variantes británicas anotadas.

| Archivo público de origen | SHA‑256 |
|---|---|
| `perceived_ssl.ckpt` | `304670a95f15f90b3787a59cc795d8b7ab6f76d72dc0770721a0f720ca9f9c18` |
| `model.ckpt` | `d1131b48e67758775a07edaff0d77750d037fd4bcf51615adfdf8d0d16077a2a` |
| `tokenizer.ckpt` | `7c18649ce9e77f51b9c68288fdfc9ab16696c4e9a47600fc1f7f441ce8ac6752` |
