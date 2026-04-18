"""
Model training module for ICU mortality prediction
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from typing import Dict, Tuple

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier

def train_logistic_regression(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    params: dict = None,
    random_state: int = 42
) -> LogisticRegression:
    """Train Logistic Regression model"""
    if params is None:
        params = {'max_iter': 1000, 'random_state': random_state, 'n_jobs': -1}
    
    print("Training Logistic Regression...")
    model = LogisticRegression(**params)
    model.fit(X_train, y_train)
    print("✓ Logistic Regression trained")
    return model

def train_random_forest(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    params: dict = None,
    random_state: int = 42
) -> RandomForestClassifier:
    """Train Random Forest model"""
    if params is None:
        params = {
            'n_estimators': 200,
            'max_depth': 20,
            'min_samples_split': 10,
            'random_state': random_state,
            'n_jobs': -1,
            'verbose': 0
        }
    
    print("Training Random Forest...")
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    print("✓ Random Forest trained")
    return model

def train_gradient_boosting(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    params: dict = None,
    random_state: int = 42
) -> GradientBoostingClassifier:
    """Train Gradient Boosting model"""
    if params is None:
        params = {
            'n_estimators': 200,
            'max_depth': 5,
            'learning_rate': 0.05,
            'random_state': random_state,
            'verbose': 0
        }
    
    print("Training Gradient Boosting...")
    model = GradientBoostingClassifier(**params)
    model.fit(X_train, y_train)
    print("✓ Gradient Boosting trained")
    return model

def train_ann_mlp(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    params: dict = None,
    random_state: int = 42
) -> MLPClassifier:
    """Train Artificial Neural Network (MLPClassifier)"""
    if params is None:
        params = {
            'hidden_layer_sizes': (128, 64, 32),
            'max_iter': 500,
            'random_state': random_state,
            'early_stopping': True,
            'validation_fraction': 0.1,
            'n_iter_no_change': 20,
            'verbose': 0
        }
    
    print("Training Artificial Neural Network (MLP)...")
    model = MLPClassifier(**params)
    model.fit(X_train, y_train)
    print("✓ ANN trained")
    return model

def train_all_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_train_scaled: pd.DataFrame = None,
    rf_params: dict = None,
    gb_params: dict = None,
    lr_params: dict = None,
    ann_params: dict = None,
    random_state: int = 42
) -> Dict[str, object]:
    """
    Train all models
    
    Args:
        X_train: Training features (unscaled)
        y_train: Training target
        X_train_scaled: Training features (scaled, required for LR and ANN)
        rf_params: Random Forest parameters
        gb_params: Gradient Boosting parameters
        lr_params: Logistic Regression parameters
        ann_params: ANN parameters
        random_state: Random seed
    
    Returns:
        Dictionary of trained models
    """
    if X_train_scaled is None:
        X_train_scaled = X_train
    
    models = {}
    
    models['Logistic Regression'] = train_logistic_regression(
        X_train_scaled, y_train, lr_params, random_state
    )
    
    models['Random Forest'] = train_random_forest(
        X_train, y_train, rf_params, random_state
    )
    
    models['Gradient Boosting'] = train_gradient_boosting(
        X_train, y_train, gb_params, random_state
    )
    
    models['ANN (MLPClassifier)'] = train_ann_mlp(
        X_train_scaled, y_train, ann_params, random_state
    )
    
    return models

def get_predictions(
    models: Dict[str, object],
    X_test: pd.DataFrame,
    X_test_scaled: pd.DataFrame = None
) -> Dict[str, np.ndarray]:
    """
    Get probability predictions from all models
    
    Args:
        models: Dictionary of trained models
        X_test: Unscaled test features
        X_test_scaled: Scaled test features (required for LR and ANN)
    
    Returns:
        Dictionary of probability predictions
    """
    predictions = {}
    
    # Models that need scaled data
    scaled_models = ['Logistic Regression', 'ANN (MLPClassifier)']
    
    for model_name, model in models.items():
        if model_name in scaled_models:
            if X_test_scaled is None:
                raise ValueError(f"X_test_scaled required for {model_name}")
            predictions[model_name] = model.predict_proba(X_test_scaled)[:, 1]
        else:
            predictions[model_name] = model.predict_proba(X_test)[:, 1]
    
    return predictions

def save_models(
    models: Dict[str, object],
    output_dir: Path
) -> None:
    """Save trained models to disk"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for model_name, model in models.items():
        filename = model_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
        filepath = output_dir / f"{filename}.pkl"
        joblib.dump(model, filepath)
        print(f"Saved {model_name}: {filepath}")

def load_models(
    model_names: list,
    input_dir: Path
) -> Dict[str, object]:
    """Load trained models from disk"""
    input_dir = Path(input_dir)
    models = {}
    
    for model_name in model_names:
        filename = model_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
        filepath = input_dir / f"{filename}.pkl"
        
        if filepath.exists():
            models[model_name] = joblib.load(filepath)
        else:
            raise FileNotFoundError(f"Model not found: {filepath}")
    
    return models

def load_single_model(model_name: str, input_dir: Path) -> object:
    """Load a single trained model"""
    input_dir = Path(input_dir)
    filename = model_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
    filepath = input_dir / f"{filename}.pkl"
    
    if filepath.exists():
        return joblib.load(filepath)
    else:
        raise FileNotFoundError(f"Model not found: {filepath}")
