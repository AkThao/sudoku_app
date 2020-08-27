# -*- mode: python -*-

block_cipher = None


a = Analysis(['/Users/akaashthao_home/Programming/PROJECTS/sudoku_app/app_files/src/main/python/main.py'],
             pathex=['/Users/akaashthao_home/Programming/PROJECTS/sudoku_app/app_files/target/PyInstaller'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=['/Users/akaashthao_home/.virtualenvs/backtrack_sudoku_env/lib/python3.6/site-packages/fbs/freeze/hooks'],
             runtime_hooks=['/Users/akaashthao_home/Programming/PROJECTS/sudoku_app/app_files/target/PyInstaller/fbs_pyinstaller_hook.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Sudoku Game',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False , icon='/Users/akaashthao_home/Programming/PROJECTS/sudoku_app/app_files/target/Icon.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='Sudoku Game')
app = BUNDLE(coll,
             name='Sudoku Game.app',
             icon='/Users/akaashthao_home/Programming/PROJECTS/sudoku_app/app_files/target/Icon.icns',
             bundle_identifier='com.akaash.sudokusolver.mac')
