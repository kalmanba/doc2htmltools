# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect everything from bs4 automatically
datas, binaries, hiddenimports = collect_all('bs4')

# Add requests explicitly to hidden imports
hiddenimports.append('requests')
hiddenimports.append('chardet')

a = Analysis(
    ['doc2htmltools.py'],
    pathex=[os.path.abspath('.')],  # current directory
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
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
    name='doc2htmltools',
    debug=False,
    strip=False,
    upx=True,
    console=True,
    onefile=True,
)

