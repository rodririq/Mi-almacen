import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuración de la página con el nombre de tu local
st.set_page_config(page_title="STOCK VITALCER ROCA", layout="wide")
st.title("🌿 STOCK VITALCER ROCA")

# 2. Inicialización de la base de datos de productos (si no existe)
if 'df_stock' not in st.session_state:
    data = {
        'Producto': ['Nueces Mariposa', 'Harina de Almendras', 'Chía', 'Aceite de Coco'],
        'Cantidad': [15.0, 3.0, 20.0, 8.0],
        'Medida': ['Kgs', 'Kgs', 'Kgs', 'Unidades'],
        'Costo': [1200.0, 4500.0, 800.0, 3200.0],
        'Precio_Venta': [1800.0, 6500.0, 1500.0, 4800.0]
    }
    st.session_state.df_stock = pd.DataFrame(data)

# 3. Inicialización del Historial de Movimientos (si no existe)
if 'historial_datos' not in st.session_state:
    st.session_state.historial_datos = []

# --- Pestañas de la App ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Stock Actual", "🔄 Ventas/Ingresos", "📜 Historial Movimientos", "🛠️ Catálogo"])

# --- TAB 1: STOCK ACTUAL ---
with tab1:
    st.subheader("Estado del Inventario")
    df_mostrar = st.session_state.df_stock.copy()
    df_mostrar['Total_Costo ($)'] = df_mostrar['Cantidad'] * df_mostrar['Costo']
    
    st.dataframe(df_mostrar.style.format({
        'Costo': '${:,.2f}',
        'Precio_Venta': '${:,.2f}',
        'Cantidad': '{:,.2f}',
        'Total_Costo ($)': '${:,.2f}'
    }), use_container_width=True)
    
    total_general = df_mostrar['Total_Costo ($)'].sum()
    st.divider()
    st.metric("CAPITAL TOTAL EN STOCK", f"${total_general:,.2f}")

# --- TAB 2: REGISTRAR MOVIMIENTO (VENTA O COMPRA) ---
with tab2:
    st.subheader("Registrar Movimiento")
    with st.container(border=True):
        p_mov = st.selectbox("Seleccioná el Producto:", st.session_state.df_stock['Producto'], key="sel_prod_mov")
        tipo = st.radio("Tipo de Operación:", ["Venta (-)", "Compra (+)"], horizontal=True)
        cant_mov = st.number_input("Cantidad a mover:", min_value=0.0, step=0.1)
        
        if st.button("Ejecutar Movimiento"):
            if cant_mov > 0:
                idx = st.session_state.df_stock.index[st.session_state.df_stock['Producto'] == p_mov][0]
                
                # Actualizar el stock
                if tipo == "Venta (-)":
                    st.session_state.df_stock.at[idx, 'Cantidad'] -= cant_mov
                else:
                    st.session_state.df_stock.at[idx, 'Cantidad'] += cant_mov
                
                # CREAR REGISTRO PARA EL HISTORIAL
                nuevo_registro = {
                    'Fecha': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    'Producto': p_mov,
                    'Operación': "Venta" if "Venta" in tipo else "Compra",
                    'Cantidad': cant_mov,
                    'Medida': st.session_state.df_stock.at[idx, 'Medida']
                }
                
                # Insertar al principio de la lista
                st.session_state.historial_datos.insert(0, nuevo_registro)
                
                st.success(f"¡Éxito! Se registró la {tipo} de {cant_mov} en {p_mov}")
                st.rerun()
            else:
                st.warning("La cantidad debe ser mayor a 0.")

# --- TAB 3: HISTORIAL DE MOVIMIENTOS ---
with tab3:
    st.subheader("Historial de Actividad")
    if len(st.session_state.historial_datos) == 0:
        st.info("Aún no se han realizado ventas o compras en esta sesión.")
    else:
        # Convertimos la lista de registros a un DataFrame para mostrarlo
        df_hist = pd.DataFrame(st.session_state.historial_datos)
        st.table(df_hist) # Usamos table para asegurar que se vea bien en móvil
        
        if st.button("Borrar Historial"):
            st.session_state.historial_datos = []
            st.rerun()

# --- TAB 4: GESTIÓN DE CATÁLOGO ---
with tab4:
    st.subheader("Administración de Productos")
    accion = st.radio("Acción:", ["Agregar", "Modificar", "Eliminar"], horizontal=True)

    if accion == "Agregar":
        with st.form("add_form"):
            n_nom = st.text_input("Nombre")
            n_med = st.selectbox("Medida", ["Kgs", "Unidades"])
            n_cos = st.number_input("Costo", min_value=0.0)
            n_ven = st.number_input("Venta", min_value=0.0)
            if st.form_submit_button("Añadir Producto"):
                nuevo = {'Producto': n_nom, 'Cantidad': 0.0, 'Medida': n_med, 'Costo': n_cos, 'Precio_Venta': n_ven}
                st.session_state.df_stock = pd.concat([st.session_state.df_stock, pd.DataFrame([nuevo])], ignore_index=True)
                st.rerun()

    elif accion == "Modificar":
        prod_ed = st.selectbox("Producto:", st.session_state.df_stock['Producto'])
        idx_e = st.session_state.df_stock.index[st.session_state.df_stock['Producto'] == prod_ed][0]
        with st.form("edit_form"):
            e_nom = st.text_input("Nuevo Nombre", value=st.session_state.df_stock.at[idx_e, 'Producto'])
            e_cos = st.number_input("Nuevo Costo", value=float(st.session_state.df_stock.at[idx_e, 'Costo']))
            e_ven = st.number_input("Nueva Venta", value=float(st.session_state.df_stock.at[idx_e, 'Precio_Venta']))
            if st.form_submit_button("Actualizar Datos"):
                st.session_state.df_stock.at[idx_e, 'Producto'] = e_nom
                st.session_state.df_stock.at[idx_e, 'Costo'] = e_cos
                st.session_state.df_stock.at[idx_e, 'Precio_Venta'] = e_ven
                st.rerun()

    elif accion == "Eliminar":
        prod_del = st.selectbox("Eliminar:", st.session_state.df_stock['Producto'])
        if st.button("Eliminar permanentemente", type="primary"):
            st.session_state.df_stock = st.session_state.df_stock[st.session_state.df_stock['Producto'] != prod_del]
            st.rerun()
