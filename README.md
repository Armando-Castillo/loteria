# Generador de Tablas de Lotería 🎲

Genera tablas de lotería profesionales de 4x4 con imágenes aleatorias en formato PDF listo para imprimir.

## Características

- ✅ Cuadrícula 4x4 (16 imágenes por tabla)
- ✅ Selección aleatoria de imágenes (sin duplicados dentro de cada tabla)
- ✅ **Leyendas automáticas**: Muestra el nombre del archivo debajo de cada imagen
- ✅ Texto con contorno para máxima legibilidad sobre cualquier fondo
- ✅ Bordes negros y márgenes blancos (estilo lotería tradicional)
- ✅ Título personalizable
- ✅ Número de folio en cada tabla
- ✅ **Argumentos de línea de comandos**: Arrastra carpetas o especifica opciones fácilmente
- ✅ Salida en PDF de alta calidad (300 DPI)
- ✅ Tamaño carta (8.5"x11") listo para imprimir

## Requisitos

- Python 3.7 o superior
- Las librerías se instalan con pip (ver instalación)

## Instalación

### 1. Clonar o descargar este proyecto

```bash
cd loteria
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

O manualmente:

```bash
pip install Pillow img2pdf
```

### 3. Preparar tus imágenes

Crea la carpeta `cartas_originales/` y coloca al menos **16 imágenes** en ella:

```bash
mkdir cartas_originales
```

Formatos aceptados: `.jpg`, `.jpeg`, `.png`

## Uso

### Método 1: Uso básico (valores por defecto)

```bash
# Usa la carpeta cartas_originales/ con configuración por defecto
python generar_loteria.py
```

### Método 2: Especificar carpeta diferente

```bash
# Arrastra la carpeta o especifica la ruta
python generar_loteria.py /ruta/a/tus/imagenes
```

### Método 3: Uso completo con todas las opciones

```bash
# Especifica carpeta, cantidad de tablas y título
python generar_loteria.py /ruta/imagenes --cantidad 20 --titulo "Mi Lotería"

# Versión corta con las mismas opciones
python generar_loteria.py /ruta/imagenes -n 20 -t "Lotería Familiar"
```

### Opciones disponibles

| Opción | Forma corta | Descripción | Default |
|--------|-------------|-------------|---------|
| `carpeta` | - | Ruta a la carpeta con imágenes | `cartas_originales` |
| `--cantidad` | `-n` | Número de tablas a generar | `10` |
| `--titulo` | `-t` | Título de la lotería | `"Lotería Mexicana"` |

### Ver ayuda

```bash
python generar_loteria.py --help
```

### Resultado

El PDF se generará en la carpeta `output/`:

```
output/loteria_completa.pdf
```

## Ejemplo de uso completo

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Crear carpeta y agregar imágenes
mkdir cartas_originales
# (Copia tus imágenes a esta carpeta)
# IMPORTANTE: El nombre del archivo se mostrará como leyenda
# Ejemplo: "el pato.png" mostrará "el pato" debajo de la imagen

# 3. Ejecutar el generador (método básico)
python generar_loteria.py

# O con opciones personalizadas
python generar_loteria.py cartas_originales -n 50 -t "Lotería Familiar"

# 4. Tu PDF estará listo en:
# output/loteria_completa.pdf
```

## Leyendas Automáticas

El generador extrae automáticamente el nombre del archivo (sin la extensión) y lo muestra como leyenda debajo de cada imagen:

- **Archivo**: `el pato.png` → **Leyenda**: "el pato"
- **Archivo**: `la sirena.jpg` → **Leyenda**: "la sirena"
- **Archivo**: `el corazón.jpeg` → **Leyenda**: "el corazón"

El texto se muestra en **blanco con contorno negro** para máxima legibilidad sobre cualquier color de imagen.

## Estructura del proyecto

```
loteria/
├── generar_loteria.py          # Script principal
├── requirements.txt            # Dependencias Python
├── README.md                   # Este archivo
├── cartas_originales/          # Coloca tus imágenes aquí (mínimo 16)
│   ├── imagen1.jpg
│   ├── imagen2.png
│   └── ...
└── output/                     # Se crea automáticamente
    └── loteria_completa.pdf   # PDF generado
```

## Especificaciones técnicas

### Dimensiones
- **Tamaño de página**: 8.5" x 11" (carta)
- **Resolución**: 300 DPI (calidad de impresión profesional)
- **Cuadrícula**: 4x4 (16 imágenes por tabla)

### Diseño
- **Borde entre imágenes**: 3px negro
- **Espaciado entre celdas**: 15px blanco
- **Márgenes**: 100-150px
- **Título**: Parte superior, centrado
- **Folio**: Esquina superior derecha (formato "Tabla #01")
- **Leyendas**: Texto blanco con contorno negro, parte inferior de cada celda
- **Fuente de leyenda**: 24pt (ajustable en código)

### Algoritmo
1. Parsea argumentos de línea de comandos (carpeta, cantidad, título)
2. Carga todas las imágenes de la carpeta especificada
3. Para cada tabla:
   - Selecciona 16 imágenes aleatorias (sin duplicados)
   - Redimensiona cada imagen manteniendo proporción
   - Extrae nombre del archivo (sin extensión)
   - Genera cuadrícula 4x4 con bordes y espaciado
   - Dibuja leyenda con nombre del archivo (texto con contorno)
   - Añade título y número de folio
4. Combina todas las tablas en un PDF (una tabla por página)

## Solución de problemas

### Error: "La carpeta 'cartas_originales' no existe"
**Solución**: Crea la carpeta y añade tus imágenes:
```bash
mkdir cartas_originales
```

### Error: "Se necesitan al menos 16 imágenes"
**Solución**: Añade más imágenes a la carpeta `cartas_originales/`. Necesitas mínimo 16 imágenes válidas.

### Error: "La librería img2pdf no está instalada"
**Solución**: Instala las dependencias:
```bash
pip install -r requirements.txt
```

### Las imágenes se ven pixeladas
**Solución**: Usa imágenes de mayor resolución. El script genera PDFs a 300 DPI, así que tus imágenes originales deben tener buena calidad.

### Quiero cambiar el tamaño de la página
**Solución**: Modifica las constantes `PAGE_WIDTH` y `PAGE_HEIGHT` en el archivo `generar_loteria.py`:
```python
# Para tamaño A4 (210x297mm a 300 DPI):
PAGE_WIDTH = 2480   # 210mm * 300 DPI / 25.4
PAGE_HEIGHT = 3508  # 297mm * 300 DPI / 25.4
```

## Personalización avanzada

Si conoces Python, puedes modificar estas constantes en `generar_loteria.py`:

### Colores
- `COLOR_BACKGROUND`: Color de fondo (default: blanco)
- `COLOR_BORDER`: Color de bordes (default: negro)
- `COLOR_TEXT`: Color de texto principal (default: negro)

### Espaciado y márgenes
- `GAP_BETWEEN_IMAGES`: Espacio entre imágenes (default: 15px)
- `BORDER_WIDTH`: Grosor del borde (default: 3px)
- `MARGIN_TOP`, `MARGIN_BOTTOM`, etc.: Márgenes de página

### Leyendas
- `LABEL_FONT_SIZE`: Tamaño de fuente de leyendas (default: 24pt)
- `LABEL_PADDING_BOTTOM`: Espacio desde el fondo de la celda (default: 30px)
- `LABEL_OUTLINE_WIDTH`: Grosor del contorno del texto (default: 2px)

### Cuadrícula
- `GRID_SIZE`: Tamaño de cuadrícula (default: 4 para 4x4)
- `IMAGES_PER_CARD`: Calculado automáticamente (GRID_SIZE * GRID_SIZE)

Todas estas constantes están documentadas en la sección de configuración del script.

## Licencia

Este proyecto es de código abierto. Siéntete libre de modificarlo según tus necesidades.

## Soporte

Si encuentras algún problema o tienes sugerencias, por favor:
1. Verifica que todas las dependencias estén instaladas
2. Asegúrate de tener al menos 16 imágenes en `cartas_originales/`
3. Verifica que las imágenes sean archivos válidos (.jpg, .png, .jpeg)

---

**¡Disfruta creando tus tablas de lotería!** 🎉
