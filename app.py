import streamlit as st
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Importaciones Boreal Medical", page_icon="🏢", layout="centered")

# URL DIRECTA DEL LOGOTIPO EN TU SERVIDOR
url_logo = "https://www.equipomedico.com.ec/app_importaciones/LOGO_BOREAL_MEDICAL_HORIZONTAL.png"

# 2. Variables de memoria
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if "busqueda_proveedor" not in st.session_state:
    st.session_state["busqueda_proveedor"] = "" # Ahora guardará la selección vacía por defecto

def limpiar_busqueda():
    st.session_state["busqueda_proveedor"] = ""

def cuadro_titulo(texto):
    return f"""
    <div style='background-color: lightgray; padding: 5px 10px; border-radius: 5px; 
                font-weight: bold; color: black; margin-bottom: 5px;'>
        {texto}
    </div>
    """

# 3. Función para cargar la base de datos desde Google Sheets
def cargar_datos():
    columnas_requeridas = ['PO', 'SUPPLIER', 'PRODUCTOS', 'STATUS', 'ARRIBO', 'WR', 'NOTES']
    url_google_sheets = "https://docs.google.com/spreadsheets/d/1sTUGAEUiVt-J1UIxjlMOSQ6PEbPh_Phff3Q4Vidv8zs/export?format=csv&gid=1010252446"
    
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
    
    if st.button("Ingresar", use_container_width=True):
        if usuario == "boreal" and contrasena == "admin2026":
            st.session_state["autenticado"] = True
            st.rerun() 
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

# 5. Diseño de la Aplicación Principal
def mostrar_aplicacion():
    col_espacio, col_salir = st.columns([8, 2])
    with col_salir:
        if st.button("Cerrar Sesión"):
            st.session_state["autenticado"] = False
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
    st.markdown("### 🔍 Rastreo por Proveedor")

    try:
        df = cargar_datos()

        # --- NUEVO: TEXTO PREDICTIVO (AUTOCOMPLETADO) ---
        # 1. Extraemos los proveedores únicos de la base de datos
        lista_proveedores = df['SUPPLIER'].dropna().unique().tolist()
        # 2. Los ordenamos alfabéticamente para mayor orden
        lista_proveedores.sort()
        # 3. Añadimos un espacio en blanco al inicio para que no busque el primero por defecto
        lista_proveedores.insert(0, "")

        # Reemplazamos text_input por selectbox. 
        # Streamlit permite escribir dentro de este selectbox para autocompletar.
        st.selectbox("🏢 Escriba o seleccione el nombre del SUPPLIER (Proveedor):", 
                      options=lista_proveedores,
                      key="busqueda_proveedor")

        termino = st.session_state["busqueda_proveedor"].strip()

        # Si el usuario seleccionó un proveedor (no está en blanco)
        if termino != "":
            # Filtramos los datos exactos de ese proveedor
            filtro_proveedor = df['SUPPLIER'].astype(str).str.strip() == termino
            resultado = df[filtro_proveedor]

            if not resultado.empty:
                
                # Extraemos los estatus únicos para el filtro secundario
                estatus_unicos = resultado['STATUS'].dropna().unique().tolist()
                estatus_unicos.insert(0, "Todos los estatus")
                
                # Filtro selector por estatus
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
                                st.success(f"**{status}**") 
                                
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
