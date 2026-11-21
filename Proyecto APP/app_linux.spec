# -*- mode: python ; coding: utf-8 -*-
"""
Especificación de PyInstaller para compilar la aplicación Flet en Linux.
Utiliza collect_all('flet') para asegurar la inclusión de binarios de Flutter,
archivos de datos e importaciones dinámicas necesarias en Linux.
"""
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

# Recolección automática de dependencias de Flet (binarios, datas y módulos ocultos)
flet_datas, flet_binaries, flet_hiddenimports = collect_all('flet')

# Lista de archivos de datos a incluir en el paquete
datas = []

# Incluir la carpeta 'assets' si existe en el proyecto
if os.path.exists('assets'):
    datas.append(('assets', 'assets'))

# Incluir archivos de base de datos si existen en el proyecto
if os.path.exists('data'):
    datas.append(('data', 'data'))
elif os.path.exists('gastos.db'):
    datas.append(('gastos.db', '.'))

# Integrar los recursos recolectados de flet
datas += flet_datas
binaries = [] + flet_binaries
hiddenimports = [] + flet_hiddenimports

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ControlDeGastos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
