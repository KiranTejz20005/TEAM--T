"""
Quick API test script for FinMDA-Bot
Run this after starting the backend to verify everything works.
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    """Test health endpoint."""
    print_section("Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_root():
    """Test root endpoint."""
    print_section("Test 2: Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_chat():
    """Test chat endpoint."""
    print_section("Test 3: Chat Query")
    try:
        data = {
            "query": "What is financial analysis?",
            "session_id": None,
            "document_id": None
        }
        response = requests.post(f"{BASE_URL}/api/v1/chat/query", json=data)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {result.get('response', '')[:200]}...")
        print(f"Model: {result.get('model_used')}")
        print(f"Confidence: {result.get('confidence_score')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_mda_analysis():
    """Test MD&A financial analysis."""
    print_section("Test 4: Financial Analysis")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/mda/analyze-financials")
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Key Metrics: {json.dumps(result.get('key_metrics', {}), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_mda_section():
    """Test MD&A section generation."""
    print_section("Test 5: MD&A Section Generation")
    try:
        data = {
            "section_type": "executive_summary",
            "period": "Q3 2024"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/mda/generate-section",
            params=data
        )
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Section Type: {result.get('section_type')}")
        print(f"Content Preview: {result.get('content', '')[:300]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_mda_full_report():
    """Test full MD&A report generation."""
    print_section("Test 6: Full MD&A Report Generation")
    try:
        data = {
            "period": "Q3 2024"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/mda/generate",
            params=data
        )
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Confidence: {result.get('confidence')}")
        print(f"Generation Time: {result.get('generation_time')}s")
        print(f"Key Metrics Count: {len(result.get('key_metrics', []))}")
        print(f"\nMD&A Draft Preview:")
        print(result.get('md_a_draft', '')[:500])
        print("...")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "🚀"*30)
    print("  FinMDA-Bot API Test Suite")
    print("🚀"*30)
    
    print("\nMake sure the backend is running on http://localhost:8000")
    print("Press Enter to start tests...")
    input()
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Chat Query", test_chat),
        ("Financial Analysis", test_mda_analysis),
        ("MD&A Section", test_mda_section),
        ("Full MD&A Report", test_mda_full_report),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            time.sleep(1)  # Avoid rate limiting
        except Exception as e:
            print(f"❌ Test '{name}' failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your API is working correctly.")
        print("\nNext steps:")
        print("1. Start the frontend: npm start (in frontend directory)")
        print("2. Visit: http://localhost:3000")
        print("3. Try uploading a document and asking questions")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\nCommon issues:")
        print("- Make sure Gemini API key is set in .env file")
        print("- Check backend logs for errors")
        print("- Verify all dependencies are installed")

if __name__ == "__main__":
    main()



