# AKI Kidney Project

A comprehensive production-ready Python pipeline for predicting kidney injury and ICU mortality using machine learning models trained on a cleaned DEU hospital retrospective dataset.

## Project Structure

```
aki-kidney-project/
├── src/
│   ├── config.py                 # Configuration and hyperparameters
│   ├── data_loader.py            # Data loading (CSV/PostgreSQL)
│   ├── preprocessing.py          # Preprocessing, imputation, scaling
│   ├── train_models.py           # Model training
│   ├── evaluate.py               # Model evaluation and metrics
│   ├── feature_importance.py     # Feature importance analysis
│   └── app.py                    # Main orchestrator
├── data/                         # Data directory
│   └── deu_icu_mortality.csv    # (Place your dataset here)
├── outputs/
│   ├── tables/                   # CSV/Excel tables
│   │   ├── model_metrics.csv
│   │   ├── model_metrics.xlsx
│   │   ├── top_15_features.csv
│   │   └── top_15_features.xlsx
│   ├── figures/                  # Plots and visualizations
│   │   ├── roc_curves.png
│   │   ├── roc_curves.pdf
│   │   └── feature_importance.png
│   └── models/                   # Saved model files
│       ├── random_forest.pkl
│       ├── gradient_boosting.pkl
│       ├── logistic_regression.pkl
│       ├── ann_mlp.pkl
│       ├── scaler.pkl
│       └── imputer.pkl
├── full_pipeline.py              # Monolithic end-to-end script
├── streamlit_app.py              # Web app for predictions
├── requirements.txt              # Python dependencies
└── README.md                      # This file

```

## Quick Start

### 1. Install Python 3.9+

Ensure you have Python 3.9 or higher installed on your system.

### 2. Create Virtual Environment (Recommended)

```bash
# Navigate to project directory
cd c:\Users\V I S I O N\OurFinalProject

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Prepare Your Data

Place your cleaned DEU hospital ICU mortality dataset at:
```
data/deu_icu_mortality.csv
```

**Expected columns:**
- `deathFlag`: Target variable (binary: 0=survived, 1=died)
- All other numeric columns: predictor variables
- Avoid columns like `row_id`, `patient_id`, `protocol_no` (will be auto-removed)

**Data should be:**
- Cleaned and preprocessed
- Numeric features (categorical features will be one-hot encoded)
- No special characters in column names

## Running the Pipeline

### Option A: Run Full End-to-End Pipeline (Modular Version)

This is the recommended approach - uses clean, modular code:

```bash
python src/app.py
```

This will:
1. Load and validate data
2. Prepare features and target
3. Perform stratified train-test split
4. Impute missing values using MICEFOREST
5. Scale features using StandardScaler
6. Train 4 models:
   - Logistic Regression
   - Random Forest
   - Gradient Boosting
   - Artificial Neural Network (MLPClassifier)
7. Evaluate models on test set
8. Generate ROC curves
9. Analyze feature importance
10. Save all outputs to `outputs/` directory

**Output files created:**
- `outputs/tables/model_metrics.csv` - Performance metrics for all models
- `outputs/tables/model_metrics.xlsx` - Same as above in Excel format
- `outputs/tables/top_15_features.csv` - Top 15 most important features
- `outputs/tables/top_15_features.xlsx` - Same as above in Excel format
- `outputs/figures/roc_curves.png` - ROC curve comparison (high resolution)
- `outputs/figures/roc_curves.pdf` - ROC curves in PDF format
- `outputs/figures/feature_importance.png` - Per-model feature importance plots
- `outputs/models/*.pkl` - Trained models and preprocessing objects

### Option B: Run Full Monolithic Script

Alternative: run the complete single-file version:

```bash
python full_pipeline.py
```

This produces identical output but uses all code in one file (good for learning).

## Running the Web App

After training the models, launch the Streamlit web application for interactive mortality predictions:

```bash
streamlit run streamlit_app.py
```

This will:
1. Open a local web browser to `http://localhost:8501`
2. Display the mortality risk predictor interface
3. Load the trained best model
4. Allow you to input patient values and get predictions

**Features:**
- Input fields for top 15 predictive features
- Real-time probability and risk level predictions
- Mortality and survival probability
- Risk level classification (LOW/MODERATE/HIGH)
- Research-only disclaimer
- Model information and limitations

## Key Features

### Data Preprocessing
- **Automatic ID column removal**: Removes non-predictive identifiers (row_id, patient_id, etc.)
- **Categorical encoding**: One-hot encoding for categorical features
- **Missing value imputation**: MICEFOREST-based multiple imputation
- **Feature scaling**: StandardScaler for models requiring scaling
- **Data leakage prevention**: Imputation and scaling fit only on training data

### Model Training
- **4 ML Algorithms**:
  1. Logistic Regression (interpretable linear model)
  2. Random Forest (tree ensemble)
  3. Gradient Boosting (sequential ensemble)
  4. Artificial Neural Network (deep learning)
- **Stratified train-test split**: 80% train, 20% test, stratified on target
- **Reproducibility**: Fixed random seeds throughout

### Evaluation Metrics
- AUC (Area Under ROC Curve)
- CA (Classification Accuracy)
- Precision
- Recall
- F1-Score
- MCC (Matthews Correlation Coefficient)

### Feature Importance
- **Random Forest**: Built-in feature importance
- **Gradient Boosting**: Built-in feature importance
- **Logistic Regression**: Absolute coefficient magnitudes
- **ANN**: Permutation importance
- **Combined**: Top 15 features aggregated across all models

### Output Formats
- CSV and Excel tables for metrics and features
- High-resolution PNG and PDF figures
- Saved trained models and preprocessing objects

## Configuration

Edit `src/config.py` to customize:

```python
# Random seed for reproducibility
RANDOM_STATE = 42

# Test set size
TEST_SIZE = 0.2

# Model hyperparameters
RANDOM_FOREST_PARAMS = {
    'n_estimators': 200,
    'max_depth': 20,
    'min_samples_split': 10,
    ...
}

# And more...
```

## Module Reference

### `config.py`
Centralized configuration, paths, and hyperparameters.

### `data_loader.py`
- `load_data()`: Load from CSV or PostgreSQL
- `validate_data()`: Check dataset integrity
- `get_data_summary()`: Statistical summary

### `preprocessing.py`
- `prepare_features_and_target()`: Extract features/target
- `train_test_split_stratified()`: Stratified split
- `impute_missing_values()`: MICE or mean imputation
- `scale_features()`: StandardScaler or RobustScaler

### `train_models.py`
- `train_all_models()`: Train all 4 models
- `get_predictions()`: Generate probability predictions
- `save_models()`, `load_models()`: Model persistence

### `evaluate.py`
- `evaluate_all_models()`: Compute all metrics
- `get_roc_data()`: ROC curve data
- `save_metrics()`: Export results

### `feature_importance.py`
- `extract_all_feature_importance()`: Importance from all models
- `get_top_n_features()`: Top N aggregated features
- `plot_feature_importance()`: Visualization
- `save_feature_importance()`: Export tables

### `app.py`
Main orchestrator that calls all modules in sequence.

## Troubleshooting

### "Data file not found"
Ensure `data/deu_icu_mortality.csv` exists with correct structure.

### "No missing values detected"
If your dataset is already complete, imputation step is skipped (normal behavior).

### Memory issues with large datasets
- Reduce `n_estimators` in `RANDOM_FOREST_PARAMS` and `GRADIENT_BOOSTING_PARAMS`
- Set `n_jobs=-1` uses all cores; use `n_jobs=4` to limit

### Streamlit app not loading models
Ensure `src/app.py` has been run successfully first.

## Important Notes

### Research Use Only
✅ Use this tool for research and demonstration  
❌ DO NOT use for clinical decision-making  
⚠️ Always validate predictions with clinical experts

### Data Privacy
- Keep all data in secure locations
- Do not share patient information
- Follow institutional data governance policies

### Model Limitations
- Trained on specific hospital population
- May not generalize to different populations
- Uses only ICU vital signs and lab values
- Missing important contextual information
- Should supplement, not replace, clinical judgment

## Citation

If you use this pipeline in research, please cite:

```
ICU Mortality Prediction Pipeline (2024)
DEU Hospital Retrospective Dataset Analysis
For research use only
```

## License

This project is provided for research and educational purposes.

## Contact & Support

For issues or questions, refer to the error messages and check:
1. Data format and column names
2. Python version (3.9+)
3. All dependencies installed (`pip list`)
4. Sufficient disk space for models and outputs

---

**Last Updated**: 2024
**Python Version**: 3.9+
**Status**: Production-Ready
