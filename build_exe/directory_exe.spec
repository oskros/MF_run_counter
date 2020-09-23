# -*- mode: python ; coding: utf-8 -*-
import PyInstaller.config
PyInstaller.config.CONF['distpath'] = './dict_release'

block_cipher = None


a = Analysis(['C:\\Users\\oskro\\PycharmProjects\\MF_counter_releases\\main.py'],
             pathex=['C:\\Users\\oskro\\PycharmProjects\\MF_counter_releases'],
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
a.datas += [('d2icon.png', 'C:\\Users\\oskro\\PycharmProjects\\MF_counter_releases\\media\\d2icon.png', 'Data')]
a.datas += [('run_sound.wav', 'C:\\Users\\oskro\\PycharmProjects\\MF_counter_releases\\media\\run_sound.wav', 'Data')]
a.datas += [('icon.ico', 'C:\\Users\\oskro\\PycharmProjects\\MF_counter_releases\\media\\icon.ico', 'Data')]
a.datas += [('item_library.csv', 'C:\\Users\\oskro\\PycharmProjects\\MF_counter_releases\\media\\item_library.csv', 'Data')]
a.datas += [('caret-down.png', 'C:\\Users\\oskro\\PycharmProjects\\MF_counter_releases\\media\\caret-down.png', 'Data')]
a.datas += [('caret-up.png', 'C:\\Users\\oskro\\PycharmProjects\\MF_counter_releases\\media\\caret-up.png', 'Data')]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='mf_timer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='C:\\Users\\oskro\\PycharmProjects\\MF_counter_releases\\media\\icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='mf_timer')
