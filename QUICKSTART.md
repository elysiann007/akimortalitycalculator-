# QUICK START GUIDE - ICU Mortality Prediction Pipeline

## ⚡ 5-Minute Quick Start

### Step 1: Prepare Your Environment

```powershell
# Open PowerShell or Command Prompt
cd c:\Users\V I S I O N\OurFinalProject

# Create virtual environment
python -m venv venv

# Activate it (Windows):
venv\Scripts\activate

# Or if using PowerShell:
venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected time:** 5-10 minutes (first time only)

### Step 3: Prepare Data

Place your CSV file at:
```
data/deu_icu_mortality.csv
```

**No file yet?** Generate sample data:
```bash
python generate_sample_data.py
```

This creates `data/deu_icu_mortality.csv` with 500 realistic ICU cases.

### Step 4: Run the Pipeline

**Option A: Modular (Recommended)**
```bash
python src/app.py
```

**Option B: Monolithic**
```bash
python full_pipeline.py
```

Both run identically, producing output in `outputs/` folder.

**Expected time:** 5-20 minutes depending on data size

### Step 5: Launch Web App (Optional)

After training:
```bash
streamlit run streamlit_app.py
```

Opens browser to `http://localhost:8501`

---

## 📊 What Gets Generated

After running the pipeline, you'll find:

### Tables (CSV + Excel)
- `outputs/tables/model_metrics.csv` - AUC, Accuracy, Precision, F1, Recall, MCC
- `outputs/tables/top_15_features.csv` - Most important features

### Figures (PNG + PDF)
- `outputs/figures/roc_curves.png` - ROC comparison for all 4 models
- `outputs/figures/feature_importance.png` - Feature importance by model

### Models (Pickle files)
- `outputs/models/random_forest.pkl` - Best performing typically
- `outputs/models/gradient_boosting.pkl`
- `outputs/models/logistic_regression.pkl`
- `outputs/models/ann_mlp.pkl`
- `outputs/models/scaler.pkl` - Feature scaling
- `outputs/models/imputer.pkl` - MICE imputer

---

## 📁 Data Format

Your CSV file should have:

```
age,hr,sbp,dbp,rr,spo2,temp,glucose,wbc,hgb,plt,cr,bun,na,k,cl,co2,alt,ast,bili,ph,pao2,paco2,lac,sofa,apache,deathFlag
65,85,120,75,18,96,37,150,10,11,200,1.0,20,140,4.0,105,24,30,35,0.8,7.35,90,40,1.5,5,15,0
70,95,110,68,20,93,37.5,180,12,10,150,1.2,25,138,4.1,104,23,40,45,1.2,7.32,85,42,2.0,8,20,1
...
```

**Key:**
- Last column: `deathFlag` (0 = survived, 1 = died)
- All other columns: numeric features
- No missing values required (MICE handles them)
- No special characters in column names

**If you have ID columns** (patient_id, row_id, etc.), they're auto-removed.

---

## 🎯 Models Trained

1. **Logistic Regression** - Fast, interpretable
2. **Random Forest** - Ensemble, robust
3. **Gradient Boosting** - Usually best performance
4. **ANN (MLPClassifier)** - Neural network

All are evaluated on test set with 6 metrics.

---

## 🔍 Key Results

After pipeline completes, you'll see:

```
METRICS COMPARISON TABLE
Model                   | AUC    | CA      | Precision | F1      | Recall  | MCC
Logistic Regression     | 0.7234 | 0.6789  | 0.6543    | 0.6234  | 0.5987  | 0.3456
Random Forest           | 0.8234 | 0.7654  | 0.7456    | 0.7234  | 0.7123  | 0.5234
Gradient Boosting       | 0.8456 | 0.7890  | 0.7654    | 0.7512  | 0.7389  | 0.5678
ANN (MLPClassifier)     | 0.8123 | 0.7456  | 0.7234    | 0.7012  | 0.6987  | 0.5012

Best model (by AUC): Gradient Boosting (0.8456)

Top 15 Features:
1. SOFA
2. APACHE
3. Age
4. Creatinine
5. Lactate
6. ...
```

---

## 🚀 Automated Setup (Windows)

Can't remember the commands? Use one of these:

### Batch File (Simple)
```batch
setup_and_run.bat
```
Then choose option 1, 2, or 3

### PowerShell Script (Advanced)
```powershell
powershell -ExecutionPolicy Bypass -File setup_and_run.ps1
```

Both handle environment creation, dependency installation, and let you choose what to run.

---

## ⚙️ Configuration

Edit `src/config.py` to adjust:

```python
# Test set proportion
TEST_SIZE = 0.2

# Random forest trees
RANDOM_FOREST_PARAMS = {'n_estimators': 200, ...}

# Gradient boosting iterations
GRADIENT_BOOSTING_PARAMS = {'n_estimators': 200, ...}

# ANN architecture
ANN_PARAMS = {'hidden_layer_sizes': (128, 64, 32), ...}

# Feature importance
TOP_N_FEATURES = 15
```

---

## 🐛 Common Issues & Solutions

### "Data file not found"
→ Run: `python generate_sample_data.py`

### "ModuleNotFoundError: No module named..."
→ Run: `pip install -r requirements.txt`

### "Permission denied" on activate script
→ Use: `powershell -ExecutionPolicy Bypass`

### Streamlit app won't load models
→ Make sure `src/app.py` finished successfully first

### Out of memory
→ Reduce `n_estimators` in config.py

---

## 📖 Detailed Documentation

See `README.md` for:
- Full module reference
- PostgreSQL data loading
- Custom hyperparameters
- Model limitations
- Troubleshooting

---

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `src/app.py` | Main orchestrator (recommended) |
| `full_pipeline.py` | Monolithic version (alternative) |
| `streamlit_app.py` | Web UI for predictions |
| `src/config.py` | Configuration & hyperparameters |
| `src/preprocessing.py` | Data prep (MICE, scaling) |
| `src/train_models.py` | Model training |
| `src/evaluate.py` | Metrics & evaluation |
| `src/feature_importance.py` | Feature analysis |
| `requirements.txt` | Dependencies |

---

## ✅ Verification Checklist

Before running:
- [ ] Python 3.9+ installed (`python --version`)
- [ ] CSV file at `data/deu_icu_mortality.csv`
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list | grep pandas`)

After running:
- [ ] `outputs/tables/model_metrics.csv` created
- [ ] `outputs/figures/roc_curves.png` created
- [ ] `outputs/models/random_forest.pkl` created
- [ ] No errors in console output

---

## 💡 Next Steps

1. **Examine results** in `outputs/tables/`
2. **Review metrics** in Excel or CSV
3. **View plots** (ROC curves, feature importance)
4. **Try predictions** with Streamlit app
5. **Adjust hyperparameters** in `config.py` if needed
6. **Analyze features** - which are most predictive?
7. **Fine-tune threshold** for your use case

---

## ⚠️ Important Reminders

🔴 **DO NOT** use for clinical decisions  
🔴 **DO NOT** share patient data  
🟢 **DO** validate with clinical experts  
🟢 **DO** follow institutional policies  
🟢 **DO** document any modifications  

---

## 📞 Help

Check these files for help:
- `README.md` - Complete documentation
- Error messages in console output
- Individual module docstrings

---

**Ready?** Run: `python src/app.py` 🚀
