from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


project_dir = Path.cwd()

datas = [
    (str(project_dir / 'manage.py'), '.'),
    (str(project_dir / 'templates'), 'templates'),
    (str(project_dir / 'static'), 'static'),
    (str(project_dir / 'media'), 'media'),
    (str(project_dir / 'db.sqlite3'), '.'),
]

hiddenimports = collect_submodules('django') + collect_submodules('apps')


a = Analysis(
    ['launcher.py'],
    pathex=[str(project_dir)],
    binaries=[],
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
    [],
    exclude_binaries=True,
    name='CostadoDende',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CostadoDende',
)