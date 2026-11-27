# Alineación temporal y diagnósticos por contraste

Reanudación desde `1fa0e1e351b4b80de6a4a243b14a557465d7fe23`. La aceptación definitiva exige sensibilidad efectiva ≥80 %, precisión ≥95 % y cobertura ≥90 %, por contraste y con voces y guiones independientes. Los niveles 60/90 y 70/95 orientan experimentos y herramientas complementarias. 90/95 y 95/99 describen metas superiores. Ningún ensayo de esta fase habilita correcciones automáticas. La reserva final permanece cerrada. [Protocolo de aceptación](validacion-fonetica-v1.2.md)

## Alineación CTC medida

Se reutilizaron las 48 tomas históricas de L2‑ARCTIC y el IF‑MDD CTC fijado. La extracción de emisiones por cuadro conservó las 48 secuencias, marcas y probabilidades publicadas en el cotejo local. Se alineó de nuevo la secuencia libre con Viterbi CTC y se probaron cambios espectrales a ±30 ms en transiciones vocal–consonante. Se compararon con intervalos manuales solo las posiciones donde la etiqueta emitida coincide con el sonido anotado. Los 896 intervalos comparados cubren 896 de 986 segmentos anotados sin omisión. El guion canónico viene de las anotaciones históricas. [Corpus L2‑ARCTIC](https://psi.engr.tamu.edu/l2-arctic-corpus/) · [Benchmark reproducible](../../modules/pronunciation-lab/tests/benchmark_ctc_contrasts.py)

| NJS | Método | Inicio y fin, error mediano | Solapamiento mediano | Intervalos comparados |
|---|---|---:|---:|---:|
| Vocales | Marcas del haz | 22,5 / 32,5 ms | 0,45 | 86/103 |
| Vocales | Viterbi CTC | 12,5 / 12,5 ms | 0,66 | 86/103 |
| Vocales | Viterbi con ajuste espectral | **10 / 10 ms** | **0,69** | 86/103 |
| Consonantes | Marcas del haz | 27,5 / 22,5 ms | 0,57 | 132/154 |
| Consonantes | Viterbi CTC | 12,5 / 12,5 ms | 0,71 | 132/154 |
| Consonantes | Viterbi con ajuste espectral | **12,5 / 10 ms** | **0,75** | 132/154 |

Sumar las probabilidades de las rutas CTC del fonema canónico y las de un sustituto, con el mismo contexto de la secuencia libre y sin ajustar cortes, no mejoró el diagnóstico en las tres direcciones con más positivos. Los recuentos excluyen otros errores porque el ensayo compara únicamente las dos realizaciones indicadas. Se mantuvo la abstención cuando la posición no se pudo alinear. [GOP sin segmentación](https://arxiv.org/abs/2507.16838) · [GOP CTC con sustituciones restringidas](https://www.isca-archive.org/interspeech_2025/parikh25_interspeech.pdf) · [CTC con información contextual](https://aclanthology.org/2026.bea-1.3/)

| Dirección | Positivos y controles en NJS | Aciertos y falsos avisos, haz → suma de rutas | Estado |
|---|---:|---:|---|
| /z/ → /s/ | 9 y 5 | 7 y 1 → 7 y 1 | 77,8 % de sensibilidad, 87,5 % de precisión, 100 % de cobertura. Bloqueada. |
| /ð/ → /d/ | 5 y 9 | 3 y 4 → 3 y 4 | 60 % de sensibilidad, 42,9 % de precisión, 100 % de cobertura. Bloqueada. |
| /ɪ/ → /iː/ | 1 y 24 | 0 y 4 → 0 y 4 | Una sola realización positiva. Bloqueada. |
| /b/ → /v/ | 1 y 6 | 0 y 0 → 0 y 0 | Una sola realización positiva y quedó sin detectar. Bloqueada. |
| /θ/ → /t/, /θ/ → /s/, /ʊ/ → /uː/, /æ/ → /ʌ/ | 0 positivos por dirección | Sin sensibilidad estimable | Controles escasos y falta de positivos. Bloqueadas. |

## Combinaciones acústicas y clases legítimas

Se entrenó por separado para `/ð/ → /d/` y `/ɪ/ → /iː/` con EBVS y ERMS, se intentó calibrar con MBMPS y se aplicaron los cortes a NJS. Se combinaron duración, periodicidad, energía espectral o F1/F2, contexto y evidencia CTC. Ninguna configuración superó 80/95/90 durante la calibración. Con un corte fijo de diagnóstico, el híbrido dental pasó de cuatro a un aviso sobre nueve controles de NJS y conservó tres aciertos de cinco. Alcanzó 75 % de precisión, 60 % de sensibilidad y 100 % de cobertura. En la vocal, una versión acústica acertó el único positivo y dio tres avisos sobre 24 controles, con 25 % de precisión y 92 % de cobertura. Estas muestras sirven para estudiar errores, todavía no sostienen un clasificador operativo.

Un segundo ensayo corrigió por separado el desplazamiento de inicio y fin estimado en EBVS y ERMS. En NJS, el solapamiento mediano de las ventanas pasó de 0,466 a 0,687 para `/ð/` y de 0,379 a 0,720 para `/ɪ/`. Al volver a extraer los rasgos dentro de esas ventanas, el clasificador acústico dental pasó de 3 a 4 aciertos de 5 y de 3 a 4 falsos avisos de 9. La precisión siguió en 50 %. En la vocal, pasó de un acierto y tres falsos avisos a cero avisos con 92 % de cobertura. La mejora temporal no se tradujo en una ganancia que conserve las tres métricas.

La alineación más fina permite medir mejor el segmento. La decisión sobre legitimidad también requiere distinguir una oclusión dental legítima de /ð/, la duración y calidad de `/ɪ/` y `/iː/`, y las variantes vocálicas. El control de Warwick mostró que cuatro voces que produjeron dos realizaciones legítimas de BATH cambiaron su F2 mediana por donante en unos −448 Hz con una grabadora y −508 Hz con el micrófono de PC. Las dos capturas por producción no constituyen voces ni tomas independientes. [Controles vocálicos de Warwick](https://wrap.warwick.ac.uk/id/eprint/138368/) · [Realizaciones y contexto de /ð/](https://pmc.ncbi.nlm.nih.gov/articles/PMC2981115/)

## Otros alineadores y modelos

**CUPE‑3‑en** funcionó en Windows mediante CPU y los entornos existentes. El paquete AGPL‑3.0 de 54.184.600 bytes se comprobó por SHA‑256 y se cargó en formato Safetensors. El código de Bournemouth Forced Aligner 2.1 se usó en una caché aislada bajo GPL‑3.0. Con la secuencia esperada de 12 tomas NJS, obtuvo 381 intervalos utilizables frente a 368 del método anterior. En 368 intervalos pareados, el error mediano de inicio y fin bajó de 22,5/22,5 a 17,5/17,5 ms y el solapamiento mediano subió de 0,544 a 0,638. Tardó 229 ms por toma en mediana, con cuatro hilos. El solapamiento en cinco casos `/ð/ → /d/` empeoró de 0,544 a 0,467. CUPE usa alineación forzada con una secuencia explícita. Sus resultados de tiempo no son diagnóstico y el conjunto de intervalos difiere del de la tabla CTC. [Pesos fijados](https://huggingface.co/Tabahi/CUPE-3-en/tree/d6c2f6b5e28fc7a2841e1519e18eb12ddcfc045d) · [Evaluación de los autores](https://speech-industry.github.io/bournemouth-forced-aligner/evaluation/)

En un ensayo posterior se exportaron las ventanas CUPE de las 48 tomas para repetir solo la extracción de rasgos y el ajuste por dirección con las mismas particiones. En NJS, el híbrido dental obtuvo 2/5 aciertos y 3/9 falsos avisos, con 40 % de precisión, 40 % de sensibilidad y 100 % de cobertura. En `/ɪ/ → /iː/` no emitió avisos y cubrió el 84 %. Ningún corte pasó la calibración. Las ventanas densas tuvieron valor para medir límites, con resultados insuficientes como entrada de estos clasificadores.

FALCON publica código MIT y describe un alineador neuronal a 10 ms. Antes de un ensayo local queda por verificar la publicación utilizable y la licencia del checkpoint concreto. SNU SLP Lab publica pesos para reconocer fonemas de aprendientes de inglés L1 coreano, con 9,05 % de PER en su propia prueba. Su ficha no declara licencia explícita para esos pesos. Se conservaron como líneas distintas de investigación. Otra conversión ONNX de los pesos Wav2Vec2 eSpeak usados como profesor de OpenPronounce aporta un formato diferente. La procedencia común limita su valor como segundo voto. [FALCON](https://github.com/MLSpeech/FALCON) · [SLP Lab](https://huggingface.co/slplab/wav2vec2-large-robust-L2-english-phoneme-recognition) · [Conversión ONNX](https://huggingface.co/Alimehdi973/wav2vec2-espeak-onnx-int8)

## Datos y modelos comprobados

| Recurso | Uso comprobado y actuación pendiente |
|---|---|
| Warwick North–South CLASS | CC BY 4.0. Se verificaron 400 archivos con límites manuales, 200 producciones, cuatro voces y dos micrófonos simultáneos. Son controles dialectales de desarrollo. [Repositorio original](https://wrap.warwick.ac.uk/id/eprint/138368/) |
| Inglés escocés y DIAPIX‑FL | Verificados 9.514 registros vocálicos de 34 voces escocesas, con alineación corregida y CC BY 4.0. La tabla derivada de DIAPIX‑FL contiene 10.956 vocales inglesas de diez voces de español L1, con CC BY 4.0. El corpus completo se ofrece con CC BY 3.0. Son medidas acústicas y categorías de referencia. Los errores que merecen corrección requieren adjudicación. [Escocés](https://doi.org/10.18710/KH6YDI) · [Tabla DIAPIX‑FL](https://zenodo.org/records/14411925) · [Corpus original](https://datashare.ed.ac.uk/items/1bd01093-dfa6-4448-970f-685a89278439/full) |
| SIAEW | CC BY 4.0 y archivo abierto. Los especialistas documentan 1.056 estímulos de 88 palabras, dos voces y pasos de modificación perceptiva. Las valoraciones son de acento percibido. Puede servir para ensayos controlados de vocales, aspiración y consonantes, con los casos modificados marcados como tales. [Corpus](https://zenodo.org/records/6371655) · [Método](https://www.isca-archive.org/interspeech_2022/perezramon22_interspeech.pdf) |
| MRPL2, EpaDB e IPCE‑IPAC | Son candidatos prioritarios para datos especializados en español L1. MRPL2 necesita autorización de Zenodo. La publicación de EpaDB describe etiquetas fonéticas expertas y permiso de investigación CC BY‑NC‑ND 4.0. El enlace original consultado devolvió 404. IPCE‑IPAC documenta límites revisados pero indica que el corpus inglés L2 carece de acceso libre. Hace falta solicitar acceso a los titulares o aportar una copia autorizada. [MRPL2](https://zenodo.org/records/22690685) · [EpaDB de los autores](https://github.com/JazminVidal/gop-dnn-epadb) · [IPCE‑IPAC](https://www.mdpi.com/2226-471X/8/4/280#sec9) |
| ISLE y otras anotaciones expertas | ISLE ofrece errores de fonema y acento revisados por lingüistas, con 46 voces de alemán o italiano L1. Su acceso sin coste para uso no comercial requiere el procedimiento de ELRA. El estudio de Elhazaz Walsh documenta 3.522 errores de escolares de español L1. La licencia y disponibilidad del audio no se verificaron. [ISLE](https://catalogue.elra.info/en-us/repository/browse/ELRA-S0083/) · [Elhazaz Walsh](https://rua.ua.es/dspace/bitstream/10045/81352/1/PLN_61_10.pdf) |

Queda pendiente reunir voces adultas de español L1 y guiones independientes con errores y controles por dirección. El siguiente ensayo con etiquetas adjudicadas debe comparar por separado la contribución de la segmentación CTC, la evidencia neuronal, la acústica y el contexto, y congelar el clasificador antes de abrir la evaluación final.

## Checkpoints

- `%TEMP%/eoi-mdd-phase4/ifmdd-es-frames.npz` guarda las emisiones congeladas. SHA‑256 `350af5bfd7da928dcd88a98cafecabc9db8de97219f56be9a5444eeb506080be`. El `ifmdd_probe.py` local admite `--frame-output` y conserva las salidas anteriores.
- `%TEMP%/eoi-mdd-phase4/ctc-contrast-results.json` guarda los resultados de alineación y diagnósticos. El benchmark requiere las emisiones y el `observed-es.json` histórico de `%TEMP%/eoi-ifmdd-audit/` como `--emissions` y `--observations`, respectivamente. Usa el Python y los corpus locales.
- `%TEMP%/eoi-mdd-phase4/multicontrast-acoustics.json`, `multicontrast-timing-bias.json` y `multicontrast-corrected-windows.json` guardan el ensayo por contraste y sus comparaciones. `%TEMP%/eoi-mdd-phase4-corpus/corpus-coverage-dialect-controls.json` conserva los recuentos y huellas de las fuentes acústicas.
- `%TEMP%/eoi-cupe-phase4/cupe-njs-boundaries.json` conserva los resultados de CUPE. La revisión del código es `8b37b8d9efe9868d0f6339c4454635a4666e6cbb`, y el SHA‑256 de los pesos es `afa23b526871b3aef0aa387d802741b8b55891e790cd1070be6f7307771e467a`. La reproducción usa `modules/pronunciation-lab/.cache/cupe_boundary_probe.py --all` en el entorno aislado de IF‑MDD.
- `%TEMP%/eoi-mdd-phase4/multicontrast-cupe.json` conserva el ensayo de rasgos con ventanas CUPE. SHA‑256 `49db740e5241847d8ba82cb4cbb427fe9f8d29f3bf14254beef57c2c45660c7a`. Se reproduce con `modules/pronunciation-lab/.cache/multicontrast_cupe.py` y las ventanas extraídas en `cupe-es-windows.json`.
- Pasaron 21 pruebas de regresión y método, incluidas tres nuevas de suma de rutas, fonemas repetidos y ajuste de fronteras. Los clips, modelos, predicciones y reservas permanecen localmente. La investigación permanece abierta para Dirección Académica.
