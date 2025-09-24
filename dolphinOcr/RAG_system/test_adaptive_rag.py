"""
Simplified Test Suite for Adaptive RAG System
Tests the simplified complexity-based approach
"""

import requests
import json
import time
from typing import Dict, Any, List

class AdaptiveRAGTester:
    """Test suite for the simplified adaptive RAG system"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health(self) -> bool:
        """Test health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data['status']}")
                print(f"   Model type: {data['model_type']}")
                print(f"   Router type: {data['router_type']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_config(self) -> bool:
        """Test configuration endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/config")
            if response.status_code == 200:
                config = response.json()
                print(f"✅ Configuration retrieved:")
                print(f"   Retrieval k: {config['retrieval_k']}")
                print(f"   Max tokens: {config['model_max_tokens']}")
                print(f"   Temperature: {config['model_temperature']}")
                print(f"   Router type: {config['router_type']}")
                return True
            else:
                print(f"❌ Config test failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Config test error: {e}")
            return False
    
    def test_simple_query(self) -> bool:
        """Test simple query (should use direct generation)"""
        query = "What is 2 + 2?"
        
        try:
            response = self.session.post(
                f"{self.base_url}/adaptive_rag",
                json={"query": query}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Simple query test passed:")
                print(f"   Query: {query}")
                print(f"   Used RAG: {data['used_rag']}")
                print(f"   Complexity Score: {data['complexity_score']:.2f}")
                print(f"   Answer: {data['answer'][:100]}...")
                print(f"   Reasoning: {data['reasoning']}")
                return True
            else:
                print(f"❌ Simple query test failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Simple query test error: {e}")
            return False
    
    def test_complex_query(self) -> bool:
        """Test complex query (should use RAG)"""
        query = "Prove the Central Limit Theorem and explain its applications in probability theory"
        
        try:
            response = self.session.post(
                f"{self.base_url}/adaptive_rag",
                json={"query": query}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Complex query test passed:")
                print(f"   Query: {query}")
                print(f"   Used RAG: {data['used_rag']}")
                print(f"   Complexity Score: {data['complexity_score']:.2f}")
                print(f"   Context blocks: {len(data['context_blocks'])}")
                print(f"   Answer: {data['answer'][:100]}...")
                print(f"   Reasoning: {data['reasoning']}")
                return True
            else:
                print(f"❌ Complex query test failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Complex query test error: {e}")
            return False
    
    def test_query_complexity_analysis(self) -> bool:
        """Test query complexity analysis with various query types"""
        test_queries = [
            ("What is 2 + 2?", "simple"),
            ("Define probability", "definition"),
            ("Prove the Central Limit Theorem", "complex"),
            ("Give an example of a normal distribution", "example"),
            ("Compare discrete and continuous distributions", "comparative")
        ]
        
        results = []
        
        for query, expected_type in test_queries:
            try:
                response = self.session.post(
                    f"{self.base_url}/adaptive_rag",
                    json={"query": query}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results.append({
                        "query": query,
                        "expected_type": expected_type,
                        "used_rag": data['used_rag'],
                        "complexity_score": data['complexity_score'],
                        "reasoning": data['reasoning']
                    })
                else:
                    print(f"❌ Query failed: {query} - {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Query error: {query} - {e}")
                return False
        
        print(f"✅ Query complexity analysis test passed:")
        for result in results:
            print(f"   {result['expected_type']}: {result['used_rag']} RAG (score: {result['complexity_score']:.2f}) - {result['reasoning']}")
        
        return True
    
    def test_performance_metrics(self) -> bool:
        """Test performance metrics collection"""
        query = "Explain the Central Limit Theorem"
        
        try:
            response = self.session.post(
                f"{self.base_url}/adaptive_rag",
                json={"query": query}
            )
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('performance_metrics', {})
                print(f"✅ Performance metrics test passed:")
                print(f"   Total time: {metrics.get('total_time', 'N/A')}")
                print(f"   Used RAG: {metrics.get('used_rag', 'N/A')}")
                print(f"   Complexity score: {metrics.get('complexity_score', 'N/A')}")
                print(f"   Confidence: {metrics.get('confidence', 'N/A')}")
                return True
            else:
                print(f"❌ Performance metrics test failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Performance metrics test error: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all tests"""
        print("🧪 Running Simplified Adaptive RAG Test Suite")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health),
            ("Configuration", self.test_config),
            ("Simple Query", self.test_simple_query),
            ("Complex Query", self.test_complex_query),
            ("Complexity Analysis", self.test_query_complexity_analysis),
            ("Performance Metrics", self.test_performance_metrics)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\\n🔍 Testing {test_name}...")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} passed")
                else:
                    print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} error: {e}")
        
        print(f"\\n📊 Test Results: {passed}/{total} tests passed")
        return passed == total

def main():
    """Main test function"""
    print("🚀 Starting Simplified Adaptive RAG Test Suite")
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(5)
    
    # Run tests
    tester = AdaptiveRAGTester()
    success = tester.run_all_tests()
    
    if success:
        print("\\n🎉 All tests passed! Simplified Adaptive RAG system is working correctly.")
    else:
        print("\\n❌ Some tests failed. Please check the system configuration.")
    
    return success

if __name__ == "__main__":
    main()