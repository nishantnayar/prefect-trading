#!/usr/bin/env python3
"""
Prefect Trading System - Test Environment Setup
===============================================

Sets up the complete test environment including dependencies and directory structure.
Works with both conda and regular Python environments.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color


def print_status(message):
    """Print a status message in green."""
    print(f"{Colors.GREEN}[INFO]{Colors.NC} {message}")


def print_warning(message):
    """Print a warning message in yellow."""
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")


def print_error(message):
    """Print an error message in red."""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")


def check_command(command, description):
    """Check if a command is available."""
    if shutil.which(command) is None:
        print_error(f"{description} is not installed. Please install {description}.")
        return False
    return True


def get_command_version(command):
    """Get the version of a command."""
    try:
        result = subprocess.run([command, '--version'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "Unknown"


def is_conda_environment():
    """Check if we're running in a conda environment."""
    return 'CONDA_DEFAULT_ENV' in os.environ


def get_conda_info():
    """Get conda environment information."""
    if is_conda_environment():
        env_name = os.environ.get('CONDA_DEFAULT_ENV', 'unknown')
        env_path = os.environ.get('CONDA_PREFIX', 'unknown')
        return env_name, env_path
    return None, None


def install_dependencies():
    """Install production and development dependencies."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Upgrade pip
    print_status("Upgrading pip...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
    except subprocess.CalledProcessError as e:
        print_warning(f"Failed to upgrade pip: {e}")
    
    # Install production dependencies
    print_status("Installing production dependencies...")
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)], check=True)
            print_status("Production dependencies installed.")
        except subprocess.CalledProcessError as e:
            print_warning(f"Failed to install production dependencies: {e}")
    else:
        print_warning(f"requirements.txt not found at {requirements_file}. Skipping production dependencies.")
    
    # Install development dependencies
    print_status("Installing development dependencies...")
    requirements_dev_file = project_root / "requirements-dev.txt"
    if requirements_dev_file.exists():
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_dev_file)], check=True)
            print_status("Development dependencies installed.")
        except subprocess.CalledProcessError as e:
            print_warning(f"Failed to install development dependencies: {e}")
    else:
        print_warning(f"requirements-dev.txt not found at {requirements_dev_file}. Skipping development dependencies.")


def check_pytest():
    """Check if pytest is installed."""
    try:
        result = subprocess.run([sys.executable, '-m', 'pytest', '--version'], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print_status(f"pytest version: {version}")
        return True
    except subprocess.CalledProcessError:
        print_error("pytest installation failed. Please install manually:")
        print("pip install pytest pytest-cov")
        return False


def setup_test_directories():
    """Create test directory structure."""
    print_status("Setting up test directory structure...")
    
    directories = [
        "test/unit/data",
        "test/unit/database",
        "test/integration",
        "test/e2e",
        "test/fixtures"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Add __init__.py files to make them Python packages
        init_file = Path(directory) / "__init__.py"
        if not init_file.exists():
            init_file.touch()
    
    print_status("Test directory structure created.")


def setup_environment_variables():
    """Set up test environment variables."""
    print_status("Setting up test environment variables...")
    
    env_vars = {
        'TESTING': 'true',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'test_trading_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print_status("Environment variables configured.")


def make_scripts_executable():
    """Make Python scripts executable (Unix-like systems only)."""
    if os.name != 'nt':  # Not Windows
        print_status("Making scripts executable...")
        try:
            subprocess.run(['chmod', '+x', 'scripts/run_tests.py'], check=True)
            subprocess.run(['chmod', '+x', 'scripts/setup_test_env.py'], check=True)
            print_status("Scripts made executable.")
        except subprocess.CalledProcessError:
            print_warning("Failed to make scripts executable.")


def main():
    """Main function to set up the test environment."""
    print("Prefect Trading System - Test Environment Setup")
    print("===============================================")
    print()
    
    # Check Python installation
    python_version = get_command_version(sys.executable)
    print_status(f"Python version: {python_version}")
    
    # Check if we're in a conda environment
    if is_conda_environment():
        env_name, env_path = get_conda_info()
        print_status(f"Running in conda environment: {env_name}")
        print_status(f"Conda environment path: {env_path}")
    else:
        print_status("Running in standard Python environment")
    
    # Check pip installation
    if not check_command('pip', 'pip'):
        return False
    
    # Install dependencies
    install_dependencies()
    
    # Check pytest installation
    if not check_pytest():
        return False
    
    # Set up test directories
    setup_test_directories()
    
    # Set up environment variables
    setup_environment_variables()
    
    # Make scripts executable
    make_scripts_executable()
    
    print()
    print_status("Test environment setup completed!")
    print()
    print("Next steps:")
    print("1. Run tests: python scripts/run_tests.py")
    print("2. Run quick tests: python scripts/run_tests.py quick")
    print("3. Run specific tests: python scripts/run_tests.py --help")
    print()
    print("For more information, see README_TESTING.md")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 