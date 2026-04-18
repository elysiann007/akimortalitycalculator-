"""
Preprocessing module for ICU mortality prediction
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from typing import Tuple, List, Optional
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer

def remove_identifier_columns(X: pd.DataFrame, id_columns: List[str]) -> pd.DataFrame:
    """Remove non-predictive identifier columns"""
    cols_to_drop = [col for col in X.columns if col.lower() in [c.lower() for c in id_columns]]
    if cols_to_drop:
        print(f"Removing identifier columns: {cols_to_drop}")
        X = X.drop(columns=cols_to_drop)
    return X

def handle_categorical_features(X: pd.DataFrame) -> pd.DataFrame:
    """Detect and encode categorical features, with special handling for numeric strings"""
    categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if categorical_cols:
        print(f"Found categorical columns: {categorical_cols}")
        
        # Handle numeric string columns separately
        numeric_string_cols = []
        true_categorical_cols = []
        
        for col in categorical_cols:
            # Try to convert to numeric
            try:
                pd.to_numeric(X[col], errors='coerce')
                # Check if most values are numeric (not NaN after conversion)
                numeric_ratio = X[col].notna().sum() / len(X[col])
                if numeric_ratio > 0.5:  # If more than 50% can be numeric
                    numeric_string_cols.append(col)
                else:
                    true_categorical_cols.append(col)
            except:
                true_categorical_cols.append(col)
        
        # Convert numeric string columns to float
        for col in numeric_string_cols:
            X[col] = pd.to_numeric(X[col], errors='coerce')
            print(f"  Converted '{col}' from string to numeric (float)")
        
        # One-hot encode only true categorical columns
        if true_categorical_cols:
            print(f"Applying one-hot encoding to: {true_categorical_cols}")
            X = pd.get_dummies(X, columns=true_categorical_cols, drop_first=True)
        
        print(f"Shape after encoding: {X.shape}")
    
    return X

def ensure_numeric(X: pd.DataFrame) -> pd.DataFrame:
    """Ensure all features are numeric"""
    X = X.astype(float)
    return X

def prepare_features_and_target(
    df: pd.DataFrame,
    target_column: str = 'deathFlag',
    id_columns: List[str] = None
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepare features and target from raw data
    
    Args:
        df: Raw DataFrame
        target_column: Name of target column
        id_columns: Identifier columns to remove
    
    Returns:
        Tuple of (features DataFrame, target Series)
    """
    if id_columns is None:
        id_columns = []
    
    y = df[target_column].astype(int)
    X = df.drop(target_column, axis=1)
    
    X = remove_identifier_columns(X, id_columns)
    X = handle_categorical_features(X)
    X = ensure_numeric(X)
    
    return X, y

def train_test_split_stratified(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Perform stratified train-test split
    
    Args:
        X: Features DataFrame
        y: Target Series
        test_size: Proportion of test set
        random_state: Random seed
    
    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )
    
    print(f"Train set: {X_train.shape} | Test set: {X_test.shape}")
    print(f"Train class distribution: {y_train.value_counts(normalize=True).to_dict()}")
    print(f"Test class distribution: {y_test.value_counts(normalize=True).to_dict()}")
    
    return X_train, X_test, y_train, y_test

def impute_missing_values(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    method: str = 'mice',
    random_state: int = 42,
    mice_iterations: int = 5
) -> Tuple[pd.DataFrame, pd.DataFrame, Optional]:
    """
    Impute missing values - fit on train, apply to test
    
    Args:
        X_train: Training features
        X_test: Test features
        method: 'mice' or 'mean'
        random_state: Random seed
        mice_iterations: Number of MICE iterations
    
    Returns:
        Tuple of (X_train_imputed, X_test_imputed, imputer_object)
    """
    train_missing = X_train.isnull().sum().sum()
    test_missing = X_test.isnull().sum().sum()
    
    print(f"Missing values - Train: {train_missing}, Test: {test_missing}")
    
    if train_missing == 0 and test_missing == 0:
        print("No missing values detected")
        return X_train, X_test, None
    
    if method == 'mice':
        print(f"Fitting MICE imputer on training data (iterations={mice_iterations})...")
        imputer = IterativeImputer(
            max_iter=mice_iterations,
            random_state=random_state,
            verbose=0
        )
        X_train_imputed = pd.DataFrame(
            imputer.fit_transform(X_train),
            columns=X_train.columns,
            index=X_train.index
        )
        X_test_imputed = pd.DataFrame(
            imputer.transform(X_test),
            columns=X_test.columns,
            index=X_test.index
        )
        print(f"MICE imputation complete (sklearn IterativeImputer, BayesianRidge)")
    else:  # mean imputation
        print("Applying mean imputation...")
        col_means = X_train.mean()
        X_train_imputed = X_train.fillna(col_means)
        X_test_imputed = X_test.fillna(col_means)
        imputer = col_means
    
    return X_train_imputed, X_test_imputed, imputer

def scale_features(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    method: str = 'standard'
) -> Tuple[pd.DataFrame, pd.DataFrame, object]:
    """
    Scale features - fit on train, apply to test
    
    Args:
        X_train: Training features
        X_test: Test features
        method: 'standard' or 'robust'
    
    Returns:
        Tuple of (X_train_scaled, X_test_scaled, scaler_object)
    """
    if method == 'robust':
        scaler = RobustScaler()
    else:
        scaler = StandardScaler()
    
    scaler.fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Convert back to DataFrame to preserve column names
    X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
    X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)
    
    print(f"Scaling method: {method}")
    
    return X_train_scaled, X_test_scaled, scaler

def save_preprocessing_objects(
    imputer,
    scaler,
    output_dir: Path
) -> None:
    """Save preprocessing objects (imputer, scaler) to disk"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if imputer is not None:
        joblib.dump(imputer, output_dir / "imputer.pkl")
        print(f"Imputer saved: {output_dir / 'imputer.pkl'}")
    
    if scaler is not None:
        joblib.dump(scaler, output_dir / "scaler.pkl")
        print(f"Scaler saved: {output_dir / 'scaler.pkl'}")

def load_preprocessing_objects(input_dir: Path) -> Tuple[Optional, Optional]:
    """Load preprocessing objects from disk"""
    input_dir = Path(input_dir)
    
    imputer = None
    scaler = None
    
    imputer_path = input_dir / "imputer.pkl"
    scaler_path = input_dir / "scaler.pkl"
    
    if imputer_path.exists():
        imputer = joblib.load(imputer_path)
    
    if scaler_path.exists():
        scaler = joblib.load(scaler_path)
    
    return imputer, scaler
