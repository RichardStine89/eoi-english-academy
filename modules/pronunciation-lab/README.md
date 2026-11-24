# EOI Pronunciation Lab

Aplicación local de Windows para grabar, revisar y comparar tomas. El [procedimiento docente](../../docs/academia/pronunciacion.md) explica cómo llevar el informe al chat de clases y qué se puede interpretar con él.

## Instalación y apertura

1. Ejecuta [Instalar.cmd](Instalar.cmd) con conexión a internet. Usa Python 3.12 x64 con Tcl/Tk. Si ya está instalado para Windows, el lanzador lo detecta. También puede reutilizar el Python incluido en el entorno de Codex si está presente. Si no tienes ninguno, instala [Python 3.12 para Windows con Tcl/Tk](https://docs.python.org/3.12/using/windows.html#installing-without-ui) o señala una instalación existente mediante la variable `EOI_LAB_PYTHON`.
2. Después, abre [Abrir.cmd](Abrir.cmd) haciendo doble clic. Puedes crear un acceso directo a ese archivo desde el Explorador. El uso normal no requiere conexión, cuenta, GPU, Codex ni comandos. Si mueves el repositorio o desaparece el Python base, vuelve a preparar el entorno virtual desde la ubicación definitiva.
3. Selecciona alumno, nivel, unidad, modo e ID de actividad. Para lectura, repetición y pares mínimos introduce el texto. Elige micrófono o usa **Importar grabación…**. Si Voz de ChatGPT está usando el micrófono, termina la llamada antes de grabar o importa una toma. El límite es 3 min. La importación admite WAV, MP3 y M4A decodificables de hasta 128 MB.
4. Tras **Detener y analizar**, usa **Oír grabación** para comprobar la toma. **Copiar informe** prepara texto breve para el mismo chat. **Exportar JSON privado** guarda los datos íntegros. Mantén ID de actividad, modo y texto para comparar tomas semejantes.

La toma queda en `%LOCALAPPDATA%\EOI English Academy\Pronunciation Lab\alumno-XX`, con un informe por intento. **Eliminar esta grabación…** y **Historial de grabaciones…** borran solo la copia local de la toma tras confirmación. Conservan su informe y el original que se haya importado. La separación por alumno se aplica dentro de la interfaz. En un equipo compartido, usa cuentas de Windows separadas si necesitas que cada alumno tenga acceso exclusivo a sus datos.

## Motor y alcance

El entorno fijado ocupa aproximadamente **54 MB de descarga** en Windows x64, más el espacio local de Python y de los paquetes instalados. En la validación se usó Python 3.12.14, Windows 11 x64, AMD Ryzen 9 7900X y 31,2 GiB de RAM visibles. La aplicación no utilizó la GPU ni descargó modelos. El consumo de una toma crece con su duración y el límite de tres minutos acota ese trabajo.

| Componente | Función y licencia |
|---|---|
| Parselmouth 0.4.7 con Praat 6.1.38 | Estimación de frecuencia fundamental por autocorrelación en tramos utilizables. Funciona en CPU sin modelo acústico ni datos de entrenamiento. GPL-3.0-o-posterior. [Proyecto](https://github.com/YannickJadoul/Parselmouth) · [Distribución Windows](https://pypi.org/project/praat-parselmouth/0.4.7/) |
| NumPy 2.4.4 | Cálculos de nivel de señal, actividad y pausas aproximadas. BSD-3-Clause. [Distribución](https://pypi.org/project/numpy/2.4.4/) |
| PyAV 16.1.0 | Decodificación local mediante FFmpeg. BSD-3-Clause en PyAV. Las bibliotecas FFmpeg tienen sus propias condiciones. [Distribución](https://pypi.org/project/av/16.1.0/) · [Licencia de FFmpeg](https://ffmpeg.org/legal.html) |
| sounddevice 0.5.3 y Tcl/Tk | Captura y reproducción locales con PortAudio e interfaz de escritorio. sounddevice tiene licencia MIT y se instala con CFFI y pycparser. Tcl/Tk viene con Python para Windows cuando está seleccionado. [Audio](https://pypi.org/project/sounddevice/0.5.3/) · [Interfaz](https://docs.python.org/3.12/library/tkinter.html) |

Las dependencias se instalan desde sus distribuidores. El repositorio conserva el código del módulo y versiones fijadas. El informe usa el inglés británico contemporáneo como referencia didáctica. El estimador acústico es independiente de la lengua y no compara con un modelo de hablante nativo. La F0 y la actividad describen la toma. La transcripción, los fonemas, las sustituciones, la fluidez lingüística y la nota quedan sin evaluar.

### Alternativas examinadas

| Candidato | Motivo de la decisión |
|---|---|
| OpenPronounce | Código y modelos AGPL-3.0. El proyecto publica tasas altas de sugerencias rechazadas en su validación y advierte del alcance del conjunto de hablantes. La configuración de referencia puede usar TTS externo. No se verificó su fiabilidad para el modelo británico y los alumnos de la academia. [Licencias](https://openpronounce.github.io/docs/licensing.html) · [Límites](https://openpronounce.github.io/docs/limits.html) |
| Pronunciada | Proyecto con código Apache-2.0 y licencias propias para datos, diccionarios y modelos. El proyecto describe una variante cuantizada de unos 71 MB. La fiabilidad británica con hispanohablantes y el rendimiento en este Windows no se verificaron. [Proyecto](https://github.com/moglearn/pronunciada) · [Licencias de datos](https://github.com/moglearn/pronunciada/blob/main/docs/LICENSING.md) |
| Montreal Forced Aligner | Código MIT. El modelo inglés v3.1.0 tiene licencia CC BY 4.0 y carece de designación dialectal. Funciona para alinear texto conocido, con instalación propia y modelo descargable. La alineación no basta para acreditar cambios de fonema. [Instalación](https://montreal-forced-aligner.readthedocs.io/en/latest/installation.html) · [Modelo](https://mfa-models.readthedocs.io/en/latest/acoustic/English/English%20MFA%20acoustic%20model%20v3_1_0.html) |
| eSpeak NG | Motor GPL-3.0-o-posterior de síntesis y conversión de texto a fonemas, con voz inglesa británica. Podría servir como modelo sintético. El análisis de una toma requiere otra técnica. [Proyecto](https://github.com/espeak-ng/espeak-ng) |
| GOP, Kaldi y wav2vec2 fonético | GOP requiere un modelo fonético y calibración con evidencia humana. Kaldi tiene licencia Apache-2.0. El modelo wav2vec2 fonético revisado se publica como Apache-2.0. No hay calibración comprobada aquí para distinguir variantes británicas válidas y errores de estudiantes. [Implementación GOP](https://github.com/kaldi-asr/kaldi/blob/master/src/bin/compute-gop.cc) · [Modelo wav2vec2](https://huggingface.co/facebook/wav2vec2-lv-60-espeak-cv-ft) |
| Whisper | Código y pesos MIT. Puede aportar una transcripción con una descarga de modelo y recursos adicionales. Esa transcripción quedaría como apoyo a una revisión humana. La versión actual prescinde de este componente. [Proyecto](https://github.com/openai/whisper) |

## Validación reproducible

Desde el directorio del módulo, una vez instalado:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Las pruebas generan señales y archivos temporales. Comprueban importación, actividad sonora, pausas, F0, rechazo de señal insuficiente, informe, JSON, separación y borrado de la copia privada. Una señal sintética permite contrastar intervalos y frecuencias conocidas. Para validar el micrófono, el sonido reproducido y la utilidad pedagógica, usa una toma voluntaria en el chat **EOI English Academy — Prueba técnica**, sin escribir calificaciones en Sheets.
