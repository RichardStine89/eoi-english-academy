# Biblioteca de exámenes EOI

Inventario del 19 de noviembre de 2026. Este catálogo guarda metadatos e identificadores de selección. Los originales y el paquete de auditoría se guardan en ubicaciones privadas. La [guía de acceso](../acceso-chatgpt.md) describe cómo consultar una copia autorizada de Drive o un archivo local.

## Índices

| Documento | Contenido |
|---|---|
| [Convocatorias y modelos](convocatorias.json) | 70 conjuntos con nivel, fecha, organismo, destrezas, lista de cuadernillos, audios, claves, estado de rúbrica e incidencias |
| [Catálogo de archivos](catalogo.json) | 442 registros. Cada uno identifica un archivo físico, su convocatoria, formato, función, destrezas y estado |
| [Manifiesto para ChatGPT](manifiesto-chatgpt.md) | Cómo elegir el material, preparar una sesión y reservar la clave hasta el cierre |
| `biblioteca/inventario-privado.json` | En la carpeta hermana privada `ExpEDIENTES EOI English Academy`. Vincula los 442 identificadores con nombres y rutas locales exactas, tamaño en bytes y huellas SHA-256 |

El campo `convocatoria_id` del catálogo enlaza con `id` en el índice de convocatorias. El `id` de archivo enlaza con el inventario privado. Los sufijos `CTE` y `CTO` identifican los cuadernillos de comprensión, `PCTE` y `PCTO` los de producción escrita y oral, `ME` los archivos de mediación, `AUDIO-01` y `AUDIO-02` las pistas y `KEY` las claves o guías. Los sufijos reflejan el contenido catalogado, que puede diferir del nombre local.

## Recuento y procedencia

| Nivel | Conjuntos | PDF | MP3 | Claves o guías independientes |
|---|---:|---:|---:|---:|
| A1 | 1 modelo sin fecha confirmada | 4 | 2 | 0 |
| A2 | 1 modelo sin fecha confirmada | 4 | 2 | 0 |
| B1 | 21 convocatorias | 111 | 21 | 21 |
| B2 | 20 convocatorias | 106 | 20 | 20 |
| C1 | 19 convocatorias | 102 | 19 | 19 |
| C2 | 8 convocatorias | 43 | 8 | 7 |
| **Total** | **68 convocatorias y 2 modelos** | **370** | **72** | **67** |

Los **442 archivos** son 370 PDF más 72 MP3. Las **67 claves o guías** forman parte de los 370 PDF y comprenden 66 archivos llamados `KEY.pdf` y el solucionario B1 de septiembre de 2012, cuyo nombre es distinto. Cada copia física cuenta en el total. Al agrupar por SHA-256 quedan **440 contenidos distintos**, con dos pares exactos. Las 23 claves de 2021 a 2023 se leyeron mediante OCR y contienen claves y baremos. Las ocho guías de 2024 incluyen claves, transcripciones y pautas de producción y mediación. Las guías y los baremos se registran como documentos de corrección.

La auditoría local volvió a calcular los 442 SHA-256, abrió los 370 PDF y renderizó sus 2.980 páginas sin incidencias de apertura. Los 23 PDF sin capa de texto son legibles por imagen. Para cada archivo, el catálogo distingue la integridad local de la correspondencia con otros materiales.

A1 y A2 constan como modelos de origen sin confirmar y tienen cuatro destrezas y dos pistas cada uno. Los conjuntos fechados B1–C2 se atribuyen a la Junta de Andalucía por la documentación de las pruebas y el archivo histórico institucional. Los enlaces institucionales sirven para localizar las convocatorias y sus instrucciones. La identidad con el original descargado se comprueba por archivo cuando se va a utilizar. Para las hojas de observación, consulte la publicación aplicable a la convocatoria. [Archivo histórico de modelos](https://www.juntadeandalucia.es/educacion/portals/es/web/ced/idiomas/pruebas-de-certificacion/modelos-convocatoria-anterior) · [Portal de certificación y hojas de observación](https://www.juntadeandalucia.es/educacion/portals/es/web/educacion/alumnado/idiomas/pruebas-certificacion) · [Convocatoria 2023/2024 en el BOJA](https://www.juntadeandalucia.es/boja/2024/46/17)

La mediación escrita aparece integrada en los cuadernillos de producción escrita de B1–C1 de 2019 y de B1–C2 de 2023 y 2024. Los `ME` de 2020 a 2022 son cuadernillos de mediación escrita. Los `ME` de 2023 son fichas de mediación oral. El catálogo indica las destrezas de cada cuadernillo y las distingue de las pautas que puedan aparecer en una guía. En el fondo local no se identificaron hojas oficiales de observación completas. C2 se conserva como material de consulta para la academia A1–C1.

## Incidencias y decisión de uso

| Conjunto | Hallazgo y tratamiento |
|---|---|
| `A1-MODELO-01`, `A2-MODELO-01` | Año y organismo sin confirmar. Hay soluciones impresas en las páginas finales de CTE, CTO y PCTE. Los dos solucionarios derivados en Drive son privados y conservan esas respuestas con anotaciones de revisión. Use las páginas de candidato señaladas en el catálogo. Excluya los ítems orales 3, 13 y 15 de A1 y 6 y 8 de A2 de la corrección automática. |
| `C1-2019-06`, `C1-2019-09` | Cada `ME` es idéntico a su `PCTE` de la misma convocatoria. `duplicado_de` conserva la relación y `alias_no_seleccionar` evita contar dos veces el mismo ejercicio. |
| `C2-2021-06` | El archivo oficial de la convocatoria ordinaria contiene seis materiales y carece de clave independiente. Queda pendiente una clave para corregir la comprensión. [Archivo oficial de la Junta](https://www.juntadeandalucia.es/educacion/portals/delegate/content/9705b341-d73e-4361-98c7-2d6e5e25d0b6/ING_C2_ord_21) |
| `C1-2021-09` | La guía local y la distribuida en el archivo oficial de septiembre tienen el mismo SHA-256. Ambas contienen un pie con la fecha de junio. Procedencia confirmada y respuestas pendientes de cotejo por ítem. [Archivo oficial de la Junta](https://www.juntadeandalucia.es/educacion/portals/delegate/content/f4223032-8329-496f-ab3c-08221e3bda2f/ING_C1_sep_21) |
| `C1-2024-06` | Los tres PDF dicen junio y la carpeta original está etiquetada mayo. El MP3 coincide en contenido y orden con las tres tareas de la guía de junio. Falta el cuadernillo CTO para el candidato. El uso de la clave queda bloqueado hasta completar el conjunto. |
| `B2-2024-06`, `B2-2024-09` | Los originales llamados `PCTO.pdf` son cuadernillos de producción y mediación escritas. Sus identificadores terminan en `PCTE`. |
| Los ocho conjuntos de 2024 | Sin cuadernillos independientes identificados de producción oral para el candidato. Las guías contienen pautas de mediación oral y remiten a las hojas de observación. |

Los **72 MP3** se decodificaron de principio a fin y contienen señal sonora. El cotejo da **20 verificados**, **47 parcialmente verificados** y **5 con incidencias**. La comprobación combinó documentos, reconocimiento de voz local y análisis de señal. En dos convocatorias se comparó también con el audio del archivo oficial. El informe privado conserva las marcas temporales y la evidencia por pista. Una correspondencia parcial requiere cotejar las tareas pendientes antes de calificar. El audio de [B1 junio de 2024](../acceso-chatgpt.md#prueba-de-aceptacion-b1-junio-2024) está verificado frente al cuadernillo y la guía para el ensayo en el chat del alumno.

Las **claves oficiales** se identifican por su procedencia institucional. Las **respuestas extraídas** conservan lo impreso en los modelos de origen sin confirmar. Las **propuestas orientativas** de la academia se identifican como no oficiales, se apoyan en evidencia y no sustituyen una clave cuando quedan discrepancias.

## Estados de la clave

| Estado | Uso |
|---|---|
| `no_identificado` | Registrar la práctica y dejar la calificación por clave vacía |
| `clave_embebida_revision_parcial` | Consultar las páginas indicadas en `claves_embebidas` tras la entrega. Usar solo los ítems que el paquete privado coteja con evidencia. La procedencia oficial del modelo sigue sin confirmar. |
| `presente_cotejo_pendiente` | Cotejar nivel, fecha, modalidad, tareas y numeración antes de autorizar la corrección |
| `cotejo_documental_parcial` | Usar exclusivamente para las destrezas que figuran en `alcance_cotejado`, con el audio comprobado si corresponde |
| `dudoso_no_calificar` | Excluir de la calificación mientras la correspondencia siga en duda |

Para un simulacro, la clave, las transcripciones y las explicaciones de respuestas se mantienen fuera del chat y de las fuentes del proyecto hasta que el alumno entregue y cierre todas sus respuestas. Si se confirma un emparejamiento o se incorpora una fuente de rúbrica, registre la fecha, los identificadores y el alcance comprobado en el inventario de trabajo antes de actualizar el estado público. Las observaciones de un intento pertenecen al expediente privado del alumno.
