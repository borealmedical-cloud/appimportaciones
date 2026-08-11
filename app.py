import streamlit as st
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Importaciones Boreal Medical", page_icon="🏢", layout="wide")

# URL DIRECTA DEL LOGOTIPO EN TU SERVIDOR
url_logo = "https://www.equipomedico.com.ec/app_importaciones/LOGO_BOREAL_MEDICAL_HORIZONTAL.png"

# 2. Variables de memoria (Sesión, Usuario y Búsqueda)
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = ""

if "busqueda_fabrica" not in st.session_state:
    st.session_state["busqueda_fabrica"] = ""

def limpiar_busqueda():
    st.session_state["busqueda_fabrica"] = ""

def cuadro_titulo(texto):
    return f"""
    <div style='background-color: lightgray; padding: 5px 10px; border-radius: 5px; 
                font-weight: bold; color: black; margin-bottom: 5px; font-size: 13px;'>
        {texto}
    </div>
    """

def formato_status_color(status_texto):
    status_upper = str(status_texto).upper().strip()
    
    if "BODEGA" in status_upper:
        bg_color = "#1E88E5" # Azul Boreal
    elif "ENTREGADO" in status_upper or "FINALIZADO" in status_upper or "COMPLETADO" in status_upper:
        bg_color = "#2E7D32" # Verde
    elif "TRANSITO" in status_upper or "CAMINO" in status_upper:
        bg_color = "#FB8C00" # Naranja
    elif "ADUANA" in status_upper or "REVISION" in status_upper:
        bg_color = "#D81B60" # Magenta/Rojo
    elif "CANCELADO" in status_upper or "RECHAZADO" in status_upper:
        bg_color = "#E53935" # Rojo intenso
    else:
        bg_color = "#757575" # Gris
        
    return f"""
    <div style='background-color: {bg_color}; color: white; padding: 8px 12px; 
                border-radius: 6px; font-weight: bold; text-align: center; font-size: 14px;'>
        {status_texto}
    </div>
    """

# Función auxiliar para limpiar y formatear fechas
def formatear_fecha(valor):
    if pd.notna(valor) and str(valor).strip() != "":
        try:
            return pd.to_datetime(valor).strftime('%Y-%m-%d')
        except:
            return str(valor)
    return "No registrada"

# 3. Función para cargar la base de datos
def cargar_datos():
    url_excel = "https://docs.google.com/spreadsheets/d/1GDj0c3NtPLi2NAXhtMGflpJR0bNLfwzu/export?format=xlsx"
    
    # Leemos la hoja 2026 y las letras exactas solicitadas
    df = pd.read_excel(
        url_excel, 
        sheet_name="2026", 
        usecols="B,E,F,G,H,K,N,Q,W,AC,AG",
        dtype=str
    )
    
    # Limpiamos los nombres de las columnas para evitar errores de tipeo y los pasamos a mayúsculas
    df.columns = df.columns.str.strip().str.upper()
    return df

# 4. Diseño de la Pantalla de Login
def mostrar_login():
    try:
        col_izq, col_centro, col_der = st.columns([1, 2, 1])
        with col_centro:
            st.image(url_logo, use_container_width=True)
    except Exception:
        st.warning("⚠️ No se pudo cargar el logotipo desde el servidor.")
    
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>Acceso al Sistema de Rastreo</h3>", unsafe_allow_html=True)
    st.write("") 

    usuario = st.text_input("👤 Usuario:")
    contrasena = st.text_input("🔑 Contraseña:", type="password") 
    
    usuarios_autorizados = {
        "boreal": "admin2026",
        "logistica": "boreal2026",
        "compras": "boreal2026"
    }
    
    if st.button("Ingresar", use_container_width=True):
        usuario_clean = usuario.strip().lower()
        if usuario_clean in usuarios_autorizados and contrasena == usuarios_autorizados[usuario_clean]:
            st.session_state["autenticado"] = True
            st.session_state["usuario_actual"] = usuario.strip().capitalize()
            st.rerun() 
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

# 5. Diseño de la Aplicación Principal
def mostrar_aplicacion():
    col_saludo, col_salir = st.columns([7, 3])
    with col_saludo:
        st.markdown(f"👤 **Bienvenido(a):** `{st.session_state['usuario_actual']}`")
    with col_salir:
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state["autenticado"] = False
            st.session_state["usuario_actual"] = ""
            st.session_state["busqueda_fabrica"] = ""
            st.rerun()

    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        try:
            st.image(url_logo, use_container_width=True)
        except:
            pass 
            
    with col_titulo:
        st.title("IMPORTACIONES BOREAL MEDICAL")

    st.markdown("---")
    st.markdown("### 🔍 Rastreo por Fábrica")

    try:
        df = cargar_datos()

        # Validación de seguridad
        if 'FABRICA' not in df.columns or 'ESTATUS' not in df.columns:
            st.error("⚠️ Error: No encuentro las columnas 'FABRICA' o 'ESTATUS' en tu Excel. Asegúrate de que estén bien escritas en la primera fila.")
            st.write("Columnas detectadas:", list(df.columns))
            return

        # Búsqueda predictiva basada en "FÁBRICA"
        lista_fabricas = df['FABRICA'].dropna().unique().tolist()
        lista_fabricas.sort()
        lista_fabricas.insert(0, "")

        st.selectbox("🏭 Escriba o seleccione el nombre de la FÁBRICA:", 
                      options=lista_fabricas,
                      key="busqueda_fabrica")

        termino = st.session_state["busqueda_fabrica"].strip()

        if termino != "":
            filtro = df['FABRICA'].astype(str).str.strip() == termino
            resultado = df[filtro]

            if not resultado.empty:
                
                # Filtro secundario por estatus
                estatus_unicos = resultado['ESTATUS'].dropna().unique().tolist()
                estatus_unicos.insert(0, "Todos los estatus")
                
                opcion_status = st.selectbox("🎛️ Filtrar resultados por Estatus:", estatus_unicos)
                
                if opcion_status != "Todos los estatus":
                    resultado = resultado[resultado['ESTATUS'] == opcion_status]

                st.success(f"✅ Se encontraron {len(resultado)} registros.")
                st.button("🔄 Limpiar búsqueda", on_click=limpiar_busqueda)
                st.write("")
                
                if not resultado.empty:
                    for index, datos in resultado.iterrows():
                        
                        # Extracción segura de datos (11 columnas)
                        fabrica = datos.get('FABRICA', "No registrado")
                        requerido_por = datos.get('REQUERIDO POR', "No registrado")
                        cliente_stock = datos.get('CLIENTE/STOCK', "No registrado")
                        productos = datos.get('PRODUCTOS', "No registrado")
                        estatus = datos.get('ESTATUS', "Sin estatus")
                        comentarios = datos.get('COMENTARIOS', "Ninguno")
                        tipo_embarque = datos.get('TIPO EMBARQUE', "No registrado")
                        bodega = datos.get('BODEGA', "No registrado")
                        
                        # Fechas formateadas
                        fecha_despacho = formatear_fecha(datos.get('FECHA DESPACHO FABRICA'))
                        tentativo_bodegas = formatear_fecha(datos.get('TENTATIVO BODEGAS'))
                        ingreso_bodega = formatear_fecha(datos.get('FECHA INGRESO BODEGA'))

                        # Distribución visual en 3 columnas para evitar amontonamiento
                        with st.container(border=True):
                            st.subheader(f"🏭 FÁBRICA: {fabrica}")
                            
                            c1, c2, c3 = st.columns(3)
                            
                            with c1:
                                st.markdown(cuadro_titulo("CLIENTE / STOCK"), unsafe_allow_html=True)
                                st.write(cliente_stock)
                                
                                st.markdown(cuadro_titulo("PRODUCTOS"), unsafe_allow_html=True)
                                st.write(productos)
                                
                                st.markdown(cuadro_titulo("REQUERIDO POR"), unsafe_allow_html=True)
                                st.write(requerido_por)
                                
                            with c2:
                                st.markdown(cuadro_titulo("ESTATUS"), unsafe_allow_html=True)
                                st.markdown(formato_status_color(estatus), unsafe_allow_html=True) 
                                st.write("") 
                                
                                st.markdown(cuadro_titulo("TIPO DE EMBARQUE"), unsafe_allow_html=True)
                                st.write(tipo_embarque)

                                st.markdown(cuadro_titulo("BODEGA"), unsafe_allow_html=True)
                                st.write(bodega)
                                
                            with c3:
                                st.markdown(cuadro_titulo("DESPACHO FÁBRICA"), unsafe_allow_html=True)
                                st.info(fecha_despacho)
                                
                                st.markdown(cuadro_titulo("TENTATIVO BODEGAS"), unsafe_allow_html=True)
                                st.warning(tentativo_bodegas)
                                
                                st.markdown(cuadro_titulo("INGRESO BODEGA"), unsafe_allow_html=True)
                                st.success(ingreso_bodega)
                                
                            # Comentarios a lo ancho completo en la parte inferior
                            st.markdown(cuadro_titulo("COMENTARIOS"), unsafe_allow_html=True)
                            st.write(comentarios)
                else:
                    st.info("No hay órdenes con ese estatus específico para esta fábrica.")

            else:
                st.error("❌ No se encontraron órdenes para esta fábrica.")
                st.button("🔄 Intentar nueva búsqueda", on_click=limpiar_busqueda)

    except Exception as e:
        st.error(f"⚠️ Error al conectar con Google Sheets. Asegúrate de que los títulos de las columnas (ej. 'CLIENTE/STOCK') estén escritos exactamente igual en la primera fila de tu Excel. Error detallado: {e}")

# 6. Lógica de control
if not st.session_state["autenticado"]:
    mostrar_login()
else:
    mostrar_aplicacion()
