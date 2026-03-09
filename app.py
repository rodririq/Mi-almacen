import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="STOCK VITALCER ROCA", layout="wide")
st.title("🌿 STOCK VITALCER ROCA")

# Conexión con Google Sheets
# Asegurate de que en Secrets el link esté bajo [connections.gsheets]
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIONES DE CARGA ---
def cargar_datos():
    try:
        # Leemos la pestaña 'Productos'
        df = conn.read(worksheet="Productos", ttl=0)
        return df.dropna(how="all")
    except Exception as e:
        st.error(f"Error al leer la pestaña 'Productos'. Revisá que el nombre sea exacto. Error: {e}")
        return pd.DataFrame(columns=['Producto', 'Cantidad', 'Medida', 'Costo', 'Precio_Venta'])

def cargar_historial():
    try:
        df_h = conn.read(worksheet="Historial", ttl=0)
        return df_h.dropna(how="all")
    except:
        return pd.DataFrame(columns=['Fecha', 'Producto', 'Operación', 'Cantidad', 'Medida'])

# Carga inicial
def cargar_datos():
    try:
        # Intentamos leer la planilla usando la URL directamente por si los secrets fallan
        url = "https://docs.google.com/spreadsheets/d/1e6AEQsI-dwA7_ek_vusM6YcWJB6tBrXhhwW-ZXVT__k/edit#gid=0"
        df = conn.read(spreadsheet=url, worksheet="Productos", ttl=0)
        return df.dropna(how="all")
    except Exception as e:
        st.error(f"Fallo de conexión. Intentando modo alternativo... Error: {e}")
        # Retorno de emergencia para que la app no se rompa
        return pd.DataFrame(columns=['Producto', 'Cantidad', 'Medida', 'Costo', 'Precio_Venta'])

# --- INTERFAZ ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Stock Actual", "🔄 Ventas/Ingresos", "📜 Historial", "🛠️ Catálogo"])

with tab1:
    if not df_stock.empty:
        df_mostrar = df_stock.copy()
        # Aseguramos que los valores sean números para calcular
        df_mostrar['Cantidad'] = pd.to_numeric(df_mostrar['Cantidad'], errors='coerce').fillna(0)
        df_mostrar['Costo'] = pd.to_numeric(df_mostrar['Costo'], errors='coerce').fillna(0)
        df_mostrar['Total_Costo ($)'] = df_mostrar['Cantidad'] * df_mostrar['Costo']
        
        st.dataframe(df_mostrar, use_container_width=True)
        st.metric("CAPITAL TOTAL EN STOCK", f"${df_mostrar['Total_Costo ($)'].sum():,.2f}")
    else:
        st.warning("No hay datos en la planilla. Agregá productos en la pestaña Catálogo.")

with tab2:
    st.subheader("Registrar Movimiento")
    if not df_stock.empty:
        with st.form("mov_form"):
            p_mov = st.selectbox("Producto:", df_stock['Producto'])
            tipo = st.radio("Operación:", ["Venta (-)", "Compra (+)"], horizontal=True)
            cant_mov = st.number_input("Cantidad:", min_value=0.0, step=0.1)
            
            if st.form_submit_button("Ejecutar y Sincronizar"):
                idx = df_stock.index[df_stock['Producto'] == p_mov][0]
                # Lógica de cálculo
                nueva_cant = df_stock.at[idx, 'Cantidad'] - cant_mov if "Venta" in tipo else df_stock.at[idx, 'Cantidad'] + cant_mov
                df_stock.at[idx, 'Cantidad'] = nueva_cant
                
                # Actualizar Google Sheets
                conn.update(worksheet="Productos", data=df_stock)
                
                # Registrar Historial
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
                
                st.success("¡Datos guardados en la nube!")
                st.rerun()

with tab3:
    st.subheader("Historial de Actividad")
    st.dataframe(cargar_historial(), use_container_width=True)

with tab4:
    st.subheader("Administrar Productos")
    # Formulario para agregar producto nuevo
    with st.expander("➕ Agregar Nuevo Producto"):
        with st.form("nuevo_p"):
            n_nom = st.text_input("Nombre")
            c1, c2 = st.columns(2)
            with c1: n_med = st.selectbox("Medida", ["Kgs", "Unidades"])
            with c2: n_cos = st.number_input("Costo", min_value=0.0)
            n_ven = st.number_input("Precio Venta", min_value=0.0)
            
            if st.form_submit_button("Guardar en Catálogo"):
                nueva_fila = pd.DataFrame([{"Producto": n_nom, "Cantidad": 0.0, "Medida": n_med, "Costo": n_cos, "Precio_Venta": n_ven}])
                df_nuevo = pd.concat([df_stock, nueva_fila], ignore_index=True)
                conn.update(worksheet="Productos", data=df_nuevo)
                st.success("Producto creado.")
                st.rerun()
