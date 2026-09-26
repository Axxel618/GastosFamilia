import streamlit as st
import requests
import pandas as pd

# Tu URL de producción en Render
API_URL = "https://gastosfamilia-c5ji.onrender.com"

st.set_page_config(page_title="Control de Gastos Familiares", page_icon="💰", layout="wide")
st.title("💰 Control de Gastos Familiares")

def obtener_datos(endpoint, clave):
    try:
        respuesta = requests.get(f"{API_URL}/{endpoint}")
        if respuesta.status_code == 200:
            return respuesta.json().get(clave, [])
    except Exception:
        pass
    return []

lista_familiares = obtener_datos("familiar/", "familiares")
lista_tematicas = obtener_datos("tematicas/", "tematicas")

tab_mov, tab_familiar, tab_tematica, tab_stats = st.tabs([
    "💸 Registrar Movimiento", 
    "👤 Añadir Familiar", 
    "🏷️ Añadir Temática", 
    "📈 Estadísticas"
])

# ==========================================
# PESTAÑA 1: REGISTRAR MOVIMIENTO (Gasto / Ingreso)
# ==========================================
with tab_mov:
    st.write("Introduce los detalles del nuevo movimiento (Gasto o Ingreso).")
    
    if not lista_familiares or not lista_tematicas:
        st.warning("⚠️ Faltan familiares o temáticas. Añádelos en las siguientes pestañas.")
    
    with st.form("formulario_movimiento"):
        tipo_movimiento = st.radio("Tipo de movimiento:", ["Gasto 💸", "Ingreso 💰"], horizontal=True)
        
        col1, col2 = st.columns(2)
        with col1:
            persona = st.selectbox("¿Quién hizo el movimiento?", options=lista_familiares if lista_familiares else ["Esperando..."])
        with col2:
            tematica = st.selectbox("Temática", options=lista_tematicas if lista_tematicas else ["Esperando..."])
            
        dinero = st.number_input("Cantidad (€)", min_value=0.01, step=0.5, format="%.2f")
        # NUEVO CAMPO AÑADIDO
        comentario = st.text_input("Comentario (Opcional)", placeholder="Ej: Regalo de cumple, supermercado extra...")
        
        enviado = st.form_submit_button("💾 Guardar Movimiento")

    if enviado:
        if not lista_familiares or not lista_tematicas:
            st.error("❌ Registra primero al menos un familiar y una temática.")
        else:
            dinero_final = dinero if "Gasto" in tipo_movimiento else -dinero
            
            datos_mov = {
                "persona": persona,
                "tema_tematica": tematica,
                "dinero_gastado": dinero_final,
                # SE ENVÍA EL COMENTARIO O NULL
                "comentario": comentario if comentario.strip() != "" else None 
            }
            try:
                respuesta = requests.post(f"{API_URL}/gasto/", json=datos_mov)
                if respuesta.status_code == 200:
                    st.success(f"✅ ¡{tipo_movimiento.split()[0]} registrado correctamente!")
                else:
                    st.error(f"❌ Error del servidor: {respuesta.text}")
            except Exception:
                st.error("⚠️ No se ha podido conectar con el backend.")

# ==========================================
# PESTAÑA 2: AÑADIR FAMILIAR
# ==========================================
with tab_familiar:
    st.write("Registra a un nuevo miembro de la familia.")
    with st.form("formulario_familiar"):
        nuevo_familiar = st.text_input("Nombre del familiar")
        btn_familiar = st.form_submit_button("➕ Añadir Familiar")
        
    if btn_familiar:
        if nuevo_familiar.strip() == "":
            st.warning("⚠️ El nombre no puede estar vacío.")
        else:
            try:
                res = requests.post(f"{API_URL}/familiar/", json={"nombre": nuevo_familiar.strip()})
                if res.status_code == 200:
                    st.success(f"✅ ¡{nuevo_familiar.strip()} añadido! Recarga la página.")
                else:
                    st.error(f"⚠️ {res.json().get('detail', 'El familiar ya existe')}")
            except Exception as e:
                st.error(f"⚠️ Sin conexión al backend: {e}")

# ==========================================
# PESTAÑA 3: AÑADIR TEMÁTICA
# ==========================================
with tab_tematica:
    st.write("Crea categorías para clasificar (ej. Nómina, Supermercado, Luz...).")
    with st.form("formulario_tematica"):
        nueva_tematica = st.text_input("Nombre de la temática")
        btn_tematica = st.form_submit_button("➕ Añadir Temática")
        
    if btn_tematica:
        if nueva_tematica.strip() == "":
            st.warning("⚠️ La temática no puede estar vacía.")
        else:
            try:
                res = requests.post(f"{API_URL}/tematica/", json={"nombre": nueva_tematica.strip()})
                if res.status_code == 200:
                    st.success(f"✅ ¡Temática añadida! Recarga la página.")
                else:
                    st.error(f"⚠️ {res.json().get('detail', 'La temática ya existe')}")
            except Exception as e:
                st.error(f"⚠️ Sin conexión al backend: {e}")

# ==========================================
# PESTAÑA 4: ESTADÍSTICAS
# ==========================================
with tab_stats:
    st.header("📊 Panel de Estadísticas y Balance")
    
    try:
        respuesta_gastos = requests.get(f"{API_URL}/gastos/")
        
        if respuesta_gastos.status_code == 200:
            df = pd.DataFrame(respuesta_gastos.json())
        else:
            df = pd.DataFrame()
            
        if df.empty:
            st.info("Aún no hay movimientos registrados.")
        else:
            # Separar Ingresos y Gastos
            df['tipo'] = df['dinero_gastado'].apply(lambda x: 'Gasto' if x > 0 else 'Ingreso')
            df['cantidad_real'] = df['dinero_gastado'].abs() # Valor absoluto para mostrar
            
            total_gastos = df[df['tipo'] == 'Gasto']['cantidad_real'].sum()
            total_ingresos = df[df['tipo'] == 'Ingreso']['cantidad_real'].sum()
            balance = total_ingresos - total_gastos
            
            # 1. Tarjetas de métricas superiores
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Ingresos Totales", f"{total_ingresos:.2f} €")
            col2.metric("💸 Gastos Totales", f"{total_gastos:.2f} €")
            
            # El delta color mostrará verde si el balance es positivo, rojo si es negativo
            col3.metric("⚖️ Balance Final", f"{balance:.2f} €", delta=f"{balance:.2f} €")
            
            st.divider()
            
            # 2. Gráficos interactivos
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                st.subheader("👤 Movimientos por Familiar")
                # Agrupa por persona y separa las barras en Gasto e Ingreso
                mov_persona = df.groupby(['persona', 'tipo'])['cantidad_real'].sum().unstack().fillna(0)
                st.bar_chart(mov_persona)
                
            with col_graf2:
                st.subheader("🏷️ Movimientos por Temática")
                mov_tematica = df.groupby(['tema_tematica', 'tipo'])['cantidad_real'].sum().unstack().fillna(0)
                st.bar_chart(mov_tematica)
                
            st.divider()
            
            # 3. Historial detallado de la base de datos
            st.subheader("📝 Historial detallado")
            df_mostrar = df[['fecha', 'persona', 'tema_tematica', 'tipo', 'cantidad_real', 'comentario']].sort_values(by="fecha", ascending=False)
            st.dataframe(df_mostrar, use_container_width=True)
            
    except Exception as e:
        st.error(f"⚠️ Error al cargar las estadísticas.")