# -*- mode: python3 -*-

block_cipher = None


a = Analysis(['lights.py'],
             pathex=['../lifx-lan-gui'],
             binaries=[],
             datas=[('*.gif', '.')],
             hiddenimports=['numpy', 'cv2', 'scipy._lib.messagestream'],
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
          console=False , icon='lifxgui.ico')
		  
app = BUNDLE(exe,
          name='LifxLanGUI.app',
          icon='lifxgui.icns',
          bundle_identifier=None)
