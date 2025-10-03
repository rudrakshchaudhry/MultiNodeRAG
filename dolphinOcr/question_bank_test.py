#!/usr/bin/env python3
"""
Comprehensive Question Bank Test for Adaptive RAG System
Tests the system with real mathematical questions and produces detailed reports
"""

import sys
import os
import json
import time
import statistics
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

def load_question_bank():
    """Load the question bank from JSON file"""
    print("📚 Loading question bank...")
    
    try:
        with open('data/question_bank.json', 'r') as f:
            questions = json.load(f)
        print(f"✅ Loaded {len(questions)} questions from question bank")
        return questions
    except Exception as e:
        print(f"❌ Failed to load question bank: {e}")
        return []

def categorize_questions(questions):
    """Categorize questions by complexity and type"""
    print("\n📊 Categorizing questions...")
    
    categories = {
        'simple': [],
        'complex': [],
        'definitions': [],
        'theorems': [],
        'worked_examples': [],
        'numerical': []
    }
    
    for q in questions:
        question_text = q.get('question', '').lower()
        question_number = q.get('question_number', '')
        is_numerical = q.get('is_numerical', False)
        
        # Categorize by complexity (simple heuristics)
        if len(question_text.split()) < 20:
            categories['simple'].append(q)
        else:
            categories['complex'].append(q)
        
        # Categorize by type
        if any(word in question_text for word in ['define', 'what is', 'definition']):
            categories['definitions'].append(q)
        elif any(word in question_text for word in ['prove', 'theorem', 'lemma', 'corollary']):
            categories['theorems'].append(q)
        elif any(word in question_text for word in ['example', 'compute', 'calculate', 'find']):
            categories['worked_examples'].append(q)
        
        # Numerical questions
        if is_numerical:
            categories['numerical'].append(q)
    
    print(f"📈 Question Distribution:")
    for category, questions_list in categories.items():
        print(f"  {category}: {len(questions_list)} questions")
    
    return categories

def test_adaptive_rag_components():
    """Test individual adaptive RAG components"""
    print("\n🧪 Testing Adaptive RAG Components...")
    
    results = {}
    
    try:
        # Test configuration
        sys.path.append('src/rag_system')
        from adaptive_rag.config.adaptive_config import get_adaptive_config
        config = get_adaptive_config()
        results['config'] = {
            'token_cutoff': config.token_cutoff,
            'start_k': config.start_k,
            'relevance_threshold': config.relevance_threshold,
            'max_context_tokens': config.max_context_tokens
        }
        print("✅ Configuration loaded successfully")
        
        # Test query analyzer
        from adaptive_rag.core.query_analyzer import QueryAnalyzer
        analyzer = QueryAnalyzer(config)
        test_complexity = analyzer.analyze_query("What is probability?")
        results['query_analyzer'] = {
            'complexity_score': test_complexity.complexity_score,
            'recommendation': test_complexity.recommendation,
            'confidence': test_complexity.confidence
        }
        print("✅ Query analyzer working")
        
        # Test retrieval system
        from adaptive_rag.retrieval.dynamic_search import DynamicRetriever
        retriever = DynamicRetriever()
        results['retrieval'] = {
            'index_dir': retriever.index_dir,
            'index_loaded': hasattr(retriever, 'index')
        }
        print("✅ Retrieval system initialized")
        
        return results
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return None

def simulate_query_processing(question, category):
    """Simulate processing a single query using complexity analysis"""
    import sys
    sys.path.append('src/rag_system')
    from adaptive_rag.core.query_analyzer import QueryAnalyzer
    from adaptive_rag.config.adaptive_config import get_adaptive_config
    
    config = get_adaptive_config()
    analyzer = QueryAnalyzer(config)
    
    # Analyze query complexity
    complexity_analysis = analyzer.analyze_query(question)
    
    # Simple questions: low complexity, direct generation
    if complexity_analysis.recommendation == "direct":
        return {
            'used_rag': False,
            'reason': 'Simple question, direct generation',
            'complexity_score': complexity_analysis.complexity_score,
            'confidence': complexity_analysis.confidence
        }
    
    # Complex questions: high complexity, RAG needed
    else:
        return {
            'used_rag': True,
            'reason': 'Complex question, RAG needed',
            'complexity_score': complexity_analysis.complexity_score,
            'confidence': complexity_analysis.confidence
        }

def run_comprehensive_test(questions, categories):
    """Run comprehensive test on question bank"""
    print("\n🚀 Running Comprehensive Question Bank Test...")
    
    test_results = []
    start_time = time.time()
    
    # Test ALL questions in the question bank
    test_questions = questions
    
    print(f"📝 Testing ALL {len(test_questions)} questions...")
    
    for i, question_data in enumerate(test_questions):
        question_text = question_data.get('question', '')
        question_number = question_data.get('question_number', '')
        category = None
        
        # Determine category
        for cat, questions_list in categories.items():
            if question_data in questions_list:
                category = cat
                break
        
        # Progress tracking
        if (i + 1) % 100 == 0 or i == 0:
            print(f"  Progress: {i + 1}/{len(test_questions)} ({((i + 1)/len(test_questions)*100):.1f}%) - Testing {question_number} ({category})...")
        elif (i + 1) % 10 == 0:
            print(f"  {i + 1}/{len(test_questions)} - {question_number} ({category})")
        
        # Simulate processing
        result = simulate_query_processing(question_text, category)
        
        test_results.append({
            'question_number': question_number,
            'category': category,
            'question_length': len(question_text.split()),
            'is_numerical': question_data.get('is_numerical', False),
            'used_rag': result['used_rag'],
            'reason': result['reason'],
            'complexity_score': result['complexity_score'],
            'confidence': result['confidence']
        })
    
    end_time = time.time()
    total_time = end_time - start_time
    
    return test_results, total_time

def generate_report(test_results, component_results, total_time, categories):
    """Generate comprehensive test report"""
    print("\n📋 Generating Comprehensive Report...")
    
    # Create report directory
    report_dir = "question_bank_reports"
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"{report_dir}/adaptive_rag_report_{timestamp}.txt"
    
    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("ADAPTIVE RAG SYSTEM - QUESTION BANK COMPREHENSIVE TEST REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Test Time: {total_time:.2f} seconds\n")
        f.write(f"Questions Tested: {len(test_results)}\n\n")
        
        # Component Test Results
        f.write("COMPONENT TEST RESULTS\n")
        f.write("-" * 40 + "\n")
        if component_results:
            for component, details in component_results.items():
                f.write(f"{component.upper()}:\n")
                for key, value in details.items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")
        
        # Question Bank Statistics
        f.write("QUESTION BANK STATISTICS\n")
        f.write("-" * 40 + "\n")
        for category, questions_list in categories.items():
            f.write(f"{category}: {len(questions_list)} questions\n")
        f.write("\n")
        
        # Test Results Summary
        f.write("TEST RESULTS SUMMARY\n")
        f.write("-" * 40 + "\n")
        
        rag_used = sum(1 for r in test_results if r['used_rag'])
        direct_generation = len(test_results) - rag_used
        
        f.write(f"Total Questions Tested: {len(test_results)}\n")
        f.write(f"RAG Used: {rag_used} ({rag_used/len(test_results)*100:.1f}%)\n")
        f.write(f"Direct Generation: {direct_generation} ({direct_generation/len(test_results)*100:.1f}%)\n")
        f.write(f"Average Complexity Score: {statistics.mean([r['complexity_score'] for r in test_results]):.2f}\n")
        f.write(f"Average Confidence: {statistics.mean([r['confidence'] for r in test_results]):.2f}\n\n")
        
        # Category-wise Analysis
        f.write("CATEGORY-WISE ANALYSIS\n")
        f.write("-" * 40 + "\n")
        
        category_stats = {}
        for result in test_results:
            category = result['category']
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'rag_used': 0, 'tokens': []}
            
            category_stats[category]['total'] += 1
            if result['used_rag']:
                category_stats[category]['rag_used'] += 1
            category_stats[category]['tokens'].append(result['complexity_score'])
        
        for category, stats in category_stats.items():
            rag_percentage = stats['rag_used'] / stats['total'] * 100
            avg_tokens = statistics.mean(stats['tokens'])
            f.write(f"{category}:\n")
            f.write(f"  Total: {stats['total']}\n")
            f.write(f"  RAG Used: {stats['rag_used']} ({rag_percentage:.1f}%)\n")
            f.write(f"  Avg Complexity: {avg_tokens:.2f}\n\n")
        
        # Detailed Results
        f.write("DETAILED TEST RESULTS\n")
        f.write("-" * 40 + "\n")
        
        for result in test_results:
            f.write(f"Question {result['question_number']} ({result['category']}):\n")
            f.write(f"  Length: {result['question_length']} words\n")
            f.write(f"  RAG Used: {result['used_rag']}\n")
            f.write(f"  Reason: {result['reason']}\n")
            f.write(f"  Complexity Score: {result['complexity_score']:.2f}\n")
            f.write(f"  Confidence: {result['confidence']:.2f}\n\n")
    
    # Create CSV report
    df = pd.DataFrame(test_results)
    csv_file = f"{report_dir}/adaptive_rag_results_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    
    print(f"✅ Report generated: {report_file}")
    print(f"✅ CSV data: {csv_file}")
    
    return report_file, csv_file

def main():
    """Main test function"""
    print("🚀 Adaptive RAG System - Question Bank Comprehensive Test")
    print("=" * 70)
    
    # Load question bank
    questions = load_question_bank()
    if not questions:
        print("❌ No questions loaded. Exiting.")
        return 1
    
    # Categorize questions
    categories = categorize_questions(questions)
    
    # Test components
    component_results = test_adaptive_rag_components()
    if not component_results:
        print("❌ Component tests failed. Exiting.")
        return 1
    
    # Run comprehensive test
    test_results, total_time = run_comprehensive_test(questions, categories)
    
    # Generate report
    report_file, csv_file = generate_report(test_results, component_results, total_time, categories)
    
    # Print summary
    print("\n📊 TEST SUMMARY")
    print("=" * 40)
    
    rag_used = sum(1 for r in test_results if r['used_rag'])
    direct_generation = len(test_results) - rag_used
    
    print(f"Total Questions Tested: {len(test_results)}")
    print(f"RAG Used: {rag_used} ({rag_used/len(test_results)*100:.1f}%)")
    print(f"Direct Generation: {direct_generation} ({direct_generation/len(test_results)*100:.1f}%)")
    print(f"Average Complexity Score: {statistics.mean([r['complexity_score'] for r in test_results]):.2f}")
    print(f"Average Confidence: {statistics.mean([r['confidence'] for r in test_results]):.2f}")
    print(f"Test Time: {total_time:.2f} seconds")
    print(f"Report: {report_file}")
    print(f"Data: {csv_file}")
    
    print("\n🎉 Question bank test completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
