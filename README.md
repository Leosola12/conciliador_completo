# 💼 Conciliador Bancario (Mayor vs Extracto)

Aplicación web desarrollada en Streamlit para conciliar movimientos entre extractos bancarios y mayores contables de forma flexible y automática.

---

## 🚀 Funcionalidades

- 📂 Carga de archivos Excel (extracto + mayor)
- 🔍 Detección automática de columnas (soporta múltiples formatos)
- ⚙️ Selección manual de columnas (por si el formato es distinto)
- 💰 Soporte para:
  - Extractos con columna **Importe**
  - Extractos con **Débito / Crédito**
- 📅 Matching por:
  - Importe
  - Fecha (con tolerancia configurable)
- 📊 Resultado dividido en:
  - Conciliados
  - Solo banco
  - Solo mayor
- 📥 Exportación a Excel

---

## 🧠 Compatibilidad de formatos

### MAYOR
Detecta automáticamente columnas como:
- `Debe / Haber`
- `DEBE / HABER`
- `Monto Debe / Monto Haber`

---

### EXTRACTO
Soporta:

#### ✔ Formato 1:
- `Importe`

#### ✔ Formato 2:
- `Débito / Crédito`
- `Debitos / Creditos`
- `Débitos / Créditos`

👉 No importa:
- Mayúsculas/minúsculas  
- Tildes  
- Singular/plural  

---

## ⚙️ Cómo usar

1. Subir archivo de **extracto bancario**
2. Subir archivo de **mayor contable**
3. Verificar / ajustar columnas detectadas
4. Seleccionar tipo de extracto:
   - Importe
   - Débito / Crédito
5. Definir tolerancia de días
6. Hacer clic en **"Ejecutar conciliación"**
7. Descargar el Excel con resultados

---

## 📦 Instalación local

```bash
pip install streamlit pandas openpyxl
streamlit run app.py
