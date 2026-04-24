#!/usr/bin/env python3
"""
Automated test runner for AllTalk TTS
Runs all tests with coverage reporting and generates test reports
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"\n❌ {description} FAILED with exit code {result.returncode}")
        return False
    else:
        print(f"\n✅ {description} PASSED")
        return True


def main():
    """Main test runner function"""
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    print("AllTalk TTS Automated Test Runner")
    print("="*60)
    
    # Test results tracking
    results = {
        "api_endpoints": False,
        "xtts_engine": False,
        "piper_engine": False,
        "config": False,
        "model_download_ui": False,
        "all_tests": False
    }
    
    # Run API endpoint tests
    results["api_endpoints"] = run_command(
        ["python", "-m", "pytest", "tests/test_api_endpoints.py", "-v"],
        "API Endpoint Tests"
    )
    
    # Run XTTS engine tests
    results["xtts_engine"] = run_command(
        ["python", "-m", "pytest", "tests/test_xtts_engine.py", "-v"],
        "XTTS Engine Tests"
    )
    
    # Run Piper engine tests
    results["piper_engine"] = run_command(
        ["python", "-m", "pytest", "tests/test_piper_engine.py", "-v"],
        "Piper Engine Tests"
    )
    
    # Run config tests
    if (tests_dir / "test_config.py").exists():
        results["config"] = run_command(
            ["python", "-m", "pytest", "tests/test_config.py", "-v"],
            "Config Tests"
        )
    
    # Run model download UI tests
    if (tests_dir / "test_model_download_ui.py").exists():
        results["model_download_ui"] = run_command(
            ["python", "-m", "pytest", "tests/test_model_download_ui.py", "-v"],
            "Model Download UI Tests"
        )
    
    # Run all tests with coverage
    print(f"\n{'='*60}")
    print("Running all tests with coverage reporting")
    print('='*60)
    results["all_tests"] = run_command(
        ["python", "-m", "pytest", "tests/", "-v", "--cov=.", "--cov-report=html", "--cov-report=term"],
        "All Tests with Coverage"
    )
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    # Calculate overall result
    total_tests = len(results)
    passed_tests = sum(1 for passed in results.values() if passed)
    
    print(f"\nOverall: {passed_tests}/{total_tests} test suites passed")
    
    if results["all_tests"]:
        print("\n📊 Coverage report generated at: htmlcov/index.html")
    
    # Exit with appropriate code
    if all(results.values()):
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
