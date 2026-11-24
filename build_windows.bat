@echo off
setlocal
cd /d "%~dp0"

echo [1/3] Checking tools...
python -c "import pyxel" 2>nul
if errorlevel 1 (
    echo Pyxel is missing. Run: pip install pyxel pyinstaller
    exit /b 1
)
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller is missing. Run: pip install pyinstaller
    exit /b 1
)

echo [2/3] Packaging TinyKnight.pyxapp...
if exist build\TinyKnight rmdir /S /Q build\TinyKnight
mkdir build\TinyKnight
copy /Y main.py build\TinyKnight\ >nul
copy /Y art.py build\TinyKnight\ >nul
python -m pyxel package build\TinyKnight build\TinyKnight\main.py
if errorlevel 1 goto :error

echo [3/3] Building Windows executable...
python -m pyxel app2exe TinyKnight.pyxapp
if errorlevel 1 goto :error

if not exist dist mkdir dist
move /Y TinyKnight.pyxapp dist\ >nul
if exist dist\TinyKnight rmdir /S /Q dist\TinyKnight
move /Y TinyKnight dist\

echo.
echo Done: dist\TinyKnight\TinyKnight.exe
echo Share the whole dist\TinyKnight folder, not just the .exe.
exit /b 0

:error
echo.
echo Build failed.
exit /b 1
