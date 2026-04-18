"""
Model evaluation module for ICU mortality prediction
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple
from sklearn.metrics import (
    auc, roc_curve, accuracy_score, precision_score, f1_score,
    recall_score, roc_auc_score, matthews_corrcoef, classification_report,
    confusion_matrix
)

def compute_metrics(
    y_true: pd.Series,
    y_pred_proba: np.ndarray,
    y_pred: np.ndarray = None,
    threshold: float = 0.5
) -> Dict[str, float]:
    """
    Compute comprehensive metrics
    
    Args:
        y_true: True labels
        y_pred_proba: Predicted probabilities
        y_pred: Binary predictions (if None, computed from proba)
        threshold: Classification threshold
    
    Returns:
        Dictionary of metrics
    """
    if y_pred is None:
        y_pred = (y_pred_proba >= threshold).astype(int)
    
    metrics = {
        'AUC': roc_auc_score(y_true, y_pred_proba),
        'CA (Accuracy)': accuracy_score(y_true, y_pred),
        'Precision': precision_score(y_true, y_pred, zero_division=0),
        'F1-Score': f1_score(y_true, y_pred, zero_division=0),
        'Recall': recall_score(y_true, y_pred, zero_division=0),
        'MCC': matthews_corrcoef(y_true, y_pred)
    }
    
    return metrics

def evaluate_all_models(
    predictions: Dict[str, np.ndarray],
    y_test: pd.Series,
    threshold: float = 0.5
) -> pd.DataFrame:
    """
    Evaluate all models and create metrics DataFrame
    
    Args:
        predictions: Dictionary of predicted probabilities
        y_test: Test labels
        threshold: Classification threshold
    
    Returns:
        DataFrame with metrics for all models
    """
    results = []
    
    for model_name, y_pred_proba in predictions.items():
        metrics = compute_metrics(y_test, y_pred_proba, threshold=threshold)
        metrics['Model'] = model_name
        results.append(metrics)
    
    results_df = pd.DataFrame(results)
    # Reorder columns
    cols = ['Model', 'AUC', 'CA (Accuracy)', 'Precision', 'F1-Score', 'Recall', 'MCC']
    results_df = results_df[cols]
    
    return results_df

def get_roc_data(
    predictions: Dict[str, np.ndarray],
    y_test: pd.Series
) -> Dict[str, Tuple[np.ndarray, np.ndarray, float]]:
    """
    Get ROC curve data for all models
    
    Args:
        predictions: Dictionary of predicted probabilities
        y_test: Test labels
    
    Returns:
        Dictionary with (fpr, tpr, auc) for each model
    """
    roc_data = {}
    
    for model_name, y_pred_proba in predictions.items():
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        auc_score = auc(fpr, tpr)
        roc_data[model_name] = (fpr, tpr, auc_score)
    
    return roc_data

def get_confusion_matrices(
    predictions: Dict[str, np.ndarray],
    y_test: pd.Series,
    threshold: float = 0.5
) -> Dict[str, np.ndarray]:
    """
    Compute confusion matrices for all models
    
    Args:
        predictions: Dictionary of predicted probabilities
        y_test: Test labels
        threshold: Classification threshold
    
    Returns:
        Dictionary of confusion matrices
    """
    cm_dict = {}
    
    for model_name, y_pred_proba in predictions.items():
        y_pred = (y_pred_proba >= threshold).astype(int)
        cm = confusion_matrix(y_test, y_pred)
        cm_dict[model_name] = cm
    
    return cm_dict

def get_detailed_report(
    predictions: Dict[str, np.ndarray],
    y_test: pd.Series,
    threshold: float = 0.5
) -> Dict[str, str]:
    """
    Get detailed classification reports for all models
    
    Args:
        predictions: Dictionary of predicted probabilities
        y_test: Test labels
        threshold: Classification threshold
    
    Returns:
        Dictionary of classification reports
    """
    reports = {}
    
    for model_name, y_pred_proba in predictions.items():
        y_pred = (y_pred_proba >= threshold).astype(int)
        report = classification_report(y_test, y_pred, output_dict=False)
        reports[model_name] = report
    
    return reports

def print_metrics_summary(results_df: pd.DataFrame) -> None:
    """Print metrics summary to console"""
    print("\n" + "=" * 80)
    print("MODEL EVALUATION RESULTS")
    print("=" * 80)
    print(results_df.to_string(index=False))
    print("\nBest models by metric:")
    
    for col in results_df.columns[1:]:
        best_idx = results_df[col].idxmax()
        best_model = results_df.loc[best_idx, 'Model']
        best_value = results_df.loc[best_idx, col]
        print(f"  {col}: {best_model} ({best_value:.4f})")

def get_best_model(results_df: pd.DataFrame, metric: str = 'AUC') -> str:
    """Get best model by specified metric"""
    best_idx = results_df[metric].idxmax()
    return results_df.loc[best_idx, 'Model']

def save_metrics(
    results_df: pd.DataFrame,
    output_dir,
    formats: list = ['csv', 'excel']
) -> None:
    """Save metrics to disk"""
    from pathlib import Path
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if 'csv' in formats:
        filepath = output_dir / "model_metrics.csv"
        results_df.to_csv(filepath, index=False)
        print(f"Metrics saved: {filepath}")
    
    if 'excel' in formats:
        filepath = output_dir / "model_metrics.xlsx"
        results_df.to_excel(filepath, index=False)
        print(f"Metrics saved: {filepath}")
