# Enhanced RAG System Configuration for College-Level Probability and General Content
# Optimized for Qwen2.5-Math-7B-Instruct and improved retrieval

# Retrieval and Context Settings
SIMILARITY_THRESHOLD = 0.35      # Minimum similarity for context inclusion
MIN_RELEVANT_RESULTS = 2         # Minimum number of relevant results needed
DOMAIN_THRESHOLD = 0.25          # Threshold for domain relevance
TOP_K_CONTEXTS = 5               # Reduced from 10 to 5 for focused answers (was 10)
MAX_CONTEXT_LENGTH = 800         # Maximum context length per chunk

# Enhanced Keywords for Better Retrieval - Covering Probability and General Content
DOMAIN_KEYWORDS = [
    # Core Probability Concepts
    "probability", "random", "distribution", "random variable", "expectation", "variance",
    "standard deviation", "covariance", "correlation", "independence", "conditional",
    
    # Probability Distributions
    "binomial", "poisson", "normal", "gaussian", "exponential", "gamma", "beta",
    "uniform", "geometric", "negative binomial", "hypergeometric", "multinomial",
    
    # Statistical Concepts
    "statistics", "sample", "population", "parameter", "estimator", "estimation",
    "hypothesis testing", "confidence interval", "p-value", "significance level",
    "type i error", "type ii error", "power", "effect size",
    
    # Mathematical Operations
    "calculate", "compute", "solve", "find", "derive", "prove", "theorem", "lemma",
    "formula", "equation", "function", "derivative", "integral", "limit", "series",
    
    # Advanced Probability Topics
    "bayesian", "bayes theorem", "prior", "posterior", "likelihood", "mle",
    "moment generating function", "characteristic function", "mgf", "cf",
    "central limit theorem", "law of large numbers", "chebyshev inequality",
    "markov chain", "stochastic process", "random walk", "martingale",
    
    # Problem Types
    "coin flip", "dice roll", "card draw", "urn problem", "birthday problem",
    "waiting time", "arrival process", "queue", "renewal process",
    
    # Mathematical Notation
    "p(a)", "p(a|b)", "e[x]", "var(x)", "cov(x,y)", "ρ", "σ", "μ", "λ",
    "n choose k", "factorial", "permutation", "combination",
    
    # General Academic Content
    "introduction", "definition", "example", "problem", "solution", "proof",
    "theorem", "corollary", "lemma", "proposition", "algorithm", "method",
    "analysis", "evaluation", "comparison", "application", "implementation",
    
    # Signal Processing and Systems
    "signal", "system", "filter", "fourier", "transform", "frequency", "time domain",
    "linear", "nonlinear", "time-invariant", "causal", "stable", "impulse response",
    
    # Random Processes
    "random process", "stochastic process", "stationary", "ergodic", "autocorrelation",
    "power spectral density", "white noise", "colored noise", "filtering", "prediction"
]

# Enhanced Response Messages
NO_RELEVANT_INFO_MESSAGE = (
    "I don't have sufficient relevant information in my knowledge base to answer this question accurately. "
    "Please provide more specific details or ask a different question. "
    "I can help with topics like probability, statistics, random processes, signal processing, "
    "mathematical analysis, and related academic content."
)

DOMAIN_DESCRIPTION = "College-Level Probability, Statistics, Random Processes, Signal Processing, and Mathematical Analysis"

# Debug Settings
DEBUG_SIMILARITY_SCORES = True   # Print similarity scores for filtered results
DEBUG_DOMAIN_CHECK = True        # Print domain relevance check details

# Enhanced Content Processing Settings
CHUNK_SIZE = 512                # Optimal chunk size for content retrieval
CHUNK_OVERLAP = 100             # Overlap to maintain context across chunks
ENABLE_MATH_ENHANCEMENT = True  # Enhance mathematical content recognition

# Model-specific settings for Qwen2.5-Math-7B-Instruct
QWEN_MATH_TEMPERATURE = 0.7      # Higher for better reasoning (was 0.3)
QWEN_MATH_TOP_P = 0.95          # More inclusive sampling (was 0.9)
QWEN_MATH_MAX_TOKENS = 1024     # Keep reasonable length
QWEN_MATH_REPETITION_PENALTY = 1.05  # Gentler penalty (was 1.1)

# Enhanced prompt templates for better generation
MATH_PROMPT_TEMPLATE = """You are a mathematics and probability tutor. Answer the following question clearly and step-by-step.

Question: {query}

Relevant Context:
{context}

Provide a clear, mathematical answer with explanation:"""

GENERAL_PROMPT_TEMPLATE = """You are a knowledgeable academic tutor. Answer the following question clearly and accurately.

Question: {query}

Relevant Context:
{context}

Provide a clear, well-structured answer:"""
