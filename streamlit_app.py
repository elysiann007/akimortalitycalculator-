"""
AKI Mortality Risk Calculator — TR/EN
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import sys, io

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent / 'src'))
from config import MODELS_DIR

st.set_page_config(
    page_title="AKI Mortalite Risk Hesaplayicisi",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
/* ── Hide chrome ── */
#MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stSidebar"] { display:none !important; }

/* ── Navbar ── */
.navbar {
    background: #003087;
    color: #fff;
    padding: 0 32px;
    height: 52px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: 8px;
    margin-bottom: 0;
}
.navbar-brand { font-size: 0.95rem; font-weight: 700; color: #fff; }
.navbar-tag {
    background: rgba(255,255,255,0.18);
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    color: #fff;
    letter-spacing: 0.4px;
}

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #003f8a 0%, #0062cc 100%);
    padding: 26px 32px 22px;
    margin-bottom: 20px;
}
.hero h1 { margin: 0 0 5px; font-size: 1.55rem; font-weight: 700; color: #fff; line-height: 1.25; }
.hero p  { margin: 0; font-size: 0.83rem; color: rgba(255,255,255,0.80); }

/* ── Disclaimer ── */
.disclaimer {
    background: #fff8e1;
    border-left: 4px solid #f59e0b;
    border-radius: 0 6px 6px 0;
    padding: 10px 16px;
    font-size: 0.81rem;
    color: #7c4b00;
    margin-bottom: 20px;
    line-height: 1.5;
}

/* ── Cards ── */
.section-card {
    background: #ffffff;
    border-radius: 10px;
    border: 1px solid #dde3ed;
    padding: 22px 26px 18px;
    margin-bottom: 18px;
    box-shadow: 0 1px 5px rgba(0,0,0,0.05);
}
.card-header {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.9px;
    color: #003087;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 2px solid #edf0f7;
}

/* ── Info table rows ── */
.info-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #f1f5f9;
    font-size: 0.84rem;
}
.info-key { color: #64748b; font-weight: 500; }
.info-val { color: #1a2540; font-weight: 700; }

/* ── Metric boxes ── */
.metric-row { display: flex; gap: 14px; margin-bottom: 18px; }
.metric-card {
    flex: 1;
    background: #f8fafc;
    border: 1px solid #dde3ed;
    border-radius: 8px;
    padding: 16px 12px;
    text-align: center;
}
.m-label { font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 6px; }
.m-value { font-size: 1.9rem; font-weight: 700; line-height: 1; }

/* ── Badge ── */
.risk-badge {
    display: inline-block;
    padding: 5px 16px;
    border-radius: 20px;
    font-size: 0.77rem;
    font-weight: 700;
    letter-spacing: 0.6px;
    margin: 10px 0 6px;
}
.badge-high     { background:#fee2e2; color:#b91c1c; }
.badge-moderate { background:#fef3c7; color:#b45309; }
.badge-low      { background:#dcfce7; color:#15803d; }

/* ── Progress bar ── */
.progress-wrap { margin: 14px 0 6px; }
.progress-label { display:flex; justify-content:space-between; font-size:0.72rem; color:#94a3b8; margin-bottom:5px; }
.progress-bar-bg { background:#e2e8f0; border-radius:8px; height:10px; overflow:hidden; }
.progress-bar-fill { height:100%; border-radius:8px; }

/* ── Result message ── */
.result-msg { font-size: 0.84rem; color: #374151; margin-top: 12px; line-height: 1.6; }

/* ── Step list ── */
.step-list { display:flex; flex-direction:column; gap:12px; margin-top:4px; }
.step-item { display:flex; align-items:flex-start; gap:12px; font-size:0.84rem; color:#374151; }
.step-num {
    min-width:26px; height:26px; background:#003087; color:#fff;
    border-radius:50%; display:flex; align-items:center; justify-content:center;
    font-size:0.75rem; font-weight:700; flex-shrink:0;
}

/* ── Feature list ── */
.feat-list { display:flex; flex-direction:column; gap:0; }
.feat-row {
    display:flex; align-items:center; gap:10px;
    padding:9px 0; border-bottom:1px solid #f1f5f9;
    font-size:0.83rem;
}
.feat-row:last-child { border-bottom:none; }
.feat-rank {
    min-width:22px; height:22px; background:#e8eef8; color:#003087;
    border-radius:50%; display:flex; align-items:center; justify-content:center;
    font-size:0.72rem; font-weight:700; flex-shrink:0;
}
.feat-name { flex:1; color:#1a2540; font-weight:600; }
.feat-tag {
    background:#eef2fb; color:#3a5080; border-radius:12px;
    padding:2px 10px; font-size:0.70rem; font-weight:600; white-space:nowrap;
}

/* ── Language radio as pills ── */
[data-testid="stRadio"] > div        { flex-direction: row !important; gap: 8px !important; }
[data-testid="stRadio"] > div > label {
    background: #eef2fb;
    border: 1.5px solid #c5d0e8;
    border-radius: 6px;
    padding: 4px 16px;
    font-size: 0.83rem;
    font-weight: 600;
    color: #3a5080 !important;
    cursor: pointer;
    transition: all 0.15s;
}
[data-testid="stRadio"] > div > label:has(input:checked) {
    background: #003087;
    border-color: #003087;
    color: #ffffff !important;
}
[data-testid="stRadio"] > div > label > div:first-child { display: none !important; }

/* ── Primary button ── */
.stButton > button {
    background: #003087 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    font-size: 0.93rem !important;
    padding: 11px 0 !important;
    box-shadow: 0 2px 8px rgba(0,48,135,0.22);
    transition: background 0.15s;
}
.stButton > button:hover { background: #0050b3 !important; }
</style>
""", unsafe_allow_html=True)

# ── Translations ────────────────────────────────────────────────────────────────
LANG = {
    'TR': {
        'title':         'Akut Böbrek Hasarı Mortalite Risk Hesaplayıcısı',
        'subtitle':      'DEU Hastanesi • Retrospektif AKI Kohortu • Yalnızca Araştırma Amaçlıdır',
        'notice_label':  'Uyarı:',
        'disclaimer':    'Bu araç yalnızca araştırma amaçlı olup klinik karar vermede kullanılmamalıdır. Tüm tahminler uzman klinisyen görüşü ile değerlendirilmelidir.',
        'patient_data':  'Hasta Parametreleri',
        'top5':          'En Önemli 5 Klinik Gösterge',
        'predict_btn':   'Mortalite Riskini Hesapla',
        'result_title':  'Tahmin Sonucu',
        'mortality_prob':'Mortalite Olasılığı',
        'survival_prob': 'Sağkalım Olasılığı',
        'risk_class':    'Risk Sınıfı',
        'high':          'YÜKSEK RİSK',
        'moderate':      'ORTA RİSK',
        'low':           'DÜŞÜK RİSK',
        'high_msg':      'Hasta yüksek AKI mortalite riski taşımaktadır. Acil klinik değerlendirme önerilmektedir.',
        'moderate_msg':  'Hasta orta düzeyde AKI mortalite riski taşımaktadır. Yakın klinik izlem önerilmektedir.',
        'low_msg':       'Hasta düşük AKI mortalite riski taşımaktadır. Rutin klinik izlem sürdürülmelidir.',
        'model_bilgi':   'Model Bilgisi',
        'algorithm':     'Algoritma',
        'dataset':       'Eğitim Verisi',
        'n_patients':    '2.230 hasta',
        'no_model':      'Model dosyaları bulunamadı. Lütfen önce eğitim pipeline\'ını çalıştırın.',
        'run_hint':      'python src/app.py komutunu çalıştırın.',
        'err':           'Tahmin hatası',
        'risk_label':    'Risk Skoru',
        'input_hint':    'Aşağıdaki klinik değerleri giriniz.',
        'how_title':     'Nasıl Kullanılır?',
        'step1':         'Sol paneldeki klinik laboratuvar değerlerini girin.',
        'step2':         '"Mortalite Riskini Hesapla" butonuna basın.',
        'step3':         'Tahmin sonucu ve risk sınıfı burada görünecektir.',
        'f1': 'Lökosit (WBC)',    'f1_tag': 'Enflamasyon',
        'f2': 'Kreatinin',        'f2_tag': 'Böbrek Fonksiyonu',
        'f3': 'Platelet',         'f3_tag': 'Koagülasyon',
        'f4': 'Total Bilirubin',  'f4_tag': 'Karaciğer Fonksiyonu',
        'f5': 'Yaş',              'f5_tag': 'Demografik Risk',
        'fields': {
            'kreatinin':     ('Kreatinin (mg/dL)',      0.1, 15.0, 0.1, 1.0),
            'wbc':           ('Lökosit (10³/µL)',       0.0, 50.0, 0.1, 10.0),
            'plt':           ('Platelet Sayısı (10³/µL)', 10, 500,  1,   200),
            'totalbilirubin':('Total Bilirubin (mg/dL)', 0.0, 20.0, 0.1, 0.8),
            'age':           ('Yaş',                    18,  120,  1,   65),
        },
    },
    'EN': {
        'title':         'Acute Kidney Injury Mortality Risk Calculator',
        'subtitle':      'DEU Hospital • Retrospective AKI Cohort • For Research Use Only',
        'notice_label':  'Notice:',
        'disclaimer':    'This tool is for research purposes only and must not be used for clinical decision-making. All predictions must be reviewed by a qualified clinician.',
        'patient_data':  'Patient Parameters',
        'top5':          'Top 5 Clinical Predictors',
        'predict_btn':   'Calculate Mortality Risk',
        'result_title':  'Prediction Result',
        'mortality_prob':'Mortality Probability',
        'survival_prob': 'Survival Probability',
        'risk_class':    'Risk Class',
        'high':          'HIGH RISK',
        'moderate':      'MODERATE RISK',
        'low':           'LOW RISK',
        'high_msg':      'Patient has a high estimated AKI mortality risk. Urgent clinical evaluation is recommended.',
        'moderate_msg':  'Patient has a moderate estimated AKI mortality risk. Close clinical monitoring is recommended.',
        'low_msg':       'Patient has a low estimated AKI mortality risk. Routine clinical follow-up should continue.',
        'model_bilgi':   'Model Information',
        'algorithm':     'Algorithm',
        'dataset':       'Training Data',
        'n_patients':    '2,230 patients',
        'no_model':      'Model files not found. Please run the training pipeline first.',
        'run_hint':      'Run python src/app.py from the project root.',
        'err':           'Prediction error',
        'risk_label':    'Risk Score',
        'input_hint':    'Enter the clinical laboratory values below.',
        'how_title':     'How to Use',
        'step1':         'Enter the clinical laboratory values in the left panel.',
        'step2':         'Click the "Calculate Mortality Risk" button.',
        'step3':         'The prediction result and risk class will appear here.',
        'f1': 'WBC (Leukocytes)',  'f1_tag': 'Inflammation',
        'f2': 'Creatinine',        'f2_tag': 'Renal Function',
        'f3': 'Platelet Count',    'f3_tag': 'Coagulation',
        'f4': 'Total Bilirubin',   'f4_tag': 'Hepatic Function',
        'f5': 'Age',               'f5_tag': 'Demographic Risk',
        'fields': {
            'kreatinin':     ('Creatinine (mg/dL)',      0.1, 15.0, 0.1, 1.0),
            'wbc':           ('WBC (10³/µL)',            0.0, 50.0, 0.1, 10.0),
            'plt':           ('Platelet Count (10³/µL)', 10,  500,  1,   200),
            'totalbilirubin':('Total Bilirubin (mg/dL)', 0.0, 20.0, 0.1, 0.8),
            'age':           ('Age (years)',              18,  120,  1,   65),
        },
    },
}

FEATURES = ['kreatinin', 'wbc', 'plt', 'totalbilirubin', 'age']

@st.cache_resource
def load_model_and_preprocessors():
    try:
        model_path = MODELS_DIR / "logistic_regression.pkl"
        if not model_path.exists():
            available = list(MODELS_DIR.glob("*.pkl"))
            if not available:
                return None, None
            model_path = available[0]
        model = joblib.load(model_path)
        if hasattr(model, '__class__') and model.__class__.__name__ == 'LogisticRegression':
            if not hasattr(model, 'multi_class'):
                model.multi_class = 'auto'
        scaler = None
        sp = MODELS_DIR / "scaler.pkl"
        if sp.exists():
            scaler = joblib.load(sp)
        return model, scaler
    except Exception as e:
        st.error(f"Model load error: {e}")
        return None, None

def progress_bar_html(prob, color):
    pct = prob * 100
    return f"""
    <div class="progress-wrap">
        <div class="progress-label"><span>0%</span><span>{pct:.1f}%</span><span>100%</span></div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width:{pct:.1f}%; background:{color};"></div>
        </div>
    </div>
    """

def main():
    model, scaler = load_model_and_preprocessors()

    # ── Top bar ──────────────────────────────────────────────────────────────
    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.markdown("""
        <div class="navbar">
            <span class="navbar-brand">DEU Hospital — Clinical Research Platform</span>
            <span class="navbar-tag">Research Use Only</span>
        </div>
        """, unsafe_allow_html=True)
    with top_r:
        lang = st.radio("", ["TR", "EN"], horizontal=True, label_visibility="collapsed")

    T = LANG[lang]

    # ── Hero ─────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero">
        <h1>{T['title']}</h1>
        <p>{T['subtitle']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Disclaimer ───────────────────────────────────────────────────────────
    st.markdown(f"<div class='disclaimer'><b>{T['notice_label']}</b> {T['disclaimer']}</div>",
                unsafe_allow_html=True)

    if model is None:
        st.error(T['no_model'])
        st.info(T['run_hint'])
        return

    # ── Two-column layout ────────────────────────────────────────────────────
    left, right = st.columns([1, 1], gap="large")

    # ── LEFT: Inputs ─────────────────────────────────────────────────────────
    with left:
        st.markdown(f"""
        <div class="section-card">
            <div class="card-header">{T['patient_data']} — {T['top5']}</div>
            <p style="font-size:0.82rem; color:#64748b; margin:-8px 0 18px;">{T['input_hint']}</p>
        </div>
        """, unsafe_allow_html=True)

        input_data = {}
        c1, c2 = st.columns(2)
        cols_map = [c1, c2, c1, c2, c1]
        for feat, col in zip(FEATURES, cols_map):
            lbl, mn, mx, step, default = T['fields'][feat]
            with col:
                input_data[feat] = st.number_input(
                    lbl,
                    min_value=float(mn), max_value=float(mx),
                    value=float(default), step=float(step)
                )

        st.markdown("<br>", unsafe_allow_html=True)
        predict = st.button(T['predict_btn'], type="primary", use_container_width=True)

    # ── RIGHT: Placeholder → Result ───────────────────────────────────────────
    with right:
        if not predict:
            st.markdown(f"""
            <div class="section-card">
                <div class="card-header">{T['how_title']}</div>
                <div class="step-list">
                    <div class="step-item"><span class="step-num">1</span><span>{T['step1']}</span></div>
                    <div class="step-item"><span class="step-num">2</span><span>{T['step2']}</span></div>
                    <div class="step-item"><span class="step-num">3</span><span>{T['step3']}</span></div>
                </div>
            </div>
            <div class="section-card" style="margin-top:0;">
                <div class="card-header">{T['top5']}</div>
                <div class="feat-list">
                    <div class="feat-row"><span class="feat-rank">1</span><span class="feat-name">{T['f1']}</span><span class="feat-tag">{T['f1_tag']}</span></div>
                    <div class="feat-row"><span class="feat-rank">2</span><span class="feat-name">{T['f2']}</span><span class="feat-tag">{T['f2_tag']}</span></div>
                    <div class="feat-row"><span class="feat-rank">3</span><span class="feat-name">{T['f3']}</span><span class="feat-tag">{T['f3_tag']}</span></div>
                    <div class="feat-row"><span class="feat-rank">4</span><span class="feat-name">{T['f4']}</span><span class="feat-tag">{T['f4_tag']}</span></div>
                    <div class="feat-row"><span class="feat-rank">5</span><span class="feat-name">{T['f5']}</span><span class="feat-tag">{T['f5_tag']}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            try:
                input_df = pd.DataFrame([input_data])

                if scaler is not None and hasattr(scaler, 'feature_names_in_'):
                    exp = list(scaler.feature_names_in_)
                    fills = dict(zip(exp, scaler.mean_))
                    input_df = input_df.reindex(columns=exp)
                    for c in exp:
                        if c not in input_data:
                            input_df[c] = fills[c]
                    try:
                        X_input = pd.DataFrame(scaler.transform(input_df), columns=exp)
                    except Exception:
                        X_input = input_df
                else:
                    X_input = input_df

                mp = model.predict_proba(X_input)[0][1]

                if mp >= 0.7:
                    risk_key  = 'high'
                    bar_color = '#ef4444'
                    badge_cls = 'badge-high'
                    card_bg   = '#fff1f2'
                    border_c  = '#fca5a5'
                elif mp >= 0.4:
                    risk_key  = 'moderate'
                    bar_color = '#f59e0b'
                    badge_cls = 'badge-moderate'
                    card_bg   = '#fffbeb'
                    border_c  = '#fcd34d'
                else:
                    risk_key  = 'low'
                    bar_color = '#22c55e'
                    badge_cls = 'badge-low'
                    card_bg   = '#f0fdf4'
                    border_c  = '#86efac'

                pct = mp * 100
                result_html = (
                    f'<div class="section-card" style="background:{card_bg}; border-color:{border_c};">'
                    f'<div class="card-header" style="border-color:{border_c};">{T["result_title"]}</div>'
                    f'<div class="metric-row">'
                    f'<div class="metric-card"><div class="m-label">{T["mortality_prob"]}</div>'
                    f'<div class="m-value" style="color:{bar_color};">{pct:.1f}%</div></div>'
                    f'<div class="metric-card"><div class="m-label">{T["survival_prob"]}</div>'
                    f'<div class="m-value" style="color:#22c55e;">{100-pct:.1f}%</div></div>'
                    f'</div>'
                    f'<div style="text-align:center;"><span class="risk-badge {badge_cls}">{T[risk_key]}</span></div>'
                    f'<div class="progress-wrap">'
                    f'<div class="progress-label"><span>0%</span><span>{pct:.1f}%</span><span>100%</span></div>'
                    f'<div class="progress-bar-bg">'
                    f'<div class="progress-bar-fill" style="width:{pct:.1f}%; background:{bar_color};"></div>'
                    f'</div></div>'
                    f'<p style="font-size:0.85rem; color:#374151; margin-top:14px; line-height:1.6;">'
                    f'{T[risk_key + "_msg"]}</p>'
                    f'</div>'
                )
                st.markdown(result_html, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"{T['err']}: {e}")

if __name__ == "__main__":
    main()
