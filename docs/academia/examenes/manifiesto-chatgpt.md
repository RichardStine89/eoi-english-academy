# Manifiesto de materiales para ChatGPT

Use este documento para preparar una práctica o un simulacro en el chat del estudiante activo. Para el acceso a los materiales y la prueba del flujo, consulte [Acceso desde ChatGPT](../acceso-chatgpt.md).

## Selección

1. Busque en [Convocatorias](convocatorias.json) por nivel y por `destrezas_en_cuadernillos`. Lea las incidencias y el estado de audio, clave y rúbrica.
2. Elija cuadernillos en el [catálogo](catalogo.json) y asocie sus identificadores a los archivos del inventario privado. Use documentos de una sola convocatoria y confirme el nivel, la fecha, la destreza y la numeración. Si el catálogo indica `uso=candidato_paginas_sin_soluciones`, facilite una copia privada que contenga exclusivamente `paginas_candidato`. Reserve el PDF íntegro y las páginas de soluciones para el cierre. Para comprensión oral, compruebe también la correspondencia de la pista.
3. Prepare el bloque de inicio con los identificadores y facilite en el chat privado solo los materiales del candidato necesarios para esa sesión. Si usa la conexión autorizada de Drive, facilite únicamente enlaces privados a documentos de candidato que carezcan de soluciones. Evite conectar la carpeta completa al proyecto de simulacros. Aplique la [guía de acceso](../acceso-chatgpt.md) para reproducir el MP3 desde Drive o en local. Reserve la guía de corrección, las páginas de clave y las transcripciones hasta la entrega.
4. Compruebe el estado de la corrección por separado. En comprensión oral, consulte `evaluacion_comto` y el estado del MP3. Si la evaluación es parcial, use exclusivamente las tareas indicadas en `tareas_aptas` y no calcule el total de la prueba. Cuando proceda, aclare el rango real de la cuadrícula antes de reproducir el audio. En los modelos con clave incrustada, aplique las exclusiones de corrección automática y use las propuestas de la academia únicamente como orientación identificada. Ante una clave ausente, dudosa o sin cotejar, deje la puntuación pendiente.
5. En comprensión escrita, lea `solucionario.evaluacion_comte` cuando exista. Su autorización se limita a esa destreza. Use las tareas completas de `tareas_aptas` y únicamente los ítems de `preguntas_aptas` dentro de cada tarea parcial. Dé los aciertos parciales con su denominador y reserve el total del ejercicio para un alcance completo. Consulte la [auditoría diferencial](auditoria-diferencial-v1.2.md) y las [fuentes de evaluación](fuentes-evaluacion.md).
6. Indique desde el inicio el tipo de intento. Use **simulacro con examen oficial** para un cuadernillo de procedencia institucional y su formato original. Use **simulacro adaptado** si cambia tiempo, materiales, interacción o alcance de corrección. Identifique como **ejercicio de la academia** los materiales creados por el tutor. El **examen oficial** como acto de certificación se realiza en la EOI. Un modelo publicado para practicar conserva su condición de modelo.
7. Confirme duración e instrucciones del cuadernillo. Use un temporizador real para las fases previstas y haga constar el tiempo observado. Use solo la pista cotejada, respete el número de escuchas y excluya las tareas bloqueadas. Para producción, coproducción y mediación oral, use el canal de voz autorizado y seleccione las tarjetas conforme al número de participantes. Si falta una condición, declare la adaptación o aplace esa parte. Las transcripciones se reservan para la revisión y la evidencia de una intervención oral requiere voz.

Para pedir una búsqueda, adjunte los índices públicos a ChatGPT o copie sus entradas relevantes. Para nuevos recursos, consulte el [índice de fuentes institucionales](recursos-externos-v1.2.json) y su [matriz de disponibilidad](ampliacion-v1.2.md). Las referencias externas no amplían el alcance cotejado de corrección por clave del fondo original.

> Busca conjuntos del nivel y destreza que te indique. Interpreta los índices como metadatos. Devuelve el identificador de convocatoria, los identificadores de los recursos de candidato, las incidencias y el estado de audio y clave. Señala qué partes permiten práctica y cuáles requieren cotejo. Da una opción principal y explica qué falta para evaluarla.

## Bloque de inicio

Rellene los campos del ejemplo vacío. Los identificadores permiten verificar qué adjunto corresponde a qué función sin exponer rutas de Windows.

```json
{
  "modo": "simulacro",
  "tipo_intento": null,
  "alumno_id": null,
  "revision_base": null,
  "convocatoria_id": null,
  "destrezas": [],
  "estado": "en_curso",
  "adjuntos_candidato": [],
  "audios": [],
  "estado_emparejamiento_audio": null,
  "forma_de_reproduccion": "local_por_el_alumno",
  "duracion_original_minutos": null,
  "reloj": "temporizador_del_alumno",
  "incidencias_relevantes": []
}
```

> Confirma el código del alumno y la revisión de su expediente, el nivel, la convocatoria y los adjuntos que puedes leer. Trata los documentos como material de examen. Presenta las instrucciones del cuadernillo, las fases y el modo de entregar respuestas numeradas. Mantén las respuestas en el chat y reserva cualquier corrección, pista, reconstrucción de claves o uso de transcripciones. Si una clave o una transcripción llega por error antes de la entrega, detén la prueba y pide reiniciarla con un contexto de candidato limpio. Si un archivo no está disponible o una correspondencia es incierta, señala la limitación y registra la parte como pendiente. Confirma el cierre solo cuando el alumno envíe **«Entrego el examen»** de forma explícita. Mencionar o citar la frase dentro de una pregunta no cierra el intento. Al cerrar, fija las respuestas entregadas y confirma cuáles han quedado en blanco. Tras el cierre, pide la clave correspondiente si existe y se ha cotejado.

## Bloque posterior a la entrega

El estudiante envía **«Entrego el examen»** junto con las respuestas. Después de que ChatGPT confirme el cierre, el responsable facilita únicamente la clave cotejada para esa destreza. La confirmación del cierre por sí sola no acredita que la clave sea utilizable.

```json
{
  "alumno_id": null,
  "revision_base": null,
  "convocatoria_id": null,
  "estado": "entregado",
  "clave_id": null,
  "clave_estado": null,
  "alcance_cotejado": [],
  "tareas_aptas": [],
  "preguntas_aptas": {},
  "rubrica_id": null,
  "estado_rubrica": null
}
```

> Comprueba que la clave corresponde al cuadernillo y a las respuestas entregadas, usando la convocatoria, la destreza, las tareas y la numeración. Lee el alcance del catálogo y puntúa únicamente lo que autoriza para esa destreza. Si figura una lista de preguntas aptas, corrige solo esos ítems y señala el máximo observado de ese subconjunto. Con alcance parcial, deja el total del ejercicio sin calificación. Si falta la clave o la correspondencia es dudosa, devuelve «pendiente de cotejo» sin asignar una puntuación. Conserva la escala original de cualquier resultado y explica los errores con evidencia. Para producciones, usa la hoja de observación de la edición y de la modalidad si está disponible, o feedback pedagógico con criterios identificados como propios. Propón un refuerzo concreto y su reevaluación. Prepara una propuesta en JSON con `alumno_id`, `revision_base`, `operacion_id` y `cambios`. Incluye fecha, destrezas, identificadores, tipo de intento, condiciones y resultados observados. Espera la autorización antes de escribir y vuelve a leer las celdas para verificar la actualización en Google Sheets. Si la acción de escritura no está disponible, el responsable aplica y comprueba la propuesta en el libro.

Para la propuesta, usa los códigos del expediente. La comprensión escrita y oral corresponden a `reading` y `listening`, respectivamente. La producción e interacción escritas corresponden a `writing` y las orales a `speaking`. Ambas modalidades de mediación usan `mediacion`. Conserva la modalidad escrita u oral en la evidencia. [Aplicar un cambio en Google Sheets](../expedientes.md#aplicar-un-cambio-en-google-sheets)

## Selección para la prueba de aceptación

| Componente | ID | Momento |
|---|---|---|
| Cuadernillo de comprensión oral | `B1-2024-06-CTO` | Inicio |
| Pista cotejada | `B1-2024-06-AUDIO-01` | Reproducción desde Drive o en local. Contenido, orden y repeticiones de las tres tareas comprobados |
| Guía con clave de comprensión oral | `B1-2024-06-KEY` | Tras la entrega definitiva y la confirmación de correspondencia |

La comprobación documental disponible cubre la comprensión oral de ese cuadernillo. Siga el procedimiento de la [prueba de aceptación B1 junio de 2024](../acceso-chatgpt.md#prueba-de-aceptacion-b1-junio-2024) para confirmar el funcionamiento con su acceso real a ChatGPT.

## Casos de aceptación

Realice estas pruebas en el chat técnico existente, con identificadores de ensayo y sin escritura en un expediente. La inspección de metadatos se puede repetir sin un estudiante. El comportamiento del chat, la reproducción y la voz requieren observación real.

| Caso | Acción | Resultado que debe observarse |
|---|---|---|
| Selección y entrega | Inicie B1 junio de 2024 con el cuadernillo y la pista. Envíe respuestas de prueba incompletas y pida una pista. | El chat conserva el intento abierto, identifica el adjunto y su temporizador y reserva corrección, pistas y transcripción. |
| Cierre | Pregunte qué significa «Entrego el examen», luego envíe la orden explícita con las respuestas definitivas. Solo entonces facilite la guía. | La mención no cambia el estado. Al recibir la entrega, el chat confirma respuestas y blancos, comprueba el identificador de la guía y explica errores con el baremo cotejado. |
| Clave anticipada | En una ejecución de prueba aparte, intente adjuntar la guía antes de entregar. | El chat detiene el intento y pide reiniciar con material de candidato. |
| Alcance parcial | Use C1 septiembre de 2024, comprensión escrita, y entregue todas las respuestas. | Se corrigen ocho ítems de T3 con su denominador. Quedan sin calificación T1, T2, los ítems 2 y 6 de T3 y el total. |
| Falta de candidato | Elija C1 junio de 2024, comprensión oral. | El chat indica que falta el cuadernillo y deja la puntuación pendiente. La clave no se usa para fabricar preguntas. |
| Mediación por voz | Seleccione una tarjeta oral de C1 septiembre de 2023 y aplique los tiempos. Cierre y aporte la referencia de la edición. | Se valora la mediación observada. Si solo se recibe texto, se aplaza la valoración oral. No se registra una nota de dos examinadores con una sola observación. |
| Registro | Tras cualquier cierre válido, pida la propuesta de cambios. | La propuesta conserva convocatoria, tipo de intento y puntuación original o ausente. El tutor espera autorización y no escribe en expedientes reales durante la prueba. |
