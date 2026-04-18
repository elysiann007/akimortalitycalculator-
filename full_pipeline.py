"""
ICU Mortality Prediction - Full End-to-End Pipeline
DEU Hospital Dataset Analysis
"""

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    auc, roc_curve, classification_report, confusion_matrix,
    accuracy_score, precision_score, f1_score, recall_score,
    roc_auc_score, matthews_corrcoef
)
from sklearn.inspection import permutation_importance
import miceforest as mf

# Set random seeds for reproducibility
np.random.seed(42)

# Configuration
RANDOM_STATE = 42
TEST_SIZE = 0.2
DATA_PATH = Path("data/deu_icu_mortality.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
(OUTPUT_DIR / "tables").mkdir(exist_ok=True)
(OUTPUT_DIR / "figures").mkdir(exist_ok=True)
(OUTPUT_DIR / "models").mkdir(exist_ok=True)

# PostgreSQL Configuration
USE_POSTGRES = True
POSTGRES_HOST = 'localhost'
POSTGRES_PORT = 5432
POSTGRES_DATABASE = 'M3'
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = '93abH@llo810'
POSTGRES_TABLE = 'deu_retro_clean'
POSTGRES_QUERY = f'SELECT * FROM {POSTGRES_TABLE}'

# ============================================================================
# 1. LOAD DATA
# ============================================================================

def load_data_csv(filepath):
    """Load data from CSV"""
    df = pd.read_csv(filepath)
    return df

def load_data_postgres(host, port, database, user, password, query):
    """Load data from PostgreSQL"""
    from sqlalchemy import create_engine
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')
    df = pd.read_sql(query, engine)
    engine.dispose()
    return df

print("=" * 80)
print("STEP 1: LOADING DATA")
print("=" * 80)

if USE_POSTGRES:
    print(f"Connecting to PostgreSQL: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}")
    try:
        df_raw = load_data_postgres(POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE, 
                                     POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_QUERY)
        print(f"✓ Successfully loaded {len(df_raw)} rows from PostgreSQL table '{POSTGRES_TABLE}'")
    except Exception as e:
        print(f"ERROR: Failed to connect to PostgreSQL: {e}")
        print(f"Falling back to CSV if available at {DATA_PATH}")
        if DATA_PATH.exists():
            df_raw = load_data_csv(DATA_PATH)
        else:
            exit(1)
else:
    if not DATA_PATH.exists():
        print(f"ERROR: Data file not found at {DATA_PATH}")
        print("Please place your DEU ICU dataset CSV file at: data/deu_icu_mortality.csv")
        print("Expected columns: deathFlag (target), and all other columns as predictors")
        exit(1)
    df_raw = load_data_csv(DATA_PATH)

print(f"\nDataset shape: {df_raw.shape}")
print(f"Dataset dtypes:\n{df_raw.dtypes}\n")
print(f"First few rows:\n{df_raw.head()}\n")

# ============================================================================
# 2. EXPLORATORY DATA ANALYSIS & VALIDATION
# ============================================================================

print("=" * 80)
print("STEP 2: DATA VALIDATION")
print("=" * 80)

# Check target variable exists
if 'deathFlag' not in df_raw.columns:
    raise ValueError("Target column 'deathFlag' not found in dataset")

print(f"\nTarget variable (deathFlag) distribution:")
print(df_raw['deathFlag'].value_counts())
print(f"Class balance: {df_raw['deathFlag'].value_counts(normalize=True).to_dict()}")

# Missing values before imputation
print(f"\nMissing values before preprocessing:")
missing_counts = df_raw.isnull().sum()
if missing_counts.sum() > 0:
    print(missing_counts[missing_counts > 0])
else:
    print("No missing values detected")

# ============================================================================
# 3. PREPROCESSING & FEATURE ENGINEERING
# ============================================================================

print("\n" + "=" * 80)
print("STEP 3: PREPROCESSING")
print("=" * 80)

df = df_raw.copy()

# Separate target from features
y = df['deathFlag'].astype(int)
X = df.drop('deathFlag', axis=1)

print(f"\nTarget variable shape: {y.shape}")
print(f"Features shape: {X.shape}")

# Remove non-predictive identifier columns
id_cols = [col for col in X.columns if col.lower() in ['row_id', 'id', 'protocol_no', 'patient_id', 'study_id']]
if id_cols:
    print(f"Removing identifier columns: {id_cols}")
    X = X.drop(columns=id_cols)

print(f"Features after removing IDs: {X.shape}")

# Handle categorical columns: identify and encode if necessary
numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
cat_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()

print(f"Numeric columns: {len(numeric_cols)}")
print(f"Categorical columns: {len(cat_cols)}")

if cat_cols:
    print(f"Categorical columns found: {cat_cols}")
    # Simple one-hot encoding for categorical variables
    X = pd.get_dummies(X, columns=cat_cols, drop_first=True)
    print(f"After one-hot encoding, shape: {X.shape}")

# Ensure all features are numeric
X = X.astype(float)

# ============================================================================
# 4. TRAIN-TEST SPLIT (BEFORE IMPUTATION)
# ============================================================================

print("\n" + "=" * 80)
print("STEP 4: TRAIN-TEST SPLIT (STRATIFIED)")
print("=" * 80)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y
)

print(f"Training set size: {X_train.shape}")
print(f"Test set size: {X_test.shape}")
print(f"Training set class balance: {y_train.value_counts(normalize=True).to_dict()}")
print(f"Test set class balance: {y_test.value_counts(normalize=True).to_dict()}")

# ============================================================================
# 5. IMPUTATION (FIT ON TRAIN, APPLY TO TEST)
# ============================================================================

print("\n" + "=" * 80)
print("STEP 5: IMPUTATION USING MICEFOREST")
print("=" * 80)

# Check for missing values
train_missing = X_train.isnull().sum()
if train_missing.sum() > 0:
    print(f"Training set missing values:\n{train_missing[train_missing > 0]}")
    
    # Fit imputer on training data
    print("\nFitting MICE imputer on training data...")
    imputer = mf.ImputationKernel(
        X_train.copy(),
        datasets=1,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )
    imputer.mice(iterations=5, verbose=False)
    X_train = imputer.complete_data()
    
    # Apply to test data
    print("Applying imputer to test data...")
    X_test_imputed = X_test.copy()
    # Use mean/forward fill for test set based on training statistics
    for col in X_test_imputed.columns:
        if X_test_imputed[col].isnull().sum() > 0:
            X_test_imputed[col].fillna(X_train[col].mean(), inplace=True)
    X_test = X_test_imputed
    
    # Save imputer
    joblib.dump(imputer, OUTPUT_DIR / "models" / "imputer.pkl")
    print(f"Imputer saved to {OUTPUT_DIR / 'models' / 'imputer.pkl'}")
else:
    print("No missing values detected in training set")
    imputer = None

print(f"Training set shape after imputation: {X_train.shape}")
print(f"Test set shape after imputation: {X_test.shape}")

# ============================================================================
# 6. SCALING (FIT ON TRAIN, APPLY TO TEST)
# ============================================================================

print("\n" + "=" * 80)
print("STEP 6: FEATURE SCALING")
print("=" * 80)

# Use StandardScaler for consistency
scaler = StandardScaler()
scaler.fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Create DataFrames to preserve column names
X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)

# Save scaler
joblib.dump(scaler, OUTPUT_DIR / "models" / "scaler.pkl")
print(f"Scaler saved to {OUTPUT_DIR / 'models' / 'scaler.pkl'}")

# ============================================================================
# 7. TRAIN MODELS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 7: TRAINING MODELS")
print("=" * 80)

models = {}
predictions = {}

# 7.1 Logistic Regression (uses scaled data)
print("\nTraining Logistic Regression...")
lr = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE, n_jobs=-1)
lr.fit(X_train_scaled, y_train)
models['Logistic Regression'] = lr
predictions['Logistic Regression'] = lr.predict_proba(X_test_scaled)[:, 1]
joblib.dump(lr, OUTPUT_DIR / "models" / "logistic_regression.pkl")
print("✓ Logistic Regression trained and saved")

# 7.2 Random Forest (uses unscaled data)
print("Training Random Forest...")
rf = RandomForestClassifier(n_estimators=200, max_depth=20, min_samples_split=10,
                             random_state=RANDOM_STATE, n_jobs=-1, verbose=0)
rf.fit(X_train, y_train)
models['Random Forest'] = rf
predictions['Random Forest'] = rf.predict_proba(X_test)[:, 1]
joblib.dump(rf, OUTPUT_DIR / "models" / "random_forest.pkl")
print("✓ Random Forest trained and saved")

# 7.3 Gradient Boosting (uses unscaled data)
print("Training Gradient Boosting...")
gb = GradientBoostingClassifier(n_estimators=200, max_depth=5, learning_rate=0.05,
                                 random_state=RANDOM_STATE, verbose=0)
gb.fit(X_train, y_train)
models['Gradient Boosting'] = gb
predictions['Gradient Boosting'] = gb.predict_proba(X_test)[:, 1]
joblib.dump(gb, OUTPUT_DIR / "models" / "gradient_boosting.pkl")
print("✓ Gradient Boosting trained and saved")

# 7.4 Artificial Neural Network (MLPClassifier) (uses scaled data)
print("Training Artificial Neural Network (MLP)...")
ann = MLPClassifier(hidden_layer_sizes=(128, 64, 32), max_iter=500, 
                     random_state=RANDOM_STATE, early_stopping=True,
                     validation_fraction=0.1, n_iter_no_change=20, verbose=0)
ann.fit(X_train_scaled, y_train)
models['ANN (MLPClassifier)'] = ann
predictions['ANN (MLPClassifier)'] = ann.predict_proba(X_test_scaled)[:, 1]
joblib.dump(ann, OUTPUT_DIR / "models" / "ann_mlp.pkl")
print("✓ ANN trained and saved")

# ============================================================================
# 8. EVALUATE MODELS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 8: MODEL EVALUATION")
print("=" * 80)

results = []

for model_name, y_pred_proba in predictions.items():
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    # Calculate metrics
    auc_score = roc_auc_score(y_test, y_pred_proba)
    ca = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    mcc = matthews_corrcoef(y_test, y_pred)
    
    results.append({
        'Model': model_name,
        'AUC': auc_score,
        'CA (Accuracy)': ca,
        'Precision': precision,
        'F1-Score': f1,
        'Recall': recall,
        'MCC': mcc
    })
    
    print(f"\n{model_name}:")
    print(f"  AUC:      {auc_score:.4f}")
    print(f"  CA:       {ca:.4f}")
    print(f"  Precision:{precision:.4f}")
    print(f"  F1:       {f1:.4f}")
    print(f"  Recall:   {recall:.4f}")
    print(f"  MCC:      {mcc:.4f}")

# Create results dataframe
results_df = pd.DataFrame(results)
print("\n" + "=" * 80)
print("METRICS COMPARISON TABLE")
print("=" * 80)
print(results_df.to_string(index=False))

# Save results
results_df.to_csv(OUTPUT_DIR / "tables" / "model_metrics.csv", index=False)
results_df.to_excel(OUTPUT_DIR / "tables" / "model_metrics.xlsx", index=False)
print(f"\n✓ Metrics saved to {OUTPUT_DIR / 'tables' / 'model_metrics.csv'}")
print(f"✓ Metrics saved to {OUTPUT_DIR / 'tables' / 'model_metrics.xlsx'}")

# ============================================================================
# 9. ROC CURVES
# ============================================================================

print("\n" + "=" * 80)
print("STEP 9: ROC CURVE PLOTTING")
print("=" * 80)

plt.figure(figsize=(12, 8))
colors = {'Logistic Regression': '#1f77b4', 'Random Forest': '#ff7f0e',
          'Gradient Boosting': '#2ca02c', 'ANN (MLPClassifier)': '#d62728'}

for model_name, y_pred_proba in predictions.items():
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    auc_score = auc(fpr, tpr)
    plt.plot(fpr, tpr, lw=2.5, label=f'{model_name} (AUC={auc_score:.3f})',
             color=colors.get(model_name, None))

plt.plot([0, 1], [0, 1], 'k--', lw=1.5, label='Chance (AUC=0.500)')
plt.xlabel('False Positive Rate', fontsize=12, fontweight='bold')
plt.ylabel('True Positive Rate', fontsize=12, fontweight='bold')
plt.title('ROC Curves - Mortality Prediction Models', fontsize=14, fontweight='bold')
plt.legend(loc='lower right', fontsize=11)
plt.grid(alpha=0.3)
plt.tight_layout()

# Save figure
plt.savefig(OUTPUT_DIR / "figures" / "roc_curves.png", dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / "figures" / "roc_curves.pdf", dpi=300, bbox_inches='tight')
print(f"✓ ROC curves saved to {OUTPUT_DIR / 'figures' / 'roc_curves.png'}")
print(f"✓ ROC curves saved to {OUTPUT_DIR / 'figures' / 'roc_curves.pdf'}")
plt.close()

# ============================================================================
# 10. FEATURE IMPORTANCE ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 10: FEATURE IMPORTANCE ANALYSIS")
print("=" * 80)

feature_importance_list = []

# Random Forest feature importance
print("\nExtracting Random Forest feature importance...")
rf_importance = pd.DataFrame({
    'Feature': X_train.columns,
    'Importance': models['Random Forest'].feature_importances_
}).sort_values('Importance', ascending=False)
rf_importance['Model'] = 'Random Forest'
feature_importance_list.append(rf_importance)

# Gradient Boosting feature importance
print("Extracting Gradient Boosting feature importance...")
gb_importance = pd.DataFrame({
    'Feature': X_train.columns,
    'Importance': models['Gradient Boosting'].feature_importances_
}).sort_values('Importance', ascending=False)
gb_importance['Model'] = 'Gradient Boosting'
feature_importance_list.append(gb_importance)

# Logistic Regression: use absolute coefficient values (from scaled model)
print("Extracting Logistic Regression coefficients...")
lr_coefs = np.abs(models['Logistic Regression'].coef_[0])
lr_importance = pd.DataFrame({
    'Feature': X_train_scaled.columns,
    'Importance': lr_coefs / lr_coefs.sum()
}).sort_values('Importance', ascending=False)
lr_importance['Model'] = 'Logistic Regression'
feature_importance_list.append(lr_importance)

# ANN: use permutation importance
print("Computing permutation importance for ANN (this may take a moment)...")
perm_importance = permutation_importance(
    models['ANN (MLPClassifier)'], X_test_scaled, y_test,
    n_repeats=10, random_state=RANDOM_STATE, n_jobs=-1
)
ann_importance = pd.DataFrame({
    'Feature': X_train_scaled.columns,
    'Importance': perm_importance.importances_mean
}).sort_values('Importance', ascending=False)
ann_importance['Model'] = 'ANN (MLPClassifier)'
feature_importance_list.append(ann_importance)

# Combine and create Top 15 overall importance
print("\nGenerating Top 15 features table...")
all_importance = pd.concat(feature_importance_list, ignore_index=True)
top_15_overall = all_importance.groupby('Feature')['Importance'].mean().sort_values(ascending=False).head(15)

top_15_df = pd.DataFrame({
    'Rank': range(1, 16),
    'Feature': top_15_overall.index,
    'Mean Importance': top_15_overall.values
})

print("\nTop 15 Features:")
print(top_15_df.to_string(index=False))

# Save feature importance
top_15_df.to_csv(OUTPUT_DIR / "tables" / "top_15_features.csv", index=False)
top_15_df.to_excel(OUTPUT_DIR / "tables" / "top_15_features.xlsx", index=False)
print(f"\n✓ Top 15 features saved to {OUTPUT_DIR / 'tables' / 'top_15_features.csv'}")
print(f"✓ Top 15 features saved to {OUTPUT_DIR / 'tables' / 'top_15_features.xlsx'}")

# Save full importance per model
for model_name, importance_df in zip(
    ['Random Forest', 'Gradient Boosting', 'Logistic Regression', 'ANN (MLPClassifier)'],
    feature_importance_list
):
    importance_df_sorted = importance_df.sort_values('Importance', ascending=False)
    filename = model_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
    importance_df_sorted.to_csv(OUTPUT_DIR / "tables" / f"feature_importance_{filename}.csv", index=False)

# ============================================================================
# 11. FEATURE IMPORTANCE VISUALIZATION
# ============================================================================

print("\nCreating feature importance plot...")
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
axes = axes.ravel()

for idx, (model_name, importance_df) in enumerate(zip(
    ['Random Forest', 'Gradient Boosting', 'Logistic Regression', 'ANN (MLPClassifier)'],
    feature_importance_list
)):
    top_15 = importance_df.nlargest(15, 'Importance')
    axes[idx].barh(range(len(top_15)), top_15['Importance'].values)
    axes[idx].set_yticks(range(len(top_15)))
    axes[idx].set_yticklabels(top_15['Feature'].values, fontsize=9)
    axes[idx].set_xlabel('Importance', fontweight='bold')
    axes[idx].set_title(f'Top 15 Features - {model_name}', fontweight='bold')
    axes[idx].invert_yaxis()

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "figures" / "feature_importance.png", dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / "figures" / "feature_importance.pdf", dpi=300, bbox_inches='tight')
print(f"✓ Feature importance plot saved to {OUTPUT_DIR / 'figures' / 'feature_importance.png'}")
plt.close()

# ============================================================================
# 12. SUMMARY & FINAL REPORT
# ============================================================================

print("\n" + "=" * 80)
print("PIPELINE COMPLETE - SUMMARY")
print("=" * 80)
print(f"\nDataset: {DATA_PATH}")
print(f"Training samples: {X_train.shape[0]} (deathFlag={y_train.sum()})")
print(f"Test samples: {X_test.shape[0]} (deathFlag={y_test.sum()})")
print(f"Number of features: {X_train.shape[1]}")
print(f"\nModels trained: {', '.join(models.keys())}")
print(f"\nBest model (by AUC): {results_df.loc[results_df['AUC'].idxmax(), 'Model']} (AUC={results_df['AUC'].max():.4f})")
print(f"\nOutput directory: {OUTPUT_DIR}")
print(f"  - Tables: {OUTPUT_DIR / 'tables'}")
print(f"  - Figures: {OUTPUT_DIR / 'figures'}")
print(f"  - Models: {OUTPUT_DIR / 'models'}")
print("\n✓ All outputs saved successfully!")
print("=" * 80)
