---
name: "estudio-cronicas"
description: "Genera un DOCUMENTO de estudio (Word o PDF) con material de nivel residencia de Medicina Familiar sobre enfermedades crónicas (ficha monográfica + diagramas explicativos reales + casos clínicos razonados + preguntas de autoevaluación) con evidencia etiquetada, guías vigentes internacionales y colombianas, y entrega en Word o PDF. Usar cuando el usuario pida una ficha, monografía, resumen descargable o material para preparar examen sobre una enfermedad crónica (HTA, DM2, ERC, EPOC, asma, IC, hipotiroidismo, osteoporosis, depresión, etc.), aunque no diga \"Word\". Si solo quiere entender o repasar en la conversación, sin archivo, usa medical-learning; si quiere practicar con preguntas, preguntas-interactivas."
---

# Estudio de Enfermedades Crónicas — Residencia de Medicina Familiar

Produce material de estudio de nivel especialista en formación sobre enfermedades crónicas, con evidencia trazable, **diagramas explicativos reales** y entrega en documento formateado.

## Cuándo activarse

El usuario pide estudiar, repasar, resumir, "hacer ficha de", o preparar examen sobre una enfermedad crónica. Alcance: **cualquier enfermedad crónica**, con énfasis operativo en tres bloques:

- **Cardiometabólico y renal**: HTA, DM2, prediabetes, dislipidemia, obesidad, síndrome metabólico, ERC, IC (FEr/FElp), fibrilación auricular, enfermedad coronaria crónica, enfermedad arterial periférica.
- **Respiratorio y otras crónicas de consulta**: EPOC, asma, SAHOS, hipotiroidismo/hipertiroidismo, osteoporosis, osteoartrosis, AR, gota, ERGE, hígado graso metabólico (MASLD), VIH, hepatitis B/C, epilepsia, migraña crónica, dolor crónico, anemia crónica.
- **Salud mental crónica**: depresión, trastorno de ansiedad generalizada, insomnio crónico, trastorno bipolar en seguimiento, demencias, trastorno por consumo de alcohol/tabaco.

Si el usuario nombra una enfermedad fuera de estos bloques pero crónica, cubrirla igual con la misma estructura.

## Regla de oro: nunca inventar

Este skill se usa para estudiar medicina. Un dato inventado es un daño real.

1. **Antes de escribir, buscar.** Ejecutar `WebSearch` para localizar la versión vigente de las guías relevantes (año actual; si no existe, el año previo, y así sucesivamente). No escribir cifras, dosis, umbrales, metas terapéuticas, sensibilidades, especificidades, NNT ni años de publicación de memoria.
2. **Revisar primero la carpeta del usuario.** Antes de buscar en la web, explorar la carpeta de trabajo (si existe en este entorno) (`Guias_Clinicas_y_Articulos`, `Clases_y_Presentaciones`, `Resumenes_y_Documentos`) buscando guías, revisiones o artículos del tema. Suelen ser fuentes excelentes y ya seleccionadas por el usuario. Extraer su texto con `lectura-eficiente-pdf` (convertir una vez y leer solo la sección necesaria) y citarlas explícitamente.
3. **Etiquetar cada afirmación no trivial**: `[Evidencia]`, `[Inferencia]`, `[Especulación]`, `[No verificado]`.
4. **Cero referencias fabricadas.** Cada referencia debe corresponder a un documento localizado en la búsqueda. Si una guía se menciona pero no se pudo confirmar versión/año, escribir el año como `[No verificado]` en vez de suponerlo.
5. Si falta información del usuario para responder correctamente (p. ej. población, comorbilidad, contexto de atención), **preguntar antes**, no rellenar con supuestos.
6. Si la evidencia es débil o hay controversia entre guías, decirlo explícitamente en el apartado correspondiente.
7. Frases permitidas ante desconocimiento: "No puedo verificar esto." / "No tengo acceso a esa información." / "La evidencia disponible no permite responder esa pregunta con certeza."
8. Si en el mismo hilo se detecta un error previo, escribir literalmente: "Corrección: previamente presenté una afirmación no verificada. Debió identificarse como [Inferencia] o [No verificado]."
9. **Corregir premisas erróneas del usuario.** Si la pregunta parte de una afirmación fisiopatológica o farmacológica incorrecta, corregirla de forma explícita y respetuosa, con la etiqueta `[Corrección]` y un recuadro destacado, en vez de responder dentro del marco equivocado. Verificar la corrección con una fuente antes de emitirla.

## Diagramas: obligatorios, no opcionales

**Toda entrega de este skill incluye diagramas generados como imágenes reales**, mediante la skill `diagramas-clinicos`. Nunca describir en texto cómo se vería un gráfico: generar el archivo.

Invocar `diagramas-clinicos` **después de la investigación y antes de construir el documento**, para que las imágenes ya existan cuando se arme el `.docx` o el `.pdf`.

### Set mínimo por enfermedad

Generar al menos cuatro diagramas, y más si el contenido lo pide:

| Diagrama | Motor | Contenido |
|---|---|---|
| **Vía fisiopatológica** | Graphviz con clusters | Mecanismo de la enfermedad conectado con los blancos farmacológicos. Es el diagrama que más rinde para comprender, no solo memorizar. |
| **Algoritmo diagnóstico** | Graphviz | Del tamizaje o la sospecha hasta la confirmación, con los umbrales exactos de la guía en los nodos de decisión. |
| **Algoritmo terapéutico** | Graphviz | A quién tratar, con qué, escalamiento, y criterios de remisión u hospitalización. |
| **Gráfico de datos** | matplotlib | Forest plot de HR/RR/OR con IC 95 %, o comparación de tasas, NNT/NNH o prevalencias, con las cifras exactas del estudio citado. |

Diagramas adicionales recomendados según el tema: línea de tiempo de la evolución de las guías cuando hubo un cambio mayor reciente; esquema del sitio de acción de los fármacos (p. ej. segmentos de la nefrona, receptores); tabla comparativa visual entre guías cuando difieren.

### Reglas de los diagramas

- **Nunca graficar un número que no esté verificado.** Si falta un dato para el gráfico, decirlo y omitir esa serie, no estimarla.
- Cada imagen lleva **su fuente visible** dentro de la propia figura, con la etiqueta de evidencia que corresponda.
- Resolución 300 dpi para documentos Word o PDF; 150–200 dpi para presentaciones.
- Insertar cada imagen en la sección del documento donde corresponde, con un pie de figura numerado ("Figura 1. ...") que incluya la fuente.

## Contexto de práctica: Colombia + internacional

Para cada tema, contrastar dos capas:

- **Capa internacional** (jerarquía por especialidad): ADA, AHA/ACC, ESC, KDIGO, GOLD, GINA, IDSA, ATS, ACP, NICE, USPSTF, AAFP, CDC, OMS, EULAR/ACR, ACOG, AAP, NCCN/ASCO, Surviving Sepsis Campaign.
- **Capa colombiana**: Guías de Práctica Clínica del Ministerio de Salud y Protección Social / IETS, Resoluciones vigentes relacionadas con la Ruta Integral de Atención en Salud (RIAS) de riesgo cardiovascular-metabólico cuando apliquen, y disponibilidad real del medicamento en el país. Buscar siempre en `minsalud.gov.co` y en el listado de GPC del IETS antes de afirmar que existe o no una guía colombiana.

Cuando la guía colombiana y la internacional difieran, **explicar la diferencia y por qué** (año de la guía, disponibilidad de fármacos, costo-efectividad local, población de referencia). No asumir que un fármaco recomendado internacionalmente está disponible o financiado en Colombia; si no se puede verificar, marcarlo `[No verificado]`.

## Flujo de trabajo

1. **Aclarar** si el tema es ambiguo (p. ej. "diabetes" → ¿DM2 en adulto, DM1, diabetes gestacional?). Preguntar también si el usuario quiere profundidad completa o un repaso rápido enfocado en un subtema.
2. **Revisar la carpeta del usuario** en busca de guías y artículos del tema.
3. **Investigar** con `WebSearch` / fetch: guía internacional vigente + guía colombiana + al menos una revisión sistemática o metaanálisis reciente si el tema tiene controversia.
4. **Generar los diagramas** con la skill `diagramas-clinicos` (set mínimo arriba).
5. **Redactar** las tres partes (ficha, casos, preguntas).
6. **Construir el documento**: leer el SKILL.md de `docx` (o de `pdf` si el usuario pide PDF) y generar el archivo con las imágenes insertadas.
7. **Verificar** antes de entregar: checklist final + revisar el render de las páginas.
8. **Entregar** el archivo con la herramienta de envío de archivos disponible (`present_files` o `SendUserFile`) y un resumen de 2–3 líneas.

## Parte 1 — Ficha monográfica

Incluir todas las secciones que apliquen, en este orden. Omitir una sección solo si es irrelevante para la enfermedad, y decir por qué se omitió.

1. Definición y clasificación
2. Fisiopatología — **con su diagrama** — explicada de forma que conecte con el diagnóstico y el tratamiento, no como dato aislado
3. Epidemiología (global + Colombia si hay dato verificable; si no, decirlo)
4. Factores de riesgo
5. Manifestaciones clínicas
6. Criterios diagnósticos y algoritmo — **con su diagrama**
7. Diagnósticos diferenciales (tabla comparativa)
8. Escalas clínicas y de estratificación de riesgo, con su interpretación y limitaciones (componentes y cortes desde `escalas-clinicas`)
9. Interpretación de laboratorios — por qué se pide cada uno y qué hacer con cada hallazgo
10. Interpretación de imágenes
11. Tratamiento no farmacológico
12. Tratamiento farmacológico — **con su diagrama de escalamiento** — fármaco, dosis inicial, titulación, dosis máxima, y **dónde actúa cada uno**
13. Ajuste renal y hepático
14. Poblaciones especiales: embarazo, lactancia, adulto mayor, pediatría si aplica
15. Interacciones y efectos adversos relevantes en primer nivel
16. Seguimiento: qué medir, cada cuánto, meta terapéutica
17. Criterios de remisión a especialista
18. Criterios de hospitalización y de UCI
19. Prevención primaria y secundaria — **con el gráfico de magnitud de beneficio**
20. Pronóstico
21. Errores frecuentes en la práctica
22. Perlas clínicas

### Formato de tratamiento farmacológico

Usar tabla con columnas: Fármaco | Clase | Sitio de acción | Dosis inicio → máxima | Ajuste TFG | Ajuste hepático | Embarazo/lactancia | Adulto mayor | RAM clave | Monitorización | Lugar en la guía (línea y fuerza de recomendación).

Cuando existan diferencias **dentro** de una misma clase que cambien la elección (p. ej. losartán y ácido úrico, clortalidona frente a hidroclorotiazida), desarrollarlas explícitamente en vez de tratar la clase como homogénea.

## Parte 2 — Casos clínicos

Dos a tres casos que cubran presentaciones distintas (típica, atípica, con comorbilidad o en adulto mayor polimedicado). Cada caso desarrolla razonamiento **paso a paso**:

- Lista de problemas activos
- Hipótesis diagnósticas ordenadas por probabilidad y por gravedad ("no me lo puedo perder")
- Diagnóstico diferencial y qué dato lo sube o lo baja
- Interpretación de paraclínicos
- Plan diagnóstico — justificar cada estudio pedido y explicar cuál **no** se pide y por qué
- Plan terapéutico con dosis concretas
- Pronóstico y plan de seguimiento

Explicar el porqué de cada decisión. El objetivo es enseñar razonamiento, no dar una respuesta cerrada.

## Parte 3 — Autoevaluación

8–12 preguntas de opción múltiple estilo examen de especialidad (viñeta clínica, 4–5 opciones, una mejor respuesta). Al final, clave de respuestas con:

- por qué la correcta es correcta
- por qué **cada** distractor es incorrecto
- la referencia que sustenta la respuesta

Incluir 2–3 preguntas de interpretación de evidencia (RAR, RRR, NNT, NNH, hazard ratio, odds ratio, IC 95 %, valor p) usando cifras tomadas de un estudio real localizado en la búsqueda, no inventadas. Al interpretarlas, distinguir siempre **significancia estadística** de **relevancia clínica**.

## Referencias

Al final de la ficha, sección **Referencias** con, por cada recomendación importante:

Organización — Título de la guía — Año — Recomendación relevante — Nivel de evidencia — Fuerza de recomendación (GRADE cuando exista) — URL.

Si la fuente no aporta nivel/fuerza, escribir "no reportado", no inventarlo.

**Declarar conflictos de interés** de las fuentes cuando existan (p. ej. una revisión comparativa entre dos fármacos financiada por el fabricante de uno de ellos), y advertir al lector sobre cómo eso afecta la interpretación.

Cerrar con **Brechas de información declaradas**: lo que se buscó y no se pudo resolver, en lugar de rellenarse.

## Cierre obligatorio

Toda entrega termina con **"Puntos clave para el residente"**: 6–15 viñetas con lo esencial para la consulta del lunes siguiente. Prácticas, accionables, sin relleno.

## Documento de salida

Por defecto **.docx**. Si el usuario pide PDF, generar PDF. Antes de construir, leer el SKILL.md correspondiente (`docx` o `pdf`).

Convenciones del documento:

- Portada: nombre de la enfermedad, "Material de estudio — Residencia de Medicina Familiar", fecha de elaboración y una nota: "Fecha de última verificación de guías: [fecha]. Verificar vigencia antes de aplicar."
- Tabla de contenido automática, con nota de que se actualiza con F9 en Word
- Encabezados jerárquicos (H1 para las tres partes, H2 para secciones)
- **Figuras numeradas con pie y fuente**
- Tablas para: diferenciales, fármacos, comparación entre guías, escalas
- Etiquetas `[Evidencia]` / `[Inferencia]` / `[Especulación]` / `[No verificado]` / `[Corrección]` visibles y con color en el cuerpo del texto
- Recuadros destacados para perlas clínicas, advertencias y correcciones
- Numeración de páginas
- Cada lista numerada reinicia en 1 (usar instancias separadas de numeración)
- Nombre de archivo: `estudio-<enfermedad>-<AAAA-MM-DD>.docx`

## Checklist de verificación (ejecutar antes de entregar)

- [ ] Toda cifra, dosis, umbral y meta proviene de una fuente localizada en esta sesión
- [ ] Cada referencia tiene URL o identificador real y verificado; ninguna fue reconstruida de memoria
- [ ] Se revisó la carpeta del usuario en busca de fuentes locales del tema
- [ ] Se buscó explícitamente guía colombiana (MinSalud/IETS) y se reporta el resultado, exista o no
- [ ] **Se generaron los diagramas del set mínimo y están insertados en el documento**
- [ ] **Ningún número graficado fue estimado o inventado**
- [ ] Las diferencias entre guías están explicadas, no promediadas
- [ ] Ajustes renal/hepático, embarazo y adulto mayor están presentes para cada fármaco de primera línea
- [ ] Los distractores de las preguntas tienen justificación individual
- [ ] Las cifras de bioestadística vienen de un estudio real
- [ ] Se declararon los conflictos de interés de las fuentes relevantes
- [ ] Existe la sección "Puntos clave para el residente" y la de brechas declaradas
- [ ] Se revisó el render de al menos 3 páginas del documento final
- [ ] Nada quedó sin etiqueta cuando debía llevarla

## Estilo

Preciso, técnico, sin relleno. Tablas comparativas cuando ayuden. Mnemotecnias solo si facilitan el aprendizaje sin sustituir la comprensión. No suavizar la incertidumbre: si la evidencia es débil, decirlo con la misma claridad con que se dice lo demás.

