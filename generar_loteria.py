#!/usr/bin/env python3
"""
Generador de Tablas de Lotería
Genera tablas de lotería de 4x4 con imágenes aleatorias en formato PDF para impresión.
"""

import os
import sys
import random
import tempfile
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

try:
    import img2pdf
except ImportError:
    print("❌ Error: La librería img2pdf no está instalada.")
    print("Por favor ejecuta: pip install img2pdf")
    sys.exit(1)

# ============================================================================
# CONFIGURACIÓN - Modifica estos valores según tus necesidades
# ============================================================================
CANTIDAD_TABLAS = 10
NOMBRE_LOTERIA = "Lotería Mexicana"

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
BORDER_WIDTH = 3  # Borde negro alrededor de cada imagen
GAP_BETWEEN_IMAGES = 15  # Margen blanco entre imágenes

# Colores
COLOR_BACKGROUND = (255, 255, 255)  # Blanco
COLOR_BORDER = (0, 0, 0)  # Negro
COLOR_TEXT = (0, 0, 0)  # Negro

# Leyenda de imagen
LABEL_FONT_SIZE = 32  # Tamaño de fuente para nombres
LABEL_PADDING_BOTTOM = 35  # Espacio desde el fondo de la celda
LABEL_OUTLINE_WIDTH = 2  # Grosor del contorno negro

# Extensiones de imagen válidas
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

# Carpetas
INPUT_FOLDER = "cartas_originales"
OUTPUT_FOLDER = "output"


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def load_images(folder_path):
    """
    Carga y valida todas las imágenes de la carpeta especificada.

    Args:
        folder_path (str): Ruta a la carpeta con las imágenes

    Returns:
        list: Lista de rutas a archivos de imagen válidos

    Raises:
        FileNotFoundError: Si la carpeta no existe
        ValueError: Si no hay suficientes imágenes
    """
    folder = Path(folder_path)

    # Verificar que la carpeta existe
    if not folder.exists():
        raise FileNotFoundError(
            f"La carpeta '{folder_path}' no existe.\n"
            f"Por favor crea la carpeta y añade al menos {IMAGES_PER_CARD} imágenes."
        )

    # Buscar todas las imágenes válidas
    image_paths = []
    for ext in VALID_EXTENSIONS:
        image_paths.extend(folder.glob(f'*{ext}'))
        image_paths.extend(folder.glob(f'*{ext.upper()}'))

    # Convertir a strings y ordenar
    image_paths = [str(path) for path in image_paths]
    image_paths.sort()

    # Validar cantidad mínima
    if len(image_paths) < IMAGES_PER_CARD:
        raise ValueError(
            f"Se necesitan al menos {IMAGES_PER_CARD} imágenes, pero solo se encontraron {len(image_paths)}.\n"
            f"Por favor añade más imágenes (.jpg, .png, .jpeg) a la carpeta '{folder_path}'."
        )

    # Verificar que las imágenes se puedan abrir
    valid_images = []
    for img_path in image_paths:
        try:
            with Image.open(img_path) as img:
                img.verify()
            valid_images.append(img_path)
        except Exception as e:
            print(f"⚠️  Advertencia: Ignorando imagen corrupta: {img_path}")

    if len(valid_images) < IMAGES_PER_CARD:
        raise ValueError(
            f"Después de validar, solo hay {len(valid_images)} imágenes válidas.\n"
            f"Se necesitan al menos {IMAGES_PER_CARD} imágenes válidas."
        )

    return valid_images


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


def create_card_image(image_paths, title, folio_number):
    """
    Genera una tabla de lotería completa con 16 imágenes en cuadrícula 4x4.

    Args:
        image_paths (list): Lista de 16 rutas a imágenes
        title (str): Título de la lotería
        folio_number (int): Número de folio de la tabla

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
        # Intentar usar una fuente más grande
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
                        font_label = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", LABEL_FONT_SIZE)
                    except:
                        try:
                            font_label = ImageFont.truetype("Arial.ttf", LABEL_FONT_SIZE)
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


def generate_pdf(card_images_paths, output_path):
    """
    Genera un PDF con todas las tablas de lotería.

    Args:
        card_images_paths (list): Lista de rutas a imágenes de tablas
        output_path (str): Ruta donde guardar el PDF
    """
    with open(output_path, "wb") as f:
        # Convertir imágenes a PDF con img2pdf
        # DPI settings para mantener calidad de impresión
        f.write(img2pdf.convert(card_images_paths))


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def parse_arguments():
    """
    Parsea los argumentos de línea de comandos.

    Returns:
        argparse.Namespace: Objeto con los argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description='Generador de Tablas de Lotería - Crea tablas 4x4 con imágenes aleatorias',
        epilog='Ejemplo: python generar_loteria.py /ruta/imagenes --cantidad 20 --titulo "Mi Lotería"'
    )

    parser.add_argument(
        'carpeta',
        nargs='?',
        default=INPUT_FOLDER,
        help=f'Ruta a la carpeta con las imágenes (default: {INPUT_FOLDER})'
    )

    parser.add_argument(
        '-n', '--cantidad',
        type=int,
        default=CANTIDAD_TABLAS,
        help=f'Cantidad de tablas a generar (default: {CANTIDAD_TABLAS})'
    )

    parser.add_argument(
        '-t', '--titulo',
        type=str,
        default=NOMBRE_LOTERIA,
        help=f'Título de la lotería (default: {NOMBRE_LOTERIA})'
    )

    return parser.parse_args()


def main():
    """
    Función principal que orquesta la generación de tablas de lotería.
    """
    # Parsear argumentos de línea de comandos
    args = parse_arguments()
    input_folder = args.carpeta
    cantidad_tablas = args.cantidad
    nombre_loteria = args.titulo

    print("=" * 60)
    print("  GENERADOR DE TABLAS DE LOTERÍA")
    print("=" * 60)
    print()

    # Validar configuración
    if cantidad_tablas <= 0:
        print("❌ Error: La cantidad de tablas debe ser mayor a 0")
        sys.exit(1)

    print(f"📋 Configuración:")
    print(f"   • Carpeta de imágenes: {input_folder}")
    print(f"   • Nombre: {nombre_loteria}")
    print(f"   • Cantidad de tablas: {cantidad_tablas}")
    print(f"   • Imágenes por tabla: {IMAGES_PER_CARD} (4x4)")
    print()

    # Paso 1: Cargar imágenes
    print("📂 Cargando imágenes...")
    try:
        all_images = load_images(input_folder)
        print(f"   ✅ Se encontraron {len(all_images)} imágenes válidas")
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    print()

    # Paso 2: Crear carpeta de salida
    output_dir = Path(OUTPUT_FOLDER)
    output_dir.mkdir(exist_ok=True)

    # Crear carpeta temporal para guardar tablas individuales
    temp_dir = tempfile.mkdtemp()
    temp_card_paths = []

    # Paso 3: Generar tablas
    print(f"🎨 Generando {cantidad_tablas} tablas...")
    print()

    for i in range(1, cantidad_tablas + 1):
        # Seleccionar 16 imágenes aleatorias sin duplicados
        selected_images = random.sample(all_images, IMAGES_PER_CARD)

        # Crear tabla
        card_image = create_card_image(selected_images, nombre_loteria, i)

        # Guardar tabla temporalmente como PNG
        temp_card_path = os.path.join(temp_dir, f"tabla_{i:03d}.png")
        card_image.save(temp_card_path, dpi=(300, 300))
        temp_card_paths.append(temp_card_path)

        # Mostrar progreso
        print(f"   ✅ Tabla {i}/{cantidad_tablas} generada")

    print()

    # Paso 4: Generar PDF
    print("📄 Generando PDF...")
    pdf_path = output_dir / "loteria_completa.pdf"
    try:
        generate_pdf(temp_card_paths, str(pdf_path))
        print(f"   ✅ PDF generado exitosamente")
    except Exception as e:
        print(f"❌ Error generando PDF: {e}")
        sys.exit(1)

    # Limpiar archivos temporales
    for temp_path in temp_card_paths:
        try:
            os.remove(temp_path)
        except:
            pass
    try:
        os.rmdir(temp_dir)
    except:
        pass

    # Paso 5: Resumen
    print()
    print("=" * 60)
    print("✅ ¡PROCESO COMPLETADO EXITOSAMENTE!")
    print("=" * 60)
    print()
    print(f"📁 Archivo generado:")
    print(f"   {pdf_path.absolute()}")
    print()
    print(f"📊 Resumen:")
    print(f"   • Total de tablas: {cantidad_tablas}")
    print(f"   • Imágenes por tabla: {IMAGES_PER_CARD}")
    print(f"   • Carpeta de origen: {input_folder}")
    print(f"   • Formato: PDF (tamaño carta 8.5\"x11\")")
    print(f"   • Calidad: 300 DPI (lista para imprimir)")
    print(f"   • Leyendas: Nombres de archivo incluidos")
    print()
    print("🎉 ¡Tu lotería está lista para imprimir!")
    print()


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
