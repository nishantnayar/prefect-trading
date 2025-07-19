#!/usr/bin/env python3
"""
Test Coverage Analysis
=====================

Analyze test coverage and identify missing tests in the optimized structure.
"""

import os
import sys
from pathlib import Path
from collections import defaultdict

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def get_source_modules():
    """Get all Python modules in the src directory."""
    modules = []
    
    for root, dirs, files in os.walk(src_path):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                # Get relative path from src
                rel_path = Path(root).relative_to(src_path)
                module_path = rel_path / file[:-3]  # Remove .py extension
                modules.append(str(module_path).replace(os.sep, '.'))
    
    return modules


def get_test_files():
    """Get all test files in the test directory."""
    test_files = []
    test_path = Path(__file__).parent
    
    for root, dirs, files in os.walk(test_path):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                # Get relative path from test
                rel_path = Path(root).relative_to(test_path)
                test_path_str = str(rel_path / file[:-3]).replace(os.sep, '.')
                test_files.append(test_path_str)
    
    return test_files


def map_source_to_test_structure():
    """Map source modules to their expected test locations."""
    mapping = {
        # Data sources
        'data.sources.alpaca_daily_loader': 'unit.data.sources.test_alpaca_daily_loader',
        'data.sources.alpaca_historical_loader': 'unit.data.sources.test_alpaca_historical_loader',
        'data.sources.alpaca_websocket': 'unit.data.sources.test_alpaca_websocket',
        'data.sources.configurable_websocket': 'unit.data.sources.test_configurable_websocket',
        'data.sources.data_recycler_server': 'unit.data.sources.test_data_recycler_server',
        'data.sources.hourly_persistence': 'unit.data.sources.test_hourly_persistence',
        'data.sources.news': 'unit.data.sources.test_news',
        'data.sources.portfolio_manager': 'unit.data.sources.test_portfolio_manager',
        'data.sources.symbol_manager': 'unit.data.sources.test_symbol_manager',
        'data.sources.yahoo_finance_loader': 'unit.data.sources.test_yahoo_finance_loader',
        
        # Database
        'database.database_connectivity': 'unit.database.test_database_connectivity',
        
        # ML
        'ml.config': 'unit.ml.test_config',
        'ml.gru_model': 'unit.ml.test_gru_model',
        'ml.model_performance_tracker': 'unit.ml.test_model_performance_tracker',
        'ml.pair_analysis': 'unit.ml.test_pair_analysis',
        'ml.train_gru_models': 'unit.ml.test_train_gru_models',
        
        # UI
        'ui.main': 'unit.ui.test_main',
        'ui.components.company_info': 'unit.ui.components.test_company_info',
        'ui.components.market_data': 'unit.ui.components.test_market_data',
        'ui.components.symbol_selector': 'unit.ui.components.test_symbol_selector',
        'ui.components.testing_results': 'unit.ui.components.test_testing_results',
        
        # Utils
        'utils.config_loader': 'unit.utils.test_config_loader',
        'utils.data_preprocessing_utils': 'unit.utils.test_data_preprocessing_utils',
        'utils.data_recycler_utils': 'unit.utils.test_data_recycler_utils',
        'utils.env_loader': 'unit.utils.test_env_loader',
        'utils.market_hours': 'unit.utils.test_market_hours',
        'utils.websocket_config': 'unit.utils.test_websocket_config',
        
        # Flows
        'flows.preprocessing_flows': 'unit.flows.test_preprocessing_flows',
        'flows.training_flows': 'unit.flows.test_training_flows',
        
        # Root level modules
        'mlflow_manager': 'unit.test_mlflow_manager',
    }
    
    return mapping


def analyze_coverage():
    """Analyze test coverage and generate report."""
    source_modules = get_source_modules()
    test_files = get_test_files()
    mapping = map_source_to_test_structure()
    
    # Track coverage
    covered = []
    missing = []
    extra_tests = []
    
    # Check which source modules have tests
    for source_module, expected_test in mapping.items():
        if expected_test in test_files:
            covered.append(source_module)
        else:
            missing.append(source_module)
    
    # Check for extra test files
    for test_file in test_files:
        if not any(test_file == expected_test for expected_test in mapping.values()):
            extra_tests.append(test_file)
    
    # Generate report
    print("🧪 Test Coverage Analysis")
    print("=" * 50)
    
    print(f"\n📊 Coverage Summary:")
    print(f"Source modules: {len(source_modules)}")
    print(f"Test files: {len(test_files)}")
    print(f"Covered modules: {len(covered)}")
    print(f"Missing tests: {len(missing)}")
    print(f"Extra test files: {len(extra_tests)}")
    
    coverage_percentage = (len(covered) / len(mapping)) * 100 if mapping else 0
    print(f"Coverage: {coverage_percentage:.1f}%")
    
    if missing:
        print(f"\n❌ Missing Tests:")
        for module in missing:
            expected_test = mapping[module]
            print(f"  {module} → {expected_test}")
    
    if extra_tests:
        print(f"\n⚠️  Extra Test Files:")
        for test_file in extra_tests:
            print(f"  {test_file}")
    
    if covered:
        print(f"\n✅ Covered Modules:")
        for module in covered:
            print(f"  {module}")
    
    return {
        'source_modules': source_modules,
        'test_files': test_files,
        'covered': covered,
        'missing': missing,
        'extra_tests': extra_tests,
        'coverage_percentage': coverage_percentage
    }


def generate_test_templates():
    """Generate template test files for missing modules."""
    mapping = map_source_to_test_structure()
    source_modules = get_source_modules()
    
    missing_templates = []
    
    for source_module, expected_test in mapping.items():
        if source_module in source_modules:
            test_path = Path(__file__).parent / expected_test.replace('.', '/') + '.py'
            
            if not test_path.exists():
                missing_templates.append((source_module, expected_test, test_path))
    
    if missing_templates:
        print(f"\n📝 Missing Test Templates ({len(missing_templates)}):")
        for source_module, expected_test, test_path in missing_templates:
            print(f"  {source_module} → {test_path}")
    
    return missing_templates


def main():
    """Main analysis function."""
    print("🔍 Test Coverage Analysis")
    print("=" * 50)
    
    # Analyze coverage
    coverage_data = analyze_coverage()
    
    # Generate templates
    missing_templates = generate_test_templates()
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    print("1. Create missing test files for uncovered modules")
    print("2. Move existing tests to their proper locations")
    print("3. Use shared fixtures to reduce duplication")
    print("4. Add integration tests for external dependencies")
    print("5. Add end-to-end tests for complete workflows")
    
    return coverage_data


if __name__ == "__main__":
    main() 