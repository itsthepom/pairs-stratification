# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
from pathlib import Path

# SPECPATH is automatically provided by PyInstaller and points to the folder containing this .spec file
ROOT = Path(SPECPATH).parent

ttk_datas, ttk_binaries, ttk_hiddenimports = collect_all('ttkbootstrap')

a = Analysis(
    [str(ROOT / 'pairsutility.py')],
    pathex=[str(ROOT)],
    binaries=ttk_binaries,
    datas=[(str(ROOT / 'helpdocs/site/'), 'helpdocs/site')] + ttk_datas,
    hiddenimports=ttk_hiddenimports,
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
    [],
    exclude_binaries=False,
    name='PairsStrat',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / 'resources\\PairsStratificationAppIco.ico'),
    version=str(ROOT / 'version_info.txt')
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='PairsStrat',
)
