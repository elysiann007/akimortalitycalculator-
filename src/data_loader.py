"""
Data loading module for ICU mortality prediction
"""

import pandas as pd
from pathlib import Path
from typing import Union, Tuple
from urllib.parse import quote

def load_csv(filepath: Union[str, Path]) -> pd.DataFrame:
    """Load data from CSV file"""
    df = pd.read_csv(filepath)
    return df

def load_from_postgres(host: str, port: int, database: str, user: str, 
                       password: str, query: str) -> pd.DataFrame:
    """
    Load data from PostgreSQL database
    
    Args:
        host: Database host
        port: Database port
        database: Database name
        user: Database user
        password: Database password (will be URL-encoded)
        query: SQL query to fetch data
    
    Returns:
        DataFrame with data from database
    """
    try:
        from sqlalchemy import create_engine
    except ImportError:
        raise ImportError("sqlalchemy required for PostgreSQL. Install via: pip install sqlalchemy psycopg2-binary")
    
    # URL-encode password to handle special characters like @
    encoded_password = quote(password, safe='')
    engine = create_engine(f'postgresql://{user}:{encoded_password}@{host}:{port}/{database}')
    df = pd.read_sql(query, engine)
    engine.dispose()
    return df

def load_data(filepath: Union[str, Path] = None, use_postgres: bool = False,
              postgres_params: dict = None) -> pd.DataFrame:
    """
    Load data from CSV or PostgreSQL
    
    Args:
        filepath: Path to CSV file (if use_postgres=False)
        use_postgres: Whether to load from PostgreSQL
        postgres_params: Dictionary with keys: host, port, database, user, password, query
    
    Returns:
        Loaded DataFrame
    """
    if use_postgres:
        if postgres_params is None:
            raise ValueError("postgres_params required for PostgreSQL loading")
        return load_from_postgres(**postgres_params)
    else:
        if filepath is None:
            raise ValueError("filepath required for CSV loading")
        return load_csv(filepath)

def validate_data(df: pd.DataFrame, target_column: str = 'deathFlag') -> Tuple[bool, str]:
    """
    Validate dataset structure and content
    
    Args:
        df: DataFrame to validate
        target_column: Expected target column name
    
    Returns:
        Tuple of (is_valid, message)
    """
    if df is None or df.empty:
        return False, "DataFrame is empty"
    
    if target_column not in df.columns:
        return False, f"Target column '{target_column}' not found"
    
    if df.shape[0] < 50:
        return False, f"Dataset too small: {df.shape[0]} rows (min 50 required)"
    
    return True, f"Validation passed: {df.shape[0]} rows, {df.shape[1]} columns"

def get_data_summary(df: pd.DataFrame, target_column: str = 'deathFlag') -> dict:
    """
    Get summary statistics of dataset
    
    Args:
        df: DataFrame to summarize
        target_column: Target column name
    
    Returns:
        Dictionary with summary statistics
    """
    summary = {
        'shape': df.shape,
        'dtypes': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_cols': df.select_dtypes(include=['number']).columns.tolist(),
        'categorical_cols': df.select_dtypes(include=['object', 'category']).columns.tolist(),
    }
    
    if target_column in df.columns:
        summary['target_distribution'] = df[target_column].value_counts().to_dict()
        summary['target_null'] = df[target_column].isnull().sum()
    
    return summary
