import PyInstaller.__main__
import os
import shutil

# Очистка предыдущих сборок
folders = ['build', 'dist']
for folder in folders:
    if os.path.exists(folder):
        shutil.rmtree(folder)

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name=ShutdownTimerPro',
    '--icon=assets/icon.ico',
    '--add-data=assets;assets',
    '--hidden-import=PIL',
    '--hidden-import=customtkinter',
    '--noconfirm',
    '--clean'
])