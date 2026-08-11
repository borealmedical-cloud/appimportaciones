import streamlit as st
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Importaciones Boreal Medical", page_icon="🏢", layout="centered")

# URL DIRECTA DEL LOGOTIPO EN TU SERVIDOR
url_logo = "https://www.equipomedico.com.ec/app_importaciones/LOGO_BOREAL_MEDICAL_HORIZONTAL.png"

# 2. Variables de memoria (Sesión, Usuario y Búsqueda)
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = ""

if "busqueda_proveedor" not in st.session_state:
    st.session_state["busqueda_proveedor"] = ""

def limpiar_busqueda():
    st.session_state["busqueda_proveedor"] = ""

def cuadro_titulo(texto):
    return f"""
    <div style='background-color: lightgray; padding: 5px 10px; border-radius: 5px; 
                font-weight: bold; color: black; margin-bottom: 5px;'>
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

# 3. Función para cargar la base de datos desde Google Sheets
def cargar_datos():
    columnas_requeridas = ['PO', 'SUPPLIER', 'PRODUCTOS', 'STATUS', 'ARRIBO', 'WR', 'NOTES']
    url_google_sheets = "https://docs.google.com/spreadsheets/d/1L2tTsNhlzqZRx737l8vxAWpLHbH06sZa/edit?usp=sharing&ouid=107170398108370076758&rtpof=true&sd=true"
    
    df = pd.read_csv(
        url_google_sheets, 
        usecols=columnas_requeridas,
        dtype=str
    )
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
    
    # --- DICCIONARIO DE USUARIOS AUTORIZADOS ---
    # Puedes agregar más usuarios y contraseñas aquí si lo deseas
    usuarios_autorizados = {
        "boreal": "admin2026",
        "logistica": "boreal2026",
        "compras": "boreal2026"
    }
    
    if st.button("Ingresar", use_container_width=True):
        usuario_clean = usuario.strip().lower()
        if usuario_clean in usuarios_autorizados and contrasena == usuarios_autorizados[usuario_clean]:
            st.session_state["autenticado"] = True
            st.session_state["usuario_actual"] = usuario.strip().capitalize() # Guardamos el nombre para mostrarlo
            st.rerun() 
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

# 5. Diseño de la Aplicación Principal
def mostrar_aplicacion():
    # Barra superior con Saludo de Usuario y Botón de Salir
    col_saludo, col_salir = st.columns([7, 3])
    
    with col_saludo:
        st.markdown(f"👤 **Bienvenido(a):** `{st.session_state['usuario_actual']}`")
        
    with col_salir:
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state["autenticado"] = False
            st.session_state["usuario_actual"] = ""
            st.session_state["busqueda_proveedor"] = ""
            st.rerun()

    # Encabezado principal
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        try:
            st.image(url_logo, use_container_width=True)
        except:
            pass 
            
    with col_titulo:
        st.title("IMPORTACIONES BOREAL MEDICAL")

    st.markdown("---")
    st.markdown("### 🔍 Rastreo por Proveedor")

    try:
        df = cargar_datos()

        # Búsqueda con autocompletado (texto predictivo)
        lista_proveedores = df['SUPPLIER'].dropna().unique().tolist()
        lista_proveedores.sort()
        lista_proveedores.insert(0, "")

        st.selectbox("🏢 Escriba o seleccione el nombre del SUPPLIER (Proveedor):", 
                      options=lista_proveedores,
                      key="busqueda_proveedor")

        termino = st.session_state["busqueda_proveedor"].strip()

        if termino != "":
            filtro_proveedor = df['SUPPLIER'].astype(str).str.strip() == termino
            resultado = df[filtro_proveedor]

            if not resultado.empty:
                
                # Filtro selector por estatus
                estatus_unicos = resultado['STATUS'].dropna().unique().tolist()
                estatus_unicos.insert(0, "Todos los estatus")
                
                opcion_status = st.selectbox("🎛️ Filtrar resultados por Estatus:", estatus_unicos)
                
                if opcion_status != "Todos los estatus":
                    resultado = resultado[resultado['STATUS'] == opcion_status]

                st.success(f"✅ Se encontraron {len(resultado)} registros para esta búsqueda.")
                st.button("🔄 Limpiar búsqueda", on_click=limpiar_busqueda)
                st.write("")
                
                if not resultado.empty:
                    for index, datos in resultado.iterrows():
                        
                        po = datos['PO'] if pd.notna(datos['PO']) else "No registrado"
                        supplier = datos['SUPPLIER'] if pd.notna(datos['SUPPLIER']) else "No registrado"
                        productos = datos['PRODUCTOS'] if pd.notna(datos['PRODUCTOS']) else "No registrado"
                        status = datos['STATUS'] if pd.notna(datos['STATUS']) else "Sin estatus"
                        wr = datos['WR'] if pd.notna(datos['WR']) else "No registrado"
                        notes = datos['NOTES'] if pd.notna(datos['NOTES']) else "Ninguna"

                        if pd.notna(datos['ARRIBO']):
                            try:
                                arribo = pd.to_datetime(datos['ARRIBO']).strftime('%Y-%m-%d')
                            except:
                                arribo = str(datos['ARRIBO'])
                        else:
                            arribo = "No registrada"

                        with st.container(border=True):
                            st.subheader(f"📦 PO: {po}")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(cuadro_titulo("SUPPLIER"), unsafe_allow_html=True)
                                st.write(supplier)
                                
                                st.markdown(cuadro_titulo("PRODUCTOS"), unsafe_allow_html=True)
                                st.write(productos)
                                
                                st.markdown(cuadro_titulo("ARRIBO"), unsafe_allow_html=True)
                                st.write(arribo)
                                
                            with col2:
                                st.markdown(cuadro_titulo("STATUS"), unsafe_allow_html=True)
                                st.markdown(formato_status_color(status), unsafe_allow_html=True) 
                                st.write("") 
                                
                                st.markdown(cuadro_titulo("WR"), unsafe_allow_html=True)
                                st.write(wr)
                                
                                st.markdown(cuadro_titulo("NOTES"), unsafe_allow_html=True)
                                st.info(notes)
                else:
                    st.info("No hay órdenes con ese estatus específico para este proveedor.")

            else:
                st.error("❌ No se encontraron órdenes para este proveedor.")
                st.button("🔄 Intentar nueva búsqueda", on_click=limpiar_busqueda)

    except Exception as e:
        st.error(f"⚠️ Error al conectar con Google Sheets. Asegúrate de que el documento esté configurado como público. Error: {e}")

# 6. Lógica de control
if not st.session_state["autenticado"]:
    mostrar_login()
else:
    mostrar_aplicacion()
