# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for HexLauncher.

Build with:
    py -3.14 build.py
or
    py -3.14 -m PyInstaller hexlauncher.spec
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('Hex.ico', '.')],
    hiddenimports=[
        'minecraft_launcher_lib',
        'customtkinter',
        'darkdetect',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter.test',
        'unittest',
        'pydoc',
        'doctest',
        'xml.etree',
        'xmlrpc',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HexLauncher',
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
    icon='Hex.ico',
)
