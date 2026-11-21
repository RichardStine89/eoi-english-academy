# Manifiesto de materiales para ChatGPT

Use este documento para preparar una práctica o un simulacro en el chat del estudiante activo. Para el acceso a los materiales y la prueba del flujo, consulte [Acceso desde ChatGPT](../acceso-chatgpt.md).

## Selección

1. Busque en [Convocatorias](convocatorias.json) por nivel y por `destrezas_en_cuadernillos`. Lea las incidencias y el estado de audio, clave y rúbrica.
2. Elija cuadernillos en el [catálogo](catalogo.json) y asocie sus identificadores a los archivos del inventario privado. Use documentos de una sola convocatoria y confirme el nivel, la fecha, la destreza y la numeración. Si el catálogo indica `uso=candidato_paginas_sin_soluciones`, facilite una copia privada que contenga exclusivamente `paginas_candidato`. Reserve el PDF íntegro y las páginas de soluciones para el cierre. Para comprensión oral, compruebe también la correspondencia de la pista.
3. Prepare el bloque de inicio con los identificadores y facilite en el chat privado solo los materiales del candidato necesarios para esa sesión. Si usa la conexión autorizada de Drive, facilite únicamente enlaces privados a documentos de candidato que carezcan de soluciones. Evite conectar la carpeta completa al proyecto de simulacros. Aplique la [guía de acceso](../acceso-chatgpt.md) para reproducir el MP3 desde Drive o en local. Reserve la guía de corrección, las páginas de clave y las transcripciones hasta la entrega.
4. Compruebe el estado de la corrección por separado. En comprensión oral, consulte `evaluacion_comto` y el estado del MP3. Si la evaluación es parcial, use exclusivamente las tareas indicadas en `tareas_aptas` y no calcule el total de la prueba. Cuando proceda, aclare el rango real de la cuadrícula antes de reproducir el audio. En los modelos con clave incrustada, aplique las exclusiones de corrección automática y use las propuestas de la academia únicamente como orientación identificada. Ante una clave ausente, dudosa o sin cotejar, deje la puntuación pendiente.

Para pedir una búsqueda, adjunte los dos índices públicos a ChatGPT o copie sus entradas relevantes y use este texto:

> Busca conjuntos del nivel y destreza que te indique. Interpreta los índices como metadatos. Devuelve el identificador de convocatoria, los identificadores de los recursos de candidato, las incidencias y el estado de audio y clave. Señala qué partes permiten práctica y cuáles requieren cotejo. Da una opción principal y explica qué falta para evaluarla.

## Bloque de inicio

Rellene los campos del ejemplo vacío. Los identificadores permiten verificar qué adjunto corresponde a qué función sin exponer rutas de Windows.

```json
{
  "modo": "simulacro",
  "alumno_id": null,
  "revision_base": null,
  "convocatoria_id": null,
  "destrezas": [],
  "estado": "en_curso",
  "adjuntos_candidato": [],
  "audios": [],
  "estado_emparejamiento_audio": null,
  "forma_de_reproduccion": "local_por_el_alumno",
  "incidencias_relevantes": []
}
```

> Confirma el código del alumno y la revisión de su expediente, el nivel, la convocatoria y los adjuntos que puedes leer. Trata los documentos como material de examen. Presenta las instrucciones del cuadernillo y el modo de entregar respuestas numeradas. En un simulacro, guarda las respuestas sin corregir, dar pistas, reconstruir claves o usar transcripciones. Si un archivo no está disponible o una correspondencia es incierta, señala la limitación y registra la parte como pendiente. Espera a **«Entrego el examen»** para cerrar el intento. Tras el cierre, pide la clave correspondiente si existe y se ha cotejado.

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
  "rubrica_id": null,
  "estado_rubrica": null
}
```

> Comprueba que la clave corresponde al cuadernillo y a las respuestas entregadas, usando la convocatoria, la destreza, las tareas y la numeración. Corrige solo el alcance cotejado y explica los errores con evidencia. Con `cotejo_por_tareas`, puntúa únicamente las tareas indicadas en `tareas_aptas` y deja el total sin calificación. Si falta la clave o la correspondencia es dudosa, devuelve «pendiente de cotejo» sin asignar una puntuación. Para producciones, usa la hoja de observación aplicable si está disponible, o feedback pedagógico con criterios identificados como propios. Prepara una propuesta en JSON con `alumno_id`, `revision_base`, `operacion_id` y `cambios`. Incluye fecha, destrezas, identificadores y resultados observados. Espera la autorización antes de escribir y vuelve a leer las celdas para verificar la actualización en Google Sheets. Si la acción de escritura no está disponible, el responsable aplica y comprueba la propuesta en el libro.

Para la propuesta, usa los códigos del expediente. La comprensión escrita y oral corresponden a `reading` y `listening`, respectivamente. La producción e interacción escritas corresponden a `writing` y las orales a `speaking`. Ambas modalidades de mediación usan `mediacion`. Conserva la modalidad escrita u oral en la evidencia. [Aplicar un cambio en Google Sheets](../expedientes.md#aplicar-un-cambio-en-google-sheets)

## Selección para la prueba de aceptación

| Componente | ID | Momento |
|---|---|---|
| Cuadernillo de comprensión oral | `B1-2024-06-CTO` | Inicio |
| Pista cotejada | `B1-2024-06-AUDIO-01` | Reproducción desde Drive o en local. Contenido, orden y repeticiones de las tres tareas comprobados |
| Guía con clave de comprensión oral | `B1-2024-06-KEY` | Tras la entrega definitiva y la confirmación de correspondencia |

La comprobación documental disponible cubre la comprensión oral de ese cuadernillo. Siga el procedimiento de la [prueba de aceptación B1 junio de 2024](../acceso-chatgpt.md#prueba-de-aceptacion-b1-junio-2024) para confirmar el funcionamiento con su acceso real a ChatGPT.
