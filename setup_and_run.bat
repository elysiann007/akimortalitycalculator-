@echo off
REM Quick setup and run script for ICU Mortality Prediction Pipeline
REM For Windows

echo ========================================
echo ICU Mortality Prediction - Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment exists
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✓ Virtual environment activated
echo.

echo Installing dependencies...
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo ✓ Dependencies installed
echo.

REM Check if data file exists
if not exist "data\deu_icu_mortality.csv" (
    echo WARNING: Data file not found at data\deu_icu_mortality.csv
    echo Please place your CSV file there before running the pipeline.
    echo.
    pause
) else (
    echo ✓ Data file found
    echo.
    echo Ready to run! Select an option:
    echo 1. Run training pipeline (src\app.py)
    echo 2. Run full monolithic pipeline (full_pipeline.py)
    echo 3. Launch Streamlit web app (streamlit_app.py)
    echo 4. Exit
    echo.
    
    set /p choice="Enter your choice (1-4): "
    
    if "%choice%"=="1" (
        echo.
        echo Running training pipeline...
        python src\app.py
    ) else if "%choice%"=="2" (
        echo.
        echo Running full monolithic pipeline...
        python full_pipeline.py
    ) else if "%choice%"=="3" (
        echo.
        echo Launching Streamlit web app...
        streamlit run streamlit_app.py
    ) else if "%choice%"=="4" (
        echo Exiting...
        exit /b 0
    ) else (
        echo Invalid choice
        pause
    )
)

pause
