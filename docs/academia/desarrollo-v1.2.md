# Seguimiento de EOI English Academy v1.2

## Punto de reanudación · 24 de noviembre de 2026

`main` local y remoto coincidían en `5b641b543c9ae713db0ce4a6d4d26f633cf26f96`. Al reanudar no había cambios rastreados ni en el índice. Los dos adaptadores `.agents` que ya estaban sin seguimiento se dejan fuera. Las asignaciones previas de currículo, exámenes e interfaz no habían dejado diffs ni commits en ese punto. La base incluye el laboratorio local y su cotejo orientativo, el writing obligatorio y la auditoría previa de los audios. La versión candidata requiere aceptación de Dirección Académica para su cierre.

| Fase de la orden | Estado al reanudar | Evidencia o trabajo pendiente |
|---|---|---|
| Diagnóstico y planificación | Punto de partida comprobado | Git local y GitHub comparados. Informes privados anteriores disponibles. |
| Currículo, destrezas y recursos | En curso | Auditoría pedagógica de las 60 unidades, correspondencia con fuentes oficiales, lagunas y complementos. |
| Pronunciación y validación | Prioritaria, en curso | Base reproducible: en 62 casos humanos, 1 verdadero positivo, 11 verdaderos negativos, 0 falsos positivos, 9 falsos negativos y 41 abstenciones. Falta explicar pérdidas y contrastar una alternativa con evidencia independiente. |
| Interfaz Tk | En curso | Maximización, lectura F11 y Escape, controles visibles y comprobación por resolución y escala. |
| Exámenes, rúbricas y simulacros | En curso | Reutilizar auditoría previa. Cotejo diferencial de documentos y fuentes oficiales. Mantener bloqueos si falta evidencia. |
| Expedientes | Pendiente | Verificación de pestañas, fórmulas, gráficos, revisión, idempotencia y separación. Las pruebas con datos sintéticos quedan fuera de los libros reales. |
| Evaluación integral y plan a septiembre de 2027 | Pendiente | Protocolo técnico, pedagógico y humano. Hitos sujetos a evidencia de nivel. |
| Regresión, documentación y publicación | Pendiente | Publicar exclusivamente los archivos seguros que pasen las comprobaciones. Sin etiqueta definitiva. |

## Reanudación · 27 de noviembre de 2026

GitHub y el `HEAD` local seguían en `5b641b5`. El índice estaba vacío. Se recuperaron 55 archivos rastreados modificados y cinco archivos nuevos de la intervención, además de los dos `.agents` preexistentes. Quedaron guardados los cambios de fonética, currículo, exámenes e interfaz. La caché de investigación conserva las 48 tomas L2‑ARCTIC de cuatro voces hispanohablantes. Se reutiliza para la comparación y queda fuera de Git.

- **Expedientes, lectura completada.** Dos libros distintos con el código correspondiente, diez pestañas y 60 códigos de unidad únicos cada uno. En el primero constan fórmulas y dos gráficos. En el segundo faltan estos indicadores en el bloque revisado. El protocolo de escritura contempla las revisiones numéricas almacenadas como texto y el identificador de operación. La [propuesta de panel y control](expedientes.md#revisión-de-v12-y-propuesta-pendiente-de-autorización) queda pendiente de autorización y de prueba desde ambas cuentas. Se conservan los libros reales.
- **Protocolo y calendario, borrador guardado.** [Aceptación, recuperación y plan a septiembre de 2027](aceptacion-v1.2.md). La fecha es un horizonte académico. El BOJA vigente sitúa las pruebas extraordinarias antes de finalizar junio y la convocatoria concreta requiere confirmación oficial.
- **Fonética, comparación completada.** Regresión SpeechOcean762 idéntica, 1/50 (2 %). En 48 tomas L2‑ARCTIC de cuatro voces hispanohablantes, el cotejo base detectó 0/144. Al incorporar la lectura exploratoria de la salida libre CTC de ZIPA, el ensayo detectó 1/144 con 3 falsos avisos. La candidata usa esa vía para escucha humana, con confianza `null` y sin intervenir en la calificación. Se documentaron límites británicos, cobertura y criterios para una validación futura con separación por hablante. [Resultados y reproducción](../../modules/pronunciation-lab/README.md#validación-con-voces-hispanohablantes)

## Candidata para aceptación académica

| Fase | Resultado comprobado | Pendiente antes de la aceptación definitiva |
|---|---|---|
| Currículo | 60 unidades revisadas, 46 corregidas conservando los identificadores, matriz completa y cinco complementos graduados. 60 filas con recursos interactivos, listening y pronunciación. Los índices de British Council confirmaron 42 títulos de gramática y 48 de escucha. | Comprobar en el dispositivo del estudiante los reproductores, las actividades interactivas y la adecuación de acento y ritmo. [Matriz](curriculo-eoi.md) · [Recursos y práctica](curriculo-practica.md) |
| Fonética | ZIPA int8 reutilizado. Regresión de voz sintética y dos corpus humanos reproducibles. Indicios libres con marcas temporales para escucha, sin nota. | Sigue bloqueada la corrección automática. Validación británica y en más hablantes pendiente. Practicar y contrastar por escucha. [Guía](pronunciacion.md) |
| Interfaz Tk | Vista de práctica maximizada, resultados separados, letra ajustable, F11 y Escape, fragmentos numerados y grabación accesible durante lectura. Comprobación visual a 1920×1080/100 % y pruebas de tamaños 1920×1080, 1366×768 y 1280×720 con 100, 125, 150 y 200 % simulados en Tk. | Confirmar uso en las pantallas y micrófonos de los estudiantes. [Lanzador y uso](../../modules/pronunciation-lab/README.md) |
| Exámenes y rúbricas | 442 rutas y tamaños sin cambios. 104 ítems COMTE cotejados. 63 aptos por tarea o ítem. B1 junio 2024 COMTO conserva su clave y baremo. Guía 2025/26 y rúbricas históricas verificadas. El material general 2026/27 consultado está rotulado como borrador. | Los totales de los cuatro COMTE parciales y las incidencias documentadas siguen bloqueados. Confirmar publicación final de rúbricas y calendario de la convocatoria concreta. [Auditoría diferencial](examenes/auditoria-diferencial-v1.2.md) · [Fuentes](examenes/fuentes-evaluacion.md) |
| Expedientes | Lectura de dos libros con códigos distintos y 60 unidades cada uno. Pruebas sintéticas de grupos de destrezas, notas vacías frente a cero, escalas, deduplicación, revisión e idempotencia. | Autorizar por separado cambios del panel, gráficos y campo de operación. Verificar aislamiento de acceso desde cada cuenta. [Propuesta](expedientes.md#revisión-de-v12-y-propuesta-pendiente-de-autorización) |
| Destrezas, repaso y promoción | Writing obligatorio mantenido. Casos originales con criterios de reading y mediación oral y escrita, plan de recuperación y práctica de simulacro con barrera de claves. Los contrastes forman parte de la práctica, y los errores requieren evidencia. | Completar los ensayos reales, conservar resultados autorizados y cerrar con Dirección Académica. [Protocolo](aceptacion-v1.2.md) |
| Regresión y seguridad | 12 pruebas unitarias aprobadas, 28 cotejos sintéticos y validación de rutas y bloqueos. Código, reglas y metadatos quedan en el repositorio. Los audios, informes privados, expedientes, modelos y cachés permanecen fuera del contenido publicado. | Los modelos y herramientas solo se revisan ante errores, requisitos académicos y mantenimiento autorizado. |

**Recomendación técnica: LISTA PARA ACEPTACIÓN CON RESTRICCIONES.** Se presenta para pruebas y decisión de Dirección Académica. No se fija etiqueta definitiva. Tras la aceptación, los cambios se limitan a mantenimiento, corrección, seguridad y mejoras pedagógicas necesarias para el itinerario.
