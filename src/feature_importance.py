"""
Feature importance analysis module for ICU mortality prediction
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Tuple
from sklearn.inspection import permutation_importance
from scipy import stats as scipy_stats

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

def compute_lr_pvalues(model, X_scaled: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    """Compute Wald test p-values and std errors from a fitted sklearn LogisticRegression"""
    coef = model.coef_[0]
    X_arr = X_scaled.values
    p_hat = model.predict_proba(X_scaled)[:, 1]
    W = p_hat * (1 - p_hat)
    H = (X_arr * W[:, None]).T @ X_arr
    try:
        cov = np.linalg.inv(H)
        std_errors = np.sqrt(np.diag(cov))
    except np.linalg.LinAlgError:
        std_errors = np.full(len(coef), np.nan)
    z_scores = coef / std_errors
    p_values = 2 * (1 - scipy_stats.norm.cdf(np.abs(z_scores)))
    return pd.DataFrame({
        'Feature': X_scaled.columns.tolist(),
        'P_Value': p_values,
        'Std_Error': std_errors,
    })


def _format_pvalue(p) -> str:
    if pd.isna(p):
        return 'N/A'
    if p < 0.001:
        return '<0.001'
    return f'{p:.3f}'


def get_top_n_features(
    all_importance: pd.DataFrame,
    n: int = 15,
    pvalues_df: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Get top N features by mean importance across all models.
    Excludes kreatininlastvalue.
    Returns columns: Feature, Importance, P_Value, Std
    """
    filtered = all_importance[all_importance['Feature'] != 'kreatininlastvalue']
    grouped = filtered.groupby('Feature')['Importance']
    mean_imp = grouped.mean().sort_values(ascending=False).head(n)
    std_imp = grouped.std().reindex(mean_imp.index).fillna(0)

    result_df = pd.DataFrame({
        'Feature': mean_imp.index,
        'Importance': mean_imp.values,
        'Std': std_imp.values,
    })

    if pvalues_df is not None:
        result_df = result_df.merge(pvalues_df[['Feature', 'P_Value']], on='Feature', how='left')
    else:
        result_df['P_Value'] = np.nan

    result_df['P_Value'] = result_df['P_Value'].apply(_format_pvalue)
    return result_df[['Feature', 'Importance', 'P_Value', 'Std']]

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

def _save_df_excel(df: pd.DataFrame, filepath: Path) -> None:
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Features')
        ws = writer.sheets['Features']
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col) + 4
            ws.column_dimensions[col[0].column_letter].width = max_len


def save_feature_importance(
    all_importance: pd.DataFrame,
    top_n_df: pd.DataFrame,
    output_dir: Path,
    formats: list = ['csv', 'excel'],
    pvalues_df: pd.DataFrame = None
) -> None:
    """Save feature importance tables — all files use columns: Feature, Importance, P_Value, Std"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── top_15_features ───────────────────────────────────────────────────────
    if 'csv' in formats:
        filepath = output_dir / "top_15_features.csv"
        top_n_df.to_csv(filepath, index=False)
        print(f"Saved: {filepath}")
    if 'excel' in formats:
        filepath = output_dir / "top_15_features.xlsx"
        _save_df_excel(top_n_df, filepath)
        print(f"Saved: {filepath}")

    # ── per-model files (same 4-column format) ────────────────────────────────
    for model_name in all_importance['Model'].unique():
        model_data = (
            all_importance[all_importance['Model'] == model_name]
            .sort_values('Importance', ascending=False)
            [['Feature', 'Importance']]
            .copy()
        )

        if pvalues_df is not None:
            model_data = model_data.merge(
                pvalues_df[['Feature', 'P_Value', 'Std_Error']].rename(columns={'Std_Error': 'Std'}),
                on='Feature', how='left'
            )
            model_data['P_Value'] = model_data['P_Value'].apply(_format_pvalue)
        else:
            model_data['P_Value'] = 'N/A'
            model_data['Std'] = 'N/A'

        model_data = model_data[['Feature', 'Importance', 'P_Value', 'Std']]
        filename = model_name.lower().replace(' ', '_').replace('(', '').replace(')', '')

        if 'csv' in formats:
            filepath = output_dir / f"feature_importance_{filename}.csv"
            model_data.to_csv(filepath, index=False)
        if 'excel' in formats:
            filepath = output_dir / f"feature_importance_{filename}.xlsx"
            _save_df_excel(model_data, filepath)
