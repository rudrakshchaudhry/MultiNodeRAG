# RAG System Configuration
# Adjust these values based on your specific use case and testing

# Similarity Thresholds
SIMILARITY_THRESHOLD = 0.6      # Minimum cosine similarity for relevance
                                # Lower values (0.3-0.5) = more lenient
                                # Higher values (0.7-0.9) = more strict

MIN_RELEVANT_RESULTS = 1        # Minimum number of relevant results needed
                                # Set to 0 to allow empty results
                                # Set to 2+ to require multiple relevant docs

# Domain Relevance Check
DOMAIN_THRESHOLD = 0.3          # Threshold for domain relevance check
                                # Lower = accept broader queries
                                # Higher = be more restrictive

# Domain-specific keywords for your knowledge base
# Customize this list based on your content
DOMAIN_KEYWORDS = [
    "probability", "statistics", "random", "regression", "distribution", 
    "variance", "mean", "standard deviation", "hypothesis", "test",
    "correlation", "sample", "population", "inference", "bayesian",
    "confidence", "interval", "normal", "binomial", "poisson",
    "chi-square", "t-test", "anova", "model", "estimation",
    "expectation", "moment", "likelihood", "estimator", "parameter"
]

# Response Messages
NO_RELEVANT_INFO_MESSAGE = "I don't have relevant information in my knowledge base to answer this question. Please ask questions related to probability, statistics, or random processes."

DOMAIN_DESCRIPTION = "Probability, Statistics, and Random Processes"

# Debug Settings
DEBUG_SIMILARITY_SCORES = True   # Print similarity scores for filtered results
DEBUG_DOMAIN_CHECK = False       # Print domain relevance check details 