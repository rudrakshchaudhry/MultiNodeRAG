#!/usr/bin/env python3
"""
Test script for RAG API hosting on Unity server
"""

import requests
import json
import time
import sys

def test_rag_api(base_url):
    """Test the RAG API endpoints"""
    print(f"🧪 Testing RAG API at {base_url}")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n🔍 Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed: {health_data['status']}")
            print(f"   RAG System: {health_data['rag_system']}")
            print(f"   Model Provider: {health_data['model_provider']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Supported models
    print("\n🔍 Testing Models Endpoint...")
    try:
        response = requests.get(f"{base_url}/models", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            print("✅ Models endpoint working:")
            for provider in models_data['providers']:
                print(f"   {provider['name']}: {', '.join(provider['models'][:3])}...")
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Models endpoint error: {e}")
    
    # Test 3: Query endpoint
    print("\n🔍 Testing Query Endpoint...")
    test_queries = [
        "What is 2 + 2?",
        "Explain the Central Limit Theorem",
        "What is machine learning?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Test Query {i}: {query}")
        try:
            response = requests.post(
                f"{base_url}/query",
                json={
                    "query": query,
                    "query_metadata": {"test": True, "query_number": i}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Response received:")
                print(f"      Answer: {data['answer'][:100]}...")
                print(f"      Used RAG: {data['used_rag']}")
                print(f"      Complexity Score: {data['complexity_score']:.2f}")
                print(f"      Model Used: {data['model_used']}")
                print(f"      Response Time: {data['performance_metrics']['total_time']:.2f}s")
            else:
                print(f"   ❌ Query failed: {response.status_code}")
                print(f"      Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Query error: {e}")
    
    print("\n🎉 RAG API testing completed!")
    return True

def main():
    """Main test function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        # Try to get the URL from the hosting management
        print("🔍 Looking for active RAG API hosting...")
        try:
            import subprocess
            result = subprocess.run(['./manage_rag_hosting.sh', 'url'], 
                                  capture_output=True, text=True, cwd='.')
            if 'API Base URL:' in result.stdout:
                for line in result.stdout.split('\n'):
                    if 'API Base URL:' in line:
                        base_url = line.split('API Base URL: ')[1].strip()
                        break
                else:
                    print("❌ No active RAG API hosting found")
                    print("💡 Start hosting with: ./run_system.sh host")
                    return
            else:
                print("❌ No active RAG API hosting found")
                print("💡 Start hosting with: ./run_system.sh host")
                return
        except Exception as e:
            print(f"❌ Error checking hosting status: {e}")
            print("💡 Start hosting with: ./run_system.sh host")
            return
    
    print(f"🌐 Testing RAG API at: {base_url}")
    success = test_rag_api(base_url)
    
    if success:
        print("\n✅ RAG API is working correctly!")
        print(f"🔗 You can now use this URL in your Next.js app:")
        print(f"   NEXT_PUBLIC_RAG_API_URL={base_url}")
    else:
        print("\n❌ RAG API testing failed!")
        print("💡 Check the logs with: ./manage_rag_hosting.sh logs")

if __name__ == "__main__":
    main()
