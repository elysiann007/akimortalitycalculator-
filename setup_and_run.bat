@echo off
REM ICU Mortality Prediction - Setup & Run Script

echo ========================================
echo ICU Mortality Prediction - Setup Script
echo ========================================

REM --- If venv exists, skip setup and go straight to menu ---
if exist "venv\Scripts\python.exe" (
    echo Virtual environment found
    goto :run_menu
)

REM --- Find Python ---
python --version >nul 2>&1
if not errorlevel 1 ( set PYTHON=python & goto :create_venv )

if exist "C:\Python312\python.exe" ( set PYTHON=C:\Python312\python.exe & goto :create_venv )
if exist "C:\Python311\python.exe" ( set PYTHON=C:\Python311\python.exe & goto :create_venv )
if exist "C:\Python314\python.exe" ( set PYTHON=C:\Python314\python.exe & goto :create_venv )
if exist "C:\Python310\python.exe" ( set PYTHON=C:\Python310\python.exe & goto :create_venv )
if exist "C:\Python39\python.exe"  ( set PYTHON=C:\Python39\python.exe  & goto :create_venv )

for /d %%P in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%P\python.exe" ( set PYTHON=%%P\python.exe & goto :create_venv )
)

echo ERROR: Python not found. Install Python 3.9+ from https://python.org
pause
exit /b 1

:create_venv
echo Python found: %PYTHON%
echo Creating virtual environment...
%PYTHON% -m venv venv
if errorlevel 1 ( echo ERROR: Failed to create venv & pause & exit /b 1 )

echo Installing dependencies (this may take a few minutes)...
venv\Scripts\python.exe -m pip install --upgrade pip --quiet
venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
if errorlevel 1 ( echo ERROR: Failed to install dependencies & pause & exit /b 1 )
echo Dependencies installed

:run_menu
set PYTHON=venv\Scripts\python.exe
set PYTHONIOENCODING=utf-8
echo.
echo Select an option:
echo 1. Run training pipeline  (src\app.py)
echo 2. Run full pipeline      (full_pipeline.py)
echo 3. Launch Streamlit UI    (streamlit_app.py)
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo Running training pipeline...
    set PYTHONIOENCODING=utf-8 & venv\Scripts\python.exe src\app.py
) else if "%choice%"=="2" (
    echo Running full pipeline...
    set PYTHONIOENCODING=utf-8 & venv\Scripts\python.exe full_pipeline.py
) else if "%choice%"=="3" (
    echo Launching Streamlit web app...
    set PYTHONIOENCODING=utf-8 & venv\Scripts\python.exe -m streamlit run streamlit_app.py
) else if "%choice%"=="4" (
    exit /b 0
) else (
    echo Invalid choice
)

pause
