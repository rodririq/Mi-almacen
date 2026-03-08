import streamlit as st
import pandas as pd

st.set_page_config(page_title="Almacén Saludable Pro", layout="wide")
st.title("🌿 Gestión de Almacén Saludable")

# 1. Inicialización de la base de datos en la sesión
if 'df_stock' not in st.session_state:
    data = {
        'Producto': ['Nueces Mariposa', 'Harina de Almendras', 'Chía', 'Aceite de Coco'],
        'Cantidad': [15.0, 3.0, 20.0, 8.0],
        'Medida': ['Kgs', 'Kgs', 'Kgs', 'Unidades'],
        'Costo': [0.0, 0.0, 0.0, 0.0],
        'Precio_Venta': [0.0, 0.0, 0.0, 0.0]
    }
    st.session_state.df_stock = pd.DataFrame(data)

# --- Pestañas para organizar la App ---
tab1, tab2, tab3 = st.tabs(["📊 Inventario", "🔄 Movimientos", "⚙️ Configuración Productos"])

with tab1:
    st.subheader("Estado Actual del Stock")
    # Mostramos la tabla. Usamos format para que los kilos tengan decimales y unidades no.
    st.dataframe(st.session_state.df_stock, use_container_width=True)
    
    total_valor_stock = (st.session_state.df_stock['Cantidad'] * st.session_state.df_stock['Costo']).sum()
    st.metric("Inversión Total en Stock", f"${total_valor_stock:,.2f}")

with tab2:
    st.subheader("Registrar Venta o Ingreso")
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        prod_sel = st.selectbox("Seleccioná Producto:", st.session_state.df_stock['Producto'])
        # Buscamos la medida del producto seleccionado
        medida_sel = st.session_state.df_stock.loc[st.session_state.df_stock['Producto'] == prod_sel, 'Medida'].values[0]
    
    with col_b:
        paso = 0.1 if medida_sel == 'Kgs' else 1.0
        cant_mov = st.number_input(f"Cantidad ({medida_sel}):", min_value=0.0, step=paso)
    
    with col_c:
        tipo_mov = st.radio("Acción:", ["Venta (-)", "Compra (+)"])

    if st.button("Confirmar Movimiento"):
        idx = st.session_state.df_stock.index[st.session_state.df_stock['Producto'] == prod_sel][0]
        if tipo_mov == "Venta (-)":
            st.session_state.df_stock.at[idx, 'Cantidad'] -= cant_mov
        else:
            st.session_state.df_stock.at[idx, 'Cantidad'] += cant_mov
        st.success("¡Stock actualizado!")
        st.rerun()

with tab3:
    st.subheader("Agregar Nuevo Producto")
    with st.container(border=True):
        n_nombre = st.text_input("Nombre del producto:")
        c1, c2, c3 = st.columns(3)
        with c1:
            n_medida = st.selectbox("Tipo de Medida:", ["Unidades", "Kgs"])
        with c2:
            n_costo = st.number_input("Costo inicial:", min_value=0.0)
        with c3:
            n_venta = st.number_input("Precio venta:", min_value=0.0)
        
        if st.button("➕ Añadir al Almacén"):
            if n_nombre:
                nuevo_item = {
                    'Producto': n_nombre, 'Cantidad': 0.0, 'Medida': n_medida,
                    'Costo': n_costo, 'Precio_Venta': n_venta
                }
                st.session_state.df_stock = pd.concat([st.session_state.df_stock, pd.DataFrame([nuevo_item])], ignore_index=True)
                st.success(f"{n_nombre} agregado.")
                st.rerun()

    st.divider()
    st.subheader("Eliminar Producto")
    prod_eliminar = st.selectbox("Seleccioná qué eliminar:", st.session_state.df_stock['Producto'], key="del")
    if st.button("🗑️ Borrar definitivamente", type="primary"):
        st.session_state.df_stock = st.session_state.df_stock[st.session_state.df_stock['Producto'] != prod_eliminar]
        st.warning(f"Se eliminó {prod_eliminar}")
        st.rerun()
