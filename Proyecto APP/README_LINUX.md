# Guía de Compilación y Ejecución en Linux (Ubuntu)

Instrucciones para compilar y ejecutar **Control de Gastos** como binario independiente en Ubuntu / Debian utilizando PyInstaller.

---

## 1. Instalar dependencias del sistema con `apt`

Actualiza los repositorios e instala las herramientas necesarias para compilar con PyInstaller y ejecutar la interfaz gráfica basada en GTK:

```bash
sudo apt update && sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    binutils \
    libc-bin \
    patchelf \
    build-essential \
    libgtk-3-0 \
    libsecret-1-0 \
    libgdk-pixbuf-2.0-0 \
    zenity
```

---

## 2. Crear y activar el entorno virtual (`venv`)

En la raíz del proyecto, crea un entorno virtual e instala las dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Compilar la aplicación con PyInstaller

Empaqueta la aplicación usando el archivo de especificación `app_linux.spec`:

```bash
pyinstaller app_linux.spec --clean
```

El ejecutable resultante se generará en el directorio `dist/ControlDeGastos`.

---

## 4. Asignar permisos y ejecutar

Otorga permisos de ejecución al binario generado y ejecuta la aplicación:

```bash
chmod +x dist/ControlDeGastos
./dist/ControlDeGastos
```

> **Nota:** La base de datos persistirá sus datos automáticamente en la carpeta `data/` junto al ejecutable o directorio de trabajo.
