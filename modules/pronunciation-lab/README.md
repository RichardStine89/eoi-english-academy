# EOI Pronunciation Lab

Aplicación local de Windows para grabar, revisar y comparar tomas. El [procedimiento docente](../../docs/academia/pronunciacion.md) explica cómo llevar el informe al chat de clases y qué se puede interpretar con él.

## Instalación y apertura

1. Ejecuta [Instalar.cmd](Instalar.cmd) con conexión a internet. Si el laboratorio ya está instalado, el lanzador conserva su entorno virtual y añade las dependencias fonéticas y el modelo verificado. Usa Python 3.12 x64 con Tcl/Tk. Si ya está instalado para Windows, el lanzador lo detecta. También puede reutilizar el Python incluido en el entorno de Codex. Si no tienes ninguno, instala [Python 3.12 para Windows con Tcl/Tk](https://docs.python.org/3.12/using/windows.html#installing-without-ui) o señala una instalación existente mediante `EOI_LAB_PYTHON`.
2. Después, abre [Abrir.cmd](Abrir.cmd) haciendo doble clic. Puedes crear un acceso directo a ese archivo desde el Explorador. El uso normal no requiere conexión, cuenta, GPU, Codex ni comandos. Si mueves el repositorio o desaparece el Python base, vuelve a preparar el entorno virtual desde la ubicación definitiva.
3. Selecciona alumno, nivel, unidad, modo e ID de actividad. Para lectura, repetición y pares mínimos introduce el texto. Elige micrófono o usa **Importar grabación…**. Si Voz de ChatGPT está usando el micrófono, termina la llamada antes de grabar o importa una toma. El límite es 3 min. La importación admite WAV, MP3 y M4A decodificables de hasta 128 MB.
4. Tras **Detener y analizar**, abre **Resultados** y usa **Oír grabación** para comprobar la toma. Con guion, abre **Ver tramos del guion…** y selecciona la palabra para revisar el intervalo o escuchar el fragmento. **Copiar informe** prepara texto breve para el mismo chat y puede incluir parte del guion. **Exportar JSON privado** guarda las medidas descriptivas y los tramos disponibles. Mantén ID de actividad, modo y texto para comparar tomas semejantes.

La ventana abre maximizada. Pulsa **F11** para la vista de lectura a pantalla completa y **Escape** para volver. El control de tamaño cambia la letra del guion. Si el guion es largo, divídelo en fragmentos numerados y comprueba la duración de cada toma. La estimación de palabras por fragmento no fija el tiempo de lectura. Los controles de micrófono y grabación permanecen en la vista de lectura.

La toma queda en `%LOCALAPPDATA%\EOI English Academy\Pronunciation Lab\alumno-XX`, con un informe por intento. **Eliminar esta grabación…** y **Historial de grabaciones…** borran solo la copia local de la toma tras confirmación. Conservan su informe y el original que se haya importado. La separación por alumno se aplica dentro de la interfaz. En un equipo compartido, usa cuentas de Windows separadas si necesitas que cada alumno tenga acceso exclusivo a sus datos.

## Modelo británico y revisión experimental

Durante la instalación, [Instalar.cmd](Instalar.cmd) intenta preparar Kokoro `bf_emma` en la caché local ignorada por Git. Reutiliza los archivos verificados disponibles. El laboratorio base abre y admite modelos de audio autorizados aunque Kokoro no se haya preparado. La generación combina Kokoro 82M ONNX en CPU, su voz británica y un diccionario inglés de Gran Bretaña de eSpeak NG. El texto se procesa en Windows y el modelo recién generado queda en memoria. La ejecución ordinaria no realiza descargas. [Modelo fijado y licencia Apache-2.0](https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/blob/a70f0e45c1cc0df9abdfbfa0f6dee9073579ee99/README.md) · [Ficha de las voces](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md) · [eSpeak NG 1.52.0, GPL](https://github.com/espeak-ng/espeak-ng/blob/1.52.0/COPYING) · [Paquete fijado espeakng-loader](https://pypi.org/project/espeakng-loader/0.2.4/)

En **Modelo británico ▾**, elige velocidad y genera el texto visible. Puedes repetir con **Oír modelo** o comparar con **Oír grabación**. El cuadro de tramos reproduce la palabra inglesa seleccionada por separado. Para un guion largo, usa fragmentos que puedas repetir con comodidad. Trata la voz como modelo sintético y comprueba por escucha las palabras importantes, incluidos los homógrafos, nombres propios y variantes.

En **Resultados**, la casilla **Modo experimental de revisión** empieza desactivada. Actívala y pulsa **Buscar un fragmento para escuchar** para probar IF-MDD con el intento actual. Se limita a /z/ dentro de una palabra entre vocales, con coincidencia temporal entre el guion alineado y la salida del motor. Un tramo solo invita a escuchar. Las notas, el informe, el JSON y el expediente permanecen fuera de este flujo. Desactiva la casilla para seguir con revisión manual.

IF-MDD usa un Python separado del laboratorio y los cinco archivos con SHA-256 fijado en [ifmdd_worker.py](src/ifmdd_worker.py). Se probó con Python 3.12, Torch y TorchAudio 2.7.1 CPU, Transformers 4.57.0 y flashlight-text 0.0.7. La instalación base no descarga estos pesos. Si ya tienes el entorno privado de investigación, el laboratorio lo busca en una instalación local `IF-MDD` dentro de su carpeta de datos o, si no existe, en `%TEMP%\eoi-ifmdd-audit`. Puedes especificar el ejecutable de ese entorno mediante `EOI_IFMDD_PYTHON` y la carpeta que contiene los pesos mediante `EOI_IFMDD_MODELS`. Un entorno temporal se puede perder al limpiar Windows. Si el motor no carga, **Ver tramos del guion…** sigue disponible. [Licencia y código IF-MDD](https://github.com/Secondtonumb/IF-MDD#license) · [Pesos CTC Apache-2.0](https://huggingface.co/Haopeng/CTC_for_IF-MDD)

## Motor y alcance

La instalación base requiere aproximadamente **124 MB de descarga** en Windows x64, incluidos los pesos cuantizados ZIPA de 70,7 MB y las dependencias fonéticas. Una instalación limpia suma unos 54 MB de los paquetes acústicos. Kokoro añade sus archivos verificados y el diccionario de eSpeak NG. En la validación se usó Python 3.12.14, Windows 11 x64 y AMD Ryzen 9 7900X. El cotejo funciona en CPU. Procesa tomas de hasta 30 segundos y guiones de hasta 65 palabras. La función acústica mantiene su límite de tres minutos.

| Componente | Función y licencia |
|---|---|
| Parselmouth 0.4.7 con Praat 6.1.38 | Estimación de frecuencia fundamental por autocorrelación en tramos utilizables. Funciona en CPU sin modelo acústico ni datos de entrenamiento. GPL-3.0-o-posterior. [Proyecto](https://github.com/YannickJadoul/Parselmouth) · [Distribución Windows](https://pypi.org/project/praat-parselmouth/0.4.7/) |
| NumPy 2.4.4 | Cálculos de nivel de señal, actividad y pausas aproximadas. BSD-3-Clause. [Distribución](https://pypi.org/project/numpy/2.4.4/) |
| PyAV 16.1.0 | Decodificación local mediante FFmpeg. BSD-3-Clause en PyAV. Las bibliotecas FFmpeg tienen sus propias condiciones. [Distribución](https://pypi.org/project/av/16.1.0/) · [Licencia de FFmpeg](https://ffmpeg.org/legal.html) |
| sounddevice 0.5.3 y Tcl/Tk | Captura y reproducción locales con PortAudio e interfaz de escritorio. sounddevice tiene licencia MIT y se instala con CFFI y pycparser. Tcl/Tk viene con Python para Windows cuando está seleccionado. [Audio](https://pypi.org/project/sounddevice/0.5.3/) · [Interfaz](https://docs.python.org/3.12/library/tkinter.html) |
| Pronunciada 1.1.0 y ZIPA `zipa-small-crctc-500k` int8 | Alineación CTC y alternativas de fonema con texto conocido. Código Apache-2.0, datos auxiliares con licencias propias y pesos de Zhu et al. CC BY 4.0. ONNX Runtime CPU, Kaldi Native Fbank y SoundFile son las dependencias principales añadidas. [Licencias del motor](https://github.com/moglearn/pronunciada/blob/main/docs/LICENSING.md) · [Pesos de ZIPA](https://huggingface.co/anyspeech/zipa-small-crctc-500k) |

El repositorio conserva el código y las versiones fijadas. El instalador verifica el tamaño y SHA-256 de los pesos y el vocabulario de una revisión de ZIPA, y los guarda en la caché excluida de Git. Durante el análisis se usan los archivos locales. El guion se alinea con un léxico estadounidense (CMUdict) para localizar tramos aproximados. La IPA británica de algunas palabras sirve como referencia docente. El laboratorio ofrece medidas descriptivas y mantiene deshabilitados los avisos, correcciones y notas automáticas. La presentación y la exportación de intentos antiguos también se limitan a estos datos. [Cierre experimental](../../docs/academia/cierre-hibrido-fonetico-v1.2.md)

### Alternativas examinadas

| Candidato | Motivo de la decisión |
|---|---|
| OpenPronounce | Código y modelos AGPL-3.0. El proyecto publica tasas altas de sugerencias rechazadas en su validación y advierte del alcance del conjunto de hablantes. La configuración de referencia puede usar TTS externo. No se verificó su fiabilidad para el modelo británico y los alumnos de la academia. [Licencias](https://openpronounce.github.io/docs/licensing.html) · [Límites](https://openpronounce.github.io/docs/limits.html) |
| Montreal Forced Aligner | Código MIT. El modelo inglés v3.1.0 tiene licencia CC BY 4.0 y carece de designación dialectal. Funciona para alinear texto conocido, con instalación propia y modelo descargable. La alineación no basta para acreditar cambios de fonema. [Instalación](https://montreal-forced-aligner.readthedocs.io/en/latest/installation.html) · [Modelo](https://mfa-models.readthedocs.io/en/latest/acoustic/English/English%20MFA%20acoustic%20model%20v3_1_0.html) |
| eSpeak NG | Motor GPL-3.0-o-posterior de síntesis y conversión de texto a fonemas, con voz inglesa británica. Podría servir como modelo sintético. El análisis de una toma requiere otra técnica. [Proyecto](https://github.com/espeak-ng/espeak-ng) |
| GOP, Kaldi y wav2vec2 fonético | GOP requiere un modelo fonético y calibración con evidencia humana. Kaldi tiene licencia Apache-2.0. El modelo wav2vec2 fonético revisado se publica como Apache-2.0. No hay calibración comprobada aquí para distinguir variantes británicas válidas y errores de estudiantes. [Implementación GOP](https://github.com/kaldi-asr/kaldi/blob/master/src/bin/compute-gop.cc) · [Modelo wav2vec2](https://huggingface.co/facebook/wav2vec2-lv-60-espeak-cv-ft) |
| Whisper | Código y pesos MIT. Puede aportar una transcripción con una descarga de modelo y recursos adicionales. Esa transcripción quedaría como apoyo a una revisión humana. La versión actual prescinde de este componente. [Proyecto](https://github.com/openai/whisper) |

## Validación reproducible

Desde el directorio del módulo, una vez instalado:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Las pruebas unitarias comprueban regresiones acústicas, abstención, informes anteriores, separación de datos y las integraciones opcionales. La audición y el micrófono se comprueban en la [aceptación real](../../docs/academia/aceptacion-v1.2.md). Los scripts de la matriz SAPI y de los benchmarks se conservan como evidencia histórica. La evaluación histórica sobre SpeechOcean762 usó un subconjunto pequeño de grabaciones humanas con anotación fonética y referencia estadounidense. [Corpus y condiciones de uso](https://www.openslr.org/101/)

En la comprobación principal se usaron 24 tomas de 20 voces adultas. De 12 contrastes anotados como errores, el detector omitió 4 y se abstuvo en 8. De 12 controles correctos, dejó 11 sin indicio y se abstuvo en 1. Hubo 0 detecciones correctas y 0 falsos positivos. La puesta en marcha tardó alrededor de un segundo con la primera toma. La mediana de las tomas siguientes fue de unos 62 ms y el pico de memoria del proceso fue de unos 424 MiB. Los resultados justifican usar los intervalos para revisión por escucha. La detección de errores reales queda pendiente de validación.

La opción `--all-annotated` amplía los mismos contrastes a 62 casos de fonema, distribuidos en 60 tomas de 27 voces. Encontró una sustitución /θ/→/t/ que coincide con la anotación, 11 negativos correctos, 0 falsos positivos, 9 falsos negativos y 41 abstenciones. Se detectó 1 de los 50 errores anotados contando las abstenciones. Esta comprobación comparte casos con la principal y muestra baja cobertura. El laboratorio sirve para localizar material que escuchar. Las hipótesis requieren verificación antes de registrar un error individual.

### Validación con voces hispanohablantes

Se seleccionaron 12 tomas anotadas de cada una de las cuatro voces hispanohablantes de L2‑ARCTIC, a intervalos regulares en la lista ordenada de anotaciones. Los códigos ARPAbet distinguen AH0, schwa, del AH acentuado. Para comparar con ZIPA se tratan *l* clara y oscura como el mismo fonema. La revisión y la caché se fijan en el script. `--download` solo recupera los tramos necesarios y guarda el audio fuera de Git. Las tomas se usan para investigación no comercial. Repite el comando sin esa opción para medir localmente. Las anotaciones se basan en guiones ARCTIC con referencia estadounidense y la muestra de cuatro voces no representa al conjunto de estudiantes. [Corpus, autores y licencia](https://psi.engr.tamu.edu/l2-arctic-corpus/)

| Método y corpus | VP | VN | FP | FN entre evaluados | Abstenciones | Sensibilidad con abstenciones | Precisión positiva | Cobertura |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Cotejo vigente, SpeechOcean762 | 1 | 11 | 0 | 9 | 41 | 1/50 · 2,0 % | 1/1 | 21/62 · 33,9 % |
| Cotejo vigente, L2‑ARCTIC español L1 | 0 | 686 | 0 | 122 | 205 | 0/144 · 0 % | Sin avisos | 808/1.013 · 79,8 % |
| Cotejo más indicios CTC libres, mismas voces de español L1 | 1 | 683 | 3 | 121 | 205 | 1/144 · 0,7 % | 1/4 · 25 % | 808/1.013 · 79,8 % |

La vía exploratoria acertó uno de cuatro `/θ/→/t/` y ninguno de 40 `/z/→/s/`, 24 `/ɪ/→/i/` o 25 `/ð/→/d/`. Los tres falsos avisos afectaron a controles `/f/`, `/p/` y `/θ/`. Con las abstenciones positivas contadas como errores no detectados, el F1 es 3,92 % en SpeechOcean762, 0 % con el cotejo vigente en L2‑ARCTIC y 1,35 % con la vía exploratoria. El desglose de todos los contrastes se emite como JSON. Las pruebas con corpus distintos describen muestras distintas. La comparación pareada en las 48 tomas es la que aísla el cambio del código.

Entre los errores de la muestra española, 22 quedaron sin evaluar y 122 pasaron el filtro sin un diagnóstico coincidente. La abstención explica una parte de la pérdida. También influyen la concordancia entre inventarios, las variantes del léxico estadounidense y la baja sensibilidad de las hipótesis después de alinear. Relajar el filtro de manera general no resolvería esas limitaciones. La secuencia libre se calcula con el mismo ZIPA y se ubica en la ventana del guion, con confianza `null`. Sirve para escuchar una posible sustitución, omisión o inserción. Queda fuera de los resultados automáticos y de las notas.

Se examinó Britfone como referencia británica de léxico, BEEP y Unisyn como referencias con restricciones de uso, y la variante de ZIPA sin cuantizar. Un léxico británico orienta las variantes esperadas y la escucha. La sustitución de léxico o de precisión del modelo requiere una prueba pareada para atribuir resultados. Se conserva ZIPA int8 y se muestran variantes británicas revisadas en entradas seleccionadas. No se introdujeron dependencias ni descargas de modelos adicionales. [Britfone](https://github.com/JoseLlarena/Britfone) · [BEEP](https://openslr.org/14/) · [Unisyn](https://www.cstr.ed.ac.uk/projects/unisyn/)

Dirección Académica establece un mínimo de **60 % de sensibilidad efectiva, 90 % de precisión y 80 % de cobertura** para avisos orientativos y un objetivo avanzado de **80 %, 95 % y 90 %**. Ambos requieren validación humana independiente por contraste, incluidas voces y guiones separados, al menos 20 errores y 20 controles en cuatro voces, y controles británicos. Ningún contraste reúne esa evidencia. La escucha humana y la repetición guiada son el procedimiento de corrección. [Validación independiente](../../docs/academia/validacion-fonetica-v1.2.md)

En **EOI English Academy — Prueba técnica**, graba voluntariamente una frase breve con guion, escucha el tramo que elijas y repite el mismo texto tras la revisión. Comprueba que las tomas comparadas son equivalentes. Mantén el audio en Windows y realiza el ensayo sin escribir notas en Sheets.
