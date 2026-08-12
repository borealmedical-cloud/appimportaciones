import streamlit as st
import pandas as pd

# 1. URLs de tus imágenes (El horizontal para la app, y el cuadrado para el ícono del celular)
url_logo_horizontal = "https://www.equipomedico.com.ec/app_importaciones/LOGO_BOREAL_MEDICAL_HORIZONTAL.png"
url_icono_cuadrado = "https://www.equipomedico.com.ec/app_importaciones/ISOTIPO_BOREAL_MEDICAL.png" # Reemplaza por tu enlace real

# 2. Configuración de la página (AQUÍ ESTÁ LA MAGIA DEL ÍCONO)
st.set_page_config(
    page_title="Importaciones Boreal Medical", 
    page_icon=url_icono_cuadrado,  # <--- Esto obliga al celular a usar tu logo
    layout="centered"
)
