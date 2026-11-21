# Expedientes académicos privados

## Fuente de referencia y acceso

**Google Sheets es el expediente principal**. Cada estudiante usa un libro privado independiente y su propio código, `alumno-01` o `alumno-02`. Vincula el libro ya existente del alumno 01 en su espacio privado. Para el alumno 02, vincula un libro separado con su código y estructura de pestañas, sin copiar filas, historial ni evidencias del alumno 01. Conserva cada enlace en el espacio privado del alumno. GitHub solo contiene instrucciones y formatos vacíos, sin enlaces a expedientes, nombres personales, notas, evidencias ni datos de acceso.

ChatGPT puede leer el libro y actualizarlo desde su conexión autorizada a Google Drive cuando la acción esté habilitada y la cuenta conectada tenga el permiso correspondiente. Comprueba la lectura en el chat que se usará para las clases. En superficies compatibles también puedes realizar la actualización desde ChatGPT Work o desde la barra lateral de ChatGPT para Google Sheets. Si en ese contexto solo puedes leer, prepara la propuesta y aplícala manualmente en Google Sheets. Mantén el mismo control de revisión y la lectura posterior. [Conectar Google Drive a ChatGPT](https://help.openai.com/en/articles/10929079-google-drive-app-and-setup-in-chatgpt) · [ChatGPT Work con Google Workspace](https://help.openai.com/en/articles/20001278-creating-and-editing-documents-spreadsheets-and-presentations-with-chatgpt-work) · [Barra lateral para Google Sheets](https://help.openai.com/en/articles/20001063-chatgpt-for-excel-and-google-sheets)

Usa un proyecto privado por estudiante y aporta solo su libro y las evidencias necesarias. Si cada alumno debe tener acceso independiente, usa cuentas separadas y comparte cada libro únicamente con quienes lo necesiten. La separación de proyectos dentro de una misma cuenta organiza el contexto. Los permisos del libro y de la cuenta conectada controlan el acceso. [Permisos y acciones de Google en ChatGPT](https://help.openai.com/en/articles/10408842-google-app-data-controls-faq)

## Alta del expediente del alumno 02

1. En la cuenta de Google del alumno 02, crea una hoja de cálculo vacía desde [Google Sheets](https://sheets.google.com). Ponle un nombre identificable, por ejemplo `EOI English Academy · alumno-02`, y conserva **Acceso general → Restringido**. La persona responsable solo necesita acceso de editor si va a mantener el expediente. Comparte el vínculo en privado con quien deba tener acceso. [Compartir archivos en Google Drive](https://support.google.com/drive/answer/2494822?hl=es)
2. Renombra la primera pestaña como `Resumen`. Escribe `Alumno ID` y `alumno-02` en `A2:B2`, y `Revisión` y el número `0` en `A3:B3`. Deja vacíos los campos académicos hasta la primera sesión real.
3. Crea las otras nueve pestañas indicadas en la tabla siguiente y añade una fila de encabezados con los campos de cada pestaña. Usa `ID` como primera columna para poder localizar filas después. En `Historial` incluye además `ID de operación` y `Verificado`. El libro arranca con sus propias filas vacías.
4. Comprueba desde la cuenta gratuita de ChatGPT del alumno 02 que el código y la revisión leídos son los de su libro. Si el conector no está disponible, abre la hoja en Google Sheets y usa la [ruta manual de la guía de acceso](acceso-chatgpt.md#alta-del-alumno-02-con-chatgpt-free).

## Estructura del libro

El libro del alumno 01 tiene diez pestañas. Conserva las columnas y los formatos existentes. Lee sus encabezados antes de dirigir operaciones a celdas concretas. Comprueba que `Resumen!A2` y `A3` son **Alumno ID** y **Revisión** antes de usar `Resumen!B2` y `B3`. La revisión es un entero no negativo. En el libro del alumno 02 confirma la ubicación de ambos campos antes de usar el mismo flujo.

| Pestaña | Qué registrar |
|---|---|
| Resumen | Código, revisión y estado vigente, con nivel estimado, última sesión, próxima unidad y objetivo cuando consten |
| Unidades | Estado y fechas por código de unidad, con evidencia en observaciones cuando se acredita la finalización |
| Sesiones | Fecha, unidad, destrezas, duración real, actividad, resultado y próxima acción |
| Evaluaciones | Fecha, nivel, unidad, destreza, tipo, nota sobre 10 si procede, criterio y referencia privada a la evidencia |
| Vocabulario | Palabra, significado, ejemplo, dominio y próximo repaso según el trabajo realizado |
| Errores | Error observado, corrección, regla y referencia a la revisión |
| Exámenes EOI | Convocatoria, destreza, tipo, puntuación y baremo si proceden, y evidencia. Conserva los identificadores del catálogo y el estado de la clave en el detalle asociado |
| Repasos | Fecha prevista, contenido, intervalo, estado y resultado del repaso realizado |
| Objetivos | Objetivo observable, destreza, prioridad, estado y fecha de cierre |
| Historial | Fecha, revisión, acción, sección, detalle y estado de verificación |

Usa los códigos `reading`, `listening`, `writing`, `speaking`, `mediacion`, `gramatica`, `vocabulario` y `pronunciacion` en registros nuevos con campo de destreza. Usa el código curricular para cada unidad, por ejemplo `A1-01`. Deja vacía una nota pendiente. El cero corresponde a un resultado medido. Registra notas, unidades completadas y avances solo con evidencia de ese alumno. Para tareas por voz, distingue grabación o voz en directo de respuestas escritas. Para un examen, asocia la evidencia de evaluación con la convocatoria, los materiales y el estado de la clave.

## Aplicar un cambio en Google Sheets

1. **Lee la base.** Abre el libro del código activo en una lectura nueva. Comprueba el código y la revisión en **Resumen**. Lee encabezados, fórmulas, validaciones y las filas exactas que podrían cambiar. Si ves otro alumno, encabezados ambiguos o dos revisiones, pide la fuente correcta antes de preparar cambios.
2. **Propón cambios concretos.** Indica alumno, revisión de partida, un identificador único de la operación, pestaña, rango o fila a añadir, valores previos y nuevos, y evidencia. Para una fila existente, usa su identificador si lo tiene. En su ausencia, comprueba su contenido identificativo y el rango actual. Pide aclaración si la fila no se puede identificar sin ambigüedad. Una propuesta sin cambios conserva la revisión.
3. **Aplica tras la autorización.** Una sola persona coordina las escrituras sobre ese libro. Inmediatamente antes de modificar, vuelve a leer los campos de control y los rangos objetivo y busca el identificador de operación en **Historial**. Si ya consta, verifica el resultado según el paso 4 sin volver a aplicar la operación. Si cambió la revisión o el contenido esperado, prepara otra propuesta a partir de los datos vigentes. Aplica solo las celdas acordadas, aumenta la revisión en uno y registra el identificador de operación, fecha, secciones y detalle en **Historial** con verificación pendiente. Si la acción ofrece un lote de cambios, agrupa las celdas, la revisión y el historial. El lote de Sheets se aplica junto, pero la lectura previa no bloquea ediciones concurrentes. [Comportamiento de las actualizaciones por lotes de Google Sheets](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/batchUpdate)
4. **Vuelve a leer y compara.** Haz una lectura nueva de los rangos cambiados, **Resumen** e **Historial**. Compara cada valor, el código, la revisión y el identificador con lo acordado. Solo cuando coincidan actualiza el campo **Verificado**, según el formato existente, y vuelve a leerlo. Informa de cualquier diferencia o verificación pendiente. Ante un error o respuesta indeterminada, lee primero los rangos y busca el identificador en **Historial** antes de reintentar. Si la operación se aplicó parcialmente o hay un conflicto, deja que la persona responsable concilie lo guardado. Una rectificación confirmada se registra como una revisión nueva.

Para preparar la propuesta, puede usarse esta instrucción en el chat privado.

> Consulta el único libro autorizado. Confirma `alumno_id` y `revision_base` con una lectura actual. Devuelve una propuesta con `alumno_id`, `revision_base`, `operacion_id` y `cambios`. Para cada cambio, indica la pestaña, el rango o fila, los valores que esperas encontrar y los nuevos, y la evidencia que los justifica. Espera mi autorización para escribir. Después de escribir, comprueba el resultado mediante una lectura nueva y comunica qué se verificó.

Si solo tienes una copia, úsala como contexto fechado. El responsable leerá el libro vigente antes de registrar cualquier cambio. Los archivos privados de Windows requieren acceso explícito. ChatGPT puede dar una propuesta o un archivo para descargar, y el responsable guarda la copia en la ubicación privada.

## Respaldo periódico en JSON

Haz una exportación privada al final del mes en que haya cambios y antes de modificaciones grandes del libro. El JSON es una copia de los datos en un momento determinado. La [plantilla JSON académica](plantillas/expediente.json) y el [resumen base](plantillas/resumen.md) siguen disponibles como formatos opcionales para notas y respaldos estructurados. Sus campos no reemplazan las pestañas ni la revisión en Google Sheets.

1. Confirma el código, la revisión y las pestañas del libro. Con la conexión autorizada, lee cada rango con datos por bloques acotados. Si el chat no puede leer el rango completo, descarga el libro desde **Archivo → Descargar → Microsoft Excel (.xlsx)** y genera el JSON a partir del archivo descargado. Un CSV de una sola pestaña no representa el libro. [Descargar archivos de Google Sheets](https://support.google.com/docs/answer/49114?hl=es)
2. Exporta los valores de todas las pestañas y conserva sus nombres, orden, encabezados y celdas vacías interiores. Indica los rangos exactos de origen. Usa `null` para una celda vacía, fechas y marcas temporales ISO 8601 cuando se pueda determinar su tipo, y números para valores numéricos. Si conservas el valor calculado de una fórmula, guarda también el XLSX cuando necesites una copia que mantenga fórmulas o formato.
3. Abre el resultado como JSON y verifica código, revisión, diez pestañas en el libro actual del alumno 01, lista de rangos, encabezados y recuento de filas con datos por pestaña. Compara valores de muestra y las celdas de **Resumen** e **Historial** con el origen. Vuelve a leer la revisión al final. Si cambió durante la exportación, repite la lectura o toma una descarga coherente con una revisión comprobada.
4. Guarda un archivo nuevo `expediente-respaldo-AAAA-MM-DD-rN.json` dentro de la carpeta privada del alumno, fuera del repositorio. Conserva versiones anteriores. Si necesitas recuperar información, compara el respaldo con el libro actual y aplica una rectificación aprobada en una nueva revisión.

La forma del JSON de respaldo es `{ "formato": "eoi-sheets-v1", "alumno_id": "...", "revision": 0, "exportado_en": "...", "hojas": [{ "nombre": "...", "rango": "...", "filas": [] }] }`. Usa una matriz de filas por pestaña. El ejemplo describe el formato y no contiene datos reales.

## Gráficas de seguimiento

Lee el libro privado del alumno activo o su respaldo validado. Trabaja con los registros observados y una única revisión. Si falta evidencia para una métrica, muestra «sin datos». [Análisis de datos en ChatGPT](https://help.openai.com/en/articles/8437071-advanced-data-)

| Gráfica | Cálculo |
|---|---|
| Evolución | Fecha y nota comparable por destreza con criterio, escala y número de observaciones |
| Calificación por destreza | Última evaluación comparable por destreza, con fecha y escala |
| Unidades completadas | Recuento de códigos curriculares distintos con estado completado, por nivel y por fecha de cierre |
| Actividades realizadas | Recuento por semana y tipo a partir de las sesiones y actividades registradas, con una sola aportación de minutos por sesión |
