# -*- mode: python ; coding: utf-8 -*-
import PyInstaller.config
import os
import site
from PyInstaller.building.datastruct import Tree

PyInstaller.config.CONF['distpath'] = './release'

block_cipher = None
path = os.getcwd()

# ----------------------------------------------------------------------
# Explicit pywin32 bundling (robust for onefile and for guarded imports)
# ----------------------------------------------------------------------
site_pkgs = site.getsitepackages()[0]
win32_dir = os.path.join(site_pkgs, "win32")
pywin32_sys_dir = os.path.join(site_pkgs, "pywin32_system32")

extra_binaries = []
extra_datas = []

# Bundle win32 extension modules (win32event.pyd, win32api.pyd, etc.)
# Use typecode='BINARY' because these are extension modules.
if os.path.isdir(win32_dir):
    extra_binaries += Tree(win32_dir, prefix="win32", typecode="BINARY")

# Bundle companion DLLs (pythoncom*.dll, pywintypes*.dll, etc.)
if os.path.isdir(pywin32_sys_dir):
    extra_binaries += Tree(pywin32_sys_dir, prefix="pywin32_system32", typecode="BINARY")

a = Analysis(
    ['..\\main.py'],
    pathex=[path + '\\..\\MF_run_counter'],
    binaries=extra_binaries,
    datas=extra_datas,
    hiddenimports=[
        "win32event",
        "win32api",
        "win32con",
        "pythoncom",
        "pywintypes",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

# Your existing data files
a.datas += [('d2icon.png', path+'\\..\\MF_run_counter\\assets\\d2icon.png', 'DATA')]
a.datas += [('run_sound.wav', path+'\\..\\MF_run_counter\\assets\\run_sound.wav', 'DATA')]
a.datas += [('icon.ico', path+'\\..\\MF_run_counter\\assets\\icon.ico', 'DATA')]
a.datas += [('item_library.csv', path+'\\..\\MF_run_counter\\assets\\item_library.csv', 'DATA')]
a.datas += [('stat_map.csv', path+'\\..\\MF_run_counter\\assets\\stat_map.csv', 'DATA')]
a.datas += [('theme_colors.csv', path+'\\..\\MF_run_counter\\assets\\theme_colors.csv', 'DATA')]
a.datas += [('caret-down.png', path+'\\..\\MF_run_counter\\assets\\caret-down.png', 'DATA')]
a.datas += [('caret-up.png', path+'\\..\\MF_run_counter\\assets\\caret-up.png', 'DATA')]
a.datas += [('about_icon.png', path+'\\..\\MF_run_counter\\assets\\about_icon.png', 'DATA')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# One-file EXE: include binaries/zipfiles/datas in the EXE call (as you already do)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mf_timer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=path+'\\assets\\icon.ico'
)
