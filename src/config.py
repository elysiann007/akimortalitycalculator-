"""
Configuration and constants for ICU mortality prediction pipeline
"""

from pathlib import Path

# Random seed for reproducibility
RANDOM_STATE = 42

# Data parameters
TEST_SIZE = 0.2
TARGET_COLUMN = 'deathflag'  # Lowercase — PostgreSQL always returns column names lowercase
IDENTIFIER_COLUMNS = ['row_id', 'id', 'protocol_no', 'patient_id', 'study_id']

# File paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
MODELS_DIR = OUTPUT_DIR / "models"
TABLES_DIR = OUTPUT_DIR / "tables"
FIGURES_DIR = OUTPUT_DIR / "figures"

# Create directories if they don't exist
for path in [DATA_DIR, MODELS_DIR, TABLES_DIR, FIGURES_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Data file paths
DATA_FILE = DATA_DIR / "deu_icu_mortality.csv"

# PostgreSQL Connection Parameters
USE_POSTGRES = True
POSTGRES_HOST = 'localhost'
POSTGRES_PORT = 5432
POSTGRES_DATABASE = 'M3'
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = '123456'
POSTGRES_TABLE = 'deu_retro_clean'
POSTGRES_QUERY = f'SELECT * FROM {POSTGRES_TABLE}'

# Model hyperparameters
RANDOM_FOREST_PARAMS = {
    'n_estimators': 200,
    'max_depth': 20,
    'min_samples_split': 10,
    'random_state': RANDOM_STATE,
    'n_jobs': -1,
    'verbose': 0
}

GRADIENT_BOOSTING_PARAMS = {
    'n_estimators': 200,
    'max_depth': 5,
    'learning_rate': 0.05,
    'random_state': RANDOM_STATE,
    'verbose': 0
}

LOGISTIC_REGRESSION_PARAMS = {
    'max_iter': 1000,
    'random_state': RANDOM_STATE,
    'n_jobs': -1
}

ANN_PARAMS = {
    'hidden_layer_sizes': (128, 64, 32),
    'max_iter': 500,
    'random_state': RANDOM_STATE,
    'early_stopping': True,
    'validation_fraction': 0.1,
    'n_iter_no_change': 20,
    'verbose': 0
}

# Preprocessing parameters
MICE_ITERATIONS = 5
SCALING_METHOD = 'standard'  # 'standard' or 'robust'

# Feature importance parameters
PERMUTATION_IMPORTANCE_REPEATS = 10
TOP_N_FEATURES = 15
