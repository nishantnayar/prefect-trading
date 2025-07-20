#!/bin/bash

# Trading System Service Starter for Unix/Linux/macOS
# This script starts both Prefect server and Streamlit UI

echo "🚀 Starting Trading System Services..."
echo "======================================"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected to find: main.py"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
if ! python3 -c "import prefect, streamlit, mlflow" &> /dev/null; then
    echo "❌ Error: Missing required packages"
    echo "   Please install requirements: pip install -r config/requirements.txt"
    exit 1
fi

echo "✅ Environment check passed"
echo

# Function to cleanup processes on exit
cleanup() {
    echo
    echo "🛑 Stopping all services..."
    kill $PREFECT_PID $DAILY_WORKER_PID $REALTIME_WORKER_PID $ENDOFDAY_WORKER_PID $HOURLY_WORKER_PID $MLFLOW_PID $STREAMLIT_PID 2>/dev/null
    wait $PREFECT_PID $DAILY_WORKER_PID $REALTIME_WORKER_PID $ENDOFDAY_WORKER_PID $HOURLY_WORKER_PID $MLFLOW_PID $STREAMLIT_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start Prefect server in background
echo "🔧 Starting Prefect server..."
python3 -m prefect server start &
PREFECT_PID=$!

# Wait a moment for Prefect to start
echo "⏳ Waiting for Prefect server to initialize..."
sleep 5

# Start Prefect workers in background
echo "⚙️ Starting Prefect workers..."
python3 -m prefect worker start --pool daily --work-queue default &
DAILY_WORKER_PID=$!

python3 -m prefect worker start --pool realtime --work-queue default &
REALTIME_WORKER_PID=$!

python3 -m prefect worker start --pool endofday --work-queue default &
ENDOFDAY_WORKER_PID=$!

python3 -m prefect worker start --pool hourly --work-queue default &
HOURLY_WORKER_PID=$!

# Wait a moment for workers to start
echo "⏳ Waiting for Prefect workers to initialize..."
sleep 3

# Start MLflow server in background
echo "🤖 Starting MLflow server..."
python3 -m mlflow server --backend-store-uri postgresql://postgres:nishant@localhost/mlflow_db --default-artifact-root file:./mlruns --host 0.0.0.0 --port 5000 &
MLFLOW_PID=$!

# Wait a moment for MLflow to start
echo "⏳ Waiting for MLflow server to initialize..."
sleep 3

# Start Streamlit UI in background
echo "🌐 Starting Streamlit UI..."
python3 -m streamlit run src/ui/main.py --server.port 8501 &
STREAMLIT_PID=$!

echo
echo "✅ All services started successfully!"
echo "🌐 Streamlit UI: http://localhost:8501"
echo "🔧 Prefect UI: http://localhost:4200"
echo "🤖 MLflow UI: http://localhost:5000"
echo "⚙️ Prefect Workers:"
echo "   - Daily Worker: daily pool, default queue"
echo "   - Realtime Worker: realtime pool, default queue"
echo "   - End-of-Day Worker: endofday pool, default queue"
echo "   - Hourly Worker: hourly pool, default queue"
echo
echo "💡 Press Ctrl+C to stop all services"
echo

# Wait for processes
wait $PREFECT_PID $DAILY_WORKER_PID $REALTIME_WORKER_PID $ENDOFDAY_WORKER_PID $HOURLY_WORKER_PID $MLFLOW_PID $STREAMLIT_PID 