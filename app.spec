# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src\\app.py'],  # Script principal
    pathex=['C:\\Users\\LUANVITOR\\OneDrive - Welington Henrique Baggio\\Área de Trabalho\\Geral\\00. Works\\LE_Helper'],  # Caminho do projeto
    binaries=[],
    datas=[
        ('C:\\Users\\LUANVITOR\\OneDrive - Welington Henrique Baggio\\Área de Trabalho\\Geral\\00. Works\\LE_Helper\\src\\resources', 'resources'),  # Inclui a pasta "resources"
        ('C:\\Users\\LUANVITOR\\OneDrive - Welington Henrique Baggio\\Área de Trabalho\\Geral\\00. Works\\LE_Helper\\src', 'src'),  # Inclui a pasta "src"
    ],
    hiddenimports=[
        'openpyxl',  # Módulo para manipulação de planilhas Excel
        'PyPDF2',    # Módulo para manipulação de PDFs
        'PyQt6',     # Módulo para interface gráfica
        'selenium',  # Módulo para automação de navegadores
        'webdriver_manager',  # Módulo para gerenciamento de drivers do Selenium
    ],
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
    name='LE_Helper',  # Nome do executável
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Oculta o console (para aplicativos GUI)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='C:\\Users\\LUANVITOR\\OneDrive - Welington Henrique Baggio\\Área de Trabalho\\Geral\\00. Works\\LE_Helper\\src\\resources\\logo.ico',  # Caminho completo do ícone
)