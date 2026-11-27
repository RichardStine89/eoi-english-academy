# EOI Pronunciation Lab

El laboratorio registra o importa una toma, la analiza en Windows y prepara evidencia para ChatGPT. Usa el chat **EOI English Academy — Clases** para recibir la consigna, compartir el informe breve y continuar la práctica. Para añadir el modelo fonético al entorno existente, ejecuta una vez [Instalar.cmd](../../modules/pronunciation-lab/Instalar.cmd) con conexión. Después abre [Abrir.cmd](../../modules/pronunciation-lab/Abrir.cmd) y analiza sin conexión ni Codex. [Guía del módulo](../../modules/pronunciation-lab/README.md)

## Antes de grabar y después de analizar

1. Escribe **«Profesor, empezamos»** o **«Profesor, speaking»**. El profesor indica unidad, actividad, objetivo e intento. Si estabas en Voz, termina la llamada y vuelve al texto en la misma conversación para liberar el micrófono.
2. En el laboratorio selecciona `alumno-01` o `alumno-02` y completa la unidad, el nivel, la actividad y el modo. Para cotejo fonético, introduce el texto exacto que vas a pronunciar y usa fragmentos de hasta 30 segundos y 65 palabras. En repetición y pares mínimos, escucha primero el modelo británico con **Cargar audio modelo…** o en el enlace didáctico indicado por el profesor.
3. Pulsa **Iniciar grabación** de forma explícita y **Detener y analizar** al finalizar. Usa **Oír grabación** para comprobar que es tu toma y que se entiende. La alternativa es **Importar grabación…** con un archivo WAV, MP3 o M4A decodificable de hasta tres minutos y 128 MB. Si el micrófono permanece ocupado o no está disponible, utiliza una grabación hecha en Windows u otro dispositivo.
4. Abre **Ver evidencia fonética…** para revisar las palabras, los indicios y sus intervalos. Si hay un intervalo utilizable y audio disponible, selecciona la palabra y pulsa **Oír fragmento**. Si falta señal útil, repite en un lugar tranquilo, a una distancia estable del micrófono y sin reproducción de fondo. Pulsa **Copiar informe** para revisar y pegar el resumen en el mismo chat de clases. Usa **Exportar JSON privado** si necesitas una copia íntegra. Para repetir, conserva el ID de actividad, el modo y el texto. El laboratorio numera el nuevo intento y permite elegir uno anterior en **Comparar con**.
5. Recibe orientación específica, repite la tarea y compara intentos bajo condiciones parecidas. El profesor valora el speaking y la pronunciación por separado, propone repaso y actualiza el expediente solo tras autorización. [Protocolo de expedientes](expedientes.md#incorporar-evidencia-de-eoi-pronunciation-lab)

El laboratorio guarda automáticamente la toma procesada y el informe completo bajo `%LOCALAPPDATA%\EOI English Academy\Pronunciation Lab`, por separado para cada alumno. Revisa la selección antes de grabar, importar, exportar o copiar. Usa **Eliminar esta grabación…** para eliminar la copia local de la toma. El informe y el archivo original importado se conservan. Mantén el audio en Windows. Para compartir un informe, usa un guion sin datos personales, ya que el resumen puede incluir parte del texto esperado. Revisa el contenido antes de pegarlo. Para una prueba inicial usa **EOI English Academy — Prueba técnica**, con una toma de ensayo y sin registrar notas reales. [Acceso y Voz](acceso-chatgpt.md#eoi-pronunciation-lab-en-el-chat-de-clases-existente)

## Elegir el modo

| Modo | Consigna y evidencia |
|---|---|
| Lectura guiada | Lee un texto conocido y breve. Revisa las palabras alineadas y escucha los fragmentos que el informe señale para confirmar o descartar las hipótesis. |
| Repetición | Escucha una palabra o frase y repítela. Compara dos intentos del mismo alumno con el mismo modelo. El modelo es un apoyo didáctico separado. |
| Pares mínimos | Discrimina primero qué palabra se oye y luego graba la repetición en orden. Elige un [contraste de práctica](#contrastes-y-hábitos-fonéticos) que encaje con la unidad. Comprueba el contraste escuchando. |
| Speaking espontáneo | Responde en voz a una consigna y a una pregunta de seguimiento en el chat. Una toma del monólogo aporta mediciones generales de tiempo y pausas. La alineación fonética requiere un guion y la valoración de interacción requiere los turnos reales. |
| Inglés turístico | Simula una bienvenida, una indicación, la explicación de un monumento o una duda de un visitante. Usa un guion exacto y breve para el cotejo fonético. Para un diálogo libre, usa las mediciones generales y la evidencia de la conversación. Es una opción para el itinerario profesional de `alumno-01`. |

En A1–A2 trabaja frases breves, palabras clave y un contraste cada vez. En B1–B2 añade acento léxico, formas débiles y grupos de sentido. En C1 trabaja entonación, foco y registro con un propósito comunicativo. Elige contrastes a partir de las necesidades observadas. Un hábito frecuente entre hispanohablantes sirve para diseñar una actividad de percepción y queda como hipótesis hasta oírlo en la toma.

## Interpretar el informe

Pronunciada con ZIPA int8 alinea la toma con las palabras y fonemas del guion y busca alternativas acústicas en un conjunto limitado de contrastes. Las palabras que muestra se toman del guion. Esta versión deja el reconocimiento independiente y la transcripción en `null`. La IPA británica que aparece en algunas palabras es una referencia didáctica. El motor se apoya en el léxico estadounidense CMUdict. Las variantes británicas y la fiabilidad con los alumnos de la academia requieren validación específica. Los informes anteriores siguen disponibles. Conserva sus mediciones acústicas y usa una toma nueva si necesitas evidencia fonética.

| Estado | Acción del profesor |
|---|---|
| **Sin desviación detectada** | Usa el resultado como evidencia limitada a los segmentos y contrastes que analiza el motor. |
| **Posible desviación** | Revisa la palabra y el intervalo. Escucha la toma antes de afirmar el cambio de fonema o la omisión. Si solo tienes el informe, formula la corrección como hipótesis y plantea una repetición controlada. |
| **Evidencia insuficiente** | Revisa señal, duración y correspondencia con el guion. Pide otra toma si se necesita una observación. |
| **No evaluado** | Usa el motivo indicado. En un monólogo libre, una toma demasiado larga o un equipo con el modelo sin instalar, continúa con la actividad docente y con las mediciones que sí estén disponibles. |

El informe puede indicar posibles sustituciones en los contrastes internos /ɪ/–/i/, /ʊ/–/u/, /æ/–/ʌ/, /æ/–/ɛ/, /b/–/v/, /θ/–/t/, /θ/–/s/, /ð/–/d/ y /s/–/z/, además de posibles omisiones de algunas consonantes. Los símbolos del motor y la IPA británica de enseñanza pueden diferir. La confianza es un indicador técnico sin calibrar. Si la evidencia no respalda un juicio, deja el rasgo pendiente.

El JSON puede aportar intervalos de palabra, sílaba y fonema, duraciones y estimaciones de F0 e intensidad por palabra. Sirven para elegir un tramo y comparar tomas semejantes. Valora acento léxico y de frase, ritmo lingüístico, entonación, velocidad, enlace e inteligibilidad con evidencia audible o déjalos pendientes. Las inserciones quedan fuera del análisis automático. Las pausas son aproximadas y la duración total no establece la velocidad del habla. [Manual de análisis de tono de Praat](https://praat.org/manual/how_to_choose_a_pitch_analysis_method.html)

El detalle de palabra muestra, cuando consta, una secuencia libre de ZIPA de la ventana alineada y posibles ediciones para revisar. Su confianza es `null`. Escucha ese fragmento y un modelo británico pertinente. Confirma el contraste y la posición con evidencia audible, o registra solo práctica de percepción y una nueva toma. Si ChatGPT recibe el informe o una transcripción, orienta la escucha del estudiante. Si un evaluador humano puede escuchar el audio autorizado en local, contrasta con él antes de aceptar un error o valorar inteligibilidad. En la prueba anotada con cuatro voces hispanohablantes la vía exploratoria acertó 1 de 144 errores y produjo 3 falsos avisos. Se usa para orientar la escucha. [Validación reproducible](../../modules/pronunciation-lab/README.md#validación-con-voces-hispanohablantes)

Si una muestra audible respalda una observación, indica palabra, tramo y objetivo IPA. Explica la articulación si ayuda, da un modelo, pide otro intento y programa repaso. Valora el speaking por gramática, vocabulario, fluidez, coherencia, interacción y adecuación comunicativa cuando haya evidencia. Registra pronunciación por separado y aplica un criterio por observación para evitar penalizar dos veces el mismo problema. La nota pedagógica sobre 10 requiere evidencia y criterio. En una prueba oficial rige su propia rúbrica y baremo. [Guía docente](docencia.md#evaluación-pedagógica-del-speaking)

Para revisar evolución usa dos o más intentos comparables del mismo alumno. Conserva modo, consigna, actividad y condiciones de grabación. Describe qué cambió y qué se pudo oír. Si hay recorte o ruido en una toma, repite antes de sacar conclusiones. El acento español y las variantes regionales válidas son compatibles con el objetivo de inteligibilidad.

## Contrastes y hábitos fonéticos

Elige uno según la unidad y la evidencia del alumno. Presenta primero un modelo audible y pide identificar lo que se oye. Después pide una repetición de las dos opciones, una frase breve con la palabra objetivo y un nuevo intento tras la corrección. Estos ejercicios permiten observar contrastes. Una dificultad habitual entre hispanohablantes solo se atribuye al alumno si la toma individual aporta evidencia suficiente.

| Qué practicar | Actividad breve |
|---|---|
| /ɪ/–/iː/ y /ʊ/–/uː/ | Escucha e identifica *ship/sheep*, *live/leave* con *live* como verbo, o *full/fool*. Compara la calidad de las vocales además de su duración. |
| /æ/ frente a /ʌ/ o /e/ | Identifica *hat/hut* o *bad/bed*, y repite ambas palabras dentro de una frase corta. |
| /b/–/v/ y /s/–/z/ | Distingue *berry/very* y *sip/zip*. Para /v/, prueba el contacto suave del labio inferior con los dientes superiores. Para /z/, observa si se mantiene la vibración durante la fricción. |
| /θ/ frente a /t/ o /s/, y /ð/ frente a /d/ | Escucha *three/tree*, *thin/sin* o *then/den*. Para /θ/ y /ð/, practica la fricción con la lengua cerca de los dientes, con voz para /ð/. |
| /h/, finales y grupos consonánticos | Identifica *heat/eat* y *bee/bead*. En *school* o *Spain*, enlaza /s/ directamente con la consonante siguiente. Escucha si aparece una vocal inicial y vuelve a intentarlo en una frase. |
| Schwa /ə/, acentuación y ortografía | Escucha *about* y *a book* antes de mirar el texto. Marca la sílaba tónica en *Spanish* o *photography*, según nivel, y repite dejando más ligeras las sílabas átonas. |

Para la percepción, usa modelos del [British Council](https://learnenglish.britishcouncil.org/apps/learnenglish-sounds-right) o de [The Sounds of English de BBC Learning English](https://feeds.bbci.co.uk/learningenglish/english/features/pronunciation/). Compara intentos de la misma consigna. Describe únicamente los cambios que puedas fundamentar.

En una revisión, confirma primero qué palabra se leyó y si la toma permite oírla bien. Escucha el fragmento y compara con las variantes válidas de esa palabra. Distingue un contraste del ejercicio de un problema de inteligibilidad en contexto. Si falta el audio o persiste la duda, deja la observación pendiente y propone una repetición breve. El ensayo IF‑MDD se conserva como evidencia técnica y las hipótesis del laboratorio siguen destinadas a la revisión por escucha. [Evaluación y límites](operacion-fonetica-v1.2.md)

## Primera actividad A1-01 · Presentarse

**Objetivo.** Saludar, dar el nombre, el trabajo y la procedencia con palabras clave inteligibles. Usa los datos que el estudiante quiera decir en privado y deja los marcadores en cualquier material que se vaya a compartir. La práctica pertenece a [A1-01 · Hello & introductions](../../languages/english/curriculum/a1/unit-01.md).

> - Hello.
> - My name is [first name].
> - I am a tour guide.
> - I am from Spain.
> - I am Spanish.
> - I am from [town].
> - Nice to meet you.

1. **Escucha.** Oye los saludos y las presentaciones. Haz la primera actividad de comprensión y di qué expresiones reconociste. [British Council · Meeting a new team member](https://learnenglish.britishcouncil.org/free-resources/listening/a1/meeting-new-team-member)
2. **Percepción y modelo.** Escucha `hello` /həˈləʊ/, `name` /neɪm/, `Spain` /speɪn/, `Spanish` /ˈspænɪʃ/ y `meet` /miːt/. Practica uno o dos rasgos según la primera escucha. Puedes usar un soplo suave para /h/, pasar de /s/ a /p/ directamente en `Spain` o distinguir /ɪ/ de /iː/ escuchando `ship` y `sheep`. Para el ritmo, prueba un grupo breve por frase y destaca **name**, **Spain** o **meet** según el mensaje. [British Council · LearnEnglish Sounds Right](https://learnenglish.britishcouncil.org/apps/learnenglish-sounds-right) · [BBC Learning English · The Sounds of English](https://feeds.bbci.co.uk/learningenglish/english/features/pronunciation/)
3. **Primera toma.** Usa lectura guiada con `A1-01`. Para el cotejo de un ensayo, cambia los marcadores por un nombre y un lugar genéricos y pronuncia exactamente el texto que introduzcas. Lee las frases con una pausa natural entre ellas. Para el intercambio en Voz, el profesor pregunta «What’s your name?», «Where are you from?» y «What do you do?» de una en una.
4. **Repetición.** Tras revisar el primer intento, conserva la consigna y repite con un solo foco. Pega los informes breves en el chat habitual si quieres comentarlos. Compara los rasgos que puedan comprobarse. El texto de preparación y los ejemplos de sonidos quedan como material docente hasta que haya una toma real.
