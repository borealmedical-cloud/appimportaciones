import streamlit as st
import pandas as pd

st.set_page_config(page_title="Importaciones Boreal Medical", layout="centered")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if "busqueda_proveedor" not in st.session_state:
    st.session_state["busqueda_proveedor"] = ""

def limpiar_busqueda():
    st.session_state["busqueda_proveedor"] = ""

def cuadro_titulo(texto):
    # Utilizamos nombres explícitos de color como lightgray y black
    return f"""
    <div style='background-color: lightgray; padding: 5px 10px; border-radius: 5px; 
                font-weight: bold; color: black; margin-bottom: 5px;'>
        {texto}
    </div>
    """

def cargar_datos():
    columnas_requeridas = ['PO', 'SUPPLIER', 'PRODUCTOS', 'STATUS', 'ARRIBO', 'WR', 'NOTES']
    # La aplicación ahora lee directamente desde tu servidor en vivo
    url_excel = "https://docs.google.com/spreadsheets/d/1sTUGAEUiVt-J1UIxjlMOSQ6PEbPh_Phff3Q4Vidv8zs/edit?usp=drive_link"
    
    df = pd.read_excel(
        url_excel, 
        sheet_name="2026", 
        usecols=columnas_requeridas,
        dtype=str
    )
    return df

# URL del logotipo alojado en tu servidor
url_logo = "https://equipomedico.com.ec/app_importaciones/LOGO_BOREAL_MEDICAL_HORIZONTAL.png"

def mostrar_login():
    try:
        st.image(url_logo, use_container_width=True)
    except Exception:
        st.warning("⚠️ No se pudo cargar el logotipo. Verifica que esté en tu cPanel.")
    
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

        st.text_input("🏢 Ingrese el nombre del SUPPLIER (Proveedor):", 
                      placeholder="Ej: Medtronic, Atlas...", 
                      key="busqueda_proveedor")

        termino = st.session_state["busqueda_proveedor"].strip()

        if termino:
            filtro = df['SUPPLIER'].astype(str).str.contains(termino, case=False, na=False)
            resultado = df[filtro]

            if not resultado.empty:
                st.success(f"✅ Se encontraron {len(resultado)} registros para el proveedor buscado.")
                st.button("🔄 Realizar una nueva búsqueda", on_click=limpiar_busqueda)
                st.write("")
                
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
                st.error("❌ No se encontraron órdenes para este proveedor.")
                st.button("🔄 Intentar nueva búsqueda", on_click=limpiar_busqueda)

    except Exception as e:
        st.error("⚠️ Error de conexión. Revisa que el Excel esté subido correctamente en cPanel.")

if not st.session_state["autenticado"]:
    mostrar_login()
else:
    mostrar_aplicacion()