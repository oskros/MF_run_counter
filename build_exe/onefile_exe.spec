# -*- mode: python ; coding: utf-8 -*-
import PyInstaller.config
PyInstaller.config.CONF['distpath'] = './release'
import os,sys

path = os.getcwd()
block_cipher = None

a = Analysis(['..\\main.py'],
             pathex=[path],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas += [('d2icon.png', path+'\..\\media\\d2icon.png', 'Data')]
a.datas += [('run_sound.wav', path+'\..\\media\\run_sound.wav', 'Data')]
a.datas += [('icon.ico', path+'\..\\media\\icon.ico', 'Data')]
a.datas += [('item_library.csv', path+'\..\\media\\item_library.csv', 'Data')]
a.datas += [('stat_map.csv', path+'\..\\media\\stat_map.csv', 'Data')]
a.datas += [('caret-down.png', path+'\..\\media\\caret-down.png', 'Data')]
a.datas += [('caret-up.png', path+'\..\\media\\caret-up.png', 'Data')]
a.datas += [('about_icon.png', path+'\..\\media\\about_icon.png', 'Data')]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
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
          console=False , icon=path+'\..\\media\\icon.ico')
