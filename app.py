import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="STOCK VITALCER ROCA", layout="wide")
st.title("🌿 STOCK VITALCER ROCA")

# Intentar conexión
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error en la conexión. Revisá los Secrets: {e}")

def cargar_datos(hoja):
    try:
        return conn.read(worksheet=hoja, ttl=0).dropna(how="all")
    except:
        if hoja == "Productos":
            return pd.DataFrame(columns=['Producto', 'Cantidad', 'Medida', 'Costo', 'Precio_Venta'])
        return pd.DataFrame(columns=['Fecha', 'Producto', 'Operación', 'Cantidad', 'Medida'])

df_stock = cargar_datos("Productos")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Stock Actual", "🔄 Movimientos", "📜 Historial", "🛠️ Catálogo"])

with tab1:
    if not df_stock.empty:
        df_mostrar = df_stock.copy()
        df_mostrar['Cantidad'] = pd.to_numeric(df_mostrar['Cantidad'], errors='coerce').fillna(0)
        df_mostrar['Costo'] = pd.to_numeric(df_mostrar['Costo'], errors='coerce').fillna(0)
        df_mostrar['Total_Costo ($)'] = df_mostrar['Cantidad'] * df_mostrar['Costo']
        st.dataframe(df_mostrar, use_container_width=True)
        st.metric("CAPITAL TOTAL", f"${df_mostrar['Total_Costo ($)'].sum():,.2f}")
    else:
        st.info("Planilla vacía o no conectada.")

with tab4:
    st.subheader("Agregar Producto")
    with st.form("nuevo"):
        n = st.text_input("Nombre")
        m = st.selectbox("Medida", ["Kgs", "Unidades"])
        c = st.number_input("Costo")
        v = st.number_input("Venta")
        if st.form_submit_button("Guardar"):
            nueva = pd.DataFrame([{"Producto": n, "Cantidad": 0.0, "Medida": m, "Costo": c, "Precio_Venta": v}])
            df_final = pd.concat([df_stock, nueva], ignore_index=True)
            conn.update(worksheet="Productos", data=df_final)
            st.success("¡Guardado! Refrescando...")
            st.rerun()
