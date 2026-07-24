@echo off
REM Build script for HexLauncher.exe (Windows)
REM Requires Python 3.14 and PyInstaller installed.

echo Building HexLauncher.exe...
py -3.14 -m PyInstaller --noconfirm --clean hexlauncher.spec
if %errorlevel% neq 0 (
    echo.
    echo Build FAILED.
    pause
    exit /b %errorlevel%
)
echo.
echo Build complete: dist\HexLauncher.exe
pause
