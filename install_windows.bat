@echo off
REM AI Video Transcription Studio - Windows Installer
REM This script installs the application and all dependencies on Windows

echo ==========================================
echo AI Video Transcription Studio - Installer
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo 📋 Please install Python 3.8+ from https://python.org
    echo    Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check if we're in the right directory
if not exist "src" (
    echo ❌ Please run this script from the application root directory
    echo    The script should be in the same folder as the 'src' directory
    pause
    exit /b 1
)

echo.
echo 🔄 Starting installation...
echo.

REM Run the Python setup script
python setup.py
if errorlevel 1 (
    echo ❌ Installation failed
    pause
    exit /b 1
)

echo.
echo 🎉 Installation completed!
echo.
echo 📋 You can now:
echo    1. Use the desktop shortcut to launch the app
echo    2. Or double-click: run_app.bat
echo    3. Or run: python src/main.py
echo.

REM Create a run script
echo @echo off > run_app.bat
echo cd /d "%~dp0" >> run_app.bat
echo venv\Scripts\python.exe src\main.py >> run_app.bat
echo pause >> run_app.bat

echo ✅ Created run_app.bat for easy launching
echo.

pause
