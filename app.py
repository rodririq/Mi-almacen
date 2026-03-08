import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Almacén Saludable Pro", layout="wide")
st.title("🌿 Gestión de Almacén Saludable")

# 1. Inicialización de la base de datos de productos
if 'df_stock' not in st.session_state:
    data = {
        'Producto': ['Nueces Mariposa', 'Harina de Almendras', 'Chía', 'Aceite de Coco'],
        'Cantidad': [15.0, 3.0, 20.0, 8.0],
        'Medida': ['Kgs', 'Kgs', 'Kgs', 'Unidades'],
        'Costo': [1200.0, 4500.0, 800.0, 3200.0],
        'Precio_Venta': [1800.0, 6500.0, 1500.0, 4800.0]
    }
    st.session_state.df_stock = pd.DataFrame(data)

# 2. Inicialización del Historial de Movimientos
if 'historial' not in st.session_state:
    st.session_state.historial = pd.DataFrame(columns=['Fecha', 'Producto', 'Tipo', 'Cantidad', 'Medida'])

# --- Pestañas de la App ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Stock Actual", "🔄 Ventas/Ingresos", "📜 Historial", "🛠️ Catálogo"])

# --- TAB 1: STOCK ACTUAL CON TOTALES ---
with tab1:
    st.subheader("Estado del Almacén")
    
    # Creamos una copia para mostrar cálculos sin afectar la base original
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
    st.metric("VALOR TOTAL DEL STOCK (Costo)", f"${total_general:,.2f}")

# --- TAB 2: REGISTRAR MOVIMIENTO ---
with tab2:
    st.subheader("Registrar Movimiento")
    with st.container(border=True):
        p_mov = st.selectbox("Producto:", st.session_state.df_stock['Producto'], key="mov_p")
        tipo = st.radio("Operación:", ["Venta (-)", "Compra (+)"], horizontal=True)
        cant_mov = st.number_input("Cantidad:", min_value=0.0, step=0.1)
        
        if st.button("Confirmar y Actualizar"):
            idx = st.session_state.df_stock.index[st.session_state.df_stock['Producto'] == p_mov][0]
            medida = st.session_state.df_stock.at[idx, 'Medida']
            
            # Actualizar Stock
            if tipo == "Venta (-)":
                st.session_state.df_stock.at[idx, 'Cantidad'] -= cant_mov
            else:
                st.session_state.df_stock.at[idx, 'Cantidad'] += cant_mov
            
            # Guardar en Historial
            nuevo_historial = {
                'Fecha': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'Producto': p_mov,
                'Tipo': "Venta" if tipo == "Venta (-)" else "Compra",
                'Cantidad': cant_mov,
                'Medida': medida
            }
            st.session_state.historial = pd.concat([pd.DataFrame([nuevo_historial]), st.session_state.historial], ignore_index=True)
            
            st.success(f"Movimiento registrado: {p_mov}")
            st.rerun()

# --- TAB 3: HISTORIAL DE MOVIMIENTOS ---
with tab3:
    st.subheader("Registro Histórico")
    if st.session_state.historial.empty:
        st.info("Todavía no hay movimientos registrados.")
    else:
        st.dataframe(st.session_state.historial, use_container_width=True)
        if st.button("Limpiar Historial"):
            st.session_state.historial = pd.DataFrame(columns=['Fecha', 'Producto', 'Tipo', 'Cantidad', 'Medida'])
            st.rerun()

# --- TAB 4: GESTIÓN DE CATÁLOGO ---
with tab4:
    st.subheader("Administrar Catálogo")
    accion = st.radio("Acción:", ["Agregar Nuevo", "Modificar Existente", "Eliminar"], horizontal=True)

    if accion == "Agregar Nuevo":
        with st.form("nuevo_form"):
            n_nom = st.text_input("Nombre del Producto")
            c1, c2, c3 = st.columns(3)
            with c1: n_med = st.selectbox("Medida", ["Kgs", "Unidades"])
            with c2: n_cos = st.number_input("Costo", min_value=0.0)
            with c3: n_ven = st.number_input("Venta", min_value=0.0)
            if st.form_submit_button("Guardar"):
                nuevo = {'Producto': n_nom, 'Cantidad': 0.0, 'Medida': n_med, 'Costo': n_cos, 'Precio_Venta': n_ven}
                st.session_state.df_stock = pd.concat([st.session_state.df_stock, pd.DataFrame([nuevo])], ignore_index=True)
                st.rerun()

    elif accion == "Modificar Existente":
        prod_a_editar = st.selectbox("Producto a editar:", st.session_state.df_stock['Producto'])
        idx_ed = st.session_state.df_stock.index[st.session_state.df_stock['Producto'] == prod_a_editar][0]
        with st.form("edit_form"):
            e_nom = st.text_input("Nombre", value=st.session_state.df_stock.at[idx_ed, 'Producto'])
            e_cos = st.number_input("Costo", value=float(st.session_state.df_stock.at[idx_ed, 'Costo']))
            e_ven = st.number_input("Venta", value=float(st.session_state.df_stock.at[idx_ed, 'Precio_Venta']))
            if st.form_submit_button("Actualizar"):
                st.session_state.df_stock.at[idx_ed, 'Producto'] = e_nom
                st.session_state.df_stock.at[idx_ed, 'Costo'] = e_cos
                st.session_state.df_stock.at[idx_ed, 'Precio_Venta'] = e_ven
                st.rerun()

    elif accion == "Eliminar":
        prod_del = st.selectbox("Producto a eliminar:", st.session_state.df_stock['Producto'])
        if st.button("Eliminar", type="primary"):
            st.session_state.df_stock = st.session_state.df_stock[st.session_state.df_stock['Producto'] != prod_del]
            st.rerun()
