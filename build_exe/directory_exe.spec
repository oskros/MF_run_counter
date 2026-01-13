# -*- mode: python ; coding: utf-8 -*-
import PyInstaller.config
import os
from PyInstaller.utils.hooks import collect_dynamic_libs
from PyInstaller.building.datastruct import Tree
import site

PyInstaller.config.CONF['distpath'] = './dict_release'

block_cipher = None
path = os.getcwd()

site_pkgs = site.getsitepackages()[0]

# The pywin32 extension modules (win32event.pyd etc.) usually live here:
win32_dir = os.path.join(site_pkgs, "win32")
pywin32_sys_dir = os.path.join(site_pkgs, "pywin32_system32")

extra_datas = []
if os.path.isdir(win32_dir):
    # bundle the entire win32 directory into the app
    extra_datas.append(Tree(win32_dir, prefix="win32"))

extra_binaries = []
# bundle pywin32_system32 DLLs (pythoncomXX.dll/pywintypesXX.dll etc.)
extra_binaries += collect_dynamic_libs("pywin32_system32")

a = Analysis(['..\\main.py'],
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
             noarchive=False)

# your datas...
a.datas += [('d2icon.png', path+'\\..\\MF_run_counter\\media\\d2icon.png', 'Data')]
a.datas += [('run_sound.wav', path+'\\..\\MF_run_counter\\media\\run_sound.wav', 'Data')]
a.datas += [('icon.ico', path+'\\..\\MF_run_counter\\media\\icon.ico', 'Data')]
a.datas += [('item_library.csv', path+'\\..\\MF_run_counter\\media\\item_library.csv', 'Data')]
a.datas += [('stat_map.csv', path+'\\..\\MF_run_counter\\media\\stat_map.csv', 'Data')]
a.datas += [('caret-down.png', path+'\\..\\MF_run_counter\\media\\caret-down.png', 'Data')]
a.datas += [('caret-up.png', path+'\\..\\MF_run_counter\\media\\caret-up.png', 'Data')]
a.datas += [('about_icon.png', path+'\\..\\MF_run_counter\\media\\about_icon.png', 'Data')]
a.datas += [('default_eth_grail_data.json', path+'\\..\\MF_run_counter\\utils\\default_eth_grail_data.json', 'Data')]
a.datas += [('default_grail_data.json', path+'\\..\\MF_run_counter\\utils\\default_grail_data.json', 'Data')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='mf_timer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon=path+'\\media\\icon.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='mf_timer')
