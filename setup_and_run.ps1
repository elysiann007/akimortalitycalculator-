# PowerShell setup script for ICU Mortality Prediction Pipeline
# Run with: powershell -ExecutionPolicy Bypass -File setup_and_run.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ICU Mortality Prediction - Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Please install Python 3.9 or higher." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Create venv if needed
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment exists" -ForegroundColor Green
}

Write-Host ""

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to upgrade pip" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Check data file
if (-not (Test-Path "data\deu_icu_mortality.csv")) {
    Write-Host "WARNING: Data file not found at data\deu_icu_mortality.csv" -ForegroundColor Yellow
    Write-Host "Please place your CSV file there before running the pipeline." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to continue"
} else {
    Write-Host "✓ Data file found" -ForegroundColor Green
    Write-Host ""
}

# Menu
Write-Host "Ready to run! Select an option:" -ForegroundColor Cyan
Write-Host "1. Run training pipeline (src\app.py)" -ForegroundColor White
Write-Host "2. Run full monolithic pipeline (full_pipeline.py)" -ForegroundColor White
Write-Host "3. Launch Streamlit web app (streamlit_app.py)" -ForegroundColor White
Write-Host "4. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Running training pipeline..." -ForegroundColor Green
        python src\app.py
    }
    "2" {
        Write-Host ""
        Write-Host "Running full monolithic pipeline..." -ForegroundColor Green
        python full_pipeline.py
    }
    "3" {
        Write-Host ""
        Write-Host "Launching Streamlit web app..." -ForegroundColor Green
        Write-Host "The app will open in your browser at http://localhost:8501" -ForegroundColor Yellow
        streamlit run streamlit_app.py
    }
    "4" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 0
    }
    default {
        Write-Host "Invalid choice" -ForegroundColor Red
    }
}

Read-Host "Press Enter to exit"
