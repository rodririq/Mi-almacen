import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Gestión Almacén Saludable", layout="wide")
st.title("🌿 Control de Stock y Precios")

# 1. Base de datos con las nuevas columnas de Costo y Venta
if 'df_stock' not in st.session_state:
    data = {
        'Producto': ['Nueces Mariposa', 'Harina de Almendras', 'Chía x 1kg', 'Aceite de Coco'],
        'Cantidad': [15, 3, 20, 8],
        'Costo': [0.0, 0.0, 0.0, 0.0],
        'Precio_Venta': [0.0, 0.0, 0.0, 0.0],
        'Min_Critico': [5, 5, 10, 3]
    }
    st.session_state.df_stock = pd.DataFrame(data)

# 2. Resumen financiero rápido
total_invertido = (st.session_state.df_stock['Cantidad'] * st.session_state.df_stock['Costo']).sum()
st.metric("Total Invertido en Stock", f"${total_invertido:,.2f}")

# 3. Visualización del Inventario
st.subheader("Inventario Detallado")
def resaltar_bajo_stock(row):
    color = 'background-color: #ffcccc' if row.Cantidad <= row.Min_Critico else ''
    return [color] * len(row)

st.dataframe(st.session_state.df_stock.style.apply(resaltar_bajo_stock, axis=1), use_container_width=True)

# 4. Panel de Actualización
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 Movimiento de Stock")
    prod = st.selectbox("Producto:", st.session_state.df_stock['Producto'], key="prod_stock")
    cant = st.number_input("Cantidad:", min_value=1, step=1)
    tipo = st.radio("Operación:", ["Venta (-)", "Compra (+)"])
    
    if st.button("Actualizar Unidades"):
        idx = st.session_state.df_stock.index[st.session_state.df_stock['Producto'] == prod][0]
        if tipo == "Venta (-)":
            st.session_state.df_stock.at[idx, 'Cantidad'] -= cant
        else:
            st.session_state.df_stock.at[idx, 'Cantidad'] += cant
        st.rerun()

with col2:
    st.subheader("💰 Actualizar Precios")
    prod_p = st.selectbox("Producto:", st.session_state.df_stock['Producto'], key="prod_precios")
    nuevo_costo = st.number_input("Nuevo Costo ($):", min_value=0.0, format="%.2f")
    nueva_venta = st.number_input("Nuevo Precio Venta ($):", min_value=0.0, format="%.2f")
    
    if st.button("Guardar Precios"):
        idx = st.session_state.df_stock.index[st.session_state.df_stock['Producto'] == prod_p][0]
        st.session_state.df_stock.at[idx, 'Costo'] = nuevo_costo
        st.session_state.df_stock.at[idx, 'Precio_Venta'] = nueva_venta
        st.success(f"Precios actualizados para {prod_p}")
        st.rerun()
