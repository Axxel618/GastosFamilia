import streamlit as st
import requests
import pandas as pd

API_URL = "https://gastosfamilia-c5ji.onrender.com"

st.set_page_config(page_title="Control de Gastos Familiares", page_icon="💰")
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

tab_gasto, tab_familiar, tab_tematica, tab_stats = st.tabs([
    "💸 Registrar Gasto", 
    "👤 Añadir Familiar", 
    "🏷️ Añadir Temática", 
    "📈 Estadísticas"
])

# ==========================================
# PESTAÑA 1: REGISTRAR GASTO
# ==========================================
with tab_gasto:
    st.write("Introduce los detalles del nuevo gasto familiar.")
    
    if not lista_familiares or not lista_tematicas:
        st.warning("⚠️ Faltan familiares o temáticas. Añádelos en las siguientes pestañas antes de registrar un gasto.")
    
    with st.form("formulario_gasto"):
        col1, col2 = st.columns(2)
        with col1:
            persona = st.selectbox("¿Quién hizo el gasto?", options=lista_familiares if lista_familiares else ["Esperando..."])
        with col2:
            tematica = st.selectbox("Temática del gasto", options=lista_tematicas if lista_tematicas else ["Esperando..."])
            
        dinero = st.number_input("Dinero gastado (€)", min_value=0.0, step=0.5, format="%.2f")
        enviado = st.form_submit_button("💾 Guardar Gasto")

    if enviado:
        if not lista_familiares or not lista_tematicas:
            st.error("❌ Registra primero al menos un familiar y una temática.")
        elif dinero <= 0:
            st.error("❌ El importe debe ser mayor que 0.")
        else:
            datos_gasto = {
                "persona": persona,
                "tema_tematica": tematica,
                "dinero_gastado": dinero
            }
            try:
                respuesta = requests.post(f"{API_URL}/gasto/", json=datos_gasto)
                if respuesta.status_code == 200:
                    st.success("✅ ¡Gasto registrado correctamente!")
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
                    st.success(f"✅ ¡{nuevo_familiar.strip()} añadido! Recarga la página para actualizar las listas.")
                elif res.status_code == 400:
                    st.error(f"⚠️ {res.json().get('detail', 'El familiar ya existe')}")
                else:
                    st.error(f"❌ Error {res.status_code}: {res.text}")
            except Exception as e:
                st.error(f"⚠️ Sin conexión al backend: {e}")

# ==========================================
# PESTAÑA 3: AÑADIR TEMÁTICA
# ==========================================
with tab_tematica:
    st.write("Crea categorías para clasificar los gastos (ej. Supermercado, Luz, Ocio...).")
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
                    st.success(f"✅ ¡Temática '{nueva_tematica.strip()}' añadida! Recarga la página.")
                elif res.status_code == 400:
                    st.error(f"⚠️ {res.json().get('detail', 'La temática ya existe')}")
                else:
                    st.error(f"❌ Error {res.status_code}: {res.text}")
            except Exception as e:
                st.error(f"⚠️ Sin conexión al backend: {e}")

# ==========================================
# PESTAÑA 4: ESTADÍSTICAS
# ==========================================
with tab_stats:
    st.header("📊 Panel de Gastos")
    
    try:
        respuesta_gastos = requests.get(f"{API_URL}/gastos/")
        
        if respuesta_gastos.status_code == 200:
            datos = respuesta_gastos.json()
            df = pd.DataFrame(datos)
        else:
            df = pd.DataFrame()
            
        if df.empty:
            st.info("Aún no hay gastos registrados para generar estadísticas.")
        else:
            gasto_total = df['dinero_gastado'].sum()
            st.metric("Total Gastado (Familia)", f"{gasto_total:.2f} €")
            st.divider()
            
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                st.subheader("👤 Gasto por Familiar")
                gasto_persona = df.groupby('persona')['dinero_gastado'].sum().reset_index()
                st.bar_chart(gasto_persona.set_index('persona'))
                
            with col_graf2:
                st.subheader("🏷️ Gasto por Temática")
                gasto_tematica = df.groupby('tema_tematica')['dinero_gastado'].sum().reset_index()
                st.bar_chart(gasto_tematica.set_index('tema_tematica'))
                
            st.divider()
            st.subheader("📝 Historial detallado")
            st.dataframe(df[['fecha', 'persona', 'tema_tematica', 'dinero_gastado']].sort_values(by="fecha", ascending=False), use_container_width=True)
            
    except Exception:
        st.error("⚠️ Error al cargar las estadísticas. Verifica el backend.")