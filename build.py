import PyInstaller.__main__
import os
import shutil

# Очистка предыдущих сборок
folders = ['build', 'dist']
for folder in folders:
    if os.path.exists(folder):
        shutil.rmtree(folder)

# Создание папки assets если её нет
if not os.path.exists("assets"):
    os.makedirs("assets")

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name=PowerControlPro',
    '--add-data=assets;assets',
    '--hidden-import=PIL',
    '--hidden-import=customtkinter',
    '--hidden-import=CTkMessagebox',
    '--noconfirm',
    '--clean'
])