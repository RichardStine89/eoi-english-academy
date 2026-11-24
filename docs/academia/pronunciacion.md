# EOI Pronunciation Lab

El laboratorio registra o importa una toma, la analiza en Windows y prepara evidencia para ChatGPT. Usa el chat **EOI English Academy — Clases** para recibir la consigna, compartir el informe breve y continuar la práctica. La instalación y el lanzador están en la [guía del módulo](../../modules/pronunciation-lab/README.md). Tras la instalación se abre con [Abrir.cmd](../../modules/pronunciation-lab/Abrir.cmd) y funciona de forma local sin abrir Codex.

## Antes de grabar y después de analizar

1. Escribe **«Profesor, empezamos»** o **«Profesor, speaking»**. El profesor indica unidad, actividad, objetivo e intento. Si estabas en Voz, termina la llamada y vuelve al texto en la misma conversación para liberar el micrófono.
2. En el laboratorio selecciona `alumno-01` o `alumno-02` y completa la unidad, el nivel, la actividad y el modo. En repetición y pares mínimos, escucha primero el modelo británico. Usa **Cargar audio modelo…** con un archivo autorizado o escucha el enlace didáctico indicado por el profesor. Conserva clara la diferencia entre modelo y grabación del alumno.
3. Pulsa **Iniciar grabación** de forma explícita y **Detener y analizar** al finalizar. Usa **Oír grabación** para comprobar que es tu toma y que se entiende. La alternativa es **Importar grabación…** con un archivo WAV, MP3 o M4A decodificable de hasta tres minutos y 128 MB. Si el micrófono permanece ocupado o no está disponible, utiliza una grabación hecha en Windows u otro dispositivo.
4. Revisa el resultado. Si falta señal útil, repite en un lugar tranquilo, a una distancia estable del micrófono y sin reproducción de fondo. Pulsa **Copiar informe** cuando quieras compartir ese resumen en el mismo chat de clases. Usa **Exportar JSON privado** si necesitas una copia íntegra. Para repetir, conserva el ID de actividad. El laboratorio numera el nuevo intento y permite elegir uno anterior en **Comparar con**.
5. Recibe orientación específica, repite la tarea y compara intentos bajo condiciones parecidas. El profesor valora el speaking y la pronunciación por separado, propone repaso y actualiza el expediente solo tras autorización. [Protocolo de expedientes](expedientes.md#incorporar-evidencia-de-eoi-pronunciation-lab)

El laboratorio guarda automáticamente la toma procesada y el informe completo bajo `%LOCALAPPDATA%\EOI English Academy\Pronunciation Lab`, por separado para cada alumno. Revisa la selección antes de grabar, importar, exportar o copiar. Usa **Eliminar esta grabación…** para eliminar la copia local de la toma. El informe y el archivo original importado se conservan. Comparte audio solo con autorización. El informe breve omite el guion y el audio. Si aportas información adicional, comprueba que sea necesaria y esté autorizada. Para una prueba inicial usa **EOI English Academy — Prueba técnica**, con una toma de ensayo y sin registrar notas reales. [Acceso y Voz](acceso-chatgpt.md#eoi-pronunciation-lab-en-el-chat-de-clases-existente)

## Elegir el modo

| Modo | Consigna y evidencia |
|---|---|
| Lectura guiada | Lee un texto conocido. El informe conserva ese texto como objetivo y las mediciones de la toma. Para comparar la producción con el texto, escucha y coteja manualmente los fragmentos que interesen. |
| Repetición | Escucha una palabra o frase y repítela. Compara dos intentos del mismo alumno con el mismo modelo. El modelo es un apoyo didáctico separado. |
| Pares mínimos | Discrimina primero qué palabra se oye y luego graba la repetición en orden. Usa contrastes pertinentes como *ship/sheep*, *live/leave* con *live* como verbo, *three/tree*, *full/fool*, *hat/hut*, *bad/bed* o *very/berry*. Comprueba el contraste escuchando. |
| Speaking espontáneo | Responde en voz a una consigna breve y a una pregunta de seguimiento en el chat. Una grabación del monólogo permite revisar el uso del tiempo y tramos candidatos a pausa. La evidencia de interacción procede de los turnos reales. |
| Inglés turístico | Simula una bienvenida, una indicación, la explicación breve de un monumento o una duda de un visitante. Adapta el vocabulario y la extensión al nivel. Es una opción para el itinerario profesional de `alumno-01`. |

En A1–A2 trabaja frases breves, palabras clave y un contraste cada vez. En B1–B2 añade acento léxico, formas débiles y grupos de sentido. En C1 trabaja entonación, foco y registro con un propósito comunicativo. Elige contrastes a partir de las necesidades observadas. Un hábito frecuente entre hispanohablantes sirve para diseñar una actividad de percepción y queda como hipótesis hasta oírlo en la toma.

## Interpretar el informe

- **Mediciones orientativas.** Usa duración, actividad sonora aproximada, calidad de señal y estadísticas de frecuencia fundamental (F0) para comparar tomas semejantes. El JSON incluye marcas temporales de las pausas cuando están disponibles. Las pausas estimadas por señal pueden incluir cierres de consonantes o silencios del entorno. Las estimaciones de F0 dependen de periodicidad, ruido y rango de voz. Si falta una medición, el JSON usa `null` o indica el estado correspondiente. [Manual de análisis de tono de Praat](https://praat.org/manual/how_to_choose_a_pitch_analysis_method.html)
- **Correspondencia fonética.** El motor acústico no transcribe ni alinea palabras o fonemas. El texto esperado, la IPA británica didáctica y el audio modelo sirven para el cotejo humano. La duración total no mide por sí sola la velocidad del habla. Para estimarla en una tarea concreta, el evaluador necesita comprobar las palabras realmente pronunciadas y el tiempo que entra en el cálculo.
- **Corrección.** Si una muestra audible respalda una observación, indica la palabra y el tramo, el rasgo observado y el objetivo IPA. Explica la articulación si ayuda, da un modelo, pide otro intento y programa repaso. Evalúa el contraste, el acento o el enlace cuando haya evidencia audible suficiente. Deja pendientes las omisiones, inserciones, sustituciones, inteligibilidad o rasgos que el informe por sí solo no pueda acreditar. Cualquier valoración de acento debe referirse a un objetivo acordado o a la comprensión del mensaje.
- **Evaluación.** Valora el speaking a partir de gramática, vocabulario, fluidez, coherencia, interacción y adecuación comunicativa cuando haya evidencia para cada criterio. Usa pronunciación como campo independiente. Una métrica acústica, el texto esperado o una transcripción no acreditan por sí solos una nota. Si se dispone de evidencia y criterio suficientes, la nota pedagógica puede expresarse de 0 a 10. En una prueba oficial rige su propia rúbrica y baremo. [Guía docente](docencia.md#evaluación-pedagógica-del-speaking)

Para revisar evolución usa dos o más intentos comparables del mismo alumno. Conserva modo, consigna, actividad y condiciones de grabación. Describe qué cambió y qué se pudo oír. Si hay recorte o ruido en una toma, repite antes de sacar conclusiones. El acento español y las variantes regionales válidas son compatibles con el objetivo de inteligibilidad.

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
3. **Primera toma.** Usa lectura guiada con `A1-01`. Lee las frases con una pausa natural entre ellas. Para el intercambio en Voz, el profesor pregunta «What’s your name?», «Where are you from?» y «What do you do?» de una en una.
4. **Repetición.** Tras revisar el primer intento, conserva la consigna y repite con un solo foco. Pega los informes breves en el chat habitual si quieres comentarlos. Compara los rasgos que puedan comprobarse. El texto de preparación y los ejemplos de sonidos quedan como material docente hasta que haya una toma real.
