@echo off
REM Trading System Service Starter for Windows
REM This script starts both Prefect server and Streamlit UI

echo 🚀 Starting Trading System Services...
echo ======================================

REM Check if we're in the right directory
if not exist "main.py" (
    echo ❌ Error: Please run this script from the project root directory
    echo    Current directory: %CD%
    echo    Expected to find: main.py
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import prefect, streamlit, mlflow" >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Missing required packages
    echo    Please install requirements: pip install -r config/requirements.txt
    pause
    exit /b 1
)

echo ✅ Environment check passed
echo.

REM Start Prefect server in background
echo 🔧 Starting Prefect server...
start "Prefect Server" cmd /k "python -m prefect server start"

REM Wait a moment for Prefect to start
timeout /t 5 /nobreak >nul

REM Start Prefect workers in background
echo ⚙️ Starting Prefect workers...
start "Daily Worker" cmd /k "python -m prefect worker start --pool daily --work-queue default"
start "Realtime Worker" cmd /k "python -m prefect worker start --pool realtime --work-queue default"
start "End-of-Day Worker" cmd /k "python -m prefect worker start --pool endofday --work-queue default"
start "Hourly Worker" cmd /k "python -m prefect worker start --pool hourly --work-queue default"

REM Wait a moment for workers to start
timeout /t 3 /nobreak >nul

REM Start MLflow server in background
echo 🤖 Starting MLflow server...
start "MLflow Server" cmd /k "python -m mlflow server --backend-store-uri postgresql://postgres:nishant@localhost/mlflow_db --default-artifact-root file:./mlruns --host 0.0.0.0 --port 5000"

REM Wait a moment for MLflow to start
timeout /t 3 /nobreak >nul

REM Start Streamlit UI in background
echo 🌐 Starting Streamlit UI...
start "Streamlit UI" cmd /k "python -m streamlit run src/ui/main.py --server.port 8501"

echo.
echo ✅ All services started successfully!
echo 🌐 Streamlit UI: http://localhost:8501
echo 🔧 Prefect UI: http://localhost:4200
echo 🤖 MLflow UI: http://localhost:5000
echo ⚙️ Prefect Workers:
echo    - Daily Worker: daily pool, default queue
echo    - Realtime Worker: realtime pool, default queue
echo    - End-of-Day Worker: endofday pool, default queue
echo    - Hourly Worker: hourly pool, default queue
echo.
echo 💡 Services are running in separate windows
echo    Close those windows to stop the services
echo.
pause 