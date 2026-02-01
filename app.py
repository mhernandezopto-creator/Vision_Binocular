# =========================
# IMPORTS
# =========================
import pandas as pd
import streamlit as st

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="Visión – Registro Público",
    layout="wide"
)

# =========================
# SECRETS
# =========================
SHEET_ID = st.secrets.get("SHEET_ID", "")
REGISTRO_GID = st.secrets.get("REGISTRO_GID", "")
RESULTADOS_GID = st.secrets.get("RESULTADOS_GID", "")

if not SHEET_ID or not REGISTRO_GID:
    st.error("❌ Faltan Secrets (SHEET_ID / REGISTRO_GID). Revisa Settings → Secrets.")
    st.write("Keys detectadas:", list(st.secrets.keys()))
    st.stop()

ID_COL = "id_publica"  # debe coincidir EXACTO con el header en Sheets

# =========================
# HELPERS
# =========================
@st.cache_data(ttl=60)
def load_csv(sheet_id: str, gid: str) -> pd.DataFrame:
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(url)
    except Exception as e:
        st.error("❌ Error cargando Google Sheet")
        st.write("URL usada:")
        st.code(url)
        st.exception(e)
        st.stop()
    df.columns = [c.strip() for c in df.columns]
    return df

# =========================
# CONTROLES UI
# =========================
st.title("📘 Registro público de evaluaciones visuales")

colA, colB = st.columns([1, 3])
with colA:
    if st.button("🔄 Recargar datos"):
        st.cache_data.clear()
with colB:
    st.caption(
        "Base pública anonimizada. "
        "Los datos se muestran sin información personal identificable."
    )

# =========================
# CARGA DE DATOS
# =========================
registro = load_csv(SHEET_ID, REGISTRO_GID)

resultados = None
if RESULTADOS_GID:
    resultados = load_csv(SHEET_ID, RESULTADOS_GID)

# =========================
# VALIDACIONES
# =========================
if ID_COL not in registro.columns:
    st.error(f"Falta la columna '{ID_COL}' en registro.")
    st.stop()

if resultados is not None and ID_COL not in resultados.columns:
    st.error(f"Falta la columna '{ID_COL}' en resultados.")
    st.stop()

# =========================
# SELECTOR / QUERY PARAM
# =========================
ids = sorted(registro[ID_COL].dropna().astype(str).unique().tolist())
picked = st.selectbox("Abrir ficha por ID pública", [""] + ids)

case = st.query_params.get("case")
if case and not picked:
    picked = case

# =========================
# VISTA FICHA POR ID
# =========================
if picked:
    st.query_params["case"] = picked
    st.subheader("🧾 Ficha del registro")

    row_reg = registro[registro[ID_COL].astype(str) == str(picked)]
    if row_reg.empty:
        st.warning("ID no encontrado.")
        st.stop()

    r = row_reg.iloc[0].to_dict()

    # --- Registro (captura) ---
    st.markdown("### Registro")
    st.write("ID pública:", picked)
    st.write("Fecha publicación:", r.get("fecha_publicacion", ""))
    st.write("Edad paciente:", r.get("edad_paciente", ""))
    st.write("Síntomas visuales:", r.get("sintomas_visuales", ""))

    # --- Resultados (si existen) ---
    st.divider()
    st.markdown("### Resultados")

    if resultados is not None:
        row_res = resultados[resultados[ID_COL].astype(str) == str(picked)]
        if not row_res.empty:
            res = row_res.iloc[0].to_dict()
            st.write("Patrón detectado:", res.get("patron_detectado", ""))
            st.write("Criterio aplicado:", res.get("criterio_aplicado", ""))
            st.write("Justificación:", res.get("justificacion", ""))
            st.write("Riesgo visual:", res.get("riesgo_visual", ""))
        else:
            st.info("Resultados aún no disponibles para este registro.")
    else:
        st.info("Módulo de resultados no activado.")

    with st.expander("Ver registro completo (debug)"):
        st.json(r)

# =========================
# VISTA REGISTRO PÚBLICO
# =========================
else:
    st.subheader("📂 Registros disponibles")

    q = st.text_input("Buscar por ID o texto", "")
    df_view = registro.copy()

    if q.strip():
        q_low = q.strip().lower()
        mask = df_view.astype(str).apply(
            lambda col: col.str.lower().str.contains(q_low, na=False)
        )
        df_view = df_view[mask.any(axis=1)]

    st.dataframe(df_view, use_container_width=True)


