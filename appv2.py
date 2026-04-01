import streamlit as st
import pandas as pd
from io import BytesIO
import unicodedata

st.set_page_config(page_title="Conciliador Bancario", layout="wide")

st.title("💼 Conciliador Mayor vs Extracto")

# =========================
# FUNCIONES
# =========================

def normalizar_texto(texto):
    texto = texto.lower().strip()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto

def detectar_columna(cols, keywords):
    cols_norm = {col: normalizar_texto(col) for col in cols}
    for col, col_norm in cols_norm.items():
        for kw in keywords:
            if kw in col_norm:
                return col
    return None

def index_safe(cols, col_detectada):
    if col_detectada in cols:
        return list(cols).index(col_detectada)
    return 0

# =========================
# KEYWORDS
# =========================

KEYWORDS = {
    "fecha": ["fecha", "date"],
    "debe": ["debe"],
    "haber": ["haber"],
    "importe": ["importe", "monto"],
    "debito": ["debito", "debitos"],
    "credito": ["credito", "creditos"],
}

# =========================
# UPLOAD
# =========================

archivo_extracto = st.file_uploader("📄 Subí el EXTRACTO bancario", type=["xlsx"])
archivo_mayor = st.file_uploader("📄 Subí el MAYOR contable", type=["xlsx"])

if archivo_extracto and archivo_mayor:

    extracto = pd.read_excel(archivo_extracto)
    mayor = pd.read_excel(archivo_mayor)

    st.subheader("👀 Preview archivos")
    col1, col2 = st.columns(2)

    with col1:
        st.write("Extracto")
        st.dataframe(extracto.head())

    with col2:
        st.write("Mayor")
        st.dataframe(mayor.head())

    # =========================
    # DETECCIÓN AUTOMÁTICA
    # =========================

    col_fecha_ext_auto = detectar_columna(extracto.columns, KEYWORDS["fecha"])
    col_importe_auto = detectar_columna(extracto.columns, KEYWORDS["importe"])
    col_debito_auto = detectar_columna(extracto.columns, KEYWORDS["debito"])
    col_credito_auto = detectar_columna(extracto.columns, KEYWORDS["credito"])

    col_fecha_may_auto = detectar_columna(mayor.columns, KEYWORDS["fecha"])
    col_debe_auto = detectar_columna(mayor.columns, KEYWORDS["debe"])
    col_haber_auto = detectar_columna(mayor.columns, KEYWORDS["haber"])

    # =========================
    # CONFIGURACIÓN USUARIO
    # =========================

    st.subheader("⚙️ Configuración")

    modo = st.radio("Tipo de extracto", ["Importe", "Débito/Crédito"])

    col_fecha_ext = st.selectbox(
        "Fecha extracto",
        extracto.columns,
        index=index_safe(extracto.columns, col_fecha_ext_auto)
    )

    if modo == "Importe":
        col_importe = st.selectbox(
            "Importe",
            extracto.columns,
            index=index_safe(extracto.columns, col_importe_auto)
        )
    else:
        col_debito = st.selectbox(
            "Débito",
            extracto.columns,
            index=index_safe(extracto.columns, col_debito_auto)
        )
        col_credito = st.selectbox(
            "Crédito",
            extracto.columns,
            index=index_safe(extracto.columns, col_credito_auto)
        )

    st.markdown("---")

    col_fecha_may = st.selectbox(
        "Fecha mayor",
        mayor.columns,
        index=index_safe(mayor.columns, col_fecha_may_auto)
    )

    col_debe = st.selectbox(
        "Debe",
        mayor.columns,
        index=index_safe(mayor.columns, col_debe_auto)
    )

    col_haber = st.selectbox(
        "Haber",
        mayor.columns,
        index=index_safe(mayor.columns, col_haber_auto)
    )

    tolerancia_dias = st.number_input("Tolerancia de días", value=2)

    # =========================
    # BOTÓN
    # =========================

    if st.button("🚀 Ejecutar conciliación"):

        try:
            # === NORMALIZAR FECHAS ===
            extracto["Fecha"] = pd.to_datetime(extracto[col_fecha_ext], dayfirst=True, errors="coerce")
            mayor["Fecha"] = pd.to_datetime(mayor[col_fecha_may], dayfirst=True, errors="coerce")

            # === IMPORTES ===
            if modo == "Importe":
                extracto["Importe"] = pd.to_numeric(
                    extracto[col_importe], errors="coerce"
                ).fillna(0)
            else:
                extracto["Importe"] = (
                    pd.to_numeric(extracto[col_credito], errors="coerce").fillna(0)
                    -
                    pd.to_numeric(extracto[col_debito], errors="coerce").fillna(0)
                )

            mayor["Importe"] = (
                pd.to_numeric(mayor[col_debe], errors="coerce").fillna(0)
                -
                pd.to_numeric(mayor[col_haber], errors="coerce").fillna(0)
            )

            # === MATCH (NO TOCADO) ===
            def buscar_match(row):
                posibles = mayor[
                    (abs(mayor["Importe"] - row["Importe"]) < 0.01) &
                    (abs((mayor["Fecha"] - row["Fecha"]).dt.days) <= tolerancia_dias)
                ]
                return len(posibles) > 0

            extracto["Match"] = extracto.apply(buscar_match, axis=1)

            # =========================
            # RESULTADOS (FIX APLICADO)
            # =========================

            ok = extracto[extracto["Match"] == True]
            solo_banco = extracto[extracto["Match"] == False]

            # 🔥 FIX: ahora considera fecha + importe
            solo_mayor = mayor[
                ~mayor.apply(
                    lambda row: any(
                        (abs(extracto["Importe"] - row["Importe"]) < 0.01) &
                        (abs((extracto["Fecha"] - row["Fecha"]).dt.days) <= tolerancia_dias)
                    ),
                    axis=1
                )
            ]

            st.success("✅ Conciliación completada")

            col1, col2, col3 = st.columns(3)
            col1.metric("Conciliados", len(ok))
            col2.metric("Solo banco", len(solo_banco))
            col3.metric("Solo mayor", len(solo_mayor))

            st.subheader("📊 Vista previa conciliados")
            st.dataframe(ok.head(50))

            # === EXPORT ===
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                ok.to_excel(writer, sheet_name="Conciliados", index=False)
                solo_banco.to_excel(writer, sheet_name="Solo_Banco", index=False)
                solo_mayor.to_excel(writer, sheet_name="Solo_Mayor", index=False)

            st.download_button(
                label="📥 Descargar Excel",
                data=output.getvalue(),
                file_name="Conciliacion.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
