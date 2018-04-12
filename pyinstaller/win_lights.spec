# -*- mode: python -*-

block_cipher = None


a = Analysis(['lights.py'],
             pathex=['c:\\dev\\lifx-lan-gui','C:\\Users\\Al-nuaimyF\\AppData\\Local\\Programs\\Python\\Python36\\Lib\\site-packages\\scipy\\extra-dll'],
             binaries=[],
             datas=[('bulb_off.gif', 'bulb_on.gif')],
             hiddenimports=['scipy._lib.messagestream'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='lights',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True , icon='lifxgui.ico')
