#!/usr/bin/env python
"""
Backend Verification & Testing Script
Tests the GitHub Profile Analyzer backend for proper configuration and functionality

Run from project root: python test_backend.py
"""

import sys
import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
import subprocess
import time

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print_success(f"{description} found: {filepath}")
        return True
    else:
        print_error(f"{description} NOT found: {filepath}")
        return False

def check_env_variables():
    """Check if required environment variables are set"""
    print_header("Environment Variables Check")
    
    # Load .env file
    env_file = Path(".env")
    if not env_file.exists():
        print_warning(".env file not found. Checking system environment variables...")
    else:
        load_dotenv(".env")
        print_success(".env file loaded")
    
    # Check required variables
    github_token = os.getenv("GITHUB_TOKEN", "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    api_host = os.getenv("API_HOST", "127.0.0.1")
    api_port = os.getenv("API_PORT", "8000")
    
    checks = {
        "GITHUB_TOKEN": github_token,
        "API_HOST": api_host,
        "API_PORT": api_port,
    }
    
    all_required = True
    for var, value in checks.items():
        if value:
            # Mask sensitive values
            if "TOKEN" in var or "KEY" in var:
                display_value = value[:10] + "***" + value[-5:] if len(value) > 15 else "***"
            else:
                display_value = value
            print_success(f"{var} = {display_value}")
        else:
            print_error(f"{var} is NOT set")
            all_required = False
    
    if gemini_key:
        print_success(f"GEMINI_API_KEY = {gemini_key[:10]}***{gemini_key[-5:] if len(gemini_key) > 15 else ''}")
    else:
        print_warning("GEMINI_API_KEY is not set (optional - AI insights will be limited)")
    
    return all_required, api_host, int(api_port)

def test_url_parsing():
    """Test the URL parsing logic"""
    print_header("URL Parsing Test")
    
    # Import the function directly
    sys.path.insert(0, str(Path("backend").absolute()))
    
    try:
        from app.api.routes import extract_username
        
        test_cases = [
            ("https://github.com/torvalds", "torvalds"),
            ("github.com/torvalds", "torvalds"),
            ("http://github.com/linus", "linus"),
            ("torvalds", "torvalds"),
            ("octocat-123", "octocat-123"),
        ]
        
        all_passed = True
        for input_val, expected in test_cases:
            try:
                result = extract_username(input_val)
                if result == expected:
                    print_success(f"extract_username('{input_val}') = '{result}'")
                else:
                    print_error(f"extract_username('{input_val}') = '{result}' (expected '{expected}')")
                    all_passed = False
            except Exception as e:
                print_error(f"extract_username('{input_val}') failed: {e}")
                all_passed = False
        
        # Test invalid input
        invalid_cases = ["", "   ", "invalid@@@username", None]
        for invalid_input in invalid_cases:
            if invalid_input is None:
                continue
            try:
                extract_username(invalid_input)
                print_warning(f"extract_username('{invalid_input}') should have raised ValueError")
                all_passed = False
            except ValueError:
                print_success(f"extract_username('{invalid_input}') correctly raised ValueError")
        
        return all_passed
        
    except ImportError as e:
        print_error(f"Could not import extract_username: {e}")
        return False

def test_api_connectivity(api_url):
    """Test API connectivity"""
    print_header("API Connectivity Test")
    
    # Test health check
    try:
        response = requests.get(f"{api_url}/api/health", timeout=5)
        if response.status_code == 200:
            print_success(f"Health check passed: {response.json()}")
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False
    except requests.ConnectionError:
        print_error(f"Could not connect to {api_url}")
        print_warning("Make sure the backend is running:")
        print_warning("  cd backend")
        print_warning("  python -m uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False
    
    # Test root endpoint
    try:
        response = requests.get(f"{api_url}/", timeout=5)
        if response.status_code == 200:
            print_success(f"Root endpoint working: {response.json()['message']}")
        else:
            print_error(f"Root endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Root endpoint error: {e}")
        return False
    
    return True

def test_analysis_endpoint(api_url, github_token):
    """Test the analysis endpoint"""
    print_header("Analysis Endpoint Test")
    
    if not github_token:
        print_error("Cannot test analysis endpoint without GITHUB_TOKEN")
        return False
    
    test_username = "torvalds"  # Always available public profile
    
    print(f"Testing with GitHub profile: {test_username}")
    print("This may take 10-30 seconds...")
    
    try:
        response = requests.get(
            f"{api_url}/api/analyze",
            params={"username": test_username},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Analysis request successful")
            print(f"  - Username: {data.get('username')}")
            print(f"  - Name: {data.get('name', 'N/A')}")
            print(f"  - Followers: {data.get('followers', 'N/A')}")
            print(f"  - Total Score: {data.get('scores', {}).get('total_score', 'N/A')}/100")
            print(f"  - Repositories analyzed: {len(data.get('repositories', []))}")
            return True
        elif response.status_code == 400:
            print_error(f"Bad request: {response.json().get('detail', 'Unknown error')}")
            return False
        elif response.status_code == 404:
            print_error(f"Profile not found: {response.json().get('detail', 'Unknown error')}")
            return False
        elif response.status_code == 500:
            print_error(f"Server error: {response.json().get('detail', 'Unknown error')}")
            print("Check the backend terminal for detailed error message")
            return False
        else:
            print_error(f"Unexpected response: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.Timeout:
        print_error("Request timed out. The analysis might take very long or the server is unresponsive.")
        return False
    except requests.ConnectionError:
        print_error("Could not connect to the API")
        return False
    except Exception as e:
        print_error(f"Error testing analysis: {e}")
        return False

def test_directory_structure():
    """Test the directory structure"""
    print_header("Directory Structure Check")
    
    required_dirs = [
        ("backend", "Backend source directory"),
        ("backend/app", "Main app package"),
        ("backend/app/api", "API routes"),
        ("backend/app/layers", "Data layers"),
        ("backend/app/models", "Database models"),
        ("frontend", "Frontend source directory"),
    ]
    
    all_exist = True
    for directory, description in required_dirs:
        if check_file_exists(directory, description):
            pass
        else:
            all_exist = False
    
    required_files = [
        ("backend/app/main.py", "Backend main file"),
        ("backend/app/api/routes.py", "API routes file"),
        ("frontend/app.py", "Frontend app file"),
        ("requirements.txt", "Python dependencies"),
    ]
    
    for filepath, description in required_files:
        if check_file_exists(filepath, description):
            pass
        else:
            all_exist = False
    
    return all_exist

def main():
    """Main execution"""
    print("\n" + Colors.BOLD + Colors.BLUE)
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   GitHub Profile Analyzer - Backend Verification Script    ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(Colors.RESET)
    
    # Change to project root if not already there
    if not Path("backend").exists():
        print_error("Please run this script from the project root directory")
        sys.exit(1)
    
    # Run all checks
    all_passed = True
    
    # 1. Check directory structure
    if not test_directory_structure():
        all_passed = False
    
    # 2. Check environment variables
    env_ok, api_host, api_port = check_env_variables()
    if not env_ok:
        all_passed = False
    
    # 3. Test URL parsing
    if not test_url_parsing():
        print_warning("URL parsing tests failed - check backend/app/api/routes.py")
        all_passed = False
    
    # 4. Test API connectivity
    api_url = f"http://{api_host}:{api_port}" if api_host != "0.0.0.0" else "http://127.0.0.1:8000"
    if not test_api_connectivity(api_url):
        print_warning("API is not running. Start it with: cd backend && python -m uvicorn app.main:app --reload")
        all_passed = False
    else:
        # 5. Test analysis endpoint (only if API is running)
        github_token = os.getenv("GITHUB_TOKEN", "").strip()
        if github_token:
            if not test_analysis_endpoint(api_url, github_token):
                all_passed = False
    
    # Print summary
    print_header("Test Summary")
    if all_passed:
        print_success("All tests passed! Your backend is properly configured.")
        print("\nNext steps:")
        print("1. Start the frontend: streamlit run frontend/app.py")
        print("2. Open your browser to http://localhost:8501")
        print("3. Try analyzing a GitHub profile!")
    else:
        print_warning("Some tests failed. Please review the output above and fix any issues.")
        print("\nCommon fixes:")
        print("1. Ensure .env file exists with GITHUB_TOKEN set")
        print("2. Make sure the backend is running: cd backend && python -m uvicorn app.main:app --reload")
        print("3. Check that all dependencies are installed: pip install -r requirements.txt")
    
    print("\n")
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
