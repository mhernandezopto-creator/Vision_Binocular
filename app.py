import streamlit as st

st.set_page_config(page_title="Visión", layout="wide")

st.title("✅ Streamlit funcionando")
st.write("Si ves esto, el deploy va bien.")

SHEET_ID = "1P79M3wDddVua_rzt4chvRa4I7sfgPJHmh1G3M37i8ww"
REGISTRO_GID = "/edit?gid=1739885561#gid=1739885561"

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Registro", layout="wide")

SHEET_ID = st.secrets.get("SHEET_ID", "")
REGISTRO_GID = st.secrets.get("REGISTRO_GID", "")

def load_registro(sheet_id: str, gid: str) -> pd.DataFrame:
    if not sheet_id or not gid:
        raise ValueError("Faltan SHEET_ID o REGISTRO_GID en Secrets.")
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    return df

st.title("📋 Registro (público)")

try:
    df = load_registro(SHEET_ID, REGISTRO_GID)
except Exception as e:
    st.error(f"No pude cargar la hoja 'registro'. Detalle: {e}")
    st.stop()

# Normaliza headers (por si acaso)
df.columns = [c.strip() for c in df.columns]

# ⚠️ Ajusta este nombre EXACTO al header real en tu sheet
ID_COL = "id_publica"

if ID_COL not in df.columns:
    st.error(f"No encontré la columna '{ID_COL}'. Columnas detectadas: {list(df.columns)}")
    st.stop()

# --- UI: búsqueda + selector ---
st.subheader("Buscar")
q = st.text_input("Buscar por ID o por texto (ej. síntoma, valor, etc.)", "")

filtered = df.copy()
if q.strip():
    q_low = q.strip().lower()
    # filtra si aparece el texto en cualquier columna (como string)
    mask = filtered.astype(str).apply(lambda col: col.str.lower().str.contains(q_low, na=False))
    filtered = filtered[mask.any(axis=1)]

# Selector por ID
ids = filtered[ID_COL].astype(str).dropna().unique().tolist()
ids_sorted = sorted(ids)

picked = st.selectbox("Abrir ficha por ID", [""] + ids_sorted)

# --- Vista por URL param (?case=...) ---
case = st.query_params.get("case")
if case and not picked:
    picked = case

if picked:
    st.query_params["case"] = picked  # fija la URL para compartir
    st.subheader("🧾 Ficha del paciente")
    st.code(picked, language="text")

    row = df[df[ID_COL].astype(str) == str(picked)]
    if row.empty:
        st.warning("No encontré ese ID en registro.")
    else:
        r = row.iloc[0].to_dict()

        # Aquí eliges qué mostrar (ejemplos):
        # Ajusta nombres a tus headers reales
        st.write("Fecha de publicación:", r.get("fecha_publicacion", ""))
        st.write("Consentimiento:", r.get("consentimiento", ""))
        st.write("Edad paciente:", r.get("edad_paciente", ""))
        st.write("Fecha y hora de evaluación:", r.get("fecha_hora_evaluacion", ""))
        st.write("Síntomas visuales:", r.get("sintomas_visuales", ""))

        st.divider()
        st.subheader("Detalle completo (debug)")
        st.json(r)

else:
    st.subheader("Tabla de registros")
    st.caption("Tip: escribe algo arriba para filtrar; o selecciona un ID para abrir ficha.")
    st.dataframe(filtered, use_container_width=True)
