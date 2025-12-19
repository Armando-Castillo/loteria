"""
Lotería Core - Lógica del generador de tablas de lotería
Módulo reutilizable para CLI y web app
"""

import os
import random
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import img2pdf
from io import BytesIO

# ============================================================================
# CONSTANTES - Parámetros de diseño y layout
# ============================================================================
GRID_SIZE = 4  # Cuadrícula 4x4
IMAGES_PER_CARD = GRID_SIZE * GRID_SIZE  # 16 imágenes por tabla

# Dimensiones de página (300 DPI para impresión de calidad)
PAGE_WIDTH = 2550   # 8.5 pulgadas * 300 DPI
PAGE_HEIGHT = 3300  # 11 pulgadas * 300 DPI

# Espacios y márgenes
TITLE_HEIGHT = 200
FOLIO_HEIGHT = 80
MARGIN_TOP = 100
MARGIN_BOTTOM = 100
MARGIN_LEFT = 150
MARGIN_RIGHT = 150

# Diseño de cuadrícula
GAP_BETWEEN_IMAGES = 15  # Margen blanco entre imágenes

# Colores
COLOR_BACKGROUND = (255, 255, 255)  # Blanco
COLOR_TEXT = (0, 0, 0)  # Negro

# Leyenda de imagen
LABEL_PADDING_BOTTOM = 35  # Espacio desde el fondo de la celda
LABEL_OUTLINE_WIDTH = 2  # Grosor del contorno negro

# Extensiones de imagen válidas
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png'}


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def resize_image_to_fit(image, target_width, target_height):
    """
    Redimensiona una imagen para que quepa dentro de las dimensiones especificadas,
    manteniendo la relación de aspecto. Centra la imagen en un fondo blanco.

    Args:
        image (PIL.Image): Imagen a redimensionar
        target_width (int): Ancho objetivo en pixels
        target_height (int): Alto objetivo en pixels

    Returns:
        PIL.Image: Imagen redimensionada con fondo blanco
    """
    # Calcular el factor de escala manteniendo aspecto
    scale = min(target_width / image.width, target_height / image.height)
    new_width = int(image.width * scale)
    new_height = int(image.height * scale)

    # Redimensionar la imagen con alta calidad
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Crear fondo blanco
    background = Image.new('RGB', (target_width, target_height), COLOR_BACKGROUND)

    # Centrar la imagen redimensionada
    offset_x = (target_width - new_width) // 2
    offset_y = (target_height - new_height) // 2
    background.paste(resized, (offset_x, offset_y))

    return background


def draw_text_with_outline(draw, position, text, font, fill_color=(255, 255, 255), outline_color=(0, 0, 0), outline_width=2):
    """
    Dibuja texto con contorno para mejor legibilidad sobre cualquier fondo.

    Args:
        draw: Objeto ImageDraw
        position: Tupla (x, y) con la posición del texto
        text: Texto a dibujar
        font: Fuente a usar
        fill_color: Color del texto principal (default: blanco)
        outline_color: Color del contorno (default: negro)
        outline_width: Grosor del contorno en pixels (default: 2)
    """
    x, y = position

    # Dibujar contorno (texto desplazado en todas direcciones)
    for offset_x in range(-outline_width, outline_width + 1):
        for offset_y in range(-outline_width, outline_width + 1):
            if offset_x != 0 or offset_y != 0:
                draw.text((x + offset_x, y + offset_y), text, fill=outline_color, font=font)

    # Dibujar texto principal encima
    draw.text((x, y), text, fill=fill_color, font=font)


def create_card_image(image_paths, title, folio_number, label_font_size=32):
    """
    Genera una tabla de lotería completa con 16 imágenes en cuadrícula 4x4.

    Args:
        image_paths (list): Lista de 16 rutas a imágenes
        title (str): Título de la lotería
        folio_number (int): Número de folio de la tabla
        label_font_size (int): Tamaño de fuente para las leyendas

    Returns:
        PIL.Image: Imagen de la tabla completa
    """
    # Crear lienzo blanco
    canvas = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGHT), COLOR_BACKGROUND)
    draw = ImageDraw.Draw(canvas)

    # Calcular espacio disponible para la cuadrícula
    available_width = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
    available_height = PAGE_HEIGHT - TITLE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM - FOLIO_HEIGHT

    # Calcular tamaño de cada celda
    cell_width = (available_width - (GRID_SIZE - 1) * GAP_BETWEEN_IMAGES) // GRID_SIZE
    cell_height = (available_height - (GRID_SIZE - 1) * GAP_BETWEEN_IMAGES) // GRID_SIZE

    # Las imágenes ocupan todo el espacio de la celda
    inner_width = cell_width
    inner_height = cell_height

    # Añadir título
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
    except:
        try:
            font_title = ImageFont.truetype("Arial.ttf", 80)
        except:
            font_title = ImageFont.load_default()

    # Dibujar título centrado
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (PAGE_WIDTH - title_width) // 2
    title_y = MARGIN_TOP // 2
    draw.text((title_x, title_y), title, fill=COLOR_TEXT, font=font_title)

    # Añadir número de folio en la esquina superior derecha
    try:
        font_folio = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        try:
            font_folio = ImageFont.truetype("Arial.ttf", 40)
        except:
            font_folio = ImageFont.load_default()

    folio_text = f"Tabla #{folio_number:02d}"
    folio_bbox = draw.textbbox((0, 0), folio_text, font=font_folio)
    folio_width = folio_bbox[2] - folio_bbox[0]
    folio_x = PAGE_WIDTH - MARGIN_RIGHT - folio_width
    folio_y = MARGIN_TOP // 2
    draw.text((folio_x, folio_y), folio_text, fill=COLOR_TEXT, font=font_folio)

    # Posición inicial de la cuadrícula
    grid_start_y = MARGIN_TOP + TITLE_HEIGHT
    grid_start_x = MARGIN_LEFT

    # Generar cuadrícula 4x4
    image_index = 0
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            # Cargar y procesar imagen
            try:
                img = Image.open(image_paths[image_index])
                # Convertir a RGB si es necesario
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Redimensionar imagen
                resized_img = resize_image_to_fit(img, inner_width, inner_height)

                # Calcular posición de la celda
                cell_x = grid_start_x + col * (cell_width + GAP_BETWEEN_IMAGES)
                cell_y = grid_start_y + row * (cell_height + GAP_BETWEEN_IMAGES)

                # Pegar imagen ocupando todo el espacio de la celda
                canvas.paste(resized_img, (cell_x, cell_y))

                # Agregar leyenda con nombre del archivo
                filename = Path(image_paths[image_index]).stem
                if filename:
                    try:
                        # Cargar fuente para leyenda
                        font_label = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", label_font_size)
                    except:
                        try:
                            font_label = ImageFont.truetype("Arial.ttf", label_font_size)
                        except:
                            font_label = ImageFont.load_default()

                    # Calcular posición del texto (centrado horizontalmente, parte inferior de la celda)
                    label_bbox = draw.textbbox((0, 0), filename, font=font_label)
                    label_width = label_bbox[2] - label_bbox[0]
                    label_height = label_bbox[3] - label_bbox[1]
                    label_x = cell_x + (cell_width - label_width) // 2
                    label_y = cell_y + cell_height - LABEL_PADDING_BOTTOM - label_height

                    # Dibujar texto con contorno para máxima legibilidad
                    draw_text_with_outline(draw, (label_x, label_y), filename, font_label,
                                         fill_color=(255, 255, 255),
                                         outline_color=(0, 0, 0),
                                         outline_width=LABEL_OUTLINE_WIDTH)

                img.close()

            except Exception as e:
                print(f"⚠️  Error procesando imagen {image_paths[image_index]}: {e}")

            image_index += 1

    return canvas


def load_images_from_uploads(uploaded_files):
    """
    Procesa archivos subidos y los guarda temporalmente.

    Args:
        uploaded_files: Lista de archivos subidos (Streamlit UploadedFile objects)

    Returns:
        tuple: (temp_dir, image_paths) - Directorio temporal y lista de rutas a imágenes
    """
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    image_paths = []

    for uploaded_file in uploaded_files:
        # Verificar extensión
        file_ext = Path(uploaded_file.name).suffix.lower()
        if file_ext in VALID_EXTENSIONS:
            # Guardar archivo temporalmente
            temp_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            image_paths.append(temp_path)

    return temp_dir, image_paths


def generate_loteria_pdf(uploaded_files, cantidad_tablas=10, nombre_loteria="Lotería Mexicana", label_font_size=32):
    """
    Genera PDF de lotería y lo retorna como bytes.

    Args:
        uploaded_files: Lista de archivos de imagen subidos
        cantidad_tablas (int): Número de tablas a generar
        nombre_loteria (str): Título de la lotería
        label_font_size (int): Tamaño de fuente de leyendas

    Returns:
        bytes: Contenido del PDF generado

    Raises:
        ValueError: Si no hay suficientes imágenes
    """
    # Procesar archivos subidos
    temp_dir, all_images = load_images_from_uploads(uploaded_files)

    try:
        # Validar cantidad de imágenes
        if len(all_images) < IMAGES_PER_CARD:
            raise ValueError(
                f"Se necesitan al menos {IMAGES_PER_CARD} imágenes, pero solo se encontraron {len(all_images)}."
            )

        # Crear directorio temporal para tablas
        cards_temp_dir = tempfile.mkdtemp()
        temp_card_paths = []

        # Generar tablas
        for i in range(1, cantidad_tablas + 1):
            # Seleccionar 16 imágenes aleatorias sin duplicados
            selected_images = random.sample(all_images, IMAGES_PER_CARD)

            # Crear tabla
            card_image = create_card_image(selected_images, nombre_loteria, i, label_font_size)

            # Guardar tabla temporalmente como PNG
            temp_card_path = os.path.join(cards_temp_dir, f"tabla_{i:03d}.png")
            card_image.save(temp_card_path, dpi=(300, 300))
            temp_card_paths.append(temp_card_path)

        # Generar PDF en memoria
        pdf_bytes = img2pdf.convert(temp_card_paths)

        # Limpiar archivos temporales de tablas
        for temp_path in temp_card_paths:
            try:
                os.remove(temp_path)
            except:
                pass
        try:
            os.rmdir(cards_temp_dir)
        except:
            pass

        return pdf_bytes

    finally:
        # Limpiar archivos temporales de imágenes subidas
        for img_path in all_images:
            try:
                os.remove(img_path)
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass
