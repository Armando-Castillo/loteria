"""
Generador de Tablas de Lotería - Interfaz Web
Aplicación Streamlit para generar tablas de lotería desde el navegador
"""

import streamlit as st
from loteria_core import generate_loteria_pdf, IMAGES_PER_CARD

# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Generador de Lotería",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ESTILOS PERSONALIZADOS
# ============================================================================

st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B6B;
        padding: 1rem 0;
    }
    .info-box {
        background-color: #f0f2f6;
        border-left: 4px solid #FF6B6B;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    .stDownloadButton button {
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        padding: 0.75rem 2rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

# Título y descripción
st.markdown('<h1 class="main-header">🎲 Generador de Tablas de Lotería</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="info-box">
    <p><strong>Crea tablas de lotería profesionales en 3 pasos:</strong></p>
    <ol>
        <li>Sube tus imágenes (mínimo 16)</li>
        <li>Configura las opciones en la barra lateral</li>
        <li>Haz clic en "Generar" y descarga tu PDF</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# BARRA LATERAL - CONFIGURACIÓN
# ============================================================================

st.sidebar.header("⚙️ Configuración")

# Cantidad de tablas
cantidad_tablas = st.sidebar.slider(
    "Cantidad de tablas",
    min_value=1,
    max_value=100,
    value=10,
    help="Número de tablas únicas a generar en el PDF"
)

# Título de la lotería
nombre_loteria = st.sidebar.text_input(
    "Título de la lotería",
    value="Lotería Mexicana",
    max_chars=50,
    help="Aparecerá en la parte superior de cada tabla"
)

# Tamaño de fuente de leyendas
label_font_size = st.sidebar.slider(
    "Tamaño de fuente",
    min_value=16,
    max_value=64,
    value=40,
    help="Tamaño del texto que muestra el nombre de cada imagen"
)

# Incluir páginas de deck
include_deck = st.sidebar.checkbox(
    "Incluir páginas de deck",
    value=True,
    help="Genera páginas con todas las cartas individuales antes de las tablas (con borde decorativo)"
)

# Información adicional en sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📋 Especificaciones
- **Formato**: Cuadrícula 4x4 (16 imágenes por tabla)
- **Tamaño**: Carta (8.5"x11")
- **Calidad**: 300 DPI
- **Formatos aceptados**: JPG, PNG, JPEG
- **Leyendas**: Automáticas desde nombre de archivo
""")

st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Tip**: Nombra tus archivos apropiadamente (ej: `el pato.png`)")

# ============================================================================
# ÁREA PRINCIPAL - UPLOAD DE IMÁGENES
# ============================================================================

st.header("📤 Subir Imágenes")

uploaded_files = st.file_uploader(
    "Arrastra tus imágenes aquí o haz clic para seleccionarlas",
    type=['png', 'jpg', 'jpeg'],
    accept_multiple_files=True,
    help=f"Necesitas al menos {IMAGES_PER_CARD} imágenes. Los nombres de archivo se usarán como leyendas."
)

# ============================================================================
# MOSTRAR PREVIEW DE IMÁGENES
# ============================================================================

if uploaded_files:
    num_files = len(uploaded_files)
    st.success(f"✅ **{num_files} imágenes cargadas**")

    # Mostrar preview de las primeras 16 imágenes
    st.subheader("Vista previa")

    # Crear grid de imágenes (4x4 para mostrar)
    preview_limit = min(16, len(uploaded_files))
    cols_per_row = 4

    for i in range(0, preview_limit, cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < preview_limit:
                with cols[j]:
                    file = uploaded_files[idx]
                    st.image(file, caption=file.name, use_column_width=True)

    if num_files > 16:
        st.info(f"ℹ️ Mostrando 16 de {num_files} imágenes. Todas serán usadas para generar las tablas.")

    st.markdown("---")

    # ============================================================================
    # BOTÓN DE GENERACIÓN
    # ============================================================================

    if num_files >= IMAGES_PER_CARD:
        st.header("🎨 Generar Tablas")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            if st.button(
                "🚀 Generar Tablas de Lotería",
                type="primary",
                use_container_width=True
            ):
                with st.spinner(f"Generando {cantidad_tablas} tablas... Por favor espera."):
                    try:
                        # Generar PDF
                        pdf_bytes = generate_loteria_pdf(
                            uploaded_files,
                            cantidad_tablas,
                            nombre_loteria,
                            label_font_size,
                            include_deck
                        )

                        # Guardar en session state para persistencia
                        st.session_state['pdf_bytes'] = pdf_bytes
                        st.session_state['generated'] = True

                        st.success("🎉 ¡PDF generado exitosamente!")
                        st.balloons()

                    except ValueError as e:
                        st.error(f"❌ Error: {e}")
                    except Exception as e:
                        st.error(f"❌ Error inesperado: {e}")

        # Mostrar botón de descarga si ya se generó el PDF
        if st.session_state.get('generated', False):
            st.markdown("---")
            st.header("📥 Descargar PDF")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(
                    label="⬇️ Descargar loteria_completa.pdf",
                    data=st.session_state['pdf_bytes'],
                    file_name="loteria_completa.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            # Resumen de lo generado
            st.markdown("---")
            st.subheader("📊 Resumen")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de tablas", cantidad_tablas)
            with col2:
                st.metric("Imágenes por tabla", IMAGES_PER_CARD)
            with col3:
                st.metric("Imágenes disponibles", num_files)

    else:
        # Advertencia si faltan imágenes
        st.warning(f"⚠️ **Necesitas al menos {IMAGES_PER_CARD} imágenes para generar las tablas.**")
        st.info(f"Actualmente tienes {num_files} imagen{'es' if num_files != 1 else ''}. Te faltan {IMAGES_PER_CARD - num_files}.")

else:
    # Estado inicial - sin archivos subidos
    st.info("👆 Sube tus imágenes para comenzar")

    # Mostrar ejemplo de uso
    with st.expander("ℹ️ ¿Cómo funciona?"):
        st.markdown("""
        ### Pasos para generar tu lotería:

        1. **Prepara tus imágenes**
           - Nombra los archivos apropiadamente (ej: `el pato.png`, `la sirena.jpg`)
           - El nombre del archivo aparecerá como leyenda en cada imagen
           - Necesitas mínimo 16 imágenes diferentes

        2. **Configura las opciones** en la barra lateral:
           - Cantidad de tablas a generar
           - Título que aparecerá en cada tabla
           - Tamaño de la fuente de las leyendas

        3. **Sube las imágenes** arrastrándolas o haciendo clic en "Browse files"

        4. **Genera el PDF** haciendo clic en el botón

        5. **Descarga tu archivo** listo para imprimir

        ### Características:
        - ✅ Cuadrícula 4x4 (16 imágenes por tabla)
        - ✅ Selección aleatoria (sin duplicados por tabla)
        - ✅ Leyendas automáticas desde nombres de archivo
        - ✅ Calidad profesional 300 DPI
        - ✅ Tamaño carta (8.5"x11")
        """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>Generador de Tablas de Lotería | Hecho con ❤️ usando Streamlit</p>
</div>
""", unsafe_allow_html=True)
