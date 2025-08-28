import PyInstaller.__main__
import os
import subprocess
import time

# Завершаем запущенные процессы приложения
try:
    subprocess.run(['taskkill', '/f', '/im', 'PowerControlPro.exe'], 
                  capture_output=True, timeout=5)
    time.sleep(2)
except:
    pass

# Сборка приложения
PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name=ShutdownTimer',
    '--noconfirm',
    '--clean'
])