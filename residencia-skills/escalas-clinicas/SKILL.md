---
name: "escalas-clinicas"
description: "Biblioteca verificada de escalas clínicas (componentes, puntaje, puntos de corte, versión vigente y fuente) para Medicina Familiar: riesgo cardiovascular (incluido Framingham calibrado para Colombia y CHA₂DS₂-VA), geriatría, cognición, salud mental, sepsis, renal/hepático, TEV, obstetricia, pediatría y funcionalidad familiar (APGAR familiar, Zarit). Úsala SIEMPRE que el usuario pregunte por una escala o puntaje (\"¿cómo se calcula el CURB-65?\", \"qué corte tiene el PHQ-9\", \"cuánto da el Wells\"), cuando un caso clínico requiera estratificar riesgo, y automáticamente al planear una presentación, ficha o banco de preguntas sobre una patología que tenga una escala diagnóstica, de severidad, de riesgo o pronóstica reconocida — sin que el usuario tenga que pedirla. No dibuja: entrega el contenido para que infografias-automaticas o diagramas-clinicos lo grafiquen."
---

# Escalas clínicas validadas — biblioteca de referencia

## Cuándo se activa

Esta skill no construye diapositivas por sí sola: entrega el contenido clínico verificado de la escala aplicable para que `infografias-automaticas` (patrón `escala`) o `diagramas-clinicos` la dibujen, y para que `presentaciones-cientificas`/`plantilla-uninavarra` la incluyan como una diapositiva más dentro del flujo normal (nunca como añadido aparte que haya que pedir).

Actívala automáticamente, sin preguntar, en tres momentos:
1. Al planear el contenido de una presentación, ficha (`estudio-cronicas`, `medical-learning`) o banco de preguntas (`preguntas-interactivas`) sobre una patología: revisa la tabla de abajo y, si existe una escala aplicable a esa patología (diagnóstica, de severidad, de riesgo o pronóstica), inclúyela.
2. Cuando el usuario pida explícitamente "la escala de X" o pregunte por una escala clínica en el chat.
3. Cuando un caso clínico necesite estratificar riesgo para decidir conducta (hospitalizar, anticoagular, remitir): calcula la escala con los datos del caso, muestra el puntaje ítem por ítem y explica qué cambia en la conducta.

## Cómo usar la biblioteca (orden de confianza)

1. **Escalas estables** (Glasgow, APGAR, PHQ-9, CURB-65, Barthel, Wells…): úsalas tal cual, citando la fuente original.
2. **Escalas con versiones que cambian** (riesgo CV, anticoagulación en FA, sepsis, MELD): antes de llevarlas a un entregable, verifica con búsqueda web que la versión registrada aquí siga siendo la vigente. Si cambió, usa la nueva y avisa al usuario para actualizar esta skill.
3. **Puntos de corte con variaciones por validación local** (MMSE por escolaridad, TUG, Zarit, APGAR familiar): menciona explícitamente que el corte depende de la validación usada.
4. **Escala que no está aquí**: búscala en la fuente original antes de usarla; nunca reconstruyas ítems o puntajes de memoria. Si no la puedes verificar: `[No verificado]`.

Última revisión de esta biblioteca: 2026-10-02.

Si la patología no tiene ninguna escala reconocida en la tabla, no inventes una ni fuerces su inclusión.

## Cómo se dibuja (infografía)

Usa el mismo lenguaje visual ya validado con el usuario (ejemplo: Escala de Downton):
- Una tarjeta por componente/dominio de la escala, con icono, encabezado de color y los ítems con su puntaje a la derecha en un chip.
- Banda inferior de interpretación segmentada por color (ej. verde=bajo, ámbar=moderado, rojo=alto), con el rango de puntaje y la categoría de riesgo.
- Título descriptivo (no narrativo), franja/línea de acento en rojo de marca `#DB0C20` si se usa plantilla UNINAVARRA.
- Fuente de la escala citada al pie, igual que cualquier otra diapositiva.
- Cuando la escala es una regresión compleja sin suma simple de puntos (PREVENT, MELD 3.0), no dibujes "puntos" por variable: muestra las variables de entrada en tarjetas y el resultado como rango de riesgo/prioridad, aclarando que el cálculo exacto requiere la calculadora oficial.

## Nota de verificación

Los puntos de corte de las escalas muy establecidas (Glasgow, APGAR, PHQ-9, CURB-65, Barthel, etc.) son estables y de uso mundial: se documentan aquí con su fuente original. Para las que cambian de versión con el tiempo (riesgo cardiovascular, MELD), se documenta la versión vigente y se marca cuando el cálculo exacto exige la calculadora oficial en vez de una suma manual. Si el usuario pide un coeficiente exacto que no está aquí, no lo inventes: dilo como `[No verificado]` y ofrece buscarlo.

---

## Biblioteca de escalas por categoría

### 1. Riesgo cardiovascular

| Escala | Qué evalúa | Componentes / puntaje | Interpretación | Fuente |
|---|---|---|---|---|
| CHA₂DS₂-VA (ESC 2024) | Riesgo de ictus en FA (sin estenosis mitral moderada-grave ni válvula mecánica) | ICC/FEVI≤40%=1, HTA=1, edad≥75=2, DM=1, ACV/AIT/tromboembolismo previo=2, enf. vascular=1, edad 65–74=1 (máx 8). **Retiró el sexo femenino** | ≥2: anticoagulación oral recomendada (clase I); 1: debe considerarse (IIa); 0: sin anticoagulación | Van Gelder IC et al. Eur Heart J 2024 (guía ESC FA 2024) |
| CHA₂DS₂-VASc | Ídem (versión previa; la siguen usando ACC/AHA/ACCP/HRS 2023) | Igual + sexo femenino=1 (máx 9) | ≥2 (H) / ≥3 (M) anticoagular; 1 (H) / 2 (M) considerar | Lip GY et al. Chest 2010; Joglar JA et al. Circulation 2024 (ACC/AHA 2023) |
| HAS-BLED | Riesgo de sangrado bajo anticoagulación | HTA no controlada, función renal/hepática anormal, ACV previo, sangrado previo, INR lábil, edad>65, fármacos/alcohol (máx 9) | ≥3 alto riesgo (no contraindica anticoagular; optimizar factores modificables) | Pisters R et al. Chest 2010 |
| AHA PREVENT (2023) | Riesgo de ECV total (aterosclerótica + falla cardiaca) a 10 y 30 años, desde los 30 años | Edad, sexo, PAS, colesterol total/HDL, estatinas/antihipertensivos, DM, tabaquismo, eGFR (CKD-EPI 2021 sin raza); versión "enhanced": +HbA1c, albúmina/creatinina urinaria, índice de privación social | Reemplazó las Pooled Cohort Equations; YA NO usa raza. Es regresión — usar calculadora oficial, no sumar puntos | Khan SS et al. Circulation 2024; AHA PREVENT |
| Framingham calibrado para Colombia | Riesgo de evento coronario a 10 años en prevención primaria | Framingham original (edad, sexo, colesterol total, HDL, PAS, tratamiento antihipertensivo, tabaquismo, DM) **× 0,75** | Recalibración recomendada por la GPC colombiana de dislipidemia porque el Framingham original sobreestima el riesgo en población colombiana. Verificar categorías vigentes de la RIAS cardiovascular antes de citarlas | GPC dislipidemia, MinSalud/Colciencias 2014; Muñoz OM et al. |
| HEART score | Dolor torácico en urgencias | History, ECG, Age, Risk factors, Troponina — 0–2 c/u (máx 10) | 0–3 bajo riesgo (alta), 4–6 moderado (observación), 7–10 alto (manejo invasivo) | Six AJ et al. Neth Heart J 2008 |
| TIMI (NSTEMI/angina inestable) | Riesgo de eventos a 14 días | 7 variables clínicas, 1 punto c/u (edad≥65, ≥3 FRCV, estenosis coronaria conocida, desviación ST, ≥2 episodios angina/24h, AAS últimos 7 días, troponina+) | 0–2 bajo, 3–4 intermedio, 5–7 alto riesgo | Antman EM et al. JAMA 2000 |
| Killip | Clasificación de falla cardiaca en IAM | I sin signos, II estertores/S3, III edema pulmonar franco, IV shock cardiogénico | Predictor de mortalidad intrahospitalaria | Killip T, Kimball J. Am J Cardiol 1967 |

### 2. Geriatría, funcionalidad y caídas

| Escala | Qué evalúa | Componentes / puntaje | Interpretación | Fuente |
|---|---|---|---|---|
| Downton (modificada) | Riesgo de caídas | Caídas previas, medicación, déficit sensorial, estado mental, deambulación (0–1 c/u aprox., máx variable) | ≥3 alto riesgo de caídas (corte usado en los estudios de validación); <3 bajo | Downton JH. Falls in the Elderly, 1993; Rosendahl E et al. Aging Clin Exp Res 2003 |
| Morse Fall Scale | Riesgo de caídas (uso hospitalario) | Historia de caídas, dx 2°, ayuda ambulatoria, vía IV/heparina, marcha, estado mental | 0–24 bajo, 25–44 moderado, ≥45 alto riesgo | Morse JM et al. Can J Aging 1989 |
| Índice de Barthel | Actividades básicas de la vida diaria | 10 ítems (alimentación, baño, vestido, aseo, esfínteres, traslado, deambulación, escaleras), 0–100 | <20 dependencia total, 20–35 grave, 40–55 moderada, 60–99 leve, 100 independiente | Mahoney FI, Barthel DW. Md State Med J 1965 |
| Lawton-Brody (IADL) | Actividades instrumentales | 8 ítems (teléfono, compras, comida, casa, lavado, transporte, medicación, finanzas) | A mayor puntaje, mayor independencia; útil para decidir supervisión/apoyo domiciliario | Lawton MP, Brody EM. Gerontologist 1969 |
| Clinical Frailty Scale (Rockwood) | Fragilidad global | 9 categorías clínicas, de "muy en forma" (1) a "enfermedad terminal" (9); es juicio clínico, no suma de puntos | ≥5 marca fragilidad relevante para decisiones de manejo/pronóstico | Rockwood K et al. CMAJ 2005 |
| Timed Up and Go (TUG) | Movilidad y riesgo de caídas | Tiempo en levantarse, caminar 3 m, volver y sentarse | <10 s normal, 10–19,9 s movilidad reducida, ≥20 s alto riesgo, requiere evaluación | Podsiadlo D, Richardson S. J Am Geriatr Soc 1991 |
| Tinetti (POMA) | Equilibrio y marcha | 16 pts equilibrio + 12 pts marcha (máx 28) | <19 alto riesgo de caídas, 19–24 riesgo moderado | Tinetti ME. J Am Geriatr Soc 1986 |

### 3. Cognición

| Escala | Qué evalúa | Componentes / puntaje | Interpretación | Fuente |
|---|---|---|---|---|
| MMSE | Tamizaje de deterioro cognitivo | 30 puntos, varios dominios | ≥27 normal, 24–26 dudoso/leve, 18–23 leve-moderado, <18 severo (ajustar por escolaridad) | Folstein MF et al. J Psychiatr Res 1975 |
| MoCA | Tamizaje de deterioro cognitivo LEVE (más sensible que MMSE) | 30 puntos, varios dominios; +1 si escolaridad ≤12 años | ≥26 normal | Nasreddine ZS et al. J Am Geriatr Soc 2005 |
| Mini-Cog | Tamizaje rápido (<3 min) | Recordar 3 palabras + reloj | Reloj normal + 3 palabras = bajo riesgo; sugiere evaluación si falla | Borson S et al. Int J Geriatr Psychiatry 2000 |

### 4. Salud mental

| Escala | Qué evalúa | Componentes / puntaje | Interpretación | Fuente |
|---|---|---|---|---|
| PHQ-9 | Severidad de depresión | 9 ítems, 0–3 c/u (máx 27) | 0–4 mínima, 5–9 leve, 10–14 moderada, 15–19 mod-severa, ≥20 severa. Ítem 9>0 = evaluar ideación suicida ya | Kroenke K et al. J Gen Intern Med 2001 |
| GAD-7 | Severidad de ansiedad | 7 ítems, 0–3 c/u (máx 21) | 0–4 mínima, 5–9 leve, 10–14 moderada, ≥15 severa | Spitzer RL et al. Arch Intern Med 2006 |
| Edimburgo (EPDS) | Depresión perinatal/posparto | 10 ítems (máx 30) | ≥13 sugiere depresión probable (tamizaje sensible desde ≥10); ítem 10>0 = evaluar autolesión siempre | Cox JL et al. Br J Psychiatry 1987 |
| AUDIT / AUDIT-C | Consumo de riesgo de alcohol | AUDIT: 10 ítems (máx 40); AUDIT-C: 3 ítems | AUDIT ≥8 (H) consumo de riesgo; AUDIT-C ≥4 (H)/≥3 (M) positivo | Saunders JB et al. Addiction 1993; OMS |
| CAGE | Tamizaje rápido de alcoholismo | 4 preguntas sí/no | ≥2 positivas sugiere problema con el alcohol | Ewing JA. JAMA 1984 |
| Fagerström | Dependencia a la nicotina | 6 ítems (máx 10) | ≥7 dependencia alta | Heatherton TF et al. Br J Addict 1991 |

### 5. Delirium

| Escala | Qué evalúa | Componentes / puntaje | Interpretación | Fuente |
|---|---|---|---|---|
| CAM (Confusion Assessment Method) | Diagnóstico de delirium | 1) Inicio agudo y curso fluctuante, 2) Inatención, 3) Pensamiento desorganizado, 4) Alteración del nivel de conciencia | Delirium = (1 y 2) y (3 o 4) | Inouye SK et al. Ann Intern Med 1990 |

### 6. Nutrición

| Escala | Qué evalúa | Componentes / puntaje | Interpretación | Fuente |
|---|---|---|---|---|
| MNA-SF | Cribado nutricional en adulto mayor | 6 ítems (máx 14) | ≥12 normal, 8–11 riesgo de desnutrición, 0–7 desnutrición | Vellas B et al. Nutrition 1999 |
| MUST | Riesgo nutricional general | IMC + pérdida de peso involuntaria + efecto de enfermedad aguda | 0 bajo, 1 medio, ≥2 alto riesgo | BAPEN, 2003 |

### 7. Piel / úlceras por presión

| Escala | Qué evalúa | Componentes / puntaje | Interpretación | Fuente |
|---|---|---|---|---|
| Braden | Riesgo de úlceras por presión | 6 subescalas (percepción sensorial, humedad, actividad, movilidad, nutrición, fricción/cizallamiento), rango 6–23 | ≤9 muy alto, 10–12 alto, 13–14 moderado, 15–18 bajo riesgo | Bergstrom N et al. Nurs Res 1987 |

### 8. Respiratorio

| Escala | Qué evalúa | Componentes / puntaje | Interpretación | Fuente |
|---|---|---|---|---|
| CURB-65 | Severidad de neumonía adquirida en comunidad | Confusión, urea>7 mmol/L (≈ BUN >19 mg/dL ≈ urea >42 mg/dL; en Colombia el laboratorio suele reportar BUN), FR≥30, PAS<90 o PAD≤60, edad≥65 — 1 punto c/u. Sin laboratorio: CRB-65 | 0–1 ambulatorio, 2 considerar hospitalización, ≥3 alto riesgo/UCI | Lim WS et al. Thorax 2003 |
| mMRC | Disnea (usada en GOLD para EPOC) | 0 (solo con ejercicio intenso) a 4 (incapacita para salir de casa) | Grado ≥2 marca síntomas relevantes en clasificación GOLD | Medical Research Council, adaptada |
| Borg modificada | Percepción de disnea/esfuerzo | Escala 0–10 | Uso en pruebas de esfuerzo y rehabilitación respiratoria | Borg G. Med Sci Sports Exerc 1982 |

### 9. Sepsis y cuidado crítico

| Escala | Qué evalúa | Componentes / puntaje | Interpretación | Fuente |
|---|---|---|---|---|
| qSOFA | Tamizaje rápido de sepsis fuera de UCI | PAS≤100, FR≥22, Glasgow<15 — 1 punto c/u | ≥2 sugiere mal pronóstico; activa evaluación de SOFA completo. **No usarlo como herramienta única de tamizaje** (SSC 2021: recomendación fuerte en contra por baja sensibilidad, frente a SIRS, NEWS o MEWS) | Singer M et al. JAMA 2016 (Sepsis-3); Evans L et al. Intensive Care Med 2021 (SSC) |
| SOFA | Disfunción orgánica en sepsis | 6 sistemas (respiratorio, coagulación, hepático, cardiovascular, SNC, renal), 0–4 c/u (máx 24) | Aumento ≥2 puntos define disfunción orgánica asociada a sepsis | Vincent JL et al. Intensive Care Med 1996; Sepsis-3 |
| Escala de coma de Glasgow | Nivel de conciencia | Ocular (1–4) + Verbal (1–5) + Motora (1–6), máx 15, mín 3 | ≤8 compromiso severo (considerar vía aérea avanzada) | Teasdale G, Jennett B. Lancet 1974 |
| NEWS2 | Deterioro clínico agudo | FR, SatO2, O2 suplementario, PAS, FC, nivel de conciencia, temperatura | ≥7 alto riesgo, evaluación urgente | Royal College of Physicians, 2017 |

### 10. Renal y hepático

| Escala | Qué evalúa | Componentes / puntaje | Interpretación | Fuente |
|---|---|---|---|---|
| CKD-EPI 2021 (sin raza) | TFG estimada | Creatinina, edad, sexo (sin coeficiente de raza) | Estadios KDIGO G1–G5 según TFG | Inker LA et al. NEJM 2021; KDIGO |
| Child-Pugh | Severidad de cirrosis | Bilirrubina, albúmina, INR, ascitis, encefalopatía — 1–3 pts c/u (máx 15) | A (5–6) buen pronóstico, B (7–9) intermedio, C (10–15) grave | Pugh RN et al. Br J Surg 1973 |
| MELD 3.0 | Prioridad de trasplante hepático | Bilirrubina, creatinina, INR, sodio, albúmina, sexo femenino (ajuste) | Es regresión, no suma simple — usar calculadora oficial UNOS/OPTN; reemplazó a MELD-Na como estándar desde 2023 | Kim WR et al. Gastroenterology 2021 |

### 11. Tromboembolismo

| Escala | Qué evalúa | Componentes / puntaje | Interpretación | Fuente |
|---|---|---|---|---|
| Wells (TVP) | Probabilidad pretest de trombosis venosa profunda | Cáncer activo, parálisis/inmovilización, encamamiento/cirugía reciente, dolor localizado, edema de toda la pierna, edema pantorrilla >3 cm, edema con fóvea, venas colaterales, TVP previa (+1 c/u); diagnóstico alternativo tan/más probable (−2) | ≥2 probable, <2 improbable | Wells PS et al. Lancet 1997 |
| Wells (TEP) | Probabilidad pretest de tromboembolismo pulmonar | Signos de TVP, dx alternativo menos probable, FC>100, inmovilización/cirugía en 4 sem, TVP/TEP previo, hemoptisis, cáncer activo | >4 probable, ≤4 improbable (o 3 niveles bajo/moderado/alto) | Wells PS et al. Thromb Haemost 2000 |
| PERC | Descartar TEP sin dímero D en baja probabilidad pretest | 8 criterios clínicos | Todos negativos = TEP descartado con seguridad razonable | Kline JA et al. J Thromb Haemost 2004 |

### 12. Gastroenterología

| Escala | Qué evalúa | Componentes / puntaje | Interpretación | Fuente |
|---|---|---|---|---|
| Escala de Bristol | Forma de las heces | Tipos 1 (bolitas duras) a 7 (líquida) | Tipos 3–4 normales; 1–2 estreñimiento, 5–7 diarrea | Lewis SJ, Heaton KW. Scand J Gastroenterol 1997 |
| Criterios de Roma IV | Trastornos funcionales digestivos (dispepsia, SII) | Dolor/molestia recurrente asociado a patrón de defecación o comida, ≥1 día/semana en últimos 3 meses, inicio ≥6 meses antes | Diagnóstico clínico por cumplimiento de criterios | Drossman DA. Gastroenterology 2016 |

### 13. Trauma y ortopedia

| Escala | Qué evalúa | Componentes / puntaje | Interpretación | Fuente |
|---|---|---|---|---|
| Reglas de Ottawa (tobillo) | Necesidad de radiografía en trauma de tobillo | Dolor maleolar + (dolor óseo en borde posterior/punta de maléolo, o incapacidad de dar 4 pasos) | Positiva = indicar radiografía | Stiell IG et al. JAMA 1993 |
| Reglas de Ottawa (rodilla) | Necesidad de radiografía en trauma de rodilla | Edad≥55, dolor aislado en rótula, dolor en cabeza de peroné, incapacidad de flexionar 90°, incapacidad de soportar peso 4 pasos | Cualquiera positivo = indicar radiografía | Stiell IG et al. JAMA 1996 |

### 14. Obstetricia y pediatría

| Escala | Qué evalúa | Componentes / puntaje | Interpretación | Fuente |
|---|---|---|---|---|
| APGAR | Adaptación neonatal inmediata | FC, esfuerzo respiratorio, tono, irritabilidad refleja, color — 0–2 c/u, al min 1 y 5 | ≥7 normal, 4–6 mod. deprimido, ≤3 severamente deprimido | Apgar V. Curr Res Anesth Analg 1953 |
| Índice de Bishop | Favorabilidad cervical para inducción del parto | Dilatación, borramiento, estación, consistencia, posición (máx 13) | ≥8–9 cérvix favorable para inducción | Bishop EH. Obstet Gynecol 1964 |
| Silverman-Anderson | Dificultad respiratoria neonatal | 5 parámetros, 0–10 (escala inversa: mayor puntaje = mayor dificultad) | 0 sin dificultad, 1–3 leve, 4–6 moderada, ≥7 severa | Silverman WA, Andersen DH. Pediatrics 1956 |

### 15. Óseo / endocrino

| Escala | Qué evalúa | Componentes / puntaje | Interpretación | Fuente |
|---|---|---|---|---|
| FRAX | Riesgo a 10 años de fractura mayor/cadera | Edad, sexo, IMC, fractura previa, padre con fractura de cadera, tabaquismo, glucocorticoides, artritis reumatoide, osteoporosis secundaria, alcohol, ± DMO | Genera % de riesgo absoluto a 10 años; umbrales de tratamiento según guía local | Kanis JA et al., Universidad de Sheffield, OMS |
| Wagner | Clasificación de pie diabético | Grados 0–5 según profundidad/infección/necrosis | A mayor grado, mayor riesgo de amputación | Wagner FW. Foot Ankle 1981 |
| FINDRISC | Riesgo de diabetes tipo 2 a 10 años | Edad, IMC, circunferencia de cintura, actividad física, consumo frutas/verduras, antihipertensivos, glucosa alterada previa, historia familiar de DM | Puntaje mayor = mayor riesgo; guía necesidad de tamizaje con glucosa | Lindström J, Tuomilehto J. Diabetes Care 2003 |

### 16. Medicina Familiar — funcionalidad familiar y cuidador

| Escala | Qué evalúa | Componentes / puntaje | Interpretación | Fuente |
|---|---|---|---|---|
| APGAR familiar | Percepción de la función familiar | 5 ítems (adaptación, participación, ganancia/crecimiento, afecto, recursos). Versión 0–4 por ítem (0–20); existe versión original 0–2 (0–10) con otros cortes — decir cuál se usa | Versión 0–20: 18–20 buena función, 14–17 disfunción leve, 10–13 moderada, ≤9 severa | Smilkstein G. J Fam Pract 1978; versión 0–20 usada en documentos colombianos (CLAP/OPS) |
| Zarit (22 ítems) | Sobrecarga del cuidador | 22 ítems Likert. Validación española 1–5 por ítem (22–110) | ≤46 sin sobrecarga, 47–55 leve, ≥56 intensa. El autor original no propuso cortes: son de la validación española y dependen de la escala de puntuación usada | Zarit SH 1980; Martín M et al. Rev Gerontol 1996 |

