# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['facerecognition_VER2.py'],
    pathex=[],
    binaries=[],
    datas=[('I:\\A_project\\haarcascade_frontalface_default.xml', '.'), ('I:\\A_project\\known_faces', 'known_faces')],
    hiddenimports=[],
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
    name='facerecognition_VER2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
