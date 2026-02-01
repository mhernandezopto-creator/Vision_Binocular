import streamlit as st

st.set_page_config(page_title="Visión", layout="wide")

st.title("✅ Streamlit funcionando")
st.write("Si ves esto, el deploy va bien.")

#VALORES REGISTRO PUBLICOS
SHEET_ID = "1P79M3wDddVua_rzt4chvRa4I7sfgPJHmh1G3M37i8ww"
REGISTRO_GID = "/edit?gid=1677150373#gid=1677150373"
RESULTADOS_GID = "/edit?gid=1739885561#gid=1739885561"


import pandas as pd
import streamlit as st

st.set_page_config(page_title="AuraVision", layout="wide")

SHEET_ID = st.secrets["1P79M3wDddVua_rzt4chvRa4I7sfgPJHmh1G3M37i8ww"]
REGISTRO_GID = st.secrets["/edit?gid=1677150373#gid=1677150373"]
RESULTADOS_GID = st.secrets["/edit?gid=1739885561#gid=1739885561"]

ID_COL = "id_publica"  # tiene que ser EXACTO al header en tus sheets

@st.cache_data(ttl=60)
def load_csv(sheet_id: str, gid: str) -> pd.DataFrame:
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    df.columns = [c.strip() for c in df.columns]
    return df

st.title("📌 Registro + Resultados")

if st.button("🔄 Recargar datos"):
    st.cache_data.clear()

# Cargar
registro = load_csv(SHEET_ID, REGISTRO_GID)
resultados = load_csv(SHEET_ID, RESULTADOS_GID)

# Validaciones
for name, df in [("registro", registro), ("resultados", resultados)]:
    if ID_COL not in df.columns:
        st.error(f"En '{name}' falta la columna '{ID_COL}'. Columnas detectadas: {list(df.columns)}")
        st.stop()

# Merge por id_publica
merged = registro.merge(resultados, on=ID_COL, how="left", suffixes=("_reg", "_res"))

# UI: buscar / abrir
st.subheader("Buscar")
q = st.text_input("Buscar por ID o texto", "")

filtered = merged.copy()
if q.strip():
    q_low = q.strip().lower()
    mask = filtered.astype(str).apply(lambda col: col.str.lower().str.contains(q_low, na=False))
    filtered = filtered[mask.any(axis=1)]

ids = sorted(filtered[ID_COL].astype(str).dropna().unique().tolist())
picked = st.selectbox("Abrir ficha por ID", [""] + ids)

case = st.query_params.get("case")
if case and not picked:
    picked = case

if picked:
    st.query_params["case"] = picked
    st.subheader("🧾 Ficha del paciente")
    st.code(picked, language="text")

    row = merged[merged[ID_COL].astype(str) == str(picked)]
    if row.empty:
        st.warning("No encontré ese ID.")
        st.stop()

    r = row.iloc[0].to_dict()

    # --- Sección Registro (inputs) ---
    st.markdown("### Registro (captura)")
    # Ajusta estos nombres a tus headers reales
    st.write("Fecha publicación:", r.get("fecha_publicacion", ""))
    st.write("Consentimiento:", r.get("consentimiento", ""))
    st.write("Edad paciente:", r.get("edad_paciente", ""))
    st.write("Fecha/hora evaluación:", r.get("fecha_hora_evaluacion", ""))
    st.write("Síntomas:", r.get("sintomas_visuales", ""))

    st.divider()

    # --- Sección Resultados (outputs) ---
    st.markdown("### Resultados (motor Python)")
    st.write("Patrón detectado:", r.get("patron_detectado", ""))
    st.write("Criterio aplicado:", r.get("criterio_aplicado", ""))
    st.write("Justificación:", r.get("justificacion", ""))
    st.write("Riesgo visual:", r.get("riesgo_visual", ""))

    # Debug opcional (puedes quitarlo cuando ya esté bonito)
    with st.expander("Ver todo el registro (debug)"):
        st.json(r)

else:
    st.subheader("Tabla (filtrada)")
    st.dataframe(filtered, use_container_width=True)
    
#EXTRA
import pandas as pd
import streamlit as st
st.set_page_config(page_title="Funcion_Binocular", layout="wide")

SHEET_ID = st.secrets["1P79M3wDddVua_rzt4chvRa4I7sfgPJHmh1G3M37i8ww"]
REGISTRO_GID = st.secrets["/edit?gid=1677150373#gid=1677150373"]
RESULTADOS_GID = st.secrets.get("/edit?gid=1739885561#gid=1739885561", "")  # opcional
ID_COL = "id_publica"
#HELPERS
@st.cache_data(ttl=60)
def load_csv(sheet_id: str, gid: str) -> pd.DataFrame:
    url = f"https://docs.google.com/spreadsheets/d/1P79M3wDddVua_rzt4chvRa4I7sfgPJHmh1G3M37i8ww/export?format=csv&gid=/edit?gid=1677150373#gid=1677150373"
    df = pd.read_csv(url)
    df.columns = [c.strip() for c in df.columns]
    return df
#BUSQUEDA
st.title("📌 Registro + Resultados")

colA, colB = st.columns([1, 2])
with colA:
    if st.button("🔄 Recargar datos"):
        st.cache_data.clear()
with colB:
    st.caption("Usa búsqueda o abre una ficha por ID.")
registro = load_csv(SHEET_ID, REGISTRO_GID)

# Si todavía no tienes resultados, comenta esto o déjalo opcional
resultados = None
if RESULTADOS_GID:
    resultados = load_csv(SHEET_ID, RESULTADOS_GID)
if ID_COL not in registro.columns:
    st.error(f"Falta la columna '{ID_COL}' en registro. Columnas: {list(registro.columns)}")
    st.stop()
merged = registro
if resultados is not None:
    if ID_COL not in resultados.columns:
        st.error(f"Falta '{ID_COL}' en resultados.")
        st.stop()
    merged = registro.merge(resultados, on=ID_COL, how="left", suffixes=("_reg", "_res"))
    #BUSQUEDA BUSCAR
st.subheader("Buscar")
q = st.text_input("Buscar por ID o texto", "")

filtered = merged.copy()
if q.strip():
    q_low = q.strip().lower()
    mask = filtered.astype(str).apply(lambda col: col.str.lower().str.contains(q_low, na=False))
    filtered = filtered[mask.any(axis=1)]

ids = sorted(filtered[ID_COL].astype(str).dropna().unique().tolist())
picked = st.selectbox("Abrir ficha por ID", [""] + ids)
#CASE
case = st.query_params.get("case")
if case and not picked:
    picked = case

if picked:
    st.query_params["case"] = picked
    st.subheader("🧾 Ficha del paciente")
    st.code(picked, language="text")

    row = merged[merged[ID_COL].astype(str) == str(picked)]
    if row.empty:
        st.warning("No encontré ese ID.")
        st.stop()

    r = row.iloc[0].to_dict()

    st.markdown("### Registro (captura)")
    st.write("Fecha publicación:", r.get("fecha_publicacion", ""))
    st.write("Edad:", r.get("edad_paciente", ""))
    st.write("Síntomas:", r.get("sintomas_visuales", ""))

    st.divider()
    st.markdown("### Resultados (si existen)")
    st.write("Patrón detectado:", r.get("patron_detectado", ""))
    st.write("Criterio aplicado:", r.get("criterio_aplicado", ""))

    with st.expander("Debug"):
        st.json(r)

else:
    st.subheader("Tabla de registros")
    st.dataframe(filtered, use_container_width=True)

