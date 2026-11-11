# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/gen_b50.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('assets/fonts/msyh.ttc', 'assets/fonts'),
        ('assets/fonts/msyh.ttc', '.'),
        ('assets/fonts/BarlowCondensed-Regular.ttf', 'assets/fonts'),
        ('assets/fonts/BarlowCondensed-SemiBold.ttf', 'assets/fonts'),
        ('assets/fonts/BarlowCondensed-Bold.ttf', 'assets/fonts'),
        ('assets/fonts/BarlowCondensed-ExtraBold.ttf', 'assets/fonts'),
        ('assets/fonts/OFL-BarlowCondensed.txt', 'assets/fonts'),
        ('assets/backgrounds/sdvx_exceed_gear_key.jpg', 'assets/backgrounds'),
        ('assets/backgrounds/README.md', 'assets/backgrounds'),
    ],
    hiddenimports=['PIL', 'PIL._imagingtk', 'PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'unittest', 'pytest', 'email', 'http',
        'xml', 'pydoc', 'doctest',
        'distutils', 'setuptools', 'pkg_resources', 'pip',
        'multiprocessing', 'concurrent', 'asyncio',
        'sqlite3', 'bz2', 'lzma', 'tarfile',
        'socket', 'ssl', 'selectors',
        'PIL._tkinter_finder', 'PIL.ImageQt', 'PIL.ImageTk',
        'numpy', 'scipy', 'mkl', 'pandas', 'matplotlib',
    ],
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
    name='SDVX_B50',
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
    icon=None,
)
