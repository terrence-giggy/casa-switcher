@echo off
echo Casa Switcher Installer
echo =======================

REM 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python found.

REM 2. Install Dependencies
if exist requirements.txt (
    echo Installing dependencies...
    pip install -r "%~dp0requirements.txt"
    if %errorlevel% neq 0 (
        echo Error: Failed to install dependencies.
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed.
) else (
    echo Warning: requirements.txt not found. Skipping dependency installation.
)

REM 3. Create Config if missing
if not exist "%~dp0config.json" (
    echo Creating default config.json...
    (
        echo {
        echo     "this_host_id": 1,
        echo     "trigger_corner": "top-right",
        echo     "safe_corner": "top-left"
        echo }
    ) > "%~dp0config.json"
    echo [OK] Default config created.
) else (
    echo [OK] config.json already exists.
)

REM 4. Create Startup Shortcut
echo Creating startup shortcut...
set "TARGET_SCRIPT=%~dp0start_casa_service.bat"
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\CasaSwitcher.lnk'); $s.TargetPath='%TARGET_SCRIPT%'; $s.Save()"

if %errorlevel% neq 0 (
    echo Error: Failed to create startup shortcut.
    pause
    exit /b 1
)
echo [OK] Startup shortcut created.

echo.
echo =======================
echo Installation Complete!
echo You can now run 'start_casa_service.bat' or restart your computer.
pause
