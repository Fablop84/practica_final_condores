# 🧠 Estructura del Proyecto y Estado Actual — ProcuraAI

---

## 🧠 1. ESTRUCTURA IDEAL DE PROYECTO (REFERENCIA)

Un proyecto como ProcuraAI debería estructurarse en 6 capas:

1. Problema & objetivo de negocio  
2. Data pipeline (ingesta + arquitectura)  
3. EDA & segmentación  
4. Modelamiento  
5. Validación & robustez  
6. Producto / capa comercial  

---

## 📊 2. COMPARACIÓN REAL vs IDEAL

### 🟣 1. Problema & objetivo

#### ✔️ Ya implementado
- Problema claro: mercado público no predictivo  
- Enfoque definido: licitaciones → forecast  
- Propuesta de valor: anticipación de oportunidades  

#### ⚠️ Pendiente
- Definir explícitamente:
  - Usuario objetivo (proveedor, consultora, Estado)
  - Caso de uso concreto (ej: priorización comercial)

---

### 🟣 2. Data pipeline

#### ✔️ Ya implementado
- Descarga desde API Mercado Público  
- Estructura en Google Drive  
- Datos históricos 2020–2026  
- Uso de formato Parquet  

#### ⚠️ Parcial
- Automatización diaria iniciada  
- Orquestación incompleta  

#### ❌ Pendiente
- Pipeline formal:
