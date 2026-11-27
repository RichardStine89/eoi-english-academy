# Biblioteca de exámenes EOI

Inventario del 19 de noviembre de 2026, con revisión diferencial v1.2 del 24 al 27 de noviembre. Este catálogo guarda metadatos e identificadores de selección. Los originales y el paquete de auditoría se guardan en ubicaciones privadas. La [guía de acceso](../acceso-chatgpt.md) describe cómo consultar una copia autorizada de Drive o un archivo local.

## Índices

| Documento | Contenido |
|---|---|
| [Convocatorias y modelos](convocatorias.json) | 70 conjuntos con nivel, fecha, organismo, destrezas, lista de cuadernillos, audios, claves, estado de rúbrica e incidencias |
| [Catálogo de archivos](catalogo.json) | 442 registros. Cada uno identifica un archivo físico, su convocatoria, formato, función, destrezas y estado |
| [Manifiesto para ChatGPT](manifiesto-chatgpt.md) | Cómo elegir el material, preparar una sesión y reservar la clave hasta el cierre |
| [Auditoría diferencial v1.2](auditoria-diferencial-v1.2.md) | Cobertura del cotejo, páginas, tareas y condiciones de uso |
| [Fuentes de evaluación](fuentes-evaluacion.md) | Normativa, guías y hojas de observación por edición |
| [Ampliación e inventario de Drive](ampliacion-v1.2.md) | Conciliación de los PDF, permisos comprobados y matriz de nuevas fuentes y documentos pendientes |
| [Índice de fuentes institucionales](recursos-externos-v1.2.json) | Referencias externas por nivel, destreza, organismo, disponibilidad y condiciones de uso |
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

La EOI de Estepa publicó los modelos A1 y A2. Las 20 páginas de los ocho PDF locales coinciden con los modelos completos del centro. Las cuatro pistas coinciden por cotejo de señal. El año del modelo sigue sin confirmar. Los conjuntos fechados B1–C2 se atribuyen a la Junta de Andalucía por la documentación de las pruebas y su archivo histórico. Para las hojas de observación, consulte la publicación aplicable a la convocatoria. [Modelos de la EOI de Estepa](https://www.eoiestepa.es/?page_id=358) · [Archivo histórico de la Junta](https://www.juntadeandalucia.es/educacion/portals/es/web/ced/idiomas/pruebas-de-certificacion/modelos-convocatoria-anterior) · [Portal de certificación y hojas de observación](https://www.juntadeandalucia.es/educacion/portales/es/web/educacion/alumnado/idiomas/pruebas-certificacion)

La mediación escrita aparece integrada en los cuadernillos de producción escrita de B1–C1 de 2019 y de B1–C2 de 2023 y 2024. Los `ME` de 2020 a 2022 son cuadernillos de mediación escrita. Los `ME` de 2023 son fichas de mediación oral. El catálogo indica las destrezas de cada cuadernillo y las distingue de las pautas que puedan aparecer en una guía. En el fondo local no se identificaron hojas oficiales de observación completas. C2 se conserva como material de consulta para la academia A1–C1.

## Incidencias y decisión de uso

| Conjunto | Hallazgo y tratamiento |
|---|---|
| `A1-MODELO-01`, `A2-MODELO-01` | Las seis copias privadas de candidato se comprobaron página por página. Los solucionarios derivados conservan la clave impresa y sus anotaciones. A1 oral 3 y 13 y A2 oral 6 y 8 tienen interpretaciones académicas respaldadas por el audio. A1 oral 15 permanece ambiguo. Los cinco ítems están excluidos de la corrección automática. |
| `B1-2018-06` | El cuadernillo coincide con el archivo oficial. La verificación del audio se basa en las dos tareas y sus tres escuchas. La comparación de señal con la pista publicada no dio una coincidencia concluyente. |
| `C1-2019-06`, `C1-2019-09` | Cada `ME` es idéntico a su `PCTE` de la misma convocatoria. `duplicado_de` conserva la relación y `alias_no_seleccionar` evita contar dos veces el mismo ejercicio. |
| `C2-2021-06` | El archivo oficial de la convocatoria ordinaria contiene seis materiales y carece de clave independiente. Queda pendiente una clave para corregir la comprensión. [Archivo oficial de la Junta](https://www.juntadeandalucia.es/educacion/portals/delegate/content/9705b341-d73e-4361-98c7-2d6e5e25d0b6/ING_C2_ord_21) |
| `C2-2022-06` | El audio corresponde al cuadernillo. En la tarea 2 la consigna numera hasta 10 y ambas escuchas terminan en el extracto 8 tras el ejemplo 0. La corrección automática de esa tarea queda bloqueada. |
| `C1-2021-09` | La guía local coincide con la del paquete oficial de septiembre. La guía dice junio en el pie y B1 en un preámbulo. Se cotejaron las 26 respuestas de comprensión oral. La corrección automática de comprensión escrita queda bloqueada por una discrepancia entre el texto y la clave de la tarea 3, ítem 8. [Archivo oficial de la Junta](https://www.juntadeandalucia.es/educacion/portals/delegate/content/f4223032-8329-496f-ab3c-08221e3bda2f/ING_C1_sep_21) |
| `C1-2024-06` | Los tres PDF dicen junio y la carpeta original está etiquetada mayo. El MP3 coincide en contenido y orden con las tres tareas de la guía de junio. Falta el cuadernillo CTO para el candidato y se mantiene bloqueada la corrección de comprensión oral. Consulte el alcance específico para comprensión escrita. |
| `B2-2024-06`, `B2-2024-09` | Los originales llamados `PCTO.pdf` son cuadernillos de producción y mediación escritas. Sus identificadores terminan en `PCTE`. |
| Los ocho conjuntos de 2024 | Sin cuadernillos independientes identificados de producción oral para el candidato. Las guías contienen pautas de mediación oral y remiten a las hojas de observación. |

Los **72 MP3** se decodificaron de principio a fin y contienen señal sonora. El cotejo del conjunto da **67 verificados**, **0 parcialmente verificados** y **5 con incidencias**. La revisión utilizó cuadernillos, transcripciones, comparación de señal y, cuando estuvo disponible, el paquete institucional. Cuatro pistas con incidencias de A1/A2 sí coinciden con el modelo publicado. Su clave o consigna siguen requiriendo las precauciones indicadas. La incidencia restante es C1 junio de 2024, cuya guía coincide con el audio y cuyo cuadernillo sigue ausente. Una correspondencia parcial se excluye de la calificación automática. El audio de [B1 junio de 2024](../acceso-chatgpt.md#prueba-de-aceptacion-b1-junio-2024) está verificado frente al cuadernillo y la guía.

Las **claves oficiales** se identifican por su procedencia institucional. Las **respuestas extraídas** conservan lo impreso en los modelos de práctica publicados por la EOI de Estepa. Las **propuestas orientativas** de la academia se identifican como no oficiales. Cuando queda una discrepancia, el ítem se excluye de la corrección automática.

## Comprensión oral utilizable para evaluación

Hay ocho conjuntos con audio, cuadernillo y clave cotejados para puntuar toda la comprensión oral con finalidad pedagógica.

| Nivel | Conjuntos aptos |
|---|---|
| B1 | Septiembre de 2012 y junio de 2024 |
| B2 | Septiembre de 2012, junio de 2024 y septiembre de 2024 |
| C1 | Septiembre de 2021 y septiembre de 2024 |
| C2 | Junio de 2024 |

En B1 septiembre de 2024 se puede puntuar la tarea 3. En C2 septiembre de 2024 se pueden puntuar las tareas 2 y 3. Las demás tareas de esos dos conjuntos presentan un conflicto entre la consigna particular y el baremo general de la guía. El catálogo documenta también los rangos de respuesta que difieren entre la consigna y la cuadrícula, y las variantes que requieren juicio humano. Consulte `evaluacion_comto` antes de puntuar. El alcance aquí indicado cubre comprensión oral.

## Comprensión escrita utilizable para evaluación

En `solucionario.evaluacion_comte`, `tareas_aptas` identifica tareas completas y `preguntas_aptas` identifica ítems aislados de una tarea parcial. Este alcance se aplica exclusivamente a comprensión escrita, con independencia del estado de comprensión oral del conjunto. Cuando una tarea tenga preguntas bloqueadas, la puntuación podrá indicar los aciertos de los ítems aptos y la cantidad revisada. El total del ejercicio queda vacío si el alcance no comprende sus tres tareas completas.

| Conjunto | Alcance de corrección automática |
|---|---|
| `B1-2024-09` | Tarea 3 completa |
| `B2-2024-09` | Tareas 2 y 3 completas |
| `C1-2024-06` | Tareas 2 y 3 completas. De T1, ítems 1 y 3–6 |
| `C1-2024-09` | Tarea 3, ítems 1, 3–5 y 7–10 |

El [registro diferencial](auditoria-diferencial-v1.2.md) documenta los bloqueos, los tiempos y el alcance de los cotejos. En A2 modelo 1, la verificación de procedencia del audio confirma que es la grabación publicada. La consigna y la numeración de la primera tarea difieren de esa grabación y se excluye la tarea completa de la corrección automática.

## Estados de la clave

| Estado | Uso |
|---|---|
| `no_identificado` | Registrar la práctica y dejar la calificación por clave vacía |
| `clave_embebida_revision_parcial` | Consultar las páginas indicadas en `claves_embebidas` tras la entrega. Usar solo los ítems que el paquete privado coteja con evidencia y respetar las exclusiones de corrección automática |
| `presente_cotejo_pendiente` | Cotejar nivel, fecha, modalidad, tareas y numeración antes de autorizar la corrección |
| `cotejo_documental_parcial` | Usar exclusivamente las destrezas que figuran en `alcance_cotejado`. Para comprensión oral, comprobar también `evaluacion_comto` |
| `cotejo_por_tareas` | Puntuar únicamente las tareas de `evaluacion_comto.tareas_aptas`. Dejar las demás y el total sin calificación |
| `dudoso_no_calificar` | Excluir de la calificación mientras la correspondencia siga en duda |

Para un simulacro, la clave, las transcripciones y las explicaciones de respuestas se mantienen fuera del chat y de las fuentes del proyecto hasta que el alumno entregue y cierre todas sus respuestas. Si se confirma un emparejamiento o se incorpora una fuente de rúbrica, registre la fecha, los identificadores y el alcance comprobado en el inventario de trabajo antes de actualizar el estado público. Las observaciones de un intento pertenecen al expediente privado del alumno.
