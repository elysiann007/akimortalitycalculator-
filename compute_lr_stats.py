"""
Logistic Regression katsayıları için Standart Sapma (SE) ve P-değeri hesaplar.
Yöntem: Fisher Bilgi Matrisi (Hessian) üzerinden analitik standart hata.
"""

import numpy as np
import pandas as pd
import joblib
from scipy import stats
from pathlib import Path
import sys, io

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent / 'src'))
from config import (MODELS_DIR, TABLES_DIR,
                    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE,
                    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_TABLE,
                    TARGET_COLUMN, IDENTIFIER_COLUMNS)

# ── 1. Veri yükle ────────────────────────────────────────────────────────────
print("Veri yükleniyor (PostgreSQL)...")
from sqlalchemy import create_engine
engine = create_engine(f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}')
df = pd.read_sql(f"SELECT * FROM {POSTGRES_TABLE}", engine)
engine.dispose()
print(f"  {len(df)} satır, {df.shape[1]} sütun")

# Binlik ayraçlı string sayıları temizle (örn. '106,926.00' → 106926.0)
for col in df.columns:
    if df[col].dtype == object:
        converted = df[col].astype(str).str.replace(',', '', regex=False)
        numeric = pd.to_numeric(converted, errors='coerce')
        if numeric.notna().mean() > 0.5:
            df[col] = numeric

# ── 2. Özellik / hedef ayır ───────────────────────────────────────────────────
drop_cols = [c for c in IDENTIFIER_COLUMNS if c in df.columns] + [TARGET_COLUMN]
y = df[TARGET_COLUMN].values
X_raw = df.drop(columns=drop_cols)

# Tüm string sütunları sayısala çevir (binlik ayraç vb.)
for col in X_raw.columns:
    if not pd.api.types.is_numeric_dtype(X_raw[col]):
        X_raw[col] = pd.to_numeric(
            X_raw[col].astype(str).str.replace(',', '', regex=False),
            errors='coerce'
        )
        print(f"  Dönüştürüldü: {col}")
feature_names = X_raw.columns.tolist()

# ── 3. Ön işleme (kayıtlı imputer + scaler) ──────────────────────────────────
imputer = joblib.load(MODELS_DIR / 'imputer.pkl')
scaler  = joblib.load(MODELS_DIR / 'scaler.pkl')

X_imp    = imputer.transform(X_raw)
X_scaled = scaler.transform(X_imp)

# ── 4. Model yükle ───────────────────────────────────────────────────────────
lr = joblib.load(MODELS_DIR / 'logistic_regression.pkl')
coef = lr.coef_[0]          # (n_features,)
intercept = lr.intercept_[0]

# ── 5. Standart Hata (Fisher Bilgi Matrisi) ──────────────────────────────────
# X'e sabit (intercept) sütunu ekle
X_aug = np.hstack([np.ones((X_scaled.shape[0], 1)), X_scaled])  # (n, p+1)

p_hat = lr.predict_proba(X_scaled)[:, 1]          # tahmin olasılıkları
W     = p_hat * (1 - p_hat)                        # ağırlıklar (diyagonal)

# Fisher bilgi matrisi: X^T W X
FIM = (X_aug * W[:, None]).T @ X_aug               # (p+1, p+1)

try:
    cov = np.linalg.inv(FIM)
    se_all = np.sqrt(np.diag(cov))
    se_features = se_all[1:]   # intercept'i çıkar
except np.linalg.LinAlgError:
    print("  Uyarı: FIM tekil — pseudo-inverse kullanılıyor")
    cov = np.linalg.pinv(FIM)
    se_all = np.sqrt(np.abs(np.diag(cov)))
    se_features = se_all[1:]

# ── 6. Z-score ve P-değeri ────────────────────────────────────────────────────
z_scores = coef / se_features
p_values = 2 * (1 - stats.norm.cdf(np.abs(z_scores)))

# ── 7. Tablo oluştur (görseldeki sıralamayı koru: normalize önem) ────────────
abs_coef   = np.abs(coef)
importance = abs_coef / abs_coef.sum()

result = pd.DataFrame({
    'Feature':    feature_names,
    'Importance': importance,
    'Coef':       coef,
    'Std_Error':  se_features,
    'Z_Score':    z_scores,
    'P_Value':    p_values,
    'Model':      'Logistic Regression'
}).sort_values('Importance', ascending=False).reset_index(drop=True)

result['Significance'] = result['P_Value'].apply(
    lambda p: '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'ns'))
)

# ── 8. Yazdır ────────────────────────────────────────────────────────────────
print("\nLogistic Regression — Katsayı İstatistikleri\n")
display = result[['Feature','Importance','Coef','Std_Error','Z_Score','P_Value','Significance']].copy()
display.index = range(1, len(display)+1)
pd.set_option('display.float_format', '{:.6f}'.format)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 120)
print(display.to_string())

# ── 9. Kaydet ─────────────────────────────────────────────────────────────────
out_csv  = TABLES_DIR / 'lr_feature_importance_with_stats.csv'
out_xlsx = TABLES_DIR / 'lr_feature_importance_with_stats.xlsx'

result.to_csv(out_csv, index=False)
result.to_excel(out_xlsx, index=False)
print(f"\nKaydedildi: {out_csv}")
print(f"Kaydedildi: {out_xlsx}")
