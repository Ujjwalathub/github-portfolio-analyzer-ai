#!/usr/bin/env python
"""
Integration test for GitHub Profile Analyzer
Tests the complete flow: config loading → backend startup → API requests
"""

import requests
import json
import sys
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_USERNAMES = ["octocat"]  # Start with smaller profile
TIMEOUT = 120  # Increased for GitHub + Gemini API calls


def test_health_check():
    """Test health check endpoint"""
    print("\n[TEST 1/5] Health Check Endpoint")
    print("-" * 50)
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Status: {data['status']}")
        print(f"✅ Environment: {data['environment']}")
        return True
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False


def test_invalid_username():
    """Test error handling with invalid username"""
    print("\n[TEST 2/5] Error Handling (Invalid Username)")
    print("-" * 50)
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/analyze",
            params={"username": "!!!invalid_username!!!"},
            timeout=TIMEOUT
        )
        assert response.status_code == 400
        data = response.json()
        print(f"✅ Correctly rejected invalid username")
        print(f"✅ Error: {data.get('detail', 'Unknown error')}")
        return True
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False


def test_analyze_user(username: str):
    """Test analysis endpoint with real GitHub user"""
    print(f"\n[TEST 3/5] Analysis - @{username}")
    print("-" * 50)
    try:
        print(f"Requesting analysis for @{username}...")
        response = requests.get(
            f"{API_BASE_URL}/api/analyze",
            params={"username": username},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            required_fields = ["username", "scores", "ai_insights", "repositories"]
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"
            
            # Verify scores
            scores = data["scores"]
            assert "total_score" in scores
            assert "documentation_score" in scores
            assert "technical_depth_score" in scores
            assert "activity_score" in scores
            
            # Verify AI insights
            insights = data["ai_insights"]
            assert "developer_profile" in insights
            assert "strong_signals" in insights
            assert "red_flags" in insights
            assert "improvement_actions" in insights
            assert len(insights.get("strong_signals", [])) >= 1
            assert len(insights.get("improvement_actions", [])) >= 1
            
            print(f"✅ Analysis completed for @{username}")
            print(f"   Total Score: {scores['total_score']:.1f}/100")
            print(f"   Documentation: {scores['documentation_score']:.1f}/100")
            print(f"   Technical Depth: {scores['technical_depth_score']:.1f}/100")
            print(f"   Activity: {scores['activity_score']:.1f}/100")
            print(f"   Developer Profile: {insights['developer_profile']}")
            print(f"   Strong Signals: {len(insights['strong_signals'])}")
            print(f"   Red Flags: {len(insights['red_flags'])}")
            print(f"   Improvements: {len(insights['improvement_actions'])}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout (API took longer than {TIMEOUT}s)")
        return False
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False


def test_leaderboard():
    """Test leaderboard endpoint"""
    print("\n[TEST 4/5] Leaderboard Endpoint")
    print("-" * 50)
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/leaderboard",
            params={"limit": 5},
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            print(f"✅ Leaderboard contains {len(data)} profiles")
            for profile in data[:3]:
                print(f"   Rank {profile['rank']}: @{profile['username']} - {profile['score']:.1f}")
        else:
            print(f"✅ Leaderboard is empty (no analyses stored yet) - This is expected on fresh start")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False


def test_config_loading():
    """Test environment configuration loading"""
    print("\n[TEST 5/5] Configuration Loading")
    print("-" * 50)
    try:
        # Check .env file exists
        env_file = Path("e:\\Github\\github-profile-analyzer\\.env")
        assert env_file.exists(), ".env file not found"
        print(f"✅ .env file exists at {env_file}")
        
        # Check .streamlit config
        streamlit_config = Path("e:\\Github\\github-profile-analyzer\\.streamlit\\config.toml")
        assert streamlit_config.exists(), ".streamlit/config.toml not found"
        print(f"✅ Streamlit config exists (analytics disabled)")
        
        # Verify actual config loading
        from backend.app.core.config import settings
        assert settings.github_token, "GitHub token not loaded"
        assert settings.gemini_api_key, "Gemini API key not loaded"
        print(f"✅ GitHub token loaded")
        print(f"✅ Gemini API key loaded")
        print(f"✅ Database URL: {settings.database_url}")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 50)
    print("GitHub Profile Analyzer - Integration Tests")
    print("=" * 50)
    
    results = {
        "Health Check": test_health_check(),
        "Error Handling": test_invalid_username(),
        "Analysis": test_analyze_user(TEST_USERNAMES[0]),
        "Leaderboard": test_leaderboard(),
        "Config Loading": test_config_loading(),
    }
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Project is ready for submission.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review above.")
        return 1


if __name__ == "__main__":
    # Wait for backend to be ready
    print("Waiting for backend to be ready...")
    for i in range(10):
        try:
            requests.get(f"{API_BASE_URL}/api/health", timeout=2)
            print("✅ Backend is ready!")
            break
        except:
            print(f"  Attempt {i+1}/10... Backend starting...")
            time.sleep(2)
    else:
        print("❌ Backend failed to start after 20 seconds")
        sys.exit(1)
    
    # Run tests
    exit_code = run_all_tests()
    sys.exit(exit_code)
