import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="STOCK VITALCER ROCA", layout="wide")
st.title("🌿 STOCK VITALCER ROCA")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para leer datos
def cargar_datos():
    productos = conn.read(worksheet="Productos", ttl=0)
    # Limpiar filas vacías que Google Sheets a veces agrega
    productos = productos.dropna(how="all")
    return productos

def cargar_historial():
    try:
        hist = conn.read(worksheet="Historial", ttl=0)
        return hist.dropna(how="all")
    except:
        return pd.DataFrame(columns=['Fecha', 'Producto', 'Operación', 'Cantidad', 'Medida'])

df_stock = cargar_datos()

# --- Pestañas ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Stock Actual", "🔄 Ventas/Ingresos", "📜 Historial", "🛠️ Catálogo"])

with tab1:
    st.subheader("Estado del Inventario")
    df_mostrar = df_stock.copy()
    df_mostrar['Total_Costo ($)'] = df_mostrar['Cantidad'] * df_mostrar['Costo']
    st.dataframe(df_mostrar, use_container_width=True)
    st.metric("CAPITAL TOTAL", f"${df_mostrar['Total_Costo ($)'].sum():,.2f}")

with tab2:
    st.subheader("Registrar Movimiento")
    with st.form("mov_form"):
        p_mov = st.selectbox("Producto:", df_stock['Producto'])
        tipo = st.radio("Operación:", ["Venta (-)", "Compra (+)"], horizontal=True)
        cant_mov = st.number_input("Cantidad:", min_value=0.0, step=0.1)
        
        if st.form_submit_button("Ejecutar"):
            idx = df_stock.index[df_stock['Producto'] == p_mov][0]
            # Actualizar stock
            nueva_cant = df_stock.at[idx, 'Cantidad'] - cant_mov if "Venta" in tipo else df_stock.at[idx, 'Cantidad'] + cant_mov
            df_stock.at[idx, 'Cantidad'] = nueva_cant
            
            # Guardar Producto
            conn.update(worksheet="Productos", data=df_stock)
            
            # Guardar Historial
            hist_actual = cargar_historial()
            nuevo_h = pd.DataFrame([{
                'Fecha': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'Producto': p_mov,
                'Operación': "Venta" if "Venta" in tipo else "Compra",
                'Cantidad': cant_mov,
                'Medida': df_stock.at[idx, 'Medida']
            }])
            hist_final = pd.concat([nuevo_h, hist_actual], ignore_index=True)
            conn.update(worksheet="Historial", data=hist_final)
            
            st.success("Sincronizado con Google Sheets")
            st.rerun()

with tab3:
    st.subheader("Historial de Actividad")
    st.dataframe(cargar_historial(), use_container_width=True)

with tab4:
    st.subheader("Gestión de Catálogo")
    # Aquí puedes agregar lógica para añadir filas nuevas al df_stock 
    # y usar conn.update(worksheet="Productos", data=df_stock)
    st.info("Para agregar productos nuevos masivamente, podés hacerlo directamente en el Excel de Google y refrescar esta app.")
