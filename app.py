import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="STOCK VITALCER ROCA", layout="wide")
st.title("🌿 STOCK VITALCER ROCA")

# Intentamos establecer la conexión
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error de configuración de conexión: {e}")

# --- FUNCIONES DE CARGA ---
def cargar_datos():
    try:
        # Forzamos la lectura de la pestaña Productos
        df = conn.read(worksheet="Productos", ttl=0)
        return df.dropna(how="all")
    except Exception as e:
        # Si falla, devolvemos una tabla vacía con las columnas correctas
        st.error(f"No se pudo leer la planilla. Verificá el nombre de la pestaña 'Productos'.")
        return pd.DataFrame(columns=['Producto', 'Cantidad', 'Medida', 'Costo', 'Precio_Venta'])

def cargar_historial():
    try:
        df_h = conn.read(worksheet="Historial", ttl=0)
        return df_h.dropna(how="all")
    except:
        return pd.DataFrame(columns=['Fecha', 'Producto', 'Operación', 'Cantidad', 'Medida'])

# CARGA DE DATOS (Esto soluciona el NameError)
df_stock = cargar_datos()

# --- INTERFAZ ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Stock Actual", "🔄 Ventas/Ingresos", "📜 Historial", "🛠️ Catálogo"])

with tab1:
    if not df_stock.empty and 'Producto' in df_stock.columns:
        df_mostrar = df_stock.copy()
        # Convertimos a números por si acaso
        df_mostrar['Cantidad'] = pd.to_numeric(df_mostrar['Cantidad'], errors='coerce').fillna(0)
        df_mostrar['Costo'] = pd.to_numeric(df_mostrar['Costo'], errors='coerce').fillna(0)
        df_mostrar['Total_Costo ($)'] = df_mostrar['Cantidad'] * df_mostrar['Costo']
        
        st.dataframe(df_mostrar, use_container_width=True)
        st.metric("CAPITAL TOTAL", f"${df_mostrar['Total_Costo ($)'].sum():,.2f}")
    else:
        st.info("La tabla está vacía. Empezá agregando productos en la pestaña 'Catálogo'.")

with tab2:
    st.subheader("Registrar Movimiento")
    if not df_stock.empty:
        with st.form("mov_form"):
            p_mov = st.selectbox("Producto:", df_stock['Producto'])
            tipo = st.radio("Operación:", ["Venta (-)", "Compra (+)"], horizontal=True)
            cant_mov = st.number_input("Cantidad:", min_value=0.0, step=0.1)
            
            if st.form_submit_button("Sincronizar Movimiento"):
                idx = df_stock.index[df_stock['Producto'] == p_mov][0]
                nueva_cant = df_stock.at[idx, 'Cantidad'] - cant_mov if "Venta" in tipo else df_stock.at[idx, 'Cantidad'] + cant_mov
                df_stock.at[idx, 'Cantidad'] = nueva_cant
                
                # Guardar cambios
                conn.update(worksheet="Productos", data=df_stock)
                
                # Historial
                h_act = cargar_historial()
                nuevo_h = pd.DataFrame([{'Fecha': datetime.now().strftime("%d/%m/%Y %H:%M"), 'Producto': p_mov, 'Operación': tipo, 'Cantidad': cant_mov, 'Medida': df_stock.at[idx, 'Medida']}])
                conn.update(worksheet="Historial", data=pd.concat([nuevo_h, h_act], ignore_index=True))
                
                st.success("¡Planilla actualizada!")
                st.rerun()

with tab3:
    st.subheader("Historial")
    st.dataframe(cargar_historial(), use_container_width=True)

with tab4:
    st.subheader("Configuración")
    with st.form("nuevo_p"):
        n_nom = st.text_input("Nombre del Producto")
        c1, c2 = st.columns(2)
        with c1: n_med = st.selectbox("Medida", ["Kgs", "Unidades"])
        with c2: n_cos = st.number_input("Costo", min_value=0.0)
        n_ven = st.number_input("Venta", min_value=0.0)
        
        if st.form_submit_button("Agregar"):
            n_fila = pd.DataFrame([{"Producto": n_nom, "Cantidad": 0.0, "Medida": n_med, "Costo": n_cos, "Precio_Venta": n_ven}])
            df_nuevo = pd.concat([df_stock, n_fila], ignore_index=True)
            conn.update(worksheet="Productos", data=df_nuevo)
            st.rerun()
