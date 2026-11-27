# Validación fonética v1.2 · Adjudicación y reserva final

El evaluador de esta fase comprueba el objetivo avanzado por contraste de **80 % de sensibilidad efectiva, 95 % de precisión y 90 % de cobertura**. El cierre experimental añade el mínimo para avisos orientativos de **60 %, 90 % y 80 %**, también con voces y guiones independientes. Se conserva el mínimo de 20 errores, 20 controles legítimos y cuatro voces con casos confirmados. Se incluyen controles británicos y se revisan por separado los avisos sobre variantes válidas. [Cierre y niveles](cierre-hibrido-fonetico-v1.2.md) · [Evidencia de la fase 2](investigacion-fonetica-v1.2-fase-2.md)

## Adjudicación del piloto externo

Las predicciones y los 15 audios de Speech Accent Archive ya disponibles se conservaron. Se preparó un paquete local ciego de 75 posiciones, con 31 prioritarias, dos fichas de revisión en orden distinto y una clave aparte. Hay 51 fragmentos con contexto, localizados con anclas fonéticas próximas, y 24 posiciones que deben localizarse en el audio completo. Se comprobó que cada fragmento corresponde a su toma. Las marcas de emisión son aproximadas. Antes de decidir, el revisor verifica que ha escuchado la palabra objetivo y su entorno.

| Prioridad | Posiciones pendientes |
|---|---:|
| Español L1 · [z] en la transcripción y [s] en IF‑MDD | 7 |
| Español L1 · [s] en la transcripción y [z] en IF‑MDD | 3 |
| Español L1 · [s] en la transcripción y sin asignación | 1 |
| Español L1 · otras etiquetas de la transcripción | 9 |
| Inglés británico L1 · [z] en la transcripción y [s] en IF‑MDD | 5 |
| Inglés británico L1 · [z] en la transcripción y sin asignación | 2 |
| Inglés británico L1 · otras etiquetas de la transcripción | 4 |

Se han recibido **cero revisiones humanas**. Las 31 posiciones prioritarias siguen pendientes. A cada revisor se le entrega su ficha, los mismos audios y el guion, con las predicciones, la transcripción IPA original y la identificación de los grupos ocultas. Ambos anotan por separado el tramo y la realización que oyen. Después indican si la realización conserva el contraste, es una variante legítima, es una sustitución, corresponde a otra lectura o queda incierta. Un tercer revisor resuelve las discrepancias. Cuando falte evidencia audible se conserva el estado ambiguo. La transcripción original aporta una comparación superficial. [Método del corpus](https://accent.gmu.edu/howto/)

## Qué aportó Praat

Se midió periodicidad durante la fricación en las ventanas estimadas del piloto. El veto se fijó con L2‑ARCTIC y deriva a revisión los avisos con periodicidad o señal insuficiente. Se reutilizaron las predicciones congeladas. La evaluación sigue comparando con las etiquetas superficiales del corpus, a la espera de adjudicación.

| Español L1, mismo subconjunto de 41 posiciones | Coincidencias [s] | Avisos sobre [z] | Precisión | Sensibilidad efectiva | Cobertura |
|---|---:|---:|---:|---:|---:|
| IF‑MDD congelado | 26/30 | 7/11 | 78,79 % | 86,67 % | 97,56 % |
| IF‑MDD con veto acústico fijo | 26/30 | 6/11 | 81,25 % | 86,67 % | 95,12 % |

Entre las 21 posiciones británicas transcritas como [z], el veto redujo los avisos de cinco a tres y elevó las abstenciones de dos a cuatro. En los avisos, la fricación estimada tuvo medianas de 65 ms tanto en [s] de español L1 como en [z] de español L1, y 70 ms en [z] británicas. Los rangos se solapan. Desplazar la ventana 20 ms en cualquiera de las dos direcciones cambió la decisión de periodicidad para al menos un desplazamiento válido en 11 de 33 avisos hispanohablantes. La ventana estimada para la vocal precedente fue más larga en [z] que en [s] entre algunos avisos, con medianas de 130 y 105 ms. La muestra es pequeña, los intervalos se solapan y los límites carecen de verificación manual. Conservar la duración como variable de investigación exige delimitar la vocal y la fricativa y controlar el entorno. [Ensordecimiento británico](https://www.internationalphoneticassociation.org/icphs-proceedings/ICPhS2011/OnlineProceedings/RegularSession/Verhoeven/Verhoeven.pdf) · [Duración vocálica y percepción](https://ora.ox.ac.uk/objects/uuid%3A1e64ab8f-92cf-46a3-bdf0-a686f5096009)

En esa muestra, mantener al menos 80 % de sensibilidad exigiría acertar 24 de 30 [s]. Una precisión del 95 % toleraría como máximo un aviso sobre [z]. Para llegar desde siete avisos a uno habría que retirar al menos seis. La cobertura del 90 % solo admite cuatro abstenciones en 41 posiciones y ya hay una. Un filtro que solo añada abstenciones es insuficiente. El siguiente ensayo debe recuperar controles correctos mediante mejor alineación, duración vocal y consonántica, periodicidad y contexto, con una comparación de cada señal por separado. Todavía faltan etiquetas adjudicadas para entrenarlo y medirlo fuera del ajuste.

## Reserva previa a la evaluación final

- **Controles británicos.** Se reservaron ocho voces candidatas y 40 guiones distintos de SLR83 a partir del índice ortográfico, con dos voces por cada grupo Midlands, Northern, Scottish y Southern. Se excluyeron coincidencias exactas de texto normalizado con CMU ARCTIC, los guiones de SpeechOcean762 disponibles y Speech Accent Archive. Las ventanas incluyen candidatos al final del enunciado y antes de vocal o consonante según el texto. Se conserva la lista y su huella fuera del código publicado. Quedan pendientes el audio y la revisión fonética. [SLR83](https://www.openslr.org/83/) · [Artículo del corpus](https://aclanthology.org/2020.lrec-1.804/)
- **Aprendientes de español L1.** Se reservaron 32 guiones originales en la caché local. Hay 24 con objetivo /z/, repartidos entre inicio, interior y final de palabra, y ocho con /s/ para comprobar aparte las alarmas sobre el otro fonema. Falta reclutar y grabar voces adultas independientes con permiso de investigación. Los guiones quedan reservados para la evaluación y no se usarán para ajustar el modelo. La disponibilidad de grabaciones se declarará cuando existan.
- **MRPL2 v1.1.** La ficha pública y la API de Zenodo confirman la versión 1.1, la declaración CC BY 4.0 y `restricted` con cero archivos públicos. La interfaz requiere una solicitud identificada y la aprobación del titular. Quedan por verificar los archivos y cualquier condición que acompañe al acceso. Los guiones procedentes de ARCTIC deben excluirse si coinciden con los usados para entrenamiento o ajuste. [Registro exacto](https://zenodo.org/records/22690685) · [Solicitud de acceso de Zenodo](https://help.zenodo.org/docs/share/access-requests/request-access/)

Antes de abrir el conjunto final, registra la huella de la configuración y la del manifiesto de casos. Usa identificadores coherentes de hablante entre fuentes y normaliza el texto de igual forma en todas las particiones. Convierte el guion en minúsculas, conserva los apóstrofos internos de palabra y une las palabras con un espacio. Calcula SHA‑256 de ese texto en UTF‑8. Comprueba también duplicados de audio recodificado y procedencia de las voces. Fuera de las huellas idénticas, estas comprobaciones requieren datos de origen. Reserva el conjunto final a una sola evaluación con la configuración fijada. Para volver a ajustar a partir del resultado, prepara otro conjunto reservado.

## Evaluador local

El [evaluador por contraste](../../modules/pronunciation-lab/tests/benchmark_independent_acceptance.py) usa datos locales y devuelve solo recuentos, métricas y el resultado técnico de los umbrales. Conserva separado `/z/ → /s/` de cualquier otra dirección. Las omisiones pueden representarse con `target` igual a `∅`. Los resultados anteriores de vocales, dentales y otros contrastes permanecen como evidencia retrospectiva. **Ningún contraste ha superado el criterio definitivo.** Se conserva la corrección por escucha en el [laboratorio actual](../../modules/pronunciation-lab/README.md).

Usa un directorio privado por evaluación. `desarrollo.json` y `final.json` son listas de casos con `id`, `speaker`, `prompt_sha256`, `audio_sha256`, `expected`, `target` y `cohort` (`learner` o `british_control`). El registro de desarrollo incluye todos los casos usados para ajustar la configuración. Los hashes de guion se calculan sobre el texto normalizado. Las revisiones son objetos cuyos nombres de campo son los `id` de caso y cuyo valor contiene `reviewer` y `verdict`. Los dictámenes permitidos son `target_error`, `valid`, `other_error` y `ambiguous`. `predicciones.json` asigna a cada `id` uno de `target_alert`, `clear`, `other_alert` o `abstain`. Las adjudicaciones de un tercer revisor usan el mismo formato de revisión.

```powershell
& .\modules\pronunciation-lab\.venv\Scripts\python.exe -B -X utf8 `
  modules/pronunciation-lab/tests/benchmark_independent_acceptance.py `
  --development "$carpetaPrivada/desarrollo.json" --final "$carpetaPrivada/final.json" `
  --final-sha256 $huellaRegistradaAntesDeEvaluar `
  --review-a "$carpetaPrivada/revision-a.json" --review-b "$carpetaPrivada/revision-b.json" `
  --predictions "$carpetaPrivada/predicciones.json"
```

Usa `--adjudications` si existen dictámenes de un tercer revisor. La herramienta exige las dos fichas completas, IDs distintos, coincidencia con la huella del manifiesto y separación por hablante, guion y audio. La independencia de las escuchas se comprueba mediante el protocolo humano. La sensibilidad cuenta como fallos las abstenciones sobre errores confirmados. La precisión cuenta también los avisos equivocados o sin confirmar. La cobertura auditable usa todo el manifiesto, de modo que un caso sin dictamen concluyente o sin decisión del modelo reduce la cobertura. El resultado técnico se presenta a Dirección Académica.

## Checkpoints locales

- Paquete ciego en `%TEMP%/eoi-mdd-phase2/saa-adjudication-v1/para-revision/`. La clave separada, las grabaciones y las fichas son material de investigación local.
- Agregado acústico en `%TEMP%/eoi-mdd-phase2/saa-acoustics-frozen-gate.json`, SHA‑256 `9e4ed48ea6d196cd7aa8b3093c5ec72876dc7a3a15dcdebecb3b431faac9b5ec`. El script ignorado `modules/pronunciation-lab/.cache/saa_acoustics_audit.py` usa las predicciones guardadas y Parselmouth 0.4.7.
- Reserva británica en `%TEMP%/eoi-mdd-phase3/holdout-slr83-z-metadata.json`, SHA‑256 `1f7b2a99c5aa8d6c79a74d7c647713c2831f585acc37331904ddde831c0b3a89`. Reserva de guiones originales en `modules/pronunciation-lab/.cache/final-reservation-v1/learner-prompts.json`, SHA‑256 `51ee523a6a3adf5bd00b50d0d9bf078839143da821c1a9b6f802008a4a5c88c5`.
- La regresión pasó 12 pruebas operativas existentes y 6 pruebas nuevas del evaluador con datos sintéticos. La evaluación definitiva y las revisiones humanas siguen pendientes.
