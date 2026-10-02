# Esquema de `contenido.json` para `build_html_dinamico.py`

Este JSON es la única entrada del generador HTML. Constrúyelo a partir del mismo
contenido diapositiva-por-diapositiva que ya redactaste (con `presentaciones-cientificas`
o el contenido que el usuario te haya dado) — no inventes datos nuevos para
"rellenar" el HTML; si una diapositiva no tiene gráfico, no le pongas un campo
`grafico` con cifras inventadas.

```json
{
  "titulo": "Hipertensión arterial en el adulto mayor",
  "slides": [
    {
      "tipo": "portada",
      "titulo": "Hipertensión arterial en el adulto mayor",
      "subtitulo": "Gran sesión — Medicina Familiar",
      "icono_3d": "corazon"
    },
    {
      "tipo": "contenido",
      "titulo": "¿Por qué el umbral cambia con la edad?",
      "bullets": [
        "Rigidez arterial aumenta con la edad (ACC/AHA 2024)",
        "Riesgo de hipotensión ortostática en >80 años",
        "Meta menos estricta si fragilidad (ESH 2023)"
      ],
      "guion": "Aquí explico que la meta tensional no es igual a los 40 que a los 85...",
      "nota_pie": "ACC/AHA 2024",
      "take_home": "Individualizar la meta según fragilidad"
    },
    {
      "tipo": "grafico",
      "titulo": "Reducción de eventos CV según meta de PAS",
      "bullets": ["SPRINT: PAS <120 vs <140 mmHg", "NNT a 5 años: 61"],
      "grafico": {
        "tipo": "bar",
        "labels": ["PAS <140", "PAS <120"],
        "series": [{"nombre": "Eventos CV mayores (%)", "datos": [3.4, 2.5]}]
      },
      "nota_pie": "SPRINT, NEJM 2015"
    },
    {
      "tipo": "diagrama",
      "titulo": "Algoritmo de inicio de tratamiento",
      "diagrama": {"pasos": ["PAS ≥140/90", "Confirmar con MAPA/AMPA", "Riesgo CV alto?", "Iniciar IECA/ARA-II + calcioantagonista"]}
    },
    {
      "tipo": "impacto",
      "titulo": "1 de cada 3 adultos mayores hipertensos no sabe que lo es"
    },
    {
      "tipo": "cierre",
      "titulo": "Perlas clínicas",
      "bullets": ["No bajar la PAS de forma brusca en frágiles", "Reevaluar ortostatismo en cada control"],
      "icono_3d": "corazon"
    }
  ]
}
```

## Campos por tipo de diapositiva

| tipo | Campos relevantes | Uso |
|---|---|---|
| `portada` | `titulo`, `subtitulo`, `icono_3d` | Primera diapositiva |
| `contenido` | `titulo`, `bullets`, `guion`, `nota_pie`, `take_home` | Diapositiva estándar (una pregunta, 70/30) |
| `grafico` | `titulo`, `grafico.{tipo,labels,series}`, `bullets` | Datos que ameritan gráfico animado (Chart.js dibuja al entrar) |
| `diagrama` | `titulo`, `diagrama.pasos` | Algoritmo/flujo — cada paso aparece en secuencia con flecha |
| `impacto` | `titulo` | Fondo negro forzado, sin encabezado — máximo 2-3 por deck (igual que en `presentaciones-cientificas`) |
| `cierre` | `titulo`, `bullets`, `icono_3d` | Última diapositiva / perlas clínicas |
| `ficha` | ver tabla siguiente | Infografía de guía de un solo vistazo (preset `ficha_clinica`) |
| `indice` | `titulo`, `secciones[].{titulo,resumen,bullets}` | Menú de navegación tipo acordeón (índice/agenda de un deck largo) |

### Revelado progresivo (`revelado`) e imágenes (`imagenes`) — tipo `contenido`

Campos nuevos para que el contenido aparezca al ritmo de la charla en vez de
todo de golpe, y para que una diapositiva con varias fotos no se sienta
cargada desde el primer segundo:

```json
{
  "tipo": "contenido",
  "titulo": "Hallazgos radiológicos según patrón",
  "revelado": "progresivo",
  "bullets": [
    "Consolidación lobar: típica de neumocócica",
    "Infiltrado intersticial: sugiere atípica/viral",
    "Derrame pleural: buscar empiema si es masivo"
  ],
  "imagenes": [
    {"src": "rx1.jpg", "alt": "Consolidación lobar", "pie": "Consolidación lobar (RxTx)", "bullet_index": 0},
    {"src": "rx2.jpg", "alt": "Infiltrado intersticial", "pie": "Patrón intersticial", "bullet_index": 1},
    {"src": "rx3.jpg", "alt": "Derrame pleural", "pie": "Derrame pleural derecho", "bullet_index": 2}
  ],
  "guion": "Explico cada patrón mientras aparece su imagen correspondiente."
}
```

`revelado` acepta tres valores (por diapositiva, no es una opción global del
deck):

| Valor | Qué pasa | Cuándo usarlo |
|---|---|---|
| `"cascada"` (default) | Todo entra solo, escalonado, apenas se activa la diapositiva — sin necesidad de que el presentador haga nada. | Diapositivas con poco contenido (≤4 viñetas, ≤1 imagen) donde no vale la pena pedir clics. |
| `"progresivo"` | Cada viñeta/imagen es un fragmento real de reveal.js: el presentador avanza con la flecha y el elemento se suma a los anteriores (se acumulan). | Cuando se quiere hablar de cada punto/imagen antes de mostrar el siguiente, sin ocultar lo ya dicho. |
| `"reemplazo"` | Igual que "progresivo" pero cada elemento nuevo hace que el anterior se atenúe (viñetas) o desaparezca del todo (imágenes, que se apilan en el mismo lugar). | Comparar 3-4 fotos o puntos uno a la vez sin que se amontonen en pantalla — p. ej. leve/moderado/severo de un mismo hallazgo. |

`imagenes[]`: cada imagen acepta `src` (ruta o URL), `alt`, `pie` (caption
opcional) y `bullet_index` (opcional) — si se especifica, esa imagen aparece
con el MISMO clic que la viñeta de ese índice (útil para sincronizar "hablo
de esto → aparece la foto de esto"); si se omite, las imágenes se numeran en
el orden de la lista, independientes de las viñetas. Con más de 1 imagen y
`revelado` no especificado, el generador fuerza automáticamente
`"progresivo"` solo para las imágenes (mostrar 2+ fotos de golpe es
exactamente lo que se quiere evitar), aunque el texto se quede en cascada.

`build_html_dinamico.py` imprime un aviso por consola (`advertencias_densidad`)
si una diapositiva tiene más de 4 viñetas o más de 1 imagen en modo cascada,
o si la densidad total (viñetas + imágenes×2) supera 8 incluso con revelado
progresivo — revisar esos avisos antes de entregar, no ignorarlos.

### Campos de `tipo: "ficha"`

```json
{
  "tipo": "ficha",
  "eyebrow": "GUÍA AHA/ACC · FICHA CLÍNICA",
  "badge": "AHA/ACC 2025",
  "badge_nota": "Reemplaza la guía ACC/AHA 2017",
  "titulo": "Presión arterial en adultos",
  "subtitulo": "Clasificación y manejo — actualización 2025",
  "nota_metodo": "Clasificación basada en el promedio de ≥2 mediciones...",
  "escala": {
    "min": 90, "max": 180,
    "segmentos": [
      {"color": "#1a9c6b", "hasta": 120},
      {"color": "#d9a72c", "hasta": 130},
      {"color": "#e8792e", "hasta": 140},
      {"color": "#c0392b", "hasta": 180}
    ],
    "marcas": [90, 120, 130, 140, "≥180"]
  },
  "tabla": {
    "columnas": ["Categoría", "Sistólica (PAS)", "Diastólica (PAD)"],
    "filas": [
      {"color": "#1a9c6b", "valores": ["Normal", "<120", "<80"]},
      {"color": "#c0392b", "valores": ["Hipertensión etapa 2", "≥140", "≥90"]}
    ],
    "nota": "La categoría se define por el valor más alto de PAS o PAD."
  },
  "tarjetas": [
    {"color": "primario", "titulo": "META DE TRATAMIENTO", "valor": "<130/80 mmHg", "descripcion": "..."},
    {"color": "alerta", "titulo": "CRISIS HIPERTENSIVA", "valor": ">180/120 mmHg", "descripcion": "..."}
  ],
  "pildoras": {"titulo": "MODIFICACIONES DEL ESTILO DE VIDA", "items": ["Dieta DASH", "Reducir sodio"]}
}
```

`escala.segmentos[].hasta` son valores acumulativos (no anchos) — el primer
segmento va desde `min` hasta su `hasta`, el siguiente desde ahí hasta el
suyo, etc. `tarjetas[].color` acepta `primario`, `alerta`, `acento` (mapean a
las variables de color del preset) o un código hex directo. Todos los datos
de `escala`/`tabla`/`tarjetas` deben salir de la guía real que se está
resumiendo — este tipo de diapositiva es el que más tienta a "rellenar" un
umbral aproximado; no lo hagas, es exactamente el tipo de cifra que el filtro
de evidencia del usuario prohíbe inventar.

### Campos de `tipo: "indice"`

```json
{
  "tipo": "indice",
  "titulo": "Índice de la gran sesión",
  "secciones": [
    {"titulo": "1. Definición y epidemiología", "resumen": "Qué es y cuánto pesa en la población.", "bullets": ["Prevalencia", "Factores de riesgo"]},
    {"titulo": "2. Diagnóstico", "resumen": "Cómo se confirma el caso."},
    {"titulo": "3. Tratamiento", "resumen": "Metas e inicio de farmacoterapia."}
  ]
}
```

Se reutiliza el mismo texto del índice/agenda que ya redactó
`presentaciones-cientificas` (ver su `SKILL.md § Índice/agenda navegable`) —
no resumir de nuevo ni inventar el contenido de cada sección. Se renderiza
como acordeón (`<details>/<summary>` nativos): cada `titulo` siempre visible,
el `resumen`/`bullets` se despliegan al hacer clic.

### Campo `diagrama.zoom_progresivo`

En una diapositiva `tipo: "diagrama"`, agregar `"zoom_progresivo": true` hace
que cada paso, además de entrar en cascada al activarse la diapositiva, se
pueda "recorrer" con las flechas del teclado: el paso actual se agranda y
resalta, los ya vistos se atenúan — una aproximación al efecto Zoom de
sección de PowerPoint hecha con fragmentos de reveal.js (ver
`references/tecnica-morph-real.md` para el porqué no se automatiza el Zoom
nativo de PowerPoint). Todos los pasos siguen visibles desde el principio —
esto solo cambia cómo se ve el recorrido, no oculta contenido.

`grafico.tipo` acepta lo mismo que Chart.js: `bar`, `line`, `doughnut`, `pie`, `radar`.
`icono_3d` acepta: `corazon`, `rinon`, `pulmon`, `cerebro`, `molecula`, `generico` — úsalo
como máximo en 2 diapositivas del deck (portada y cierre), nunca en todas: es un acento,
no un patrón de fondo.

`guion` alimenta las notas del orador de reveal.js (se ven con la tecla `S` al presentar,
el público no las ve) — si ya escribiste el guion oral para el .pptx, reutilízalo aquí
tal cual, no lo resumas ni lo reescribas.
