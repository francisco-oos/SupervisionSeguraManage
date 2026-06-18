@echo off
REM ============================================================
REM Compilación Windows - SupervisionSeguraManager.exe
REM ============================================================
REM Ejecutar desde la raíz del proyecto:
REM   .\build_exe.bat
REM Requiere: pip install -r requirements.txt && pip install pyinstaller

rmdir /S /Q build 2>NUL
rmdir /S /Q dist 2>NUL

pyinstaller --noconfirm --onedir --windowed ^
  --name SupervisionSeguraManager ^
  --add-data "assets;assets" ^
  --add-data "config;config" ^
  app.py

pause
