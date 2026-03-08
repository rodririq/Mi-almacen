import streamlit as st
import pandas as pd

st.set_page_config(page_title="Almacén Saludable Pro", layout="wide")
st.title("🌿 Gestión de Almacén Saludable")

# 1. Inicialización de la base de datos (Memoria temporal)
if 'df_stock' not in st.session_state:
    data = {
        'Producto': ['Nueces Mariposa', 'Harina de Almendras', 'Chía', 'Aceite de Coco'],
        'Cantidad': [15.0, 3.0, 20.0, 8.0],
        'Medida': ['Kgs', 'Kgs', 'Kgs', 'Unidades'],
        'Costo': [1200.0, 4500.0, 800.0, 3200.0],
        'Precio_Venta': [1800.0, 6500.0, 1500.0, 4800.0]
    }
    st.session_state.df_stock = pd.DataFrame(data)

# --- Pestañas de la App ---
tab1, tab2, tab3 = st.tabs(["📊 Stock Actual", "🔄 Ventas/Ingresos", "🛠️ Catálogo de Productos"])

# --- TAB 1: INVENTARIO ---
with tab1:
    st.subheader("Estado del Almacén")
    # Formateamos la tabla para que se vea pro
    st.dataframe(st.session_state.df_stock.style.format({
        'Costo': '${:,.2f}',
        'Precio_Venta': '${:,.2f}',
        'Cantidad': '{:,.2f}'
    }), use_container_width=True)

# --- TAB 2: MOVIMIENTOS ---
with tab2:
    st.subheader("Registrar Movimiento")
    with st.container(border=True):
        p_mov = st.selectbox("Producto:", st.session_state.df_stock['Producto'], key="mov_p")
        tipo = st.radio("Operación:", ["Venta (-)", "Compra (+)"], horizontal=True)
        cant_mov = st.number_input("Cantidad:", min_value=0.0, step=0.1)
        
        if st.button("Confirmar y Actualizar"):
            idx = st.session_state.df_stock.index[st.session_state.df_stock['Producto'] == p_mov][0]
            if tipo == "Venta (-)":
                st.session_state.df_stock.at[idx, 'Cantidad'] -= cant_mov
            else:
                st.session_state.df_stock.at[idx, 'Cantidad'] += cant_mov
            st.success("Stock actualizado con éxito.")
            st.rerun()

# --- TAB 3: GESTIÓN COMPLETA (CRUD) ---
with tab3:
    st.subheader("Administrar Productos")
    
    accion = st.segmented_control("¿Qué querés hacer?", ["Agregar Nuevo", "Modificar Existente", "Eliminar"], default="Agregar Nuevo")

    # --- AGREGAR ---
    if accion == "Agregar Nuevo":
        with st.form("nuevo_form"):
            n_nom = st.text_input("Nombre del Producto")
            c1, c2, c3 = st.columns(3)
            with c1: n_med = st.selectbox("Medida", ["Kgs", "Unidades"])
            with c2: n_cos = st.number_input("Costo", min_value=0.0)
            with c3: n_ven = st.number_input("Venta", min_value=0.0)
            
            if st.form_submit_button("Guardar Producto"):
                nuevo = {'Producto': n_nom, 'Cantidad': 0.0, 'Medida': n_med, 'Costo': n_cos, 'Precio_Venta': n_ven}
                st.session_state.df_stock = pd.concat([st.session_state.df_stock, pd.DataFrame([nuevo])], ignore_index=True)
                st.success("Producto agregado al catálogo.")
                st.rerun()

    # --- MODIFICAR ---
    elif accion == "Modificar Existente":
        prod_a_editar = st.selectbox("Seleccioná el producto a editar:", st.session_state.df_stock['Producto'])
        idx_ed = st.session_state.df_stock.index[st.session_state.df_stock['Producto'] == prod_a_editar][0]
        
        with st.form("edit_form"):
            col1, col2 = st.columns(2)
            with col1:
                e_nom = st.text_input("Nombre", value=st.session_state.df_stock.at[idx_ed, 'Producto'])
                e_med = st.selectbox("Medida", ["Kgs", "Unidades"], index=0 if st.session_state.df_stock.at[idx_ed, 'Medida'] == 'Kgs' else 1)
            with col2:
                e_cos = st.number_input("
