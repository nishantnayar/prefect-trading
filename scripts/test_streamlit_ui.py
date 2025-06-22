#!/usr/bin/env python3
"""
Script to test the Streamlit UI with the new testing results page.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Main function to test the Streamlit UI."""
    project_root = Path(__file__).parent.parent
    
    print("🧪 Testing Streamlit UI with Testing Results Page")
    print("=" * 50)
    
    # Check if streamlit is available
    try:
        import streamlit
        print(f"✅ Streamlit version: {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit not found. Please install it first.")
        return 1
    
    # Check if the testing results component can be imported
    try:
        sys.path.append(str(project_root))
        from src.ui.components.testing_results import render_testing_results
        print("✅ Testing results component imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import testing results component: {e}")
        return 1
    
    # Check if the main app can be imported
    try:
        from src.ui.streamlit_app import main as streamlit_main
        print("✅ Main Streamlit app imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import main Streamlit app: {e}")
        return 1
    
    # Run the unit tests for the testing results component
    print("\n🧪 Running unit tests for testing results component...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            'test/unit/ui/test_testing_results.py',
            '-v'
        ], cwd=project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Unit tests passed")
        else:
            print("❌ Unit tests failed")
            print(result.stdout)
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running unit tests: {e}")
    
    print("\n🚀 To run the Streamlit app with testing results page:")
    print(f"cd {project_root}")
    print("streamlit run src/ui/streamlit_app.py")
    print("\n📋 The testing results page will be available in the 'Testing' tab.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 