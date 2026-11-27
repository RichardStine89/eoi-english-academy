# Cierre experimental de Pronunciation Lab v1.2

**Resultado operativo.** Pronunciation Lab queda como apoyo local para grabar, importar, escuchar una toma o un fragmento, comparar intentos y generar informes acústicos descriptivos. **Ningún contraste está habilitado para avisos, correcciones o notas automáticas.** Todos los contrastes de la guía pueden practicarse mediante modelos británicos, pares mínimos y revisión humana. Se detienen los experimentos fonéticos de esta versión. La aceptación general corresponde a Dirección Académica. [Uso en clase](pronunciacion.md)

| Nivel | Sensibilidad efectiva | Precisión | Cobertura |
|---|---:|---:|---:|
| Mínimo para avisos orientativos | ≥60 % | ≥90 % | ≥80 % |
| Objetivo avanzado | ≥80 % | ≥95 % | ≥90 % |

Cada nivel requiere evidencia humana independiente por contraste, con voces y guiones separados, 20 errores y 20 controles legítimos en al menos cuatro voces y revisión de variantes británicas. El objetivo avanzado por sí solo no autoriza calificaciones. El ensayo NJS es retrospectivo y usa una voz. Las reservas definitivas conservan sus huellas. [Protocolo de validación](validacion-fonetica-v1.2.md)

## Comparación final en las mismas muestras humanas

Se reutilizaron las emisiones IF‑MDD y las ventanas CTC espectrales y CUPE. Se midieron los rasgos Praat sobre esas ventanas sin volver a ejecutar los modelos. Se probaron un especialista por contraste, una votación con dos componentes y una cascada de confirmación del aviso IF‑MDD con evidencia acústica. ZIPA se comparó como referencia agregada. Sus artefactos no contienen observaciones por posición que permitan votación pareada. Los informes de Zira y Kokoro permanecen archivados. El ajuste se hizo con EBVS y ERMS. MBMPS eligió una regla por familia con prioridad a los niveles y luego a F1 efectivo. Se selló la selección antes de aplicar las reglas a NJS. Las abstenciones en positivos cuentan como falsos negativos efectivos. Los controles corresponden a realizaciones canónicas anotadas de cada dirección. [Banco anterior](alineacion-fonetica-v1.2.md) · [Ensayo sintético](aumento-sintetico-fonetico-v1.2.md)

| Contraste y método | VP | FP | FN efectivos | Sensibilidad | Precisión | Cobertura |
|---|---:|---:|---:|---:|---:|---:|
| /z/ → /s/ · IF‑MDD histórico · 9 errores y 5 controles | 7 | 1 | 2 | 77,8 % | 87,5 % | 100 % |
| Especialista, voto y cascada · mismo resultado cada uno | 7 | 1 | 2 | 77,8 % | 87,5 % | 100 % |
| /ð/ → /d/ · híbrido refinado histórico · 5 errores y 9 controles | 3 | 1 | 2 | 60,0 % | 75,0 % | 100 % |
| Especialista acústico CUPE | 3 | 6 | 2 | 60,0 % | 33,3 % | 100 % |
| Voto neuronal y acústico CUPE | 2 | 3 | 3 | 40,0 % | 40,0 % | 100 % |
| Cascada IF‑MDD y acústica CUPE | 3 | 3 | 2 | 60,0 % | 50,0 % | 92,9 % |
| /ɪ/ → /iː/ · acústico histórico · 1 error y 24 controles | 1 | 3 | 0 | 100 % | 25,0 % | 92,0 % |
| Especialista neuronal | 0 | 2 | 1 | 0 % | 0 % | 100 % |
| Voto neuronal y acústico CTC | 0 | 1 | 1 | 0 % | 0 % | 92,0 % |
| Cascada IF‑MDD y acústica CUPE | 0 | 0 | 1 | 0 % | Sin avisos | 96,0 % |

ZIPA obtuvo 0 VP y 0 FP, con 9, 5 y 1 FN efectivos y coberturas de 100 %, 50 % y 76 %, respectivamente. El haz de IF‑MDD en dental obtuvo 3 VP, 4 FP y 2 FN efectivos, con cobertura completa. La cascada redujo un aviso falso sobre ese haz, con una abstención adicional y peor precisión que el mejor híbrido histórico a igual número de aciertos. Para la vocal, el 100 % histórico de sensibilidad representa un único acierto.

En calibración, los tres enfoques de `/z/ → /s/` alcanzaron el objetivo avanzado y convergieron en el mismo resultado agregado en NJS, que quedó por debajo del 90 % de precisión. El voto dental cumplió el mínimo orientativo en calibración y cayó al 40 % de precisión en NJS. El especialista vocálico cumplió el objetivo avanzado en calibración y perdió el único positivo de NJS. Ninguna regla cumplió siquiera el mínimo orientativo en NJS. Los demás contrastes siguen deshabilitados por falta de evaluación humana independiente suficiente.

La evaluación futura debe reconocer el ensordecimiento legítimo de `/z/`, las realizaciones dentales de `/ð/` y las diferencias regionales de calidad y duración vocálica. Los conjuntos con adjudicación humana y controles británicos siguen pendientes. Las mediciones de F0, intensidad y duración ayudan a comparar condiciones y tomas. El juicio de pronunciación se basa en el audio y el contexto. [Variantes y adjudicación](validacion-fonetica-v1.2.md)

## Reanudación y alcance verificado

El [benchmark](../../modules/pronunciation-lab/tests/benchmark_final_hybrid.py) dispone de fases `prepare`, `select` y `evaluate`. Las fases leen las cachés locales documentadas y no ejecutan de nuevo los modelos. Usa el Python de laboratorio y un `--workdir` privado y nuevo fuera del repositorio. Los resultados están en `%TEMP%/eoi-mdd-final-hybrid/`. SHA‑256 de `frozen-selection.json` `40e056fcb9b2ace2d1e657d2244cdde2e65e968c431ea128a451335a3490f441`. SHA‑256 de `comparison.json` `2ba2464d3c93fb121505d999a23565c12004ad9f31cb907e7661c6d69744ac82`.

La vista **Ver tramos del guion…** ofrece reproducción por fragmentos. Los informes nuevos, el portapapeles y las exportaciones de intentos anteriores mantienen medidas y tramos sin mostrar sustituciones o confianzas del motor. Los archivos históricos se conservaron. Pasaron 26 pruebas automatizadas. Se verificaron el arranque mediante `Abrir.cmd`, el diálogo de tramos y el flujo de importación, comparación y exportación local. La comprobación con el micrófono y los altavoces del estudiante sigue pendiente como parte de la aceptación en clase.
