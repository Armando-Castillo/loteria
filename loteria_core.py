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


def wrap_text(text, font, max_width, draw):
    """
    Divide el texto en múltiples líneas si excede el ancho máximo.

    Args:
        text (str): Texto a dividir
        font: Fuente a usar
        max_width (int): Ancho máximo permitido
        draw: Objeto ImageDraw para medir el texto

    Returns:
        list: Lista de líneas de texto que caben en el ancho especificado
    """
    # Si el texto cabe en una línea, retornarlo tal cual
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]

    if text_width <= max_width:
        return [text]

    # Dividir texto en palabras
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        # Probar agregar la palabra a la línea actual
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = bbox[2] - bbox[0]

        if test_width <= max_width:
            current_line.append(word)
        else:
            # Si la línea actual tiene palabras, guardarla
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # Si una sola palabra es muy larga, dividirla
                lines.append(word)

    # Agregar la última línea
    if current_line:
        lines.append(' '.join(current_line))

    return lines


def draw_multiline_text_with_outline(draw, position, lines, font, fill_color=(255, 255, 255), outline_color=(0, 0, 0), outline_width=2, line_spacing=5):
    """
    Dibuja texto multilínea con contorno.

    Args:
        draw: Objeto ImageDraw
        position: Tupla (x, y) con la posición inicial del texto
        lines: Lista de líneas de texto
        font: Fuente a usar
        fill_color: Color del texto principal
        outline_color: Color del contorno
        outline_width: Grosor del contorno
        line_spacing: Espacio entre líneas en pixels
    """
    x, y = position

    for i, line in enumerate(lines):
        # Calcular altura de la línea
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]

        # Posición Y de esta línea
        line_y = y + i * (line_height + line_spacing)

        # Dibujar la línea con contorno
        draw_text_with_outline(draw, (x, line_y), line, font, fill_color, outline_color, outline_width)


def create_card_image(image_paths, title, folio_number, label_font_size=40):
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

                    # Calcular ancho máximo para el texto (con padding a los lados)
                    max_text_width = cell_width - 20  # 10px padding a cada lado

                    # Dividir texto en múltiples líneas si es necesario
                    text_lines = wrap_text(filename, font_label, max_text_width, draw)

                    # Calcular altura total necesaria para todas las líneas
                    total_text_height = 0
                    line_heights = []
                    for line in text_lines:
                        bbox = draw.textbbox((0, 0), line, font=font_label)
                        line_height = bbox[3] - bbox[1]
                        line_heights.append(line_height)
                        total_text_height += line_height

                    # Agregar espaciado entre líneas
                    line_spacing = 5
                    if len(text_lines) > 1:
                        total_text_height += (len(text_lines) - 1) * line_spacing

                    # Calcular posición Y inicial (ajustada para centrar todo el bloque de texto)
                    label_y = cell_y + cell_height - LABEL_PADDING_BOTTOM - total_text_height

                    # Dibujar cada línea centrada horizontalmente
                    current_y = label_y
                    for i, line in enumerate(text_lines):
                        bbox = draw.textbbox((0, 0), line, font=font_label)
                        line_width = bbox[2] - bbox[0]
                        line_x = cell_x + (cell_width - line_width) // 2

                        # Dibujar texto con contorno para máxima legibilidad
                        draw_text_with_outline(draw, (line_x, current_y), line, font_label,
                                             fill_color=(255, 255, 255),
                                             outline_color=(0, 0, 0),
                                             outline_width=LABEL_OUTLINE_WIDTH)

                        current_y += line_heights[i] + line_spacing

                img.close()

            except Exception as e:
                print(f"⚠️  Error procesando imagen {image_paths[image_index]}: {e}")

            image_index += 1

    return canvas


def create_deck_page(image_paths, label_font_size=40, page_number=None):
    """
    Genera una página con cartas individuales del deck en cuadrícula 4x4.

    Args:
        image_paths (list): Lista de hasta 16 rutas a imágenes para esta página
        label_font_size (int): Tamaño de fuente para las leyendas
        page_number (int): Número de página del deck (opcional)

    Returns:
        PIL.Image: Imagen de la página del deck
    """
    # Crear lienzo blanco
    canvas = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGHT), COLOR_BACKGROUND)
    draw = ImageDraw.Draw(canvas)

    # Calcular espacio disponible (sin título ni folio, más espacio)
    available_width = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
    available_height = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM

    # Calcular tamaño de cada celda (4x4)
    cell_width = (available_width - (GRID_SIZE - 1) * GAP_BETWEEN_IMAGES) // GRID_SIZE
    cell_height = (available_height - (GRID_SIZE - 1) * GAP_BETWEEN_IMAGES) // GRID_SIZE

    # Constantes para el borde decorativo
    CARD_BORDER_WIDTH = 5  # Borde más grueso que en tablas
    CARD_BORDER_COLOR = (0, 0, 0)  # Negro

    # Espacio interior (imagen + leyenda)
    inner_width = cell_width - (2 * CARD_BORDER_WIDTH) - 10  # -10 para padding
    inner_height = cell_height - (2 * CARD_BORDER_WIDTH) - 10

    # Espacio para leyenda
    legend_height = 50  # Espacio reservado para el texto
    image_height = inner_height - legend_height

    # Posición inicial de la cuadrícula
    grid_start_x = MARGIN_LEFT
    grid_start_y = MARGIN_TOP

    # Generar cuadrícula 4x4
    for idx, img_path in enumerate(image_paths):
        if idx >= 16:  # Solo 16 cartas por página
            break

        row = idx // GRID_SIZE
        col = idx % GRID_SIZE

        try:
            # Cargar imagen
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Calcular posición de la celda
            cell_x = grid_start_x + col * (cell_width + GAP_BETWEEN_IMAGES)
            cell_y = grid_start_y + row * (cell_height + GAP_BETWEEN_IMAGES)

            # Dibujar borde decorativo (doble línea)
            # Borde exterior
            draw.rectangle(
                [cell_x, cell_y, cell_x + cell_width, cell_y + cell_height],
                outline=CARD_BORDER_COLOR,
                width=CARD_BORDER_WIDTH
            )

            # Borde interior (efecto doble)
            draw.rectangle(
                [cell_x + 8, cell_y + 8,
                 cell_x + cell_width - 8, cell_y + cell_height - 8],
                outline=CARD_BORDER_COLOR,
                width=2
            )

            # Redimensionar imagen
            resized_img = resize_image_to_fit(img, inner_width, image_height)

            # Posicionar imagen (centrada en el espacio disponible)
            img_x = cell_x + CARD_BORDER_WIDTH + 5
            img_y = cell_y + CARD_BORDER_WIDTH + 5
            canvas.paste(resized_img, (img_x, img_y))

            # Agregar leyenda
            filename = Path(img_path).stem
            if filename:
                try:
                    font_label = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", label_font_size)
                except:
                    try:
                        font_label = ImageFont.truetype("Arial.ttf", label_font_size)
                    except:
                        font_label = ImageFont.load_default()

                # Calcular ancho máximo para el texto (considerando bordes y padding)
                max_text_width = cell_width - (2 * CARD_BORDER_WIDTH) - 20  # Bordes + padding

                # Dividir texto en múltiples líneas si es necesario
                text_lines = wrap_text(filename, font_label, max_text_width, draw)

                # Calcular altura total necesaria para todas las líneas
                total_text_height = 0
                line_heights = []
                for line in text_lines:
                    bbox = draw.textbbox((0, 0), line, font=font_label)
                    line_height = bbox[3] - bbox[1]
                    line_heights.append(line_height)
                    total_text_height += line_height

                # Agregar espaciado entre líneas
                line_spacing = 5
                if len(text_lines) > 1:
                    total_text_height += (len(text_lines) - 1) * line_spacing

                # Calcular posición Y inicial (ajustada para todo el bloque de texto)
                label_y = cell_y + cell_height - LABEL_PADDING_BOTTOM - total_text_height - CARD_BORDER_WIDTH

                # Dibujar cada línea centrada horizontalmente
                current_y = label_y
                for i, line in enumerate(text_lines):
                    bbox = draw.textbbox((0, 0), line, font=font_label)
                    line_width = bbox[2] - bbox[0]
                    line_x = cell_x + (cell_width - line_width) // 2

                    # Dibujar texto con contorno
                    draw_text_with_outline(
                        draw, (line_x, current_y), line, font_label,
                        fill_color=(255, 255, 255),
                        outline_color=(0, 0, 0),
                        outline_width=LABEL_OUTLINE_WIDTH
                    )

                    current_y += line_heights[i] + line_spacing

            img.close()

        except Exception as e:
            print(f"⚠️  Error procesando imagen {img_path}: {e}")

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


def generate_loteria_pdf(uploaded_files, cantidad_tablas=10, nombre_loteria="Lotería Mexicana", label_font_size=40, include_deck=True):
    """
    Genera PDF de lotería con deck de cartas y tablas.

    Args:
        uploaded_files: Lista de archivos de imagen subidos
        cantidad_tablas (int): Número de tablas a generar
        nombre_loteria (str): Título de la lotería
        label_font_size (int): Tamaño de fuente de leyendas
        include_deck (bool): Si True, incluye páginas de deck antes de las tablas

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

        # Crear directorio temporal para todas las páginas
        pages_temp_dir = tempfile.mkdtemp()
        all_page_paths = []

        # ===== GENERAR PÁGINAS DE DECK =====
        if include_deck:
            num_deck_pages = (len(all_images) + 15) // 16  # Redondear hacia arriba

            for page_num in range(num_deck_pages):
                start_idx = page_num * 16
                end_idx = min(start_idx + 16, len(all_images))
                page_images = all_images[start_idx:end_idx]

                # Crear página de deck
                deck_page = create_deck_page(page_images, label_font_size, page_num + 1)

                # Guardar página
                deck_page_path = os.path.join(pages_temp_dir, f"deck_page_{page_num + 1:03d}.png")
                deck_page.save(deck_page_path, dpi=(300, 300))
                all_page_paths.append(deck_page_path)

        # ===== GENERAR TABLAS DE LOTERÍA =====
        for i in range(1, cantidad_tablas + 1):
            # Seleccionar 16 imágenes aleatorias sin duplicados
            selected_images = random.sample(all_images, IMAGES_PER_CARD)

            # Crear tabla
            card_image = create_card_image(selected_images, nombre_loteria, i, label_font_size)

            # Guardar tabla temporalmente como PNG
            temp_card_path = os.path.join(pages_temp_dir, f"tabla_{i:03d}.png")
            card_image.save(temp_card_path, dpi=(300, 300))
            all_page_paths.append(temp_card_path)

        # ===== GENERAR PDF FINAL =====
        pdf_bytes = img2pdf.convert(all_page_paths)

        # Limpiar archivos temporales
        for page_path in all_page_paths:
            try:
                os.remove(page_path)
            except:
                pass
        try:
            os.rmdir(pages_temp_dir)
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
