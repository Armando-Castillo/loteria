# Generador de Lotería - Versión Web 🌐

Interfaz web para generar tablas de lotería profesionales desde tu navegador.

## Características

- ✅ **Interfaz moderna y fácil de usar**
- ✅ **Drag & drop** de imágenes
- ✅ **Configuración en tiempo real** (cantidad, título, tamaño de fuente)
- ✅ **Preview** de imágenes subidas
- ✅ **Descarga directa** del PDF generado
- ✅ **Sin almacenamiento en la nube** - Todo procesado en tiempo real
- ✅ **Gratis** para desplegar en Streamlit Cloud

## Ejecutar Localmente

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar la aplicación

```bash
streamlit run app.py
```

### 3. Abrir en el navegador

La aplicación se abrirá automáticamente en http://localhost:8501

## Uso de la Aplicación

### Paso 1: Preparar tus imágenes

- Nombra los archivos apropiadamente (ej: `el pato.png`, `la sirena.jpg`)
- El nombre del archivo se mostrará como leyenda en cada imagen
- Necesitas mínimo **16 imágenes** diferentes

### Paso 2: Configurar opciones

En la barra lateral puedes ajustar:
- **Cantidad de tablas**: De 1 a 100 tablas
- **Título**: Aparecerá en la parte superior de cada tabla
- **Tamaño de fuente**: De 16 a 48 puntos

### Paso 3: Subir imágenes

- Arrastra tus imágenes al área de carga
- O haz clic en "Browse files" para seleccionarlas
- Verás un preview de las primeras 16 imágenes

### Paso 4: Generar

- Haz clic en "🚀 Generar Tablas de Lotería"
- Espera mientras se procesan (usualmente unos segundos)
- Aparecerá el botón de descarga cuando esté listo

### Paso 5: Descargar

- Haz clic en "⬇️ Descargar loteria_completa.pdf"
- El archivo se descargará automáticamente
- ¡Listo para imprimir!

## Desplegar en Streamlit Cloud (GRATIS)

### Requisitos previos

1. Cuenta de GitHub
2. Tu proyecto en un repositorio GitHub

### Pasos para desplegar

#### 1. Crear repositorio en GitHub

```bash
# Si aún no tienes git inicializado
git init

# Agregar archivos
git add .

# Crear commit
git commit -m "Add Streamlit web app for Lotería generator"

# Conectar con tu repositorio (reemplaza con tu URL)
git remote add origin https://github.com/tu-usuario/loteria.git

# Subir a GitHub
git push -u origin main
```

#### 2. Desplegar en Streamlit Cloud

1. Ve a https://share.streamlit.io
2. Haz clic en "Sign in with GitHub"
3. Autoriza Streamlit Cloud
4. Haz clic en "New app"
5. Selecciona tu repositorio: `tu-usuario/loteria`
6. Branch: `main`
7. Main file path: `app.py`
8. Haz clic en "Deploy!"

#### 3. Obtener URL pública

- Streamlit generará una URL automáticamente
- Formato: `https://tu-usuario-loteria-app-xxx.streamlit.app`
- Comparte esta URL con quien quieras

### Actualizar la app desplegada

Simplemente haz push a GitHub:

```bash
git add .
git commit -m "Update app"
git push
```

Streamlit Cloud detectará los cambios y actualizará automáticamente.

## Opciones de Despliegue Alternativas

### Hugging Face Spaces (También gratis)

1. Crea una cuenta en https://huggingface.co
2. Crea un nuevo Space
3. Selecciona "Streamlit" como SDK
4. Sube tus archivos o conecta con GitHub
5. La app se despliega automáticamente

### Render (Free Tier)

1. Crea una cuenta en https://render.com
2. Crea un nuevo "Web Service"
3. Conecta tu repositorio GitHub
4. Build command: `pip install -r requirements.txt`
5. Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Estructura del Proyecto Web

```
loteria/
├── app.py                      # Aplicación Streamlit principal
├── loteria_core.py             # Lógica del generador
├── generar_loteria.py          # CLI (sigue funcionando)
├── requirements.txt            # Dependencias (incluye streamlit)
├── .streamlit/
│   └── config.toml            # Configuración de Streamlit
├── README.md                   # Docs para versión CLI
└── README_WEB.md              # Este archivo (docs versión web)
```

## Configuración Avanzada

### Límite de carga de archivos

Edita `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 200  # Tamaño máximo en MB
```

### Tema personalizado

Edita `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

## Solución de Problemas

### Error: "Uploaded file exceeds maxUploadSize"

**Solución**: Aumenta el límite en `.streamlit/config.toml` o reduce el tamaño/cantidad de imágenes.

### La app se reinicia al generar muchas tablas

**Solución**: Esto es normal en el free tier. Reduce la cantidad de tablas o considera un tier pagado.

### Error al instalar dependencias

**Solución**:
```bash
# Actualizar pip
pip install --upgrade pip

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### La app no se conecta localmente

**Solución**:
```bash
# Verificar que Streamlit esté instalado
streamlit --version

# Ejecutar con verbose
streamlit run app.py --logger.level=debug
```

## Comparación CLI vs Web

| Característica | CLI | Web |
|---------------|-----|-----|
| **Facilidad de uso** | Requiere terminal | Solo navegador |
| **Configuración** | Editar código o args | Interface gráfica |
| **Compartir** | Script Python | URL pública |
| **Costo** | Gratis (local) | Gratis (Streamlit Cloud) |
| **Velocidad** | Más rápido | Ligeramente más lento |
| **Instalación** | Python + deps | Solo navegador (web) |

## Limitaciones del Free Tier

### Streamlit Cloud
- ✅ **1 GB RAM** - Suficiente para este proyecto
- ✅ **CPU compartida** - Adecuada para uso moderado
- ⚠️ **Límite de usuarios simultáneos** - ~10-20 users
- ⚠️ **Inactividad** - App se apaga después de 7 días sin uso (se reactiva al acceder)

### Hugging Face Spaces
- ✅ **2 vCPU** - Buen rendimiento
- ✅ **16 GB RAM** - Más que suficiente
- ⚠️ **Tiempo de ejecución** - 48 horas de inactividad

### Render
- ✅ **512 MB RAM** - Puede ser justo pero funciona
- ⚠️ **Spin down** - Se apaga después de 15 min de inactividad
- ⚠️ **Startup lento** - Tarda ~30 seg en reactivarse

## FAQ

**P: ¿Puedo usar la versión CLI y web al mismo tiempo?**
R: Sí, son completamente independientes. El CLI (`generar_loteria.py`) sigue funcionando.

**P: ¿Las imágenes se guardan en algún servidor?**
R: No. Se procesan en memoria y se eliminan inmediatamente después de generar el PDF.

**P: ¿Cuánto cuesta desplegar?**
R: Gratis en Streamlit Cloud, Hugging Face Spaces, o Render (free tier).

**P: ¿Cuántas imágenes puedo subir?**
R: Hasta 200 MB en total (configurable). En la práctica, puedes subir cientos de imágenes.

**P: ¿Funciona en móvil?**
R: Sí, la interfaz es responsive y funciona en tablets y smartphones.

**P: ¿Puedo personalizar el diseño de las tablas desde la web?**
R: Actualmente solo puedes cambiar cantidad, título y tamaño de fuente. Para más personalización, usa el CLI.

## Recursos Adicionales

- [Documentación de Streamlit](https://docs.streamlit.io)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Galería de apps Streamlit](https://streamlit.io/gallery)

## Soporte

¿Problemas o preguntas?

1. Revisa la sección de "Solución de problemas"
2. Verifica los logs en la terminal o en el dashboard de Streamlit Cloud
3. Asegúrate de tener las versiones correctas de las dependencias

---

**¡Disfruta creando tus tablas de lotería desde el navegador!** 🎉
