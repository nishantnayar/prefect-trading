#!/usr/bin/env python3
"""
Alternative Service Starter with Worker Delays
This script starts services with delays between worker startups to reduce database contention.
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path
import threading
import logging
from typing import List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServiceManagerWithDelays:
    """Manages Prefect server, Prefect workers, Streamlit UI, and MLflow server processes with delays."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.processes: List[subprocess.Popen] = []
        self.running = False
        
    def start_prefect_server(self) -> subprocess.Popen:
        """Start Prefect server in background."""
        logger.info("Starting Prefect server...")
        
        # Change to project root directory
        os.chdir(self.project_root)
        
        # Start Prefect server
        process = subprocess.Popen(
            [sys.executable, "-m", "prefect", "server", "start"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        logger.info(f"Prefect server started with PID: {process.pid}")
        return process
    
    def start_prefect_worker(self, pool: str, work_queue: str = "default") -> subprocess.Popen:
        """Start Prefect worker in background."""
        logger.info(f"Starting Prefect worker for pool '{pool}'...")
        
        # Change to project root directory
        os.chdir(self.project_root)
        
        # Start Prefect worker
        process = subprocess.Popen(
            [
                sys.executable, "-m", "prefect", "worker", "start",
                "--pool", pool,
                "--work-queue", work_queue
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        logger.info(f"Prefect worker ({pool}) started with PID: {process.pid}")
        return process
    
    def start_mlflow_server(self) -> subprocess.Popen:
        """Start MLflow server in background."""
        logger.info("Starting MLflow server...")
        
        # Change to project root directory
        os.chdir(self.project_root)
        
        # Start MLflow server
        process = subprocess.Popen(
            [
                sys.executable, "-m", "mlflow", "server",
                "--backend-store-uri", "postgresql://postgres:nishant@localhost/mlflow_db",
                "--default-artifact-root", "file:./mlruns",
                "--host", "0.0.0.0",
                "--port", "5000"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        logger.info(f"MLflow server started with PID: {process.pid}")
        return process
    
    def start_streamlit_ui(self) -> subprocess.Popen:
        """Start Streamlit UI in background."""
        logger.info("Starting Streamlit UI...")
        
        # Change to project root directory
        os.chdir(self.project_root)
        
        # Start Streamlit UI
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "src/ui/main.py", "--server.port", "8501"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        logger.info(f"Streamlit UI started with PID: {process.pid}")
        return process
    
    def monitor_process(self, process: subprocess.Popen, name: str):
        """Monitor a process and log its output."""
        while process.poll() is None and self.running:
            # Read stdout
            if process.stdout:
                line = process.stdout.readline()
                if line:
                    logger.info(f"[{name}] {line.strip()}")
            
            # Read stderr
            if process.stderr:
                line = process.stderr.readline()
                if line:
                    logger.warning(f"[{name}] {line.strip()}")
            
            time.sleep(0.1)
    
    def start_services(self):
        """Start Prefect server, Prefect workers, Streamlit UI, and MLflow server with delays."""
        try:
            logger.info("Starting trading system services with worker delays...")
            self.running = True
            
            # Start Prefect server
            prefect_process = self.start_prefect_server()
            self.processes.append(prefect_process)
            
            # Wait longer for Prefect to initialize
            logger.info("Waiting for Prefect server to initialize...")
            time.sleep(10)
            
            # Start Prefect workers with delays between each
            logger.info("Starting Prefect workers with delays...")
            
            # Start Daily Worker first
            daily_worker_process = self.start_prefect_worker("daily")
            self.processes.append(daily_worker_process)
            time.sleep(5)  # Wait 5 seconds between workers
            
            # Start Realtime Worker
            realtime_worker_process = self.start_prefect_worker("realtime")
            self.processes.append(realtime_worker_process)
            time.sleep(5)  # Wait 5 seconds between workers
            
            # Start End-of-Day Worker
            endofday_worker_process = self.start_prefect_worker("endofday")
            self.processes.append(endofday_worker_process)
            time.sleep(5)  # Wait 5 seconds between workers
            
            # Start Hourly Worker
            hourly_worker_process = self.start_prefect_worker("hourly")
            self.processes.append(hourly_worker_process)
            
            # Wait for workers to initialize
            logger.info("Waiting for Prefect workers to initialize...")
            time.sleep(5)
            
            # Start MLflow server
            mlflow_process = self.start_mlflow_server()
            self.processes.append(mlflow_process)
            
            # Wait for MLflow to initialize
            logger.info("Waiting for MLflow server to initialize...")
            time.sleep(5)
            
            # Start Streamlit UI
            streamlit_process = self.start_streamlit_ui()
            self.processes.append(streamlit_process)
            
            # Start monitoring threads
            prefect_monitor = threading.Thread(
                target=self.monitor_process, 
                args=(prefect_process, "Prefect"),
                daemon=True
            )
            daily_worker_monitor = threading.Thread(
                target=self.monitor_process, 
                args=(daily_worker_process, "DailyWorker"),
                daemon=True
            )
            realtime_worker_monitor = threading.Thread(
                target=self.monitor_process, 
                args=(realtime_worker_process, "RealtimeWorker"),
                daemon=True
            )
            endofday_worker_monitor = threading.Thread(
                target=self.monitor_process, 
                args=(endofday_worker_process, "EndOfDayWorker"),
                daemon=True
            )
            hourly_worker_monitor = threading.Thread(
                target=self.monitor_process, 
                args=(hourly_worker_process, "HourlyWorker"),
                daemon=True
            )
            mlflow_monitor = threading.Thread(
                target=self.monitor_process, 
                args=(mlflow_process, "MLflow"),
                daemon=True
            )
            streamlit_monitor = threading.Thread(
                target=self.monitor_process, 
                args=(streamlit_process, "Streamlit"),
                daemon=True
            )
            
            prefect_monitor.start()
            daily_worker_monitor.start()
            realtime_worker_monitor.start()
            endofday_worker_monitor.start()
            hourly_worker_monitor.start()
            mlflow_monitor.start()
            streamlit_monitor.start()
            
            logger.info("✅ All services started successfully!")
            logger.info("🌐 Streamlit UI: http://localhost:8501")
            logger.info("🔧 Prefect UI: http://localhost:4200")
            logger.info("🤖 MLflow UI: http://localhost:5000")
            logger.info("⚙️ Prefect Workers (started with delays):")
            logger.info("   - Daily Worker: daily pool, default queue")
            logger.info("   - Realtime Worker: realtime pool, default queue")
            logger.info("   - End-of-Day Worker: endofday pool, default queue")
            logger.info("   - Hourly Worker: hourly pool, default queue")
            logger.info("Press Ctrl+C to stop all services")
            
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
                
                # Check if any process has died
                for process in self.processes:
                    if process.poll() is not None:
                        logger.error(f"Process {process.pid} has terminated unexpectedly")
                        self.stop_services()
                        return
                        
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping services...")
            self.stop_services()
        except Exception as e:
            logger.error(f"Error starting services: {e}")
            self.stop_services()
    
    def stop_services(self):
        """Stop all running services."""
        logger.info("Stopping all services...")
        self.running = False
        
        for process in self.processes:
            if process.poll() is None:  # Process is still running
                logger.info(f"Terminating process {process.pid}")
                try:
                    process.terminate()
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Process {process.pid} didn't terminate gracefully, killing...")
                    process.kill()
                except Exception as e:
                    logger.error(f"Error stopping process {process.pid}: {e}")
        
        self.processes.clear()
        logger.info("All services stopped")


def main():
    """Main entry point."""
    print("🚀 Trading System Service Manager (with Worker Delays)")
    print("=" * 55)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   Current directory:", os.getcwd())
        print("   Expected to find: main.py")
        sys.exit(1)
    
    # Check if required packages are installed
    try:
        import prefect
        import streamlit
        import mlflow
    except ImportError as e:
        print(f"❌ Error: Missing required package: {e}")
        print("   Please install requirements: pip install -r config/requirements.txt")
        sys.exit(1)
    
    # Create and start service manager
    manager = ServiceManagerWithDelays()
    
    try:
        manager.start_services()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 