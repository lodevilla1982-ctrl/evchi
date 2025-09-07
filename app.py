# app.py
import streamlit as st
import os
import tempfile
from utils.generator import FunkoChibiGenerator
import base64
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Funko Chibi Generator",
    page_icon="🎨",
    layout="wide"
)

# Título
st.title("🎨 Funko Chibi Generator")
st.write("Crea tu propio Funko Chibi personalizado para imprimir en 3D")

# Inicializar generador
if 'generator' not in st.session_state:
    st.session_state.generator = FunkoChibiGenerator()

generator = st.session_state.generator

# Columnas
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Configuración")

    # Tipo de personaje
    character_type = st.selectbox("Tipo", ["human", "child", "dog", "cat", "bear"])
    generator.character_type = character_type

    # Género
    gender = st.selectbox("Género", ["male", "female", "neutral"])
    generator.gender = gender

    # Escala
    scale = st.slider("Escala", 0.5, 2.0, 1.0, 0.1)
    generator.scale = scale

    # Tolerancia
    tolerance = st.slider("Tolerancia (mm)", -0.2, 0.0, -0.05, 0.01)
    generator.set_tolerance(tolerance)

    # Estilo de pelo
    hair_style = st.selectbox("Estilo de pelo", ["short", "long", "none"])
    generator.hair_style = hair_style

    # Ropa
    clothing = st.selectbox("Ropa", ["none", "shirt", "hat"])
    generator.clothing = clothing

    # Botón generar
    if st.button("Generar Modelo"):
        with st.spinner("Generando modelo..."):
            parts = generator.generate_full_model()
            st.session_state.parts = parts
            st.success("Modelo generado!")

    # Exportar
    if 'parts' in st.session_state:
        file_format = st.selectbox("Formato", ["STL", "OBJ"])
        if st.button("Descargar Todas las Partes"):
            with tempfile.TemporaryDirectory() as tmpdir:
                generator.export_parts(tmpdir, file_format)
                zip_path = os.path.join(tmpdir, "funko_parts.zip")
                # Crear zip
                import zipfile
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for root, _, files in os.walk(tmpdir):
                        for file in files:
                            zipf.write(os.path.join(root, file), file)
                
                with open(zip_path, "rb") as f:
                    bytes_data = f.read()
                    b64 = base64.b64encode(bytes_data).decode()
                    href = f'<a href="data:application/zip;base64,{b64}" download="funko_parts.zip">Descargar ZIP</a>'
                    st.markdown(href, unsafe_allow_html=True)

with col2:
    st.header("Vista 3D")
    
    if 'parts' in st.session_state:
        st.write("Visualización de partes (próximamente con Three.js)")
        st.image("https://via.placeholder.com/600x400?text=3D+View", use_column_width=True)
    else:
        st.write("Genera un modelo para ver la vista 3D")

# Footer
st.markdown("---")
st.caption("Desarrollado con ❤️ para impresión 3D")
