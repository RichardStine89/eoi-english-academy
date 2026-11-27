# EOI English Academy

Academia de inglés A1–C1 impartida en **ChatGPT**. Cada estudiante tiene su diagnóstico, itinerario, práctica y expediente. Codex se reserva para mantenimiento puntual del repositorio.

## Empezar

1. Configura el espacio privado de cada alumno con la [guía de acceso desde ChatGPT](acceso-chatgpt.md).
2. Carga la [guía docente](docencia.md) y conecta el [expediente privado en Google Sheets](expedientes.md) del alumno que va a estudiar.
3. Inicia el diagnóstico si el expediente está vacío. Después usa la [matriz curricular](curriculo-eoi.md) y la unidad que corresponda.
4. Si vais a preparar una prueba, selecciona los materiales en la [biblioteca de exámenes](examenes/README.md) y usa el [manifiesto de sesión](examenes/manifiesto-chatgpt.md). La [prueba de aceptación de B1](acceso-chatgpt.md#prueba-de-aceptacion-b1-junio-2024) describe la entrega y la corrección con clave.

## Documentos de referencia

| Documento | Qué contiene |
|---|---|
| [Currículo A1–C1](curriculo-eoi.md) | Índice de las 60 unidades y su relación con el MCER y las cinco actividades de lengua de EOI Andalucía |
| [Recursos y complementos](curriculo-practica.md) | Práctica interactiva, listening y pronunciación por unidad, con actividades de refuerzo y claves propias |
| [Biblioteca de aprendizaje](biblioteca-aprendizaje.md) | Recursos de práctica por destreza y certificaciones complementarias |
| [Pronunciación por unidad](pronunciacion-por-unidad.md) | 60 prácticas, de los sonidos de A1 a la inteligibilidad y adaptación del registro en C1 |
| [Inglés turístico](ingles-turistico.md) | Itinerario complementario para situaciones profesionales de A1 a C1 |
| [Guía docente](docencia.md) | Diagnóstico, estructura de clase, recursos gratuitos, práctica oral, corrección y progresión |
| [Biblioteca de exámenes](examenes/README.md) | Materiales A1–C2, estados de verificación, inventario privado y criterios para seleccionar pruebas |
| [Expedientes](expedientes.md) | Acceso, actualización y verificación en Google Sheets, separación de alumnos y respaldo en JSON |
| [Plantillas](plantillas/expediente.json) y [resumen Markdown](plantillas/resumen.md) | Formatos vacíos, sin datos de estudiantes |
| [Fuentes de AI Language Tutor](../../languages/english/curriculum/overview.md) | Unidades originales y [metodología de referencia](../methodology.md) |
| [Aceptación v1.2](aceptacion-v1.2.md) | Protocolo pedagógico, pruebas humanas, promoción y plan de preparación hasta septiembre de 2027 |
| [Pronunciation Lab](pronunciacion.md) | Grabación, práctica con modelo británico, revisión de tramos y transferencia privada al tutor |
| [Seguimiento v1.2](desarrollo-v1.2.md) | Estado comprobado, límites y puntos para reanudar |

La matriz distingue el material institucional identificado, los recursos externos y los ejercicios originales. Las calificaciones de ChatGPT sirven para orientar el estudio. El simulador Cambridge del repositorio es práctica complementaria y C2 queda disponible en la biblioteca como nivel de consulta.

Cada expediente principal vive en un Google Sheets privado. La carpeta hermana `ExpEDIENTES EOI English Academy` puede conservar los respaldos JSON y el inventario con rutas y huellas. El repositorio contiene la documentación, el catálogo de metadatos y las plantillas vacías.

## Mantenimiento mensual

1. Consulta el portal de certificación y el BOJA. Registra la fecha, la fuente y el cambio que afecte a inscripción, convocatorias, destrezas o baremos. [Portal de certificación](https://www.juntadeandalucia.es/educacion/portales/es/web/educacion/alumnado/idiomas/pruebas-certificacion)
2. Al incorporar un examen o recurso, comprueba nivel, fecha, destreza, acceso y condiciones de uso. Coteja PDF, audio, clave o rúbrica por contenido y comprueba duplicados con huellas cuando los archivos estén disponibles. Mantén en el catálogo las incidencias y bloquea la corrección de lo que quede sin evidencia. [Biblioteca](examenes/README.md)
3. Abre una muestra de enlaces del nivel activo, en especial los ejercicios autocorregibles y el audio. Sustituye enlaces rotos con un recurso verificado y actualiza su ficha. Añade materiales a la unidad cuando tengan un propósito concreto.
4. Con la cuenta y permiso correspondientes, comprueba código de alumno, última revisión, fórmulas y accesos. Guarda una copia privada cuando el libro haya cambiado. Cambia celdas solo con autorización sobre esa operación. [Respaldo de expedientes](expedientes.md#respaldo-periódico-en-json)
5. Registra el mantenimiento y los resultados. Ejecuta `python tools/validate_academia.py` si cambiaste el catálogo o la documentación. Si modificaste Pronunciation Lab, ejecuta su regresión antes de publicar. Mantén las clases, práctica y seguimiento diario en ChatGPT y Sheets. Para reabrir la investigación fonética hace falta autorización expresa de Dirección Académica.
