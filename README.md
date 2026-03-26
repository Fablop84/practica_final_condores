📊 Resumen del Notebook — ProcuraAI
🔹 FASE 1 — Inteligencia Analítica del Mercado Público
🎯 Objetivo

Reducir el universo de licitaciones del mercado público chileno a un segmento analíticamente robusto, identificando organismos con comportamiento cíclico relevante para modelamiento predictivo.

🧩 Desarrollo
1. Carga y preparación de datos
Se cargan datasets globales de:
Licitaciones
Órdenes de compra
Se construyen catálogos de:
Estados de licitación
Tipos de licitación
Se realiza:
Validación de estructura
Revisión de nulos y duplicados
Optimización de memoria
2. Construcción del embudo de licitaciones

Se aplica un filtro progresivo:

Universo inicial: licitaciones totales
→ Licitaciones adjudicadas
→ Licitaciones públicas
→ Tipo LE (Licitación Pública estándar)
→ Periodo 2020–2025

🔎 Resultado:

~263.000 licitaciones relevantes
3. Enriquecimiento del dataset

Se construyen nuevas variables:

codigo_organismo
codigo_tipo
anio_licitacion
tipo_base (pública / privada / especial)
4. Análisis de organismos
Se agrupan licitaciones por organismo
Se filtran organismos con al menos 150 licitaciones
Se obtiene:
451 organismos
128.849 registros
5. Identificación de patrones cíclicos

Se construyen métricas avanzadas por organismo:

Coeficiente de variación (CV)
Peso del mes dominante
Entropía inversa
Índice HHI
Estabilidad interanual
Ciclicidad relativa al mercado
6. Score de ciclicidad

Se define un score compuesto ponderado que resume el comportamiento temporal de cada organismo.

7. Clustering de organismos
Se aplica KMeans (k=4)
Se identifican clusters de comportamiento temporal

📌 Resultado clave:

Identificación de un cluster estratégico altamente cíclico
8. Ranking estratégico
Se combina:
score de ciclicidad
volumen de licitaciones
Se construye un ranking final

📌 Resultado final:

21 organismos estratégicos
4.362 licitaciones asociadas
✅ Resultado de la Fase 1
Segmentación del mercado público
Identificación de organismos estratégicos
Construcción de un dataset enfocado para modelamiento
🔹 FASE 2 — Modelamiento Predictivo (ProcuraAI)
🎯 Objetivo

Desarrollar y comparar modelos de predicción de licitaciones mensuales para estimar comportamiento futuro del mercado.

🧩 Desarrollo
1. Construcción de serie temporal
Se agregan licitaciones mensualmente
Se construye serie histórica
Se separa:
Train
Test (últimos 12 meses)
2. Feature Engineering

Se crean variables:

Temporales:
mes
año
trimestre
Lags:
lag_1, lag_2, lag_3, lag_6, lag_12
Rolling:
promedio móvil (rolling_3)
Tendencia
3. Modelos desarrollados
🔹 Modelo Base — Random Forest
Primer benchmark
Resultados:
MAPE ~14%
🔹 Modelo PRO — XGBoost
Mayor complejidad
Resultados:
Peor desempeño que baseline
🔹 Modelos híbridos
Incorporan ajustes estacionales
Corrigen comportamiento en meses críticos (ej: diciembre)
Resultados:
Mejora parcial
🔹 Modelo final — ProcuraAI
Selección optimizada de features
Tratamiento especial de estacionalidad
Modelo simplificado y robusto

📌 Resultados finales:

MAPE: ~10.76%
Mejor desempeño global
4. Forecast futuro
Se proyectan 12 meses hacia adelante
Se genera serie de predicción futura
✅ Resultado de la Fase 2
Modelo predictivo funcional
Selección del mejor enfoque (ProcuraAI)
Capacidad de forecast del mercado agregado
🔹 FASE 3 — Aplicación del Modelo y Enfoque Comercial
🎯 Objetivo

Aplicar el modelo a nivel de organismo y transformar los resultados en insights accionables para negocio.

🧩 Desarrollo
1. Selección de organismos
Se seleccionan los Top 20 organismos por volumen
Se filtran aquellos con suficiente historial temporal
2. Modelamiento por organismo

Para cada organismo:

Construcción de serie mensual
Feature engineering individual
Entrenamiento de modelo (XGBoost)
Evaluación:
MAE
RMSE
MAPE
Forecast de 12 meses
3. Evaluación de desempeño

Resultados generales:

Alta variabilidad en desempeño
Promedio MAPE elevado
Solo algunos organismos presentan buena predictibilidad
4. Clasificación de modelos

Se define umbral:

✔️ Modelo bueno: MAPE < 35
❌ Modelo deficiente: MAPE alto
5. Construcción del score comercial

Se integran:

Precisión del modelo
Volumen proyectado
Estabilidad

Se genera:

Ranking de oportunidades
Identificación de organismos prioritarios
6. Generación de alertas
Se detectan cambios relevantes en forecast
Ejemplo:
Variaciones > 30%
7. Exportación de resultados
Se exportan datasets finales:
Forecast por organismo
Evaluación de modelos
Ranking comercial
✅ Resultado de la Fase 3
Forecast a nivel de organismo
Identificación de oportunidades comerciales
Primer prototipo de sistema de inteligencia predictiva
🧠 CONCLUSIÓN GENERAL

El notebook desarrolla un flujo completo:

1️⃣ Inteligencia de mercado

→ Segmentación y detección de patrones

2️⃣ Modelamiento predictivo

→ Construcción y selección de modelos

3️⃣ Aplicación comercial

→ Transformación en oportunidades de negocio

🚀 Resultado final del proyecto

ProcuraAI se configura como:

Un sistema de inteligencia predictiva aplicado al mercado público chileno, capaz de identificar organismos estratégicos, modelar su comportamiento y generar oportunidades comerciales basadas en datos.

Si quieres, en el siguiente paso te puedo armar:

✅ versión ultra ejecutiva (tipo pitch 5 min)
✅ o una slide lista para PowerPoint
✅ o el discurso completo para presentación final
