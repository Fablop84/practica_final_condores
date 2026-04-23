# 🇨🇱 ChileCompraEficiente: Análisis y Predicción de Licitaciones Públicas

Este proyecto, desarrollado por el grupo **Cóndores**, ofrece una solución integral de ciencia de datos para el mercado público de Chile. El sistema abarca desde la extracción automatizada de datos (2020-2025) mediante la API de Mercado Público hasta la implementación de modelos de Machine Learning para predecir la demanda futura de licitaciones, culminando en un dashboard interactivo para la toma de decisiones.

## 🎯 Objetivos del Proyecto
* **Automatización:** Extraer datos históricos y actuales de la plataforma ChileCompra de forma eficiente.
* **Inteligencia de Datos:** Realizar un análisis exploratorio profundo (EDA) para identificar patrones de comportamiento en los organismos del Estado.
* **Predicción:** Implementar un modelo de Machine Learning capaz de proyectar el volumen de licitaciones futuras.
* **Visualización:** Desplegar una herramienta analítica interactiva (Dashboard) que facilite la interpretación de los resultados.

---

## 🛠️ Stack Tecnológico
* **Lenguajes:** Python 3.11.
* **Extracción & Cloud:** Requests, Google Cloud Storage, PyArrow (Parquet).
* **Ciencia de Datos:** Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn.
* **Visualización:** Plotly, Dash, Dash Bootstrap Components.

---

## 📂 Estructura del Repositorio

### 1. Extracción de Datos (`notebook_extraccion_data.ipynb`)
Este módulo se encarga del pipeline de ingesta:
* Conexión con la **API de Mercado Público**.
* Procesamiento de datos en formato JSON/CSV y conversión a **Parquet** para optimizar el almacenamiento.
* Carga automatizada a **Google Cloud Storage** para asegurar la persistencia y escalabilidad de la data.

### 2. EDA y Machine Learning (`proyecto_final_condores_ultima_version.ipynb`)
El núcleo analítico del proyecto donde se desarrollan las siguientes fases:
* **Análisis Exploratorio (EDA):** Identificación del "Top 5" de organismos con mayor actividad y análisis de estacionalidad.
* **Pre-procesamiento:** Limpieza de datos, ingeniería de variables (*Feature Engineering*) y normalización.
* **Modelo Predictivo:** Entrenamiento de modelos de regresión para estimar el número de licitaciones futuras por organismo, permitiendo a los proveedores anticiparse a la demanda.

### 3. Visualización Avanzada (`Dashboard_Licitaciones_2025_v4.py`)
Una aplicación web interactiva construida con **Dash/Plotly**:
* **Forecast 2026:** Visualización de las proyecciones de licitaciones por mes para los organismos líderes.
* **Filtros Dinámicos:** Selección por código de organismo y visualización de scores de precisión del modelo.
* **UI/UX:** Interfaz profesional con tema oscuro (*Dark Mode*) diseñada para analistas de mercado.

---

## 🧠 Elección y Justificación del Modelo Predictivo
Para el desarrollo del núcleo de inteligencia de este proyecto, se realizó un proceso de evaluación comparativa entre algoritmos de última generación. Tras una fase de pruebas rigurosas, el modelo Random Forest Híbrido fue seleccionado como el algoritmo ganador para realizar las proyecciones de Mercado Público.

## 🎯 Justificación del Modelo Ganador:
1. Precisión Superior (R² = 0.957): El modelo híbrido logró explicar el 95.7% de la variabilidad de los datos, superando significativamente la capacidad predictiva del XGBoost estándar. Esto asegura que las tendencias de licitaciones proyectadas en el Dashboard sean altamente confiables.

2. Reducción de Errores (MAE y RMSE): Presentó el error absoluto medio más bajo (0.0891), lo que significa que las desviaciones entre las licitaciones reales y las predichas son mínimas, permitiendo una planificación financiera más exacta para las organizaciones.

2. Naturaleza Híbrida: Al combinar la capacidad de generalización del Random Forest con ajustes de parámetros específicos para series temporales, el modelo demostró una mayor estabilidad frente a la volatilidad histórica de los datos de licitaciones chilenas.

4. Manejo de la Complejidad: La estructura de este modelo permite capturar las estacionalidades mensuales sin sobreajustarse (overfitting), manteniendo un rendimiento óptimo incluso al procesar el volumen masivo de datos de los últimos 6 años.

## 🚀 Implementación en el Dashboard
El modelo Random Forest Híbrido es el motor que genera el "Forecast Mensual 2026" visible en la aplicación. Gracias a su alto puntaje de precisión, el sistema puede asignar un Score de confianza a cada organismo público, permitiendo identificar patrones de compra con una certeza estadística validada.

---

## 🚀 Instalación y Uso

### Requisitos previos
* Python 3.10+
* Cuenta de servicio en Google Cloud (opcional, para almacenamiento en la nube).
* API Key de Mercado Público Chile.

### Ejecución
1.  **Instalar dependencias:**
    ```bash
    pip install pandas plotly dash dash-bootstrap-components numpy scikit-learn pyarrow
    ```
2.  **Ejecutar el Dashboard:**
    ```bash
    python Dashboard_Licitaciones_2025_v4.py
    ```
3.  Accede a la dirección local `http://127.0.0.1:8053` en tu navegador.

---

## 📊 Resultados e Impacto
El modelo denominado **"ChileCompraEficiente"** permite:
* Reducir la incertidumbre para las PYMES proveedoras del Estado.
* Optimizar los tiempos de respuesta ante nuevas licitaciones.
* Entender el ciclo de vida del gasto público por región y unidad gubernamental.

---

**Contribuciones:**
Este proyecto fue desarrollado bajo una arquitectura modular, permitiendo que el extractor, el modelo y el dashboard funcionen de manera independiente o como un pipeline integrado.

## 👥 Equipo
- Fabian Camilo López
- Jon Abaroa
- Luis Manuel Hernandez Cancho
- Christian Guevara
  
**Fecha**: Abril 2026

**Bootcamp**: Proyecto final Bootcamp Big Data, Inteligencia Artificial & Machine Learning | Edición XVI.
