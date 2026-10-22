from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_data_files

ROOT = Path(SPECPATH).resolve().parent
datas = [
    (str(ROOT / "assets"), "assets"),
    (str(ROOT / "LICENSE"), "."),
    (str(ROOT / "THIRD_PARTY_NOTICES"), "."),
    (str(ROOT / "THIRD_PARTY_LICENSES"), "THIRD_PARTY_LICENSES"),
    (str(ROOT / "src/diskmize/_licenses"), "diskmize/_licenses"),
]

ttk_datas, ttk_binaries, ttk_hidden = collect_all("ttkthemes")
datas += ttk_datas

pillow_datas = collect_data_files("PIL")
datas += pillow_datas

a = Analysis(
    [str(ROOT / "launcher.py")],
    pathex=[str(ROOT / "src")],
    binaries=ttk_binaries,
    datas=datas,
    hiddenimports=sorted(set(ttk_hidden + ["PIL.ImageTk", "PIL._tkinter_finder", "PIL._imagingtk"])),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="diskmize",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="DiskMize",
)
