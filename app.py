import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="STOCK VITALCER ROCA", layout="wide")
st.title("🌿 STOCK VITALCER ROCA")

# Conexión usando la llave JSON de los Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos(hoja):
    try:
        return conn.read(worksheet=hoja, ttl=0).dropna(how="all")
    except:
        if hoja == "Productos":
            return pd.DataFrame(columns=['Producto', 'Cantidad', 'Medida', 'Costo', 'Precio_Venta'])
        return pd.DataFrame(columns=['Fecha', 'Producto', 'Operación', 'Cantidad', 'Medida'])

df_stock = cargar_datos("Productos")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Stock Actual", "🔄 Ventas/Ingresos", "📜 Historial", "🛠️ Catálogo"])

with tab1:
    if not df_stock.empty:
        df_mostrar = df_stock.copy()
        for col in ['Cantidad', 'Costo']: 
            df_mostrar[col] = pd.to_numeric(df_mostrar[col], errors='coerce').fillna(0)
        df_mostrar['Total_Costo ($)'] = df_mostrar['Cantidad'] * df_mostrar['Costo']
        st.dataframe(df_mostrar, use_container_width=True)
        st.metric("CAPITAL TOTAL", f"${df_mostrar['Total_Costo ($)'].sum():,.2f}")
    else:
        st.info("Planilla vacía. Cargá productos en 'Catálogo'.")

with tab2:
    if not df_stock.empty:
        with st.form("mov"):
            p = st.selectbox("Producto", df_stock['Producto'])
            t = st.radio("Tipo", ["Venta (-)", "Compra (+)"], horizontal=True)
            c = st.number_input("Cantidad", min_value=0.0, step=0.1)
            if st.form_submit_button("Registrar"):
                idx = df_stock.index[df_stock['Producto'] == p][0]
                df_stock.at[idx, 'Cantidad'] = float(df_stock.at[idx, 'Cantidad']) + (c if "Compra" in t else -c)
                conn.update(worksheet="Productos", data=df_stock)
                
                df_h = cargar_datos("Historial")
                nuevo_h = pd.DataFrame([{'Fecha': datetime.now().strftime("%d/%m/%Y %H:%M"), 'Producto': p, 'Operación': t, 'Cantidad': c, 'Medida': df_stock.at[idx, 'Medida']}])
                conn.update(worksheet="Historial", data=pd.concat([nuevo_h, df_h], ignore_index=True))
                st.success("Sincronizado!")
                st.rerun()

with tab3:
    st.dataframe(cargar_datos("Historial"), use_container_width=True)

with tab4:
    with st.form("nuevo"):
        n = st.text_input("Nombre")
        col1, col2 = st.columns(2)
        with col1: m = st.selectbox("Medida", ["Kgs", "Unidades"])
        with col2: co = st.number_input("Costo")
        ve = st.number_input("Venta")
        if st.form_submit_button("Agregar Producto"):
            nueva = pd.DataFrame([{"Producto": n, "Cantidad": 0.0, "Medida": m, "Costo": co, "Precio_Venta": ve}])
            conn.update(worksheet="Productos", data=pd.concat([df_stock, nueva], ignore_index=True))
            st.rerun()
