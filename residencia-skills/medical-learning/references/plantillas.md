# Plantillas de contenido — medical-learning

Este archivo lo referencia `SKILL.md`. Cada plantilla define **qué** debe cubrirse; el **cómo**
(cadena causal, bloques, flechas, visuales, filtro de realidad) sigue rigiéndose por el SKILL.md.
Omite una sección solo si no aplica, y di en una línea por qué se omitió.

## Índice
1. Ficha de enfermedad (19 secciones → 4 bloques)
2. Ficha de examen paraclínico o escala clínica
3. Ficha de medicamento
4. Caso clínico progresivo
5. Bioestadística al interpretar evidencia

---

## 1. Ficha de enfermedad

| # | Sección | Bloque | Qué no puede faltar |
|---|---|---|---|
| 1 | EN UNA FRASE | A | Mecanismo central + consecuencia clínica en ≤ 25 palabras |
| 2 | Fisiología necesaria | A | Solo lo indispensable para entender el fallo |
| 3 | Fisiopatología paso a paso | A | Cadena causal con flechas; cada eslabón verificable |
| 4 | Respuesta compensatoria y su precio | A | Por qué la compensación termina causando daño |
| 5 | Epidemiología | B | Global + Colombia solo con dato verificable; si no, decirlo |
| 6 | Factores de riesgo | B | Agrupados por mecanismo, no en lista plana |
| 7 | Síntomas y signos con su porqué | B | Un eslabón causal por hallazgo |
| 8 | Paraclínicos: por qué pido cada uno | B | Qué espero encontrar y qué cambia si sale alterado |
| 9 | Criterios diagnósticos | B | Con la guía y el año; umbrales exactos |
| 10 | Clasificación / escalas | B | Usar `escalas-clinicas`; mostrar cómo cambia la conducta |
| 11 | Diagnósticos diferenciales | B | Tabla: dato que sube / dato que baja cada uno |
| 12 | Objetivo terapéutico | C | Meta concreta (cifra, desenlace) y quién la define |
| 13 | Tratamiento no farmacológico | C | Con magnitud de beneficio si existe evidencia |
| 14 | Tratamiento farmacológico | C | Genérico + dosis + vía + frecuencia + titulación + ajustes (renal, hepático, edad, embarazo, lactancia); por qué ES primera línea y por qué NO la alternativa |
| 15 | Qué pasa si no trato | C | Historia natural; complicaciones en cadena |
| 16 | Seguimiento y criterios de remisión / hospitalización / UCI | D | Qué medir, cada cuánto, umbral de remisión |
| 17 | Enfoque de Medicina Familiar | D | Prevención, familia, adherencia, RIAS, primer nivel en Colombia |
| 18 | Errores frecuentes y perlas | D | 3–5 de cada uno, accionables |
| 19 | Mapa mental de 30 s + Puntos clave para el residente | D | Cierra el ciclo |

## 2. Ficha de examen paraclínico o escala clínica

No fuerces la plantilla de enfermedad. Cubre:

1. Qué mide (en una frase) y **qué fenómeno fisiológico** lo produce.
2. Indicaciones: cuándo pedirlo / aplicarla, y cuándo **no** aporta.
3. Técnica o componentes (ítems y puntaje para escalas: tomar de `escalas-clinicas`).
4. Valores de referencia o puntos de corte, con unidad y fuente.
5. Interpretación por patrones: qué significa cada alteración y su cadena causal.
6. Falsos positivos / falsos negativos y sus mecanismos (interferencias, fármacos, condiciones).
7. Rendimiento diagnóstico (sensibilidad, especificidad, LR) **solo si está verificado**; si no, "No puedo verificar esto".
8. Qué hago con el resultado: conducta según cada rango.
9. Disponibilidad y costo-oportunidad en primer nivel en Colombia.
10. Errores frecuentes de interpretación + Puntos clave.

## 3. Ficha de medicamento

Sigue el orden de las preferencias del usuario:

familia · mecanismo de acción (como cadena causal hasta el efecto clínico) · farmacocinética ·
farmacodinamia · indicaciones (aprobadas INVIMA vs. uso fuera de indicación) · contraindicaciones ·
dosis inicial → titulación → dosis máxima · ajuste renal (por TFG) · ajuste hepático (Child-Pugh) ·
embarazo · lactancia · geriatría (criterios de Beers/STOPP si aplican) · pediatría si aplica ·
RAM (con su mecanismo: "produce tos PORQUE…") · interacciones relevantes en primer nivel ·
monitorización (qué, cuándo, umbral de suspensión) · evidencia clínica: estudios pivote con
desenlace, magnitud (RRA, NNT) y población · lugar en las guías actuales (línea, fuerza) ·
disponibilidad en Colombia (PBS/MIPRES) · Puntos clave.

## 4. Caso clínico progresivo

Una pregunta a la vez; no reveles el siguiente dato hasta que el usuario responda.

1. **Presentación inicial** (motivo de consulta, edad, contexto) → "¿Qué hipótesis planteas y por qué?"
2. **Anamnesis y examen dirigidos** → "¿Qué dato sube o baja cada hipótesis?"
3. **Lista de problemas activos**.
4. **Paraclínicos** → "¿Qué pides, qué NO pides y por qué?" Luego entrega resultados.
5. **Interpretación** → diagnóstico más probable y el "no me lo puedo perder".
6. **Plan terapéutico** con dosis concretas → "¿Por qué este y no otro?"
7. **Giro del caso** (complicación, comorbilidad, efecto adverso) → nueva decisión.
8. **Cierre**: pronóstico, seguimiento, criterios de remisión, y qué error habría sido el más probable.

Retroalimentación tras cada respuesta: qué acertó, qué faltó, el eslabón causal que lo justifica.

## 5. Bioestadística al interpretar evidencia

Cuando aparezca un resultado, tradúcelo siempre así (solo con cifras verificadas del estudio):

| Medida | Cómo explicarla |
|---|---|
| Riesgo absoluto en cada grupo | "De cada 100 pacientes, X tuvieron el evento con A y Y con B" |
| RRA y NNT | NNT = 1 / RRA, con el horizonte temporal ("durante 3 años") |
| RR / HR / OR | Diferenciar: HR es instantáneo en el tiempo; OR sobreestima el RR si el evento es frecuente |
| NNH | Igual que NNT, para el daño |
| IC 95 % | Si cruza 1 (razones) o 0 (diferencias) → no significativo; ancho = imprecisión |
| Valor p | Probabilidad de los datos si H0 fuera cierta; no es la probabilidad de que el tratamiento funcione |
| Importancia clínica vs. estadística | ¿El efecto supera la diferencia mínima clínicamente importante? |

Si el estudio no reporta riesgos absolutos, dilo y no los reconstruyas de memoria.
