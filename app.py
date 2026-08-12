import streamlit as st
import pandas as pd
from PIL import Image  # <-- AÑADE ESTA LIBRERÍA

# 1. URLs de las imágenes
url_logo_horizontal = "https://www.equipomedico.com.ec/app_importaciones/LOGO_BOREAL_MEDICAL_HORIZONTAL.png"
url_icono_cuadrado = "https://www.equipomedico.com.ec/app_importaciones/ISOTIPO_BOREAL_MEDICAL.png"

# 2. Configuración general
st.set_page_config(
    page_title="Importaciones Boreal Medical", 
    page_icon=url_icono_cuadrado, 
    layout="centered"
)

# --- TRUCO AVANZADO PARA FORZAR EL ÍCONO EN IPHONE ---
components.html(f"""
    <script>
        // Buscamos la 'cabeza' de la página principal
        const doc = window.parent.document;
        
        // Creamos la etiqueta estricta de Apple
        let link = doc.querySelector("link[rel~='apple-touch-icon']");
        if (!link) {{
            link = doc.createElement('link');
            link.rel = 'apple-touch-icon';
            doc.head.appendChild(link);
        }}
        // Le inyectamos tu imagen
        link.href = '{url_icono_cuadrado}';
    </script>
""", height=0, width=0)
# -----------------------------------------------------


# Inyección de CSS para Responsividad y Diseño Compacto
st.markdown("""
    <style>
    /* Limitar ancho máximo y reducir rellenos globales */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
        max-width: 850px !important;
    }
    
    /* Ajuste de tipografías generales */
    h1 {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        color: #1a202c;
    }
    h2, h3 {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
    }
    
    /* Ajuste de campos de entrada y desplegables */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        font-size: 0.88rem !important;
        border-radius: 6px !important;
    }
    
    /* Estilizar botones */
    .stButton button {
        font-size: 0.88rem !important;
        padding: 0.35rem 0.8rem !important;
        border-radius: 6px !important;
    }

    /* Tarjetas de resultados elegantes y adaptables */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 12px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    
    /* Ajuste de etiquetas de sección */
    .badge-label {
        background-color: #edf2f7;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        color: #2d3748;
        font-size: 0.78rem;
        margin-bottom: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Variables de memoria (Sesión, Usuario y Búsqueda)
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = ""

if "busqueda_fabrica" not in st.session_state:
    st.session_state["busqueda_fabrica"] = ""

def limpiar_busqueda():
    st.session_state["busqueda_fabrica"] = ""

def cuadro_titulo(texto):
    return f"<div class='badge-label'>{texto}</div>"

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
        bg_color = "#E53935" # Rojo
    else:
        bg_color = "#757575" # Gris
        
    return f"""
    <div style='background-color: {bg_color}; color: white; padding: 6px 10px; 
                border-radius: 5px; font-weight: bold; text-align: center; font-size: 0.85rem;'>
        {status_texto}
    </div>
    """

def formatear_fecha(valor):
    if pd.notna(valor) and str(valor).strip() != "":
        try:
            return pd.to_datetime(valor).strftime('%Y-%m-%d')
        except:
            return str(valor)
    return "No registrada"

# 4. Función para cargar la base de datos desde Google Sheets
def cargar_datos():
    url_excel = "https://docs.google.com/spreadsheets/d/1GDj0c3NtPLi2NAXhtMGflpJR0bNLfwzu/export?format=xlsx"
    
    df = pd.read_excel(
        url_excel, 
        sheet_name="2026", 
        usecols="B,E,F,G,H,K,N,Q,W,AC,AG",
        dtype=str
    )
    df.columns = df.columns.str.strip().str.upper()
    return df

# 5. Pantalla de Login Compacta
def mostrar_login():
    _, col_login, _ = st.columns([1, 2.2, 1])
    
    with col_login:
        with st.container(border=True):
            try:
                st.image(url_logo_horizontal, use_container_width=True)
            except Exception:
                st.warning("⚠️ No se pudo cargar el logotipo.")
            
            st.markdown("<h3 style='text-align: center; margin-top: 10px; font-size: 1.1rem;'>Acceso al Sistema</h3>", unsafe_allow_html=True)
            
            usuario = st.text_input("👤 Usuario:")
            contrasena = st.text_input("🔑 Contraseña:", type="password") 
            
            usuarios_autorizados = {
                "boreal": "admin2026",
                "logistica": "boreal2026",
                "compras": "boreal2026"
            }
            
            st.write("")
            if st.button("Ingresar", use_container_width=True):
                usuario_clean = usuario.strip().lower()
                if usuario_clean in usuarios_autorizados and contrasena == usuarios_autorizados[usuario_clean]:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_actual"] = usuario.strip().capitalize()
                    st.rerun() 
                else:
                    st.error("❌ Credenciales incorrectas.")

# 6. Pantalla Principal de la Aplicación
def mostrar_aplicacion():
    col_saludo, col_salir = st.columns([7, 3])
    with col_saludo:
        st.markdown(f"👤 **Usuario:** `{st.session_state['usuario_actual']}`")
    with col_salir:
        if st.button("🚪 Salir", use_container_width=True):
            st.session_state["autenticado"] = False
            st.session_state["usuario_actual"] = ""
            st.session_state["busqueda_fabrica"] = ""
            st.rerun()

    col_logo, col_titulo = st.columns([1.2, 3.8])
    with col_logo:
        try:
            st.image(url_logo_horizontal, use_container_width=True)
        except:
            pass 
            
    with col_titulo:
        st.markdown("<h1 style='margin-top: 5px;'>IMPORTACIONES BOREAL MEDICAL</h1>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔍 Rastreo por Fábrica")

    try:
        df = cargar_datos()

        if 'FABRICA' not in df.columns or 'ESTATUS' not in df.columns:
            st.error("⚠️ No se encuentran las columnas 'FABRICA' o 'ESTATUS' en el Excel.")
            return

        lista_fabricas = df['FABRICA'].dropna().unique().tolist()
        lista_fabricas.sort()
        lista_fabricas.insert(0, "")

        st.selectbox("🏭 Escriba o seleccione la FÁBRICA:", 
                      options=lista_fabricas,
                      key="busqueda_fabrica")

        termino = st.session_state["busqueda_fabrica"].strip()

        if termino != "":
            filtro = df['FABRICA'].astype(str).str.strip() == termino
            resultado = df[filtro]

            if not resultado.empty:
                
                estatus_unicos = resultado['ESTATUS'].dropna().unique().tolist()
                estatus_unicos.insert(0, "Todos los estatus")
                
                opcion_status = st.selectbox("🎛️ Filtrar por Estatus:", estatus_unicos)
                
                if opcion_status != "Todos los estatus":
                    resultado = resultado[resultado['ESTATUS'] == opcion_status]

                st.success(f"✅ Se encontraron {len(resultado)} registro(s).")
                st.button("🔄 Limpiar búsqueda", on_click=limpiar_busqueda)
                st.write("")
                
                if not resultado.empty:
                    for index, datos in resultado.iterrows():
                        
                        fabrica = datos.get('FABRICA', "No registrado")
                        requerido_por = datos.get('REQUERIDO POR', "No registrado")
                        cliente_stock = datos.get('CLIENTE/STOCK', "No registrado")
                        productos = datos.get('PRODUCTOS', "No registrado")
                        estatus = datos.get('ESTATUS', "Sin estatus")
                        comentarios = datos.get('COMENTARIOS', "Ninguno")
                        tipo_embarque = datos.get('TIPO EMBARQUE', "No registrado")
                        bodega = datos.get('BODEGA', "No registrado")
                        
                        fecha_despacho = formatear_fecha(datos.get('FECHA DESPACHO FABRICA'))
                        tentativo_bodegas = formatear_fecha(datos.get('TENTATIVO BODEGAS'))
                        ingreso_bodega = formatear_fecha(datos.get('FECHA INGRESO BODEGA'))

                        with st.container(border=True):
                            st.markdown(f"<h3 style='color: #2b6cb0; margin-bottom: 10px;'>🏭 {fabrica}</h3>", unsafe_allow_html=True)
                            
                            c1, c2 = st.columns(2)
                            
                            with c1:
                                st.markdown(cuadro_titulo("CLIENTE / STOCK"), unsafe_allow_html=True)
                                st.write(cliente_stock)
                                
                                st.markdown(cuadro_titulo("PRODUCTOS"), unsafe_allow_html=True)
                                st.write(productos)
                                
                                st.markdown(cuadro_titulo("REQUERIDO POR"), unsafe_allow_html=True)
                                st.write(requerido_por)

                                st.markdown(cuadro_titulo("DESPACHO FÁBRICA"), unsafe_allow_html=True)
                                st.write(fecha_despacho)

                                st.markdown(cuadro_titulo("TENTATIVO BODEGAS"), unsafe_allow_html=True)
                                st.write(tentativo_bodegas)
                                
                            with c2:
                                st.markdown(cuadro_titulo("ESTATUS"), unsafe_allow_html=True)
                                st.markdown(formato_status_color(estatus), unsafe_allow_html=True) 
                                st.write("") 
                                
                                st.markdown(cuadro_titulo("TIPO EMBARQUE / BODEGA"), unsafe_allow_html=True)
                                st.write(f"📦 {tipo_embarque} | 🏢 {bodega}")

                                st.markdown(cuadro_titulo("INGRESO BODEGA"), unsafe_allow_html=True)
                                st.write(ingreso_bodega)
                                
                            st.markdown(cuadro_titulo("COMENTARIOS"), unsafe_allow_html=True)
                            st.write(comentarios)
                else:
                    st.info("No hay órdenes con ese estatus específico.")

            else:
                st.error("❌ No se encontraron órdenes para esta fábrica.")
                st.button("🔄 Intentar nueva búsqueda", on_click=limpiar_busqueda)

    except Exception as e:
        st.error(f"⚠️ Error al conectar con Google Sheets. Error: {e}")

# 7. Control de flujo de autenticación
if not st.session_state["autenticado"]:
    mostrar_login()
else:
    mostrar_aplicacion()
