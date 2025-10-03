"""
Generic query complexity analyzer for adaptive RAG
Works with any model type (transformer, RL, etc.)
"""

import re
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer

@dataclass
class QueryComplexity:
    """Represents query complexity analysis"""
    complexity_score: float  # 0.0 (simple) to 1.0 (complex)
    confidence: float
    reasoning: str
    features: Dict[str, Any]
    recommendation: str  # "direct", "rag", "uncertain"

class QueryAnalyzer:
    """Generic query complexity analyzer that works with any model type"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.embedding_model = None
        self._load_embedding_model()
        
        # Complexity indicators
        self.complex_keywords = [
            'prove', 'derive', 'calculate', 'solve', 'analyze', 'explain',
            'theorem', 'lemma', 'corollary', 'definition', 'proof',
            'probability', 'distribution', 'expectation', 'variance',
            'convergence', 'limit', 'integral', 'derivative',
            'matrix', 'eigenvalue', 'eigenvector', 'determinant',
            'optimization', 'minimize', 'maximize', 'constraint'
        ]
        
        self.simple_keywords = [
            'what', 'how', 'when', 'where', 'why', 'which',
            'define', 'meaning', 'example', 'instance',
            'yes', 'no', 'true', 'false', 'correct', 'incorrect'
        ]
        
        # Mathematical complexity patterns
        self.math_patterns = [
            r'\b\w+\s*=\s*\w+',  # equations
            r'\$\$.*?\$\$',      # LaTeX math
            r'\\[a-zA-Z]+',      # LaTeX commands
            r'\b\w+\([^)]+\)',   # functions
            r'\b\w+\s*[+\-*/]\s*\w+',  # arithmetic
        ]
    
    def _load_embedding_model(self):
        """Load embedding model for semantic analysis"""
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Could not load embedding model: {e}")
            self.embedding_model = None
    
    def analyze_query(self, query: str, query_metadata: Optional[Dict[str, Any]] = None) -> QueryComplexity:
        """
        Analyze query complexity using multiple heuristics
        Returns complexity score and recommendation
        """
        features = self._extract_features(query, query_metadata)
        complexity_score = self._calculate_complexity_score(features)
        confidence = self._calculate_confidence(features)
        reasoning = self._generate_reasoning(features, complexity_score)
        recommendation = self._make_recommendation(complexity_score, confidence, features)
        
        return QueryComplexity(
            complexity_score=complexity_score,
            confidence=confidence,
            reasoning=reasoning,
            features=features,
            recommendation=recommendation
        )
    
    def _extract_features(self, query: str, query_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract various features from the query"""
        features = {
            'query_length': len(query.split()),
            'char_length': len(query),
            'has_math': self._has_mathematical_content(query),
            'complex_keywords': self._count_keywords(query, self.complex_keywords),
            'simple_keywords': self._count_keywords(query, self.simple_keywords),
            'question_type': self._classify_question_type(query),
            'has_equations': self._has_equations(query),
            'has_definitions': self._has_definitions(query),
            'has_proofs': self._has_proofs(query),
            'has_examples': self._has_examples(query),
            'semantic_complexity': self._calculate_semantic_complexity(query),
            'metadata': query_metadata or {}
        }
        
        return features
    
    def _has_mathematical_content(self, query: str) -> bool:
        """Check if query contains mathematical content"""
        for pattern in self.math_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        return False
    
    def _count_keywords(self, query: str, keywords: List[str]) -> int:
        """Count occurrences of keywords in query"""
        query_lower = query.lower()
        count = 0
        for keyword in keywords:
            count += query_lower.count(keyword.lower())
        return count
    
    def _classify_question_type(self, query: str) -> str:
        """Classify the type of question"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['what', 'define', 'definition']):
            return 'definition'
        elif any(word in query_lower for word in ['how', 'prove', 'derive', 'calculate']):
            return 'procedural'
        elif any(word in query_lower for word in ['why', 'explain', 'reason']):
            return 'explanatory'
        elif any(word in query_lower for word in ['example', 'instance', 'case']):
            return 'example'
        elif any(word in query_lower for word in ['compare', 'difference', 'similarity']):
            return 'comparative'
        else:
            return 'general'
    
    def _has_equations(self, query: str) -> bool:
        """Check if query contains equations"""
        equation_patterns = [
            r'\$\$.*?\$\$',      # LaTeX math
            r'\$.*?\$',          # Inline math
            r'\b\w+\s*=\s*\w+',  # Simple equations
            r'\b\w+\([^)]+\)',   # Functions
        ]
        for pattern in equation_patterns:
            if re.search(pattern, query):
                return True
        return False
    
    def _has_definitions(self, query: str) -> bool:
        """Check if query asks for definitions"""
        definition_indicators = [
            'define', 'definition', 'what is', 'meaning of',
            'explain the concept', 'describe'
        ]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in definition_indicators)
    
    def _has_proofs(self, query: str) -> bool:
        """Check if query asks for proofs"""
        proof_indicators = [
            'prove', 'proof', 'show that', 'demonstrate',
            'derive', 'deduce', 'establish'
        ]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in proof_indicators)
    
    def _has_examples(self, query: str) -> bool:
        """Check if query asks for examples"""
        example_indicators = [
            'example', 'instance', 'case', 'illustrate',
            'give an example', 'show an example'
        ]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in example_indicators)
    
    def _calculate_semantic_complexity(self, query: str) -> float:
        """Calculate semantic complexity using embeddings"""
        if not self.embedding_model:
            return 0.5  # Default moderate complexity
        
        try:
            # Get embedding for the query
            query_embedding = self.embedding_model.encode([query])
            
            # Simple heuristic: longer queries with more diverse vocabulary
            # are more complex
            words = query.split()
            unique_words = len(set(words))
            vocabulary_diversity = unique_words / len(words) if words else 0
            
            # Combine with query length
            length_factor = min(len(query) / 100, 1.0)  # Normalize to 0-1
            
            return (vocabulary_diversity + length_factor) / 2
            
        except Exception:
            return 0.5  # Default moderate complexity
    
    def _calculate_complexity_score(self, features: Dict[str, Any]) -> float:
        """Calculate overall complexity score from features"""
        score = 0.0
        weights = {
            'query_length': 0.1,
            'has_math': 0.2,
            'complex_keywords': 0.15,
            'simple_keywords': -0.1,
            'question_type': 0.1,
            'has_equations': 0.15,
            'has_definitions': 0.05,
            'has_proofs': 0.2,
            'has_examples': 0.05,
            'semantic_complexity': 0.1
        }
        
        # Normalize query length (0-1 scale)
        length_score = min(features['query_length'] / 20, 1.0)
        score += weights['query_length'] * length_score
        
        # Binary features
        for feature, weight in weights.items():
            if feature in ['query_length', 'semantic_complexity']:
                continue
            if feature in features and isinstance(features[feature], bool):
                score += weight * (1.0 if features[feature] else 0.0)
            elif feature in features and isinstance(features[feature], int):
                score += weight * min(features[feature] / 3, 1.0)  # Normalize counts
        
        # Question type scoring
        type_scores = {
            'definition': 0.3,
            'procedural': 0.8,
            'explanatory': 0.6,
            'example': 0.4,
            'comparative': 0.7,
            'general': 0.5
        }
        question_type = features.get('question_type', 'general')
        score += weights['question_type'] * type_scores.get(question_type, 0.5)
        
        # Semantic complexity
        score += weights['semantic_complexity'] * features.get('semantic_complexity', 0.5)
        
        return max(0.0, min(1.0, score))  # Clamp to [0, 1]
    
    def _calculate_confidence(self, features: Dict[str, Any]) -> float:
        """Calculate confidence in the complexity assessment"""
        # Higher confidence when we have more indicators
        indicator_count = sum(1 for key in ['has_math', 'has_equations', 'has_definitions', 
                                          'has_proofs', 'has_examples'] if features.get(key, False))
        
        # Higher confidence for longer queries (more information)
        length_confidence = min(features['query_length'] / 10, 1.0)
        
        # Higher confidence when we have clear indicators
        clear_indicators = features['complex_keywords'] + features['simple_keywords']
        indicator_confidence = min(clear_indicators / 3, 1.0)
        
        # Combine confidence factors
        confidence = (indicator_count * 0.3 + length_confidence * 0.4 + indicator_confidence * 0.3)
        return max(0.1, min(1.0, confidence))  # Clamp to [0.1, 1.0]
    
    def _generate_reasoning(self, features: Dict[str, Any], complexity_score: float) -> str:
        """Generate human-readable reasoning for the complexity assessment"""
        reasons = []
        
        if features['has_math']:
            reasons.append("contains mathematical content")
        if features['has_equations']:
            reasons.append("includes equations")
        if features['has_proofs']:
            reasons.append("requests proofs or derivations")
        if features['complex_keywords'] > 0:
            reasons.append(f"uses {features['complex_keywords']} complex keywords")
        if features['query_length'] > 15:
            reasons.append("is a long, detailed query")
        
        if features['simple_keywords'] > 0:
            reasons.append(f"uses {features['simple_keywords']} simple keywords")
        if features['has_examples']:
            reasons.append("requests examples")
        
        if not reasons:
            reasons.append("has moderate complexity indicators")
        
        complexity_level = "high" if complexity_score > 0.7 else "moderate" if complexity_score > 0.4 else "low"
        return f"Query has {complexity_level} complexity because it {', '.join(reasons)}"
    
    def _make_recommendation(self, complexity_score: float, confidence: float, features: Dict[str, Any]) -> str:
        """Make routing recommendation based on complexity and confidence"""
        # High confidence decisions
        if confidence > 0.8:
            if complexity_score > 0.6:
                return "rag"
            elif complexity_score < 0.3:
                return "direct"
            else:
                return "rag"  # Default to RAG for moderate complexity
        
        # Medium confidence decisions
        elif confidence > 0.5:
            if complexity_score > 0.7:
                return "rag"
            elif complexity_score < 0.2:
                return "direct"
            else:
                return "rag"  # Default to RAG for uncertain cases
        
        # Low confidence - default to RAG for safety
        else:
            return "rag"
