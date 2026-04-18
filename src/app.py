"""
Main orchestrator for ICU mortality prediction pipeline
Runs the complete end-to-end workflow
"""

import warnings
warnings.filterwarnings('ignore')

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config import *
from data_loader import load_data, validate_data, get_data_summary
from preprocessing import (
    prepare_features_and_target, train_test_split_stratified,
    impute_missing_values, scale_features, save_preprocessing_objects
)
from train_models import train_all_models, get_predictions, save_models
from evaluate import evaluate_all_models, get_roc_data, print_metrics_summary, save_metrics
from feature_importance import (
    extract_all_feature_importance, get_top_n_features, plot_feature_importance,
    save_feature_importance
)

def main():
    print("=" * 80)
    print("ICU MORTALITY PREDICTION - FULL PIPELINE")
    print("=" * 80)
    
    # ========================================================================
    # 1. LOAD DATA
    # ========================================================================
    print("\n[1/11] LOADING DATA")
    print("-" * 80)
    
    if USE_POSTGRES:
        print(f"Connecting to PostgreSQL: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}")
        postgres_params = {
            'host': POSTGRES_HOST,
            'port': POSTGRES_PORT,
            'database': POSTGRES_DATABASE,
            'user': POSTGRES_USER,
            'password': POSTGRES_PASSWORD,
            'query': POSTGRES_QUERY
        }
        try:
            df_raw = load_data(use_postgres=True, postgres_params=postgres_params)
            print(f"✓ Successfully loaded {len(df_raw)} rows from PostgreSQL table '{POSTGRES_TABLE}'")
        except Exception as e:
            print(f"ERROR: Failed to connect to PostgreSQL: {e}")
            print(f"Falling back to CSV if available at {DATA_FILE}")
            if DATA_FILE.exists():
                df_raw = load_data(DATA_FILE)
            else:
                sys.exit(1)
    else:
        if not DATA_FILE.exists():
            print(f"ERROR: Data file not found at {DATA_FILE}")
            print(f"Please place your CSV file at: {DATA_FILE}")
            print("Expected columns: deathFlag (target), and all other columns as predictors")
            sys.exit(1)
        df_raw = load_data(DATA_FILE)
    
    is_valid, msg = validate_data(df_raw, TARGET_COLUMN)
    if not is_valid:
        print(f"ERROR: {msg}")
        sys.exit(1)
    
    print(f"Dataset shape: {df_raw.shape}")
    summary = get_data_summary(df_raw, TARGET_COLUMN)
    print(f"Target distribution: {summary['target_distribution']}")
    
    # ========================================================================
    # 2. PREPARE FEATURES AND TARGET
    # ========================================================================
    print("\n[2/11] PREPARING FEATURES AND TARGET")
    print("-" * 80)
    
    X, y = prepare_features_and_target(df_raw, TARGET_COLUMN, IDENTIFIER_COLUMNS)
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    
    # ========================================================================
    # 3. TRAIN-TEST SPLIT
    # ========================================================================
    print("\n[3/11] TRAIN-TEST SPLIT (STRATIFIED)")
    print("-" * 80)
    
    X_train, X_test, y_train, y_test = train_test_split_stratified(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    
    # ========================================================================
    # 4. IMPUTATION
    # ========================================================================
    print("\n[4/11] IMPUTATION (MICEFOREST)")
    print("-" * 80)
    
    X_train, X_test, imputer = impute_missing_values(
        X_train, X_test, method='mice', random_state=RANDOM_STATE,
        mice_iterations=MICE_ITERATIONS
    )
    
    # ========================================================================
    # 5. SCALING
    # ========================================================================
    print("\n[5/11] FEATURE SCALING")
    print("-" * 80)
    
    X_train_scaled, X_test_scaled, scaler = scale_features(
        X_train, X_test, method=SCALING_METHOD
    )
    
    # Save preprocessing objects
    save_preprocessing_objects(imputer, scaler, MODELS_DIR)
    
    # ========================================================================
    # 6. TRAIN MODELS
    # ========================================================================
    print("\n[6/11] TRAINING MODELS")
    print("-" * 80)
    
    models = train_all_models(
        X_train, y_train,
        X_train_scaled=X_train_scaled,
        rf_params=RANDOM_FOREST_PARAMS,
        gb_params=GRADIENT_BOOSTING_PARAMS,
        lr_params=LOGISTIC_REGRESSION_PARAMS,
        ann_params=ANN_PARAMS,
        random_state=RANDOM_STATE
    )
    
    save_models(models, MODELS_DIR)
    
    # ========================================================================
    # 7. GET PREDICTIONS
    # ========================================================================
    print("\n[7/11] GENERATING PREDICTIONS")
    print("-" * 80)
    
    predictions = get_predictions(models, X_test, X_test_scaled)
    print(f"Predictions generated for {len(predictions)} models")
    
    # ========================================================================
    # 8. EVALUATE MODELS
    # ========================================================================
    print("\n[8/11] EVALUATING MODELS")
    print("-" * 80)
    
    results_df = evaluate_all_models(predictions, y_test, threshold=0.5)
    print_metrics_summary(results_df)
    save_metrics(results_df, TABLES_DIR, formats=['csv', 'excel'])
    
    # ========================================================================
    # 9. ROC CURVES
    # ========================================================================
    print("\n[9/11] PLOTTING ROC CURVES")
    print("-" * 80)
    
    roc_data = get_roc_data(predictions, y_test)
    
    plt.figure(figsize=(12, 8))
    colors = {'Logistic Regression': '#1f77b4', 'Random Forest': '#ff7f0e',
              'Gradient Boosting': '#2ca02c', 'ANN (MLPClassifier)': '#d62728'}
    
    for model_name, (fpr, tpr, auc_score) in roc_data.items():
        plt.plot(fpr, tpr, lw=2.5, label=f'{model_name} (AUC={auc_score:.3f})',
                 color=colors.get(model_name, None))
    
    plt.plot([0, 1], [0, 1], 'k--', lw=1.5, label='Chance (AUC=0.500)')
    plt.xlabel('False Positive Rate', fontsize=12, fontweight='bold')
    plt.ylabel('True Positive Rate', fontsize=12, fontweight='bold')
    plt.title('ROC Curves - ICU Mortality Prediction Models', fontsize=14, fontweight='bold')
    plt.legend(loc='lower right', fontsize=11)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(FIGURES_DIR / "roc_curves.png", dpi=300, bbox_inches='tight')
    plt.savefig(FIGURES_DIR / "roc_curves.pdf", dpi=300, bbox_inches='tight')
    print(f"✓ ROC curves saved to {FIGURES_DIR}")
    plt.close()
    
    # ========================================================================
    # 10. FEATURE IMPORTANCE
    # ========================================================================
    print("\n[10/11] FEATURE IMPORTANCE ANALYSIS")
    print("-" * 80)
    
    all_importance = extract_all_feature_importance(
        models, X_train, X_test_scaled, y_test,
        random_state=RANDOM_STATE,
        perm_repeats=PERMUTATION_IMPORTANCE_REPEATS
    )
    
    top_15_df = get_top_n_features(all_importance, n=TOP_N_FEATURES)
    print("\nTop 15 Features:")
    print(top_15_df.to_string(index=False))
    
    save_feature_importance(all_importance, top_15_df, TABLES_DIR, formats=['csv', 'excel'])
    
    # Plot feature importance
    fig = plot_feature_importance(all_importance, top_n=15)
    fig.savefig(FIGURES_DIR / "feature_importance.png", dpi=300, bbox_inches='tight')
    fig.savefig(FIGURES_DIR / "feature_importance.pdf", dpi=300, bbox_inches='tight')
    print(f"✓ Feature importance plots saved to {FIGURES_DIR}")
    plt.close()
    
    # ========================================================================
    # 11. SUMMARY
    # ========================================================================
    print("\n[11/11] PIPELINE COMPLETE")
    print("=" * 80)
    print(f"\nDataset: {DATA_FILE}")
    print(f"Training samples: {X_train.shape[0]} (deathFlag={y_train.sum()})")
    print(f"Test samples: {X_test.shape[0]} (deathFlag={y_test.sum()})")
    print(f"Number of features: {X_train.shape[1]}")
    print(f"\nModels trained: {len(models)}")
    
    best_model = results_df.loc[results_df['AUC'].idxmax(), 'Model']
    best_auc = results_df['AUC'].max()
    print(f"Best model (by AUC): {best_model} ({best_auc:.4f})")
    
    print(f"\nOutputs saved to:")
    print(f"  Tables:  {TABLES_DIR}")
    print(f"  Figures: {FIGURES_DIR}")
    print(f"  Models:  {MODELS_DIR}")
    print("\n✓ All outputs saved successfully!")
    print("=" * 80)

if __name__ == "__main__":
    main()
