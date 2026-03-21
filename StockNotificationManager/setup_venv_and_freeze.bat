@echo off
setlocal EnableDelayedExpansion

REM Create a virtual environment in the .venv folder
echo Creating virtual environment in .venv...
python -m venv .venv
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment. Ensure Python is installed and on PATH.
    exit /b %ERRORLEVEL%
)

REM Activate the virtual environment
call .venv\Scripts\activate.bat
if "%VIRTUAL_ENV%"=="" (
    echo Failed to activate virtual environment.
    exit /b 1
)

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing PySide6...
pip install PySide6
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install PySide6.
    exit /b %ERRORLEVEL%
)

echo Freezing installed packages to requirements.txt...
pip freeze > requirements.txt

echo Done. Virtual environment is at .venv and requirements.txt was created.
echo To activate the venv later run: .venv\Scripts\activate.bat

endlocal