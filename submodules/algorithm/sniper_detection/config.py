"""
Configuration for sniper detection module
"""

# Data processing
SESSION_THRESHOLD_MINUTES = 30
REQUIRED_COLUMNS = [
    'transaction_hash', 'trader_address', 'price',
    'amount_usd', 'timestamp', 'side', 'market_id'
]

# Sniper definition
LARGE_TRADE_THRESHOLD = 5000  # USD
MAX_HOLDING_TIME = 300  # seconds
SNIPER_TRADE_COUNT = 2

# Model parameters
ISOLATION_FOREST_PARAMS = {
    'contamination': 0.05,
    'n_estimators': 100,
    'random_state': 42
}

# Sentence-BERT model
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
EMBEDDING_DIM = 384

# Paths
RESULTS_DIR = 'results'
ATTACK_WINDOWS_DIR = 'results/attack_windows'
