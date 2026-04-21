"""
Feature importance analysis module for ICU mortality prediction
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Tuple
from sklearn.inspection import permutation_importance

def extract_rf_importance(
    model,
    feature_names: pd.Index
) -> pd.DataFrame:
    """Extract feature importance from Random Forest"""
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': model.feature_importances_,
        'Model': 'Random Forest'
    }).sort_values('Importance', ascending=False)
    
    return importance_df

def extract_gb_importance(
    model,
    feature_names: pd.Index
) -> pd.DataFrame:
    """Extract feature importance from Gradient Boosting"""
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': model.feature_importances_,
        'Model': 'Gradient Boosting'
    }).sort_values('Importance', ascending=False)
    
    return importance_df

def extract_lr_coefficients(
    model,
    feature_names: pd.Index
) -> pd.DataFrame:
    """Extract absolute coefficient values from Logistic Regression"""
    coefs = np.abs(model.coef_[0])
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': coefs / coefs.sum(),
        'Model': 'Logistic Regression'
    }).sort_values('Importance', ascending=False)
    
    return importance_df

def compute_permutation_importance(
    model,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    n_repeats: int = 10,
    random_state: int = 42
) -> pd.DataFrame:
    """Compute permutation importance"""
    perm_importance = permutation_importance(
        model, X_test, y_test,
        n_repeats=n_repeats,
        random_state=random_state,
        n_jobs=-1
    )
    
    importance_df = pd.DataFrame({
        'Feature': X_test.columns,
        'Importance': perm_importance.importances_mean,
        'Model': 'ANN (MLPClassifier)'
    }).sort_values('Importance', ascending=False)
    
    return importance_df

def extract_all_feature_importance(
    models: Dict[str, object],
    X_train: pd.DataFrame,
    X_test_scaled: pd.DataFrame,
    y_test: pd.Series,
    random_state: int = 42,
    perm_repeats: int = 10
) -> pd.DataFrame:
    """
    Extract feature importance from all models
    
    Args:
        models: Dictionary of trained models
        X_train: Training features (unscaled)
        X_test_scaled: Test features (scaled, for ANN)
        y_test: Test labels
        random_state: Random seed
        perm_repeats: Permutation importance repeats
    
    Returns:
        Combined DataFrame with importance from all models
    """
    all_importance = []
    
    # Random Forest
    print("Extracting Random Forest feature importance...")
    all_importance.append(extract_rf_importance(models['Random Forest'], X_train.columns))
    
    # Gradient Boosting
    print("Extracting Gradient Boosting feature importance...")
    all_importance.append(extract_gb_importance(models['Gradient Boosting'], X_train.columns))
    
    # Logistic Regression
    print("Extracting Logistic Regression coefficients...")
    all_importance.append(extract_lr_coefficients(models['Logistic Regression'], X_test_scaled.columns))
    
    # ANN - Permutation importance
    print("Computing ANN permutation importance (this may take a moment)...")
    all_importance.append(compute_permutation_importance(
        models['ANN (MLPClassifier)'], X_test_scaled, y_test,
        n_repeats=perm_repeats, random_state=random_state
    ))
    
    combined = pd.concat(all_importance, ignore_index=True)
    return combined

def get_top_n_features(
    all_importance: pd.DataFrame,
    n: int = 15
) -> pd.DataFrame:
    """
    Get top N features by mean importance across all models
    Excludes kreatininlastvalue
    
    Args:
        all_importance: Combined importance DataFrame
        n: Number of top features
    
    Returns:
        Top N features DataFrame
    """
    # Filter out kreatininlastvalue
    filtered_importance = all_importance[all_importance['Feature'] != 'kreatininlastvalue']
    
    top_n = filtered_importance.groupby('Feature')['Importance'].mean().sort_values(ascending=False).head(n)
    
    result_df = pd.DataFrame({
        'Rank': range(1, len(top_n) + 1),
        'Feature': top_n.index,
        'Mean Importance': top_n.values
    })
    
    return result_df

def plot_feature_importance(
    all_importance: pd.DataFrame,
    top_n: int = 15,
    figsize: Tuple[int, int] = (15, 12)
) -> plt.Figure:
    """
    Plot feature importance for all models
    
    Args:
        all_importance: Combined importance DataFrame
        top_n: Number of top features per model
        figsize: Figure size
    
    Returns:
        Matplotlib figure
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    axes = axes.ravel()
    
    # Filter out kreatininlastvalue
    filtered_importance = all_importance[all_importance['Feature'] != 'kreatininlastvalue']
    
    model_names = filtered_importance['Model'].unique()
    from config import MODEL_COLORS
    colors = MODEL_COLORS
    
    for idx, model_name in enumerate(sorted(model_names)):
        model_data = filtered_importance[filtered_importance['Model'] == model_name].nlargest(top_n, 'Importance')
        
        ax = axes[idx]
        ax.barh(range(len(model_data)), model_data['Importance'].values,
                color=colors.get(model_name, '#555555'))
        ax.set_yticks(range(len(model_data)))
        ax.set_yticklabels(model_data['Feature'].values, fontsize=9)
        ax.set_xlabel('Importance', fontweight='bold')
        ax.set_title(f'Top {top_n} Features - {model_name}', fontweight='bold', fontsize=11)
        ax.invert_yaxis()
    
    plt.tight_layout()
    return fig

def save_feature_importance(
    all_importance: pd.DataFrame,
    top_n_df: pd.DataFrame,
    output_dir: Path,
    formats: list = ['csv', 'excel']
) -> None:
    """
    Save feature importance tables to disk
    
    Args:
        all_importance: Combined importance DataFrame
        top_n_df: Top N features DataFrame
        output_dir: Output directory
        formats: Output formats ['csv', 'excel']
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save top N features
    if 'csv' in formats:
        filepath = output_dir / "top_15_features.csv"
        top_n_df.to_csv(filepath, index=False)
        print(f"Saved: {filepath}")
    
    if 'excel' in formats:
        filepath = output_dir / "top_15_features.xlsx"
        top_n_df.to_excel(filepath, index=False)
        print(f"Saved: {filepath}")
    
    # Save per-model importance
    for model_name in all_importance['Model'].unique():
        model_data = all_importance[all_importance['Model'] == model_name].sort_values('Importance', ascending=False)
        filename = model_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
        
        if 'csv' in formats:
            filepath = output_dir / f"feature_importance_{filename}.csv"
            model_data.to_csv(filepath, index=False)
        
        if 'excel' in formats:
            filepath = output_dir / f"feature_importance_{filename}.xlsx"
            model_data.to_excel(filepath, index=False)
