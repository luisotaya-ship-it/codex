# Mejoras a las skills de residencia — 2026-10-02

Copia de las 16 skills médicas propias. Las 11 modificadas están empaquetadas en `dist/*.skill`
para instalarlas (abrir el archivo → **Save skill**, o subirlo en claude.ai → Settings → Skills).

## Problemas encontrados y corregidos

| Skill | Problema | Corrección |
|---|---|---|
| `medical-learning` | Citaba `references/plantillas.md` y `references/estudio-interactivo.md`, **que no existían** | Se crearon ambos archivos; descripción recortada a <1024 caracteres (estaba sobre el límite) y separada de `estudio-cronicas` |
| `medical-learning` | Dependía de `show_widget`, que solo existe en claude.ai | Alternativa para Claude Code/Cowork |
| `enrutador-de-skills` | No mencionaba 9 de las 16 skills propias; citaba skills inexistentes (`explain-usage`, `learn` para medicina) | Reescrito completo: aprender / exponer / evidencia / oficina / código / bio-research / otros |
| `enrutador-de-skills` | Sin Codex | Agregados `codex-review:plan`, `codex-review:code`, `codex-dispatch:codex-dispatch`, cuándo usar cada uno y cadenas típicas |
| `escalas-clinicas` | CHA₂DS₂-VASc como único estándar | Agregado CHA₂DS₂-VA (ESC 2024, sin sexo; ≥2 recomendada, 1 considerar); se mantiene CHA₂DS₂-VASc para ACC/AHA |
| `escalas-clinicas` | Downton: corte "≥4 alto riesgo" | Corregido a ≥3 (corte de los estudios de validación) |
| `escalas-clinicas` | qSOFA sin advertencia | SSC 2021: recomendación fuerte en contra de usarlo como tamizaje único |
| `escalas-clinicas` | CURB-65 solo en mmol/L | Equivalencia en BUN/urea mg/dL |
| `escalas-clinicas` | Faltaban escalas de Medicina Familiar y Colombia | Framingham calibrado ×0,75 (GPC dislipidemia MinSalud), APGAR familiar, Zarit |
| `auditor-presentaciones` | El script marcaba la cita de 8 pt de UNINAVARRA como ilegible y fuera de zona en **todas** las diapositivas | El script reconoce la franja de cita (mínimo 8 pt); probado |
| `presentaciones-cientificas` / `auditor` / `plantilla-uninavarra` | Densidad contradictoria (6 vs. 4 viñetas) | Unificado: 4 visibles con UNINAVARRA |
| `presentaciones-cientificas` | Se activaba ante cualquier PDF con nombre de enfermedad (chocaba con estudio/quiz); rutas `/mnt/...` | Desambiguación en la descripción + tabla de skills que encadena; rutas portables |
| `preguntas-interactivas` | Solo funcionaba con `ask_user_input_v0` (claude.ai) | Tabla por entorno (`AskUserQuestion` en Claude Code/Cowork); usa `escalas-clinicas` |
| `lectura-eficiente-pdf` | Delegaba en `pdf-reading`, no instalada | Rasterizado de una página con `pdftoppm` |
| `estudio-cronicas` | Descripción igual a la de `medical-learning` | Ahora = documento Word/PDF; usa `lectura-eficiente-pdf` y `escalas-clinicas` |
| `imagenes-*`, `auditor` | Rutas `/home/claude/...`; Canva sin alternativa | Rutas portables; alternativa si Canva no está conectado |

## Pendiente (requiere tu decisión o tus archivos)

- `plantilla-uninavarra`: el fondo `Plantilla_UNINAVARRA_fondo_2025.jpg` no está dentro de la skill;
  si lo subes, se puede empaquetar en `assets/` para que funcione en cualquier entorno.
- `preguntas-interactivas`: `interrogatorio.html` tampoco está en la skill; mismo caso.
- Evaluación con casos de prueba (skill-creator) de cada skill: no se ejecutó.
