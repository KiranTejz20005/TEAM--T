#!/usr/bin/env python3
"""
Comprehensive test runner for FinMDA-Bot project.
"""
import subprocess
import sys
import os
import json
import time
from pathlib import Path

def run_command(command, cwd=None, timeout=300):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Command timed out after {timeout} seconds',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

def test_backend_imports():
    """Test backend imports."""
    print("🔍 Testing backend imports...")
    
    backend_path = Path("TEAM--T/backend")
    if not backend_path.exists():
        # Test Python imports
        result = run_command(
            "python -c 'import sys; sys.path.append(\".\"); from app.main import app; print(\"Backend imports successful\")'",
            cwd=backend_path
        )
        
        if result['success']:
            print("✅ Backend imports successful")
            return True
        else:
            print(f"❌ Backend imports failed: {result['stderr']}")
            return False
    else:
        print("❌ Backend directory not found")
        return False

def test_frontend_build():
    """Test frontend build."""
    print("🔍 Testing frontend build...")
    
    frontend_path = Path("TEAM--T/frontend")
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check if node_modules exists
    if not (frontend_path / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        install_result = run_command("npm install", cwd=frontend_path, timeout=600)
        if not install_result['success']:
            print(f"❌ Failed to install frontend dependencies: {install_result['stderr']}")
            return False
    
    # Test build
    build_result = run_command("npm run build", cwd=frontend_path, timeout=300)
    if build_result['success']:
        print("✅ Frontend build successful")
        return True
    else:
        print(f"❌ Frontend build failed: {build_result['stderr']}")
        return False

def test_docker_build():
    """Test Docker build."""
    print("🔍 Testing Docker build...")
    
    # Test backend Docker build
    backend_result = run_command(
        "docker build -t finmda-backend .",
        cwd=Path("TEAM--T/backend"),
        timeout=600
    )
    
    if not backend_result['success']:
        print(f"❌ Backend Docker build failed: {backend_result['stderr']}")
        return False
    
    # Test frontend Docker build
    frontend_result = run_command(
        "docker build -t finmda-frontend .",
        cwd=Path("TEAM--T/frontend"),
        timeout=600
    )
    
    if not frontend_result['success']:
        print(f"❌ Frontend Docker build failed: {frontend_result['stderr']}")
        return False
    
    print("✅ Docker builds successful")
    return True

def test_python_tests():
    """Test Python unit tests."""
    print("🔍 Running Python unit tests...")
    
    backend_path = Path("TEAM--T/backend")
    if not backend_path.exists():
        print("❌ Backend directory not found")
        return False
    
    # Install dependencies
    install_result = run_command("pip install -r requirements.txt", cwd=backend_path, timeout=300)
    if not install_result['success']:
        print(f"❌ Failed to install Python dependencies: {install_result['stderr']}")
        return False
    
    # Run tests
    test_result = run_command("python -m pytest tests/ -v", cwd=backend_path, timeout=300)
    if test_result['success']:
        print("✅ Python tests passed")
        return True
    else:
        print(f"❌ Python tests failed: {test_result['stderr']}")
        return False

def test_api_endpoints():
    """Test API endpoints."""
    print("🔍 Testing API endpoints...")
    
    # Start the backend server
    backend_path = Path("TEAM--T/backend")
    server_process = subprocess.Popen(
        ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=backend_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # Wait for server to start
        time.sleep(10)
        
        # Test health endpoint
        health_result = run_command("curl -f http://localhost:8000/api/v1/health", timeout=30)
        if health_result['success']:
            print("✅ API health check passed")
            return True
        else:
            print(f"❌ API health check failed: {health_result['stderr']}")
            return False
    
    finally:
        # Stop the server
        server_process.terminate()
        server_process.wait()

def test_notebooks():
    """Test Jupyter notebooks."""
    print("🔍 Testing Jupyter notebooks...")
    
    notebooks_path = Path("TEAM--T/notebooks")
    if not notebooks_path.exists():
        print("❌ Notebooks directory not found")
        return False
    
    # Find all notebook files
    notebook_files = list(notebooks_path.glob("*.ipynb"))
    
    if not notebook_files:
        print("❌ No notebook files found")
        return False
    
    success_count = 0
    for notebook in notebook_files:
        print(f"📓 Testing {notebook.name}...")
        
        # Convert notebook to Python and run
        result = run_command(
            f"jupyter nbconvert --to python --execute {notebook}",
            cwd=notebooks_path,
            timeout=300
        )
        
        if result['success']:
            print(f"✅ {notebook.name} executed successfully")
            success_count += 1
        else:
            print(f"❌ {notebook.name} failed: {result['stderr']}")
    
    if success_count == len(notebook_files):
        print("✅ All notebooks executed successfully")
        return True
    else:
        print(f"❌ {len(notebook_files) - success_count} notebooks failed")
        return False

def generate_test_report(results):
    """Generate a test report."""
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_tests': len(results),
        'passed_tests': sum(1 for r in results.values() if r),
        'failed_tests': sum(1 for r in results.values() if not r),
        'results': results
    }
    
    # Save report
    with open('TEAM--T/test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

def main():
    """Main test runner."""
    print("🚀 FinMDA-Bot Test Runner")
    print("=" * 50)
    
    # Define tests
    tests = {
        'Backend Imports': test_backend_imports,
        'Frontend Build': test_frontend_build,
        'Docker Build': test_docker_build,
        'Python Tests': test_python_tests,
        'API Endpoints': test_api_endpoints,
        'Notebooks': test_notebooks
    }
    
    results = {}
    
    # Run tests
    for test_name, test_func in tests.items():
        print(f"\n📋 Running {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results[test_name] = False
    
    # Generate report
    report = generate_test_report(results)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"Total Tests: {report['total_tests']}")
    print(f"Passed: {report['passed_tests']}")
    print(f"Failed: {report['failed_tests']}")
    print(f"Success Rate: {(report['passed_tests'] / report['total_tests'] * 100):.1f}%")
    
    print("\n📋 Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    # Save report
    print(f"\n📄 Test report saved to: TEAM--T/test_report.json")
    
    # Exit with appropriate code
    if report['failed_tests'] > 0:
        print("\n❌ Some tests failed. Please check the report for details.")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
