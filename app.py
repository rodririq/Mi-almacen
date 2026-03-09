import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Configuración de la App
st.set_page_config(page_title="STOCK VITALCER ROCA", layout="wide")
st.title("🌿 STOCK VITALCER ROCA")

# 2. Conexión con Google Sheets
# Nota: La URL debe ser la que pusiste en los Secrets de Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos(hoja):
    try:
        # ttl=0 para que no use memoria vieja y traiga siempre lo último del Excel
        df = conn.read(worksheet=hoja, ttl=0)
        return df.dropna(how="all")
    except Exception:
        if hoja == "Productos":
            return pd.DataFrame(columns=['Producto', 'Cantidad', 'Medida', 'Costo', 'Precio_Venta'])
        else:
            return pd.DataFrame(columns=['Fecha', 'Producto', 'Operación', 'Cantidad', 'Medida'])

# Carga inicial de datos
df_stock = cargar_datos("Productos")

# --- Pestañas de Navegación ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Stock Actual", "🔄 Ventas/Ingresos", "📜 Historial", "🛠️ Catálogo"])

# --- TAB 1: STOCK ACTUAL ---
with tab1:
    if not df_stock.empty:
        df_mostrar = df_stock.copy()
        df_mostrar['Cantidad'] = pd.to_numeric(df_mostrar['Cantidad'], errors='coerce').fillna(0)
        df_mostrar['Costo'] = pd.to_numeric(df_mostrar['Costo'], errors='coerce').fillna(0)
        df_mostrar['Total_Costo ($)'] = df_mostrar['Cantidad'] * df_mostrar['Costo']
        
        st.dataframe(df_mostrar, use_container_width=True)
        
        total_inv = df_mostrar['Total_Costo ($)'].sum()
        st.divider()
        st.metric("CAPITAL TOTAL EN MERCADERÍA", f"${total_inv:,.2f}")
    else:
        st.info("No hay productos cargados. Andá a la pestaña 'Catálogo' para empezar.")

# --- TAB 2: VENTAS E INGRESOS ---
with tab2:
    st.subheader("Registrar Movimiento")
    if not df_stock.empty:
        with st.form("form_movimiento"):
            p_mov = st.selectbox("Elegí el Producto:", df_stock['Producto'])
            tipo = st.radio("¿Qué pasó?:", ["Venta (-)", "Compra (+)"], horizontal=True)
            cant_mov = st.number_input("Cantidad:", min_value=0.0, step=0.1)
            
            if st.form_submit_button("Actualizar y Guardar"):
                idx = df_stock.index[df_stock['Producto'] == p_mov][0]
                
                # Calcular nuevo stock
                if "Venta" in tipo:
                    df_stock.at[idx, 'Cantidad'] = float(df_stock.at[idx, 'Cantidad']) - cant_mov
                else:
                    df_stock.at[idx, 'Cantidad'] = float(df_stock.at[idx, 'Cantidad']) + cant_mov
                
                # Guardar en Google Sheets (Hoja Productos)
                conn.update(worksheet="Productos", data=df_stock)
                
                # Registrar en Historial
                df_h = cargar_datos("Historial")
                nuevo_h = pd.DataFrame([{
                    'Fecha': datetime.now().strftime("%d/%m/%Y %H:%M"),
                    'Producto': p_mov,
                    'Operación': "Venta" if "Venta" in tipo else "Compra",
                    'Cantidad': cant_mov,
                    'Medida': df_stock.at[idx, 'Medida']
                }])
                df_h_final = pd.concat([nuevo_h, df_h], ignore_index=True)
                conn.update(worksheet="Historial", data=df_h_final)
                
                st.success(f"Movimiento de {p_mov} guardado correctamente.")
                st.rerun()
    else:
        st.warning("Primero debés agregar productos en el Catálogo.")

# --- TAB 3: HISTORIAL ---
with tab3:
    st.subheader("Últimos Movimientos")
    historial_df = cargar_datos("Historial")
    if not historial_df.empty:
        st.dataframe(historial_df, use_container_width=True)
    else:
        st.info("Aún no hay movimientos registrados.")

# --- TAB 4: CATÁLOGO (Agregar/Eliminar) ---
with tab4:
    st.subheader("Administración de Productos")
    
    with st.expander("➕ Agregar Nuevo Producto"):
        with st.form("form_nuevo"):
            n_nom = st.text_input("Nombre del Producto")
            c1, c2, c3 = st.columns(3)
            with c1: n_med = st.selectbox("Medida", ["Kgs", "Unidades"])
            with c2: n_cos = st.number_input("Costo inicial", min_value=0.0)
            with c3: n_ven = st.number_input("Precio Venta", min_value=0.0)
            
            if st.form_submit_button("Guardar en Google Sheets"):
                if n_nom:
                    nueva_f = pd.DataFrame([{"Producto": n_nom, "Cantidad": 0.0, "Medida": n_med, "Costo": n_cos, "Precio_Venta": n_ven}])
                    df_stock_n = pd.concat([df_stock, nueva_f], ignore_index=True)
                    conn.update(worksheet="Productos", data=df_stock_n)
                    st.success("Producto creado exitosamente.")
                    st.rerun()

    if not df_stock.empty:
        with st.expander("🗑️ Eliminar Producto"):
            p_del = st.selectbox("Seleccioná producto a borrar:", df_stock['Producto'])
            if st.button("Eliminar Permanentemente", type="primary"):
                df_stock_d = df_stock[df_stock['Producto'] != p_del]
                conn.update(worksheet="Productos", data=df_stock_d)
                st.warning(f"Se eliminó {p_del}")
                st.rerun()
