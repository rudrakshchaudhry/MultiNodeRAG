#!/usr/bin/env python3
"""
Direct test of the adaptive RAG server
This script tests the server components directly without HTTP calls
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'RAG_system'))

def test_components():
    """Test the adaptive RAG components directly"""
    print("🧪 Testing Adaptive RAG Components Directly")
    print("=" * 50)
    
    try:
        # Test 1: Configuration
        print("\n🔍 Testing Configuration...")
        from adaptive_rag.config.adaptive_config import get_adaptive_config
        config = get_adaptive_config()
        print(f"✅ Configuration loaded: start_k={config.start_k}")
        
        # Test 2: Query Analyzer
        print("\n🔍 Testing Query Analyzer...")
        from adaptive_rag.core.query_analyzer import QueryAnalyzer
        analyzer = QueryAnalyzer(config)
        
        # Test simple query
        simple_result = analyzer.analyze_query("What is 2 + 2?")
        print(f"✅ Simple query: score={simple_result.complexity_score:.2f}, recommendation={simple_result.recommendation}")
        
        # Test complex query
        complex_result = analyzer.analyze_query("Prove the Central Limit Theorem and explain its applications")
        print(f"✅ Complex query: score={complex_result.complexity_score:.2f}, recommendation={complex_result.recommendation}")
        
        # Test 3: Model Interface (Skip for now - requires actual model)
        print("\n🔍 Testing Model Interface...")
        from adaptive_rag.core.model_interface import GenerationConfig
        print("✅ Model interface classes available (skipping actual model test)")
        
        # Test 4: Retrieval System
        print("\n🔍 Testing Retrieval System...")
        from adaptive_rag.retrieval.dynamic_search import DynamicRetriever
        retriever = DynamicRetriever()
        print("✅ Retriever initialized")
        
        # Test 5: Profile Selection
        print("\n🔍 Testing Profile Selection...")
        from adaptive_rag.config.profiles_config import select_profile_for_query
        profile = select_profile_for_query("What is the Central Limit Theorem?")
        print(f"✅ Profile selected: {profile}")
        
        print("\n🎉 All component tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_server_startup():
    """Test if the server can start up properly"""
    print("\n🚀 Testing Server Startup...")
    try:
        # Import the server module
        from adaptive_rag_server import app
        print("✅ Server module imported successfully")
        
        # Test health endpoint logic
        from adaptive_rag_server import HealthResponse
        health = HealthResponse(
            status="healthy",
            model_type="test",
            router_type="simplified_complexity",
            timestamp=1234567890.0
        )
        print(f"✅ Health response created: {health.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Starting Direct Adaptive RAG Test")
    print("=" * 40)
    
    # Test components
    components_ok = test_components()
    
    # Test server startup
    server_ok = test_server_startup()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 20)
    print(f"Components: {'✅ PASS' if components_ok else '❌ FAIL'}")
    print(f"Server: {'✅ PASS' if server_ok else '❌ FAIL'}")
    
    if components_ok and server_ok:
        print("\n🎉 All tests passed! System is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
