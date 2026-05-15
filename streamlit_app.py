"""AKI Mortality Risk Calculator — v6 medical teal design system"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import math
from pathlib import Path
import sys, io

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent / 'src'))
from config import MODELS_DIR

st.set_page_config(
    page_title="AKI Risk Calculator",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Google Fonts ─────────────────────────────────────────────────────────────
st.markdown(
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700;800&family=Noto+Sans:wght@300;400;500;700&display=swap" rel="stylesheet">'
    '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">',
    unsafe_allow_html=True
)

# ── Base CSS — light (blue/white) default, dark navy override ────────────────
st.markdown("""
<style>
/* hide streamlit chrome */
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stSidebar"]{display:none!important}

/* ── tokens ── */
:root{
  --bg:      #f0fdfa;
  --surface: #ffffff;
  --surf2:   #f0fdfa;
  --border:  #99f6e4;
  --bd-focus:#67e8f9;
  --primary: #0891b2;
  --p-hover: #0e7490;
  --p-dim:   rgba(8,145,178,0.10);
  --p-glow:  rgba(8,145,178,0.20);
  --text:    #134e4a;
  --sub:     #0f766e;
  --muted:   #5eead4;
  --success: #22c55e;
  --warn:    #d97706;
  --danger:  #dc2626;
  --r:       12px;
  --rs:      8px;
  --shadow:  0 1px 3px rgba(8,145,178,0.07),0 4px 16px rgba(8,145,178,0.05);
  --shadow-md:0 4px 12px rgba(8,145,178,0.10),0 12px 32px rgba(8,145,178,0.08);
  --ff: 'Noto Sans',sans-serif;
  --ff-head: 'Figtree',sans-serif;
}

/* ── Page shell ── */
[data-testid="stAppViewContainer"]{background:var(--bg)!important}
[data-testid="block-container"]{padding-top:0!important;padding-bottom:2rem!important;max-width:1100px!important}
body,[data-testid="stAppViewContainer"]{font-family:var(--ff)}

/* ── Nav bar ── */
.nav-bar{
  background:var(--surface);
  border-bottom:1px solid var(--border);
  padding:0 28px;
  display:flex;align-items:center;justify-content:space-between;
  position:sticky;top:0;z-index:100;
  box-shadow:0 1px 4px rgba(0,0,0,0.06);
}
.nav-brand{display:flex;align-items:center;gap:10px;padding:14px 0}
.nav-logo{
  width:36px;height:36px;
  background:linear-gradient(135deg,#0e7490,#0891b2);
  border-radius:9px;
  display:flex;align-items:center;justify-content:center;
  font-size:0.58rem;font-weight:800;letter-spacing:0.6px;color:#fff;font-family:var(--ff);
}
.nav-title{font-size:0.97rem;font-weight:700;color:var(--text);font-family:var(--ff-head)}
.nav-sub{font-size:0.67rem;color:var(--muted);letter-spacing:0.2px}

/* ── Cards ── */
.card{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:var(--r);
  padding:24px;
  margin-bottom:16px;
  box-shadow:var(--shadow);
  transition:box-shadow .18s;
}
.card:hover{box-shadow:var(--shadow-md)}
.card-title{
  font-size:0.82rem;font-weight:700;
  text-transform:uppercase;letter-spacing:1.8px;
  color:var(--primary);margin:0 0 18px;
  font-family:var(--ff);
  display:flex;align-items:center;gap:8px;
}
.card-title::after{content:'';flex:1;height:1px;background:var(--border)}

/* ── Landing hero ── */
.hero{
  background:linear-gradient(135deg,#134e4a 0%,#0891b2 55%,#22d3ee 100%);
  border-radius:var(--r);
  padding:52px 44px 44px;
  color:#fff;
  position:relative;overflow:hidden;
  margin-bottom:24px;
}
.hero::before{
  content:'';position:absolute;
  top:-60px;right:-60px;
  width:280px;height:280px;
  background:radial-gradient(circle,rgba(255,255,255,0.12) 0%,transparent 70%);
  pointer-events:none;
}
.hero::after{
  content:'';position:absolute;
  bottom:-80px;left:40%;
  width:240px;height:240px;
  background:radial-gradient(circle,rgba(255,255,255,0.06) 0%,transparent 70%);
  pointer-events:none;
}
.hero-badge{
  display:inline-flex;align-items:center;gap:6px;
  background:rgba(255,255,255,0.15);
  border:1px solid rgba(255,255,255,0.25);
  border-radius:20px;padding:4px 14px;
  font-size:0.68rem;font-weight:600;letter-spacing:0.8px;
  margin-bottom:20px;color:rgba(255,255,255,0.9);
}
.hero-title{
  font-family:var(--ff-head);
  font-size:2.4rem;font-weight:800;line-height:1.15;
  margin:0 0 14px;color:#fff;
}
.hero-sub{
  font-size:1.0rem;color:rgba(255,255,255,0.80);
  line-height:1.7;max-width:580px;margin-bottom:32px;
}
.hero-cta{display:flex;gap:12px;flex-wrap:wrap;position:relative;z-index:1}
.btn-white{
  background:#fff;color:#0e7490;
  border:none;border-radius:var(--rs);
  padding:12px 28px;font-size:0.88rem;font-weight:700;
  cursor:pointer;transition:all .18s;font-family:var(--ff);
  box-shadow:0 2px 12px rgba(0,0,0,0.15);
}
.btn-white:hover{transform:translateY(-1px);box-shadow:0 6px 20px rgba(0,0,0,0.2)}
.btn-outline{
  background:rgba(255,255,255,0.12);color:#fff;
  border:1px solid rgba(255,255,255,0.35);border-radius:var(--rs);
  padding:12px 28px;font-size:0.88rem;font-weight:600;
  cursor:pointer;transition:all .18s;font-family:var(--ff);
}
.btn-outline:hover{background:rgba(255,255,255,0.22)}

/* ── Stats row ── */
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px}
.stat-card{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--r);padding:20px 16px;text-align:center;
  box-shadow:var(--shadow);
  transition:border-color .18s,transform .18s;
}
.stat-card:hover{border-color:var(--bd-focus);transform:translateY(-2px)}
.stat-val{font-size:2rem;font-weight:800;color:var(--primary);line-height:1;margin-bottom:6px;font-family:var(--ff-head)}
.stat-lbl{font-size:0.67rem;font-weight:600;color:var(--sub);text-transform:uppercase;letter-spacing:1.2px}

/* ── Feature cards ── */
.feature-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:24px}
.feature-card{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--r);padding:22px 18px;
  box-shadow:var(--shadow);
  transition:border-color .18s,box-shadow .18s;
}
.feature-card:hover{border-color:var(--bd-focus);box-shadow:var(--shadow-md)}
.feature-icon{
  width:44px;height:44px;border-radius:10px;
  background:var(--p-dim);
  display:flex;align-items:center;justify-content:center;
  margin-bottom:14px;font-size:1.25rem;
}
.feature-title{font-size:0.93rem;font-weight:700;color:var(--text);margin-bottom:6px}
.feature-desc{font-size:0.80rem;color:var(--sub);line-height:1.65}

/* ── How-it-works steps ── */
.steps-row{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:24px}
.step-card{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--r);padding:22px 18px;
  box-shadow:var(--shadow);text-align:center;
}
.step-num{
  width:40px;height:40px;
  background:linear-gradient(135deg,#0e7490,#0891b2);
  border-radius:50%;color:#fff;
  display:flex;align-items:center;justify-content:center;
  font-size:1rem;font-weight:800;
  margin:0 auto 14px;
  box-shadow:0 4px 12px rgba(8,145,178,0.35);
}
.step-title{font-size:0.90rem;font-weight:700;color:var(--text);margin-bottom:6px}
.step-desc{font-size:0.78rem;color:var(--sub);line-height:1.6}

/* ── Page section header ── */
.section-header{
  display:flex;align-items:center;justify-content:space-between;
  margin-bottom:20px;padding-bottom:14px;
  border-bottom:2px solid var(--border);
}
.section-title{font-family:var(--ff-head);font-size:1.35rem;font-weight:800;color:var(--text);margin:0}
.section-sub{font-size:0.80rem;color:var(--sub);margin:4px 0 0}

/* ── Input card ── */
.input-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:24px;box-shadow:var(--shadow)}
.input-label{font-size:0.72rem;font-weight:600;color:var(--sub);text-transform:uppercase;letter-spacing:1px;margin-bottom:18px;display:block}

/* ── Number inputs ── */
[data-testid="stNumberInput"]>div>div>input{
  background:var(--surf2)!important;
  border:1.5px solid var(--border)!important;
  border-radius:var(--rs)!important;
  color:var(--text)!important;
  font-family:var(--ff)!important;
  font-size:0.92rem!important;
  padding:10px 12px!important;
  transition:border-color .15s,box-shadow .15s!important;
}
[data-testid="stNumberInput"]>div>div>input:focus{
  border-color:var(--primary)!important;
  box-shadow:0 0 0 3px var(--p-dim)!important;
}
[data-testid="stNumberInput"] label{
  color:var(--sub)!important;font-size:0.82rem!important;font-weight:500!important;
}
[data-baseweb="base-input"],[data-baseweb="input"]{background:var(--surf2)!important}

/* ── Number input stepper buttons ── */
[data-testid="stNumberInput"] button{
  background:var(--surf2)!important;
  border:1px solid var(--border)!important;
  color:var(--text)!important;
  border-radius:var(--rs)!important;
}
[data-testid="stNumberInput"] button:hover{background:var(--border)!important}
[data-testid="stNumberInput"] button svg{fill:var(--text)!important;stroke:var(--text)!important}

/* ── Primary button ── */
.stButton>button{
  background:linear-gradient(135deg,#0e7490,#0891b2)!important;
  color:#fff!important;border:none!important;
  border-radius:var(--rs)!important;
  font-family:var(--ff)!important;font-weight:600!important;
  font-size:0.90rem!important;letter-spacing:0.3px!important;
  padding:12px 0!important;
  box-shadow:0 4px 14px rgba(8,145,178,0.35)!important;
  transition:all .18s!important;
  min-height:44px!important;
  cursor:pointer!important;
}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 8px 20px rgba(8,145,178,0.45)!important}
.stButton>button:focus{outline:3px solid var(--bd-focus)!important;outline-offset:2px!important}

/* ── Risk result card ── */
.result-card{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--r);padding:28px 24px;
  box-shadow:var(--shadow);
}
.result-card-high     {border-top:4px solid #dc2626}
.result-card-moderate {border-top:4px solid #d97706}
.result-card-low      {border-top:4px solid #059669}

/* ── Risk badge ── */
.risk-badge{
  display:inline-flex;align-items:center;gap:8px;
  padding:8px 20px;border-radius:20px;
  font-size:0.80rem;font-weight:700;letter-spacing:0.8px;
}
.badge-high    {background:#fef2f2;color:#dc2626;border:1.5px solid #fecaca}
.badge-moderate{background:#fffbeb;color:#d97706;border:1.5px solid #fde68a}
.badge-low     {background:#f0fdf4;color:#059669;border:1.5px solid #bbf7d0}

/* ── Metric boxes ── */
.metric-pair{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:20px 0}
.metric-box{
  background:var(--surf2);border:1px solid var(--border);
  border-radius:var(--rs);padding:16px 12px;text-align:center;
}
.metric-label{font-size:0.65rem;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:1.2px;margin-bottom:6px}
.metric-value{font-size:2rem;font-weight:800;line-height:1;font-family:var(--ff-head)}

/* ── Progress bar ── */
.prog-wrap{margin:14px 0 6px}
.prog-labels{display:flex;justify-content:space-between;font-size:0.65rem;color:var(--muted);margin-bottom:6px}
.prog-track{height:6px;background:var(--border);border-radius:3px;overflow:hidden}
.prog-fill{height:100%;border-radius:3px;transition:width 1.2s cubic-bezier(.4,0,.2,1)}

/* ── Disclaimer ── */
.disclaimer{
  background:#fffbeb;border:1px solid #fde68a;border-radius:var(--rs);
  padding:12px 16px;font-size:0.78rem;color:#92400e;line-height:1.6;margin-top:12px;
}

/* ── How-to steps ── */
.how-step{display:flex;align-items:flex-start;gap:14px;padding:12px 0;border-bottom:1px solid var(--border)}
.how-step:last-child{border-bottom:none}
.how-num{
  min-width:28px;height:28px;
  background:var(--p-dim);color:var(--primary);
  border:1.5px solid var(--bd-focus);
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:0.72rem;font-weight:700;flex-shrink:0;margin-top:1px;
}
.how-txt{font-size:0.84rem;color:var(--text);line-height:1.6}

/* ── Top 5 feature list ── */
.feat-row{display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--border);transition:background .12s}
.feat-row:last-child{border-bottom:none}
.feat-row:hover{background:var(--p-dim);border-radius:var(--rs);padding-left:8px}
.feat-rank{
  min-width:26px;height:26px;
  background:var(--p-dim);color:var(--primary);
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:0.68rem;font-weight:700;flex-shrink:0;
}
.feat-name{font-size:0.84rem;font-weight:600;color:var(--text);flex:1}
.feat-cat{font-size:0.70rem;color:var(--muted);white-space:nowrap;
  background:var(--surf2);border:1px solid var(--border);
  border-radius:4px;padding:2px 8px;
}

/* ── About stat strip ── */
.about-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}
.about-stat{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--r);padding:18px 12px;text-align:center;
  box-shadow:var(--shadow);
}
.about-stat-val{font-size:1.8rem;font-weight:800;color:var(--primary);line-height:1;margin-bottom:6px;font-family:var(--ff-head)}
.about-stat-lbl{font-size:0.64rem;font-weight:600;color:var(--sub);text-transform:uppercase;letter-spacing:1px}

/* ── Model cards ── */
.model-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.model-card{
  background:var(--surf2);border:1.5px solid var(--border);
  border-radius:var(--rs);padding:18px;
  transition:border-color .18s,transform .18s;
}
.model-card:hover{border-color:var(--bd-focus);transform:translateY(-2px)}
.model-name{font-size:0.90rem;font-weight:700;color:var(--text);margin-bottom:4px}
.model-desc{font-size:0.74rem;color:var(--sub);line-height:1.55;margin-bottom:12px}
.model-auc-lbl{font-size:0.60rem;font-weight:700;color:var(--primary);text-transform:uppercase;letter-spacing:1px;margin-bottom:3px}
.model-auc-val{font-size:1.2rem;font-weight:800;color:var(--primary);margin-bottom:6px;font-family:var(--ff-head)}
.auc-track{height:5px;background:var(--border);border-radius:3px;overflow:hidden}
.auc-fill{height:100%;border-radius:3px;background:linear-gradient(90deg,#0e7490,#22d3ee)}

/* ── AKI info cards ── */
.aki-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.aki-card{
  background:var(--surf2);border:1.5px solid var(--border);
  border-radius:var(--rs);padding:20px;
  transition:border-color .18s;
}
.aki-card:hover{border-color:var(--bd-focus)}
.aki-title{font-size:0.90rem;font-weight:700;color:var(--text);margin-bottom:8px}
.aki-text{font-size:0.79rem;color:var(--sub);line-height:1.7}

/* ── Feature bars ── */
.fb-row{display:flex;align-items:center;gap:12px;padding:9px 0;border-bottom:1px solid var(--border);transition:background .12s;border-radius:4px}
.fb-row:last-child{border-bottom:none}
.fb-row:hover{background:var(--p-dim);padding-left:6px}
.fb-rank{min-width:24px;height:24px;background:var(--p-dim);color:var(--primary);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.67rem;font-weight:700;flex-shrink:0}
.fb-info{min-width:140px}
.fb-name{font-size:0.82rem;font-weight:600;color:var(--text)}
.fb-cat{font-size:0.67rem;color:var(--muted)}
.fb-track{flex:1;height:5px;background:var(--border);border-radius:3px;overflow:hidden}
.fb-fill{height:100%;border-radius:3px;background:linear-gradient(90deg,#0e7490,#22d3ee)}
.fb-pct{font-size:0.72rem;font-weight:700;color:var(--primary);min-width:32px;text-align:right}

/* ── Project landing ── */
.proj-hero{
  background:linear-gradient(135deg,rgba(8,145,178,0.07) 0%,rgba(34,211,238,0.04) 60%,transparent 100%);
  border:1px solid #67e8f9;border-radius:var(--r);
  padding:36px 32px 28px;margin-bottom:20px;
  position:relative;overflow:hidden;
}
.proj-hero::before{content:'';position:absolute;top:-70px;right:-70px;width:260px;height:260px;background:radial-gradient(circle,rgba(8,145,178,0.08) 0%,transparent 70%);pointer-events:none}
.proj-hero-badge{display:inline-flex;background:var(--p-dim);border:1px solid var(--bd-focus);border-radius:20px;padding:4px 14px;font-size:0.65rem;font-weight:700;color:var(--primary);letter-spacing:1px;margin-bottom:14px;text-transform:uppercase;font-family:var(--ff-head)}
.proj-hero-title{font-family:var(--ff-head);font-size:1.9rem;font-weight:800;color:var(--text);margin:0 0 10px;line-height:1.2}
.proj-hero-sub{font-size:0.88rem;color:var(--sub);line-height:1.75;margin-bottom:24px;max-width:680px}
.proj-hero-stats{display:flex;gap:12px;flex-wrap:wrap}
.proj-stat{background:var(--surface);border:1px solid var(--border);border-radius:var(--rs);padding:14px 18px;min-width:100px;transition:border-color .18s,transform .18s;box-shadow:var(--shadow)}
.proj-stat:hover{border-color:var(--bd-focus);transform:translateY(-2px)}
.proj-stat-val{font-family:var(--ff-head);font-size:1.5rem;font-weight:800;color:var(--primary);line-height:1;margin-bottom:4px}
.proj-stat-lbl{font-size:0.62rem;font-weight:600;color:var(--sub);text-transform:uppercase;letter-spacing:.7px}

.proj-ds-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px}
.proj-ds-box{background:var(--surf2);border:1px solid var(--border);border-radius:var(--rs);padding:14px 10px;text-align:center}
.proj-ds-val{font-family:var(--ff-head);font-size:1.4rem;font-weight:800;color:var(--primary);line-height:1;margin-bottom:4px}
.proj-ds-lbl{font-size:0.62rem;font-weight:600;color:var(--sub);text-transform:uppercase;letter-spacing:.6px}

.proj-chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}
.proj-chip{padding:4px 10px;border-radius:20px;font-size:0.71rem;font-weight:600}
.proj-chip-blue {background:#ecfeff;color:#0e7490;border:1px solid #67e8f9}
.proj-chip-green{background:#f0fdf4;color:#059669;border:1px solid #bbf7d0}
.proj-chip-red  {background:#fef2f2;color:#dc2626;border:1px solid #fecaca}

.proj-pipeline{display:flex;flex-direction:column}
.proj-pipe-step{display:flex;align-items:flex-start;gap:12px;position:relative;padding-bottom:18px}
.proj-pipe-step::after{content:'';position:absolute;left:13px;top:28px;width:2px;height:calc(100% - 12px);background:var(--border)}
.proj-pipe-step:last-child::after{display:none}
.proj-pipe-step:last-child{padding-bottom:0}
.proj-pipe-num{width:28px;height:28px;background:var(--p-dim);color:var(--primary);border:1.5px solid var(--bd-focus);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.67rem;font-weight:700;flex-shrink:0;z-index:1}
.proj-pipe-txt{font-size:0.82rem;color:var(--text);line-height:1.55;padding-top:4px;font-weight:600}
.proj-pipe-detail{font-size:0.70rem;color:var(--muted);margin-top:2px}

.proj-model-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.proj-model-card{background:var(--surf2);border:1.5px solid var(--border);border-radius:var(--rs);padding:18px;position:relative;overflow:hidden;transition:border-color .18s,transform .18s}
.proj-model-card:hover{transform:translateY(-2px);border-color:var(--bd-focus)}
.proj-model-best{border-color:#67e8f9!important;background:#ecfeff!important}
.proj-best-badge{display:inline-flex;background:var(--p-dim);border:1px solid var(--bd-focus);color:var(--primary);border-radius:20px;padding:2px 10px;font-size:0.61rem;font-weight:700;letter-spacing:.6px;margin-bottom:8px;text-transform:uppercase}
.proj-model-name{font-family:var(--ff-head);font-size:0.93rem;font-weight:800;margin-bottom:4px}
.proj-model-desc{font-size:0.74rem;color:var(--sub);line-height:1.55;margin-bottom:6px}
.proj-model-params{font-size:0.65rem;color:var(--muted);margin-bottom:12px;font-family:monospace;letter-spacing:.1px}
.proj-metrics-mini{display:flex;gap:14px}
.proj-mini-lbl{font-size:0.58rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;margin-bottom:2px}
.proj-mini-val{font-size:1.0rem;font-weight:800;color:var(--text);font-family:var(--ff-head)}

.proj-table{width:100%;border-collapse:collapse;font-size:0.82rem}
.proj-table th{font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--muted);padding:8px 12px;border-bottom:2px solid var(--border);text-align:left}
.proj-table td{padding:11px 12px;border-bottom:1px solid var(--border);color:var(--text)}
.proj-table tr:last-child td{border-bottom:none}
.proj-tr-best td{background:#ecfeff}
.proj-td-name{font-weight:700!important}
.proj-td-auc{font-weight:800!important;font-size:0.9rem!important}
.proj-best-chip{background:var(--p-dim);border:1px solid var(--bd-focus);color:var(--primary);border-radius:20px;padding:2px 9px;font-size:0.61rem;font-weight:700;letter-spacing:.4px}

.proj-fi-row{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--border);transition:background .12s;border-radius:4px}
.proj-fi-row:last-child{border-bottom:none}
.proj-fi-row:hover{background:var(--p-dim);padding-left:6px}
.proj-fi-rank{min-width:24px;height:24px;background:var(--p-dim);color:var(--primary);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.63rem;font-weight:700;flex-shrink:0}
.proj-fi-name{min-width:150px;font-size:0.81rem;font-weight:600;color:var(--text)}
.proj-fi-track{flex:1;height:5px;background:var(--border);border-radius:3px;overflow:hidden}
.proj-fi-fill{height:100%;border-radius:3px}
.proj-fi-pct{min-width:38px;text-align:right;font-size:0.72rem;font-weight:700}

.proj-finding{display:flex;align-items:flex-start;gap:14px;padding:13px 0;border-bottom:1px solid var(--border)}
.proj-finding:last-child{border-bottom:none}
.proj-finding-num{font-size:1.3rem;font-weight:800;color:var(--primary);opacity:0.3;flex-shrink:0;line-height:1.3;min-width:28px;font-family:var(--ff-head)}
.proj-finding-txt{font-size:0.82rem;color:var(--text);line-height:1.7}

.proj-stack-grid{display:flex;flex-wrap:wrap;gap:8px}
.proj-stack-chip{
  background:var(--surf2);border:1px solid var(--border);
  border-radius:var(--rs);padding:7px 14px;
  font-size:0.74rem;font-weight:500;color:var(--sub);
  transition:all .15s;cursor:default;
}
.proj-stack-chip:hover{border-color:var(--bd-focus);color:var(--primary);background:#ecfeff}

/* ── Radio pills ── */
[data-testid="stRadio"]>div{flex-direction:row!important;gap:4px!important}
[data-testid="stRadio"]>div>label{
  background:var(--surf2);border:1.5px solid var(--border);
  border-radius:20px;padding:5px 16px;
  font-size:0.78rem;font-weight:600;color:var(--sub)!important;
  cursor:pointer;transition:all .15s;letter-spacing:.3px;
}
[data-testid="stRadio"]>div>label:has(input:checked){
  background:var(--p-dim);border-color:var(--bd-focus);color:var(--primary)!important;
  font-family:var(--ff-head)!important;
}
[data-testid="stRadio"]>div>label>div:first-child{display:none!important}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:rgba(8,145,178,0.22);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:rgba(8,145,178,0.40)}

/* ── Animations ── */
@keyframes cardIn{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.anim-in{animation:cardIn .38s ease both}
.anim-in-2{animation:cardIn .38s .08s ease both}
.anim-in-3{animation:cardIn .38s .16s ease both}

/* ── Caption ── */
[data-testid="stCaption"]{color:var(--muted)!important;font-size:0.73rem!important}

/* ── Reduced motion (WCAG) ── */
@media (prefers-reduced-motion: reduce){
  .anim-in,.anim-in-2,.anim-in-3{animation:none!important}
  .card,.stat-card,.feature-card,.step-card,.model-card,.aki-card,
  .proj-model-card,.proj-stat{transition:none!important}
  .stButton>button{transition:none!important}
}

/* ══ DARK MODE ══════════════════════════════════════════════════════ */
.dark-mode{
  --bg:      #042f2e;
  --surface: #0d3b38;
  --surf2:   #134e4a;
  --border:  rgba(20,184,166,0.18);
  --bd-focus:rgba(34,211,238,0.5);
  --primary: #22d3ee;
  --p-hover: #67e8f9;
  --p-dim:   rgba(34,211,238,0.12);
  --p-glow:  rgba(34,211,238,0.25);
  --text:    #f0fdfa;
  --sub:     #99f6e4;
  --muted:   rgba(240,253,250,0.35);
  --success: #4ade80;
  --warn:    #fbbf24;
  --danger:  #f87171;
  --shadow:  0 1px 3px rgba(0,0,0,0.40),0 4px 16px rgba(0,0,0,0.32);
  --shadow-md:0 4px 12px rgba(0,0,0,0.45),0 12px 32px rgba(0,0,0,0.35);
}

/* ══ MOBILE RESPONSIVE ══════════════════════════════════════════ */
@media (max-width:768px){

  /* ── Page shell ── */
  [data-testid="block-container"]{
    padding-left:.75rem!important;
    padding-right:.75rem!important;
    padding-top:.25rem!important;
  }

  /* ── Stack ALL Streamlit columns ── */
  [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:6px 0!important}
  [data-testid="stColumn"]{
    min-width:100%!important;
    flex:1 1 100%!important;
    max-width:100%!important;
    width:100%!important;
  }

  /* ── Nav: show brand full-width, buttons as 2×2 grid ── */
  .mob-nav-brand{display:block!important}

  /* ── Hero ── */
  .hero{padding:26px 18px 22px!important;border-radius:10px!important}
  .hero-badge{font-size:.62rem!important}
  .hero-title{font-size:1.55rem!important;line-height:1.2!important}
  .hero-sub{font-size:.83rem!important;margin-bottom:18px!important}

  /* ── Stats strip: 2×2 ── */
  .stats-row{grid-template-columns:1fr 1fr!important;gap:10px!important}
  .stat-val{font-size:1.7rem!important}

  /* ── Feature grid: single col ── */
  .feature-grid{grid-template-columns:1fr!important;gap:10px!important}

  /* ── How-it-works: single col ── */
  .steps-row{grid-template-columns:1fr!important;gap:10px!important}

  /* ── Section header ── */
  .section-title{font-size:1.15rem!important}

  /* ── About stats: 2×2 ── */
  .about-stats{grid-template-columns:1fr 1fr!important;gap:10px!important}
  .about-stat-val{font-size:1.6rem!important}

  /* ── Model & AKI grids: single col ── */
  .model-grid,.aki-grid,.proj-model-grid{grid-template-columns:1fr!important}

  /* ── Cards ── */
  .card,.result-card,.input-card{padding:16px!important}

  /* ── Metric pair ── */
  .metric-pair{gap:8px!important}
  .metric-value{font-size:1.7rem!important}

  /* ── Feature bar names ── */
  .fb-info{min-width:100px!important}
  .proj-fi-name{min-width:100px!important}

  /* ── Project hero ── */
  .proj-hero{padding:22px 16px 18px!important}
  .proj-hero-title{font-size:1.35rem!important}
  .proj-hero-stats{flex-wrap:wrap!important;gap:8px!important}
  .proj-stat{min-width:calc(50% - 4px)!important;padding:10px 12px!important}
  .proj-stat-val{font-size:1.25rem!important}

  /* ── Dataset grid: 2×2 ── */
  .proj-ds-grid{grid-template-columns:1fr 1fr!important}

  /* ── Metrics table: compact ── */
  .proj-table{font-size:.70rem!important}
  .proj-table th,.proj-table td{padding:7px 8px!important}
  .proj-td-name{font-size:.72rem!important}

  /* ── Pipeline ── */
  .proj-pipe-txt{font-size:.79rem!important}
  .proj-pipe-detail{font-size:.67rem!important}

  /* ── Stack grid ── */
  .proj-stack-grid{gap:6px!important}
  .proj-stack-chip{padding:5px 10px!important;font-size:.70rem!important}

  /* ── Radio pills ── */
  [data-testid="stRadio"]>div>label{padding:5px 10px!important;font-size:.72rem!important}

  /* ── Gauge ── */
  .gauge-wrap svg{width:190px!important;height:114px!important}

  /* ── Button min height for tap targets ── */
  .stButton>button{min-height:44px!important;font-size:.80rem!important}

  /* ── Number inputs ── */
  [data-testid="stNumberInput"]>div>div>input{font-size:1rem!important;padding:12px!important}
  [data-testid="stNumberInput"] button{min-width:44px!important;min-height:44px!important}

  /* ── Ensure result card gauge centres ── */
  .result-card{text-align:center}
  .result-card .metric-pair{text-align:left}
}

@media (max-width:480px){
  .hero-title{font-size:1.35rem!important}
  .stats-row{grid-template-columns:1fr 1fr!important}
  .proj-metrics-mini{flex-wrap:wrap!important;gap:8px!important}
  .proj-mini-val{font-size:.88rem!important}
  .proj-table th:nth-child(5),.proj-table td:nth-child(5),
  .proj-table th:nth-child(6),.proj-table td:nth-child(6){display:none!important}
}

/* ── Key factors (result card) ── */
.key-factors{
  background:var(--surf2);border:1px solid var(--border);
  border-radius:var(--rs);padding:14px 16px;margin-top:14px;
}
.kf-label{
  font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:1.4px;
  color:var(--sub);margin-bottom:10px;
}
.kf-row{
  display:flex;justify-content:space-between;align-items:center;
  padding:6px 0;border-bottom:1px solid var(--border);
}
.kf-row:last-child{border-bottom:none}
.kf-name{font-size:0.82rem;color:var(--text);font-weight:500}
.kf-val{font-size:0.82rem;font-weight:700;color:var(--primary);font-family:monospace}

/* ── Mobile disclaimer collapse ── */
.disclaimer-wrap details summary{
  cursor:pointer;font-weight:600;list-style:none;display:flex;align-items:center;gap:6px;
  font-size:0.78rem;color:#92400e;
}
.disclaimer-wrap details summary::marker{display:none}
.disclaimer-wrap details summary::-webkit-details-marker{display:none}
.disclaimer-wrap details .disc-body{font-size:0.78rem;color:#92400e;line-height:1.6;margin-top:6px}
@media (min-width:769px){
  .disclaimer-wrap details summary{pointer-events:none;color:#92400e}
}
</style>
""", unsafe_allow_html=True)

# ── Translations ─────────────────────────────────────────────────────────────
LANG = {
    'TR': {
        'nav_home': 'Ana Sayfa', 'nav_calc': 'Hesaplayıcı',
        'nav_about': 'Hakkında', 'nav_project': 'Proje',
        'theme_dark': 'Karanlık', 'theme_light': 'Aydınlık',
        'hero_badge': 'DEU Hastanesi · YBÜ Kohortu · Araştırma Amaçlı',
        'hero_title': 'AKI Mortalite Risk Hesaplayıcısı',
        'hero_sub': 'Yoğun bakım ünitesindeki AKI hastalarında mortalite riskini tahmin etmek için dört makine öğrenmesi modelini bir arada kullanan klinik araştırma aracı.',
        'hero_cta1': 'Riski Hesapla',
        'hero_cta2': 'Araştırmayı İncele',
        's1_val': '2.230', 's1_lbl': 'YBÜ Hastası',
        's2_val': '4', 's2_lbl': 'ML Modeli',
        's3_val': '91%', 's3_lbl': 'En İyi AUC',
        's4_val': '15', 's4_lbl': 'Klinik Gösterge',
        'feat1_title': 'Çoklu Model Ensemble',
        'feat1_desc': 'Dört farklı ML algoritması (LR, RF, GB, ANN) birlikte değerlendirilerek güvenilir risk tahmini yapılır.',
        'feat2_title': 'Klinik Parametreler',
        'feat2_desc': 'Kreatinin, WBC, Platelet, Total Bilirubin ve Yaş gibi temel laboratuvar değerlerine dayalı analiz.',
        'feat3_title': 'Anlık Sonuç',
        'feat3_desc': 'Değerleri girer girmez mortalite olasılığı ve risk sınıfı anında hesaplanır.',
        'how_title': 'Nasıl Çalışır?',
        'how1_title': 'Değerleri Girin',
        'how1_desc': 'Hastanın laboratuvar ölçümlerini ilgili alanlara girin.',
        'how2_title': 'Analiz Edin',
        'how2_desc': '"Riski Hesapla" butonuna tıklayın; modeller saniyeler içinde çalışır.',
        'how3_title': 'Sonucu Okuyun',
        'how3_desc': 'Mortalite olasılığı, risk sınıfı ve açıklama ekrana yansır.',
        'calc_page_title': 'Mortalite Risk Hesaplayıcısı',
        'calc_page_sub': 'Klinik laboratuvar değerlerini girerek AKI mortalite riskini tahmin edin',
        'patient_data': 'Hasta Parametreleri',
        'input_hint': 'Her alan için referans aralığı yardım simgesinde gösterilmiştir.',
        'predict_btn': 'Mortalite Riskini Hesapla',
        'result_title': 'Tahmin Sonucu',
        'mortality_prob': 'Mortalite Olasılığı',
        'survival_prob': 'Sağkalım Olasılığı',
        'high': 'YÜKSEK RİSK',
        'moderate': 'ORTA RİSK',
        'low': 'DÜŞÜK RİSK',
        'high_msg': 'Hasta yüksek AKI mortalite riski taşımaktadır. Acil klinik değerlendirme önerilmektedir.',
        'moderate_msg': 'Hasta orta düzeyde AKI mortalite riski taşımaktadır. Yakın klinik izlem önerilmektedir.',
        'low_msg': 'Hasta düşük AKI mortalite riski taşımaktadır. Rutin klinik izlem sürdürülmelidir.',
        'no_model': 'Model dosyaları bulunamadı. Lütfen eğitim pipeline\'ını çalıştırın.',
        'err': 'Tahmin hatası',
        'how_use_title': 'Nasıl Kullanılır?',
        'step1': 'Sol paneldeki klinik laboratuvar değerlerini girin.',
        'step2': '"Mortalite Riskini Hesapla" düğmesine tıklayın.',
        'step3': 'Tahmin sonucu ve risk sınıfı sağ panelde görünecektir.',
        'top5': 'En Önemli 5 Klinik Gösterge',
        'kf_label': 'Girilen Değerler',
        'disclaimer': 'Bu araç yalnızca araştırma amaçlıdır. Klinik karar vermede kullanılmamalıdır. Tüm tahminler uzman klinisyen tarafından değerlendirilmelidir.',
        'fields': {
            'kreatinin':     ('Kreatinin (mg/dL)',        0.1, 15.0, 0.1, 1.0,  'Normal: 0.6 – 1.2 mg/dL'),
            'wbc':           ('Lökosit / WBC (10³/µL)',   0.0, 50.0, 0.1, 10.0, 'Normal: 4.0 – 11.0 × 10³/µL'),
            'plt':           ('Platelet (10³/µL)',          10,  500,  1,  200,   'Normal: 150 – 400 × 10³/µL'),
            'totalbilirubin':('Total Bilirubin (mg/dL)',   0.0, 20.0, 0.1, 0.8,  'Normal: 0.2 – 1.2 mg/dL'),
            'age':           ('Yaş (yıl)',                  18,  120,  1,   65,   ''),
        },
        'f1': 'Lökosit (WBC)',   'f1_cat': 'Enflamasyon',
        'f2': 'Kreatinin',       'f2_cat': 'Böbrek Fonk.',
        'f3': 'Platelet',        'f3_cat': 'Koagülasyon',
        'f4': 'Total Bilirubin', 'f4_cat': 'Karaciğer',
        'f5': 'Yaş',             'f5_cat': 'Demografik',
        'about_page_title': 'Sistem Hakkında',
        'about_page_sub': 'Model mimarisi, dataset ve klinik arka plan',
        'about_s1': 'YBÜ Hastası', 'about_s2': 'ML Modeli',
        'about_s3': 'Ort. AUC',   'about_s4': 'Özellik',
        'about_models_title': 'Makine Öğrenmesi Modelleri',
        'm1n': 'Lojistik Regresyon', 'm1d': 'Yorumlanabilir doğrusal model; Wald p-değerleri',
        'm2n': 'Rastgele Orman',      'm2d': '200 karar ağacı; Gini önem skoru',
        'm3n': 'Gradyan Artırma',     'm3d': '200 iterasyon; öğrenme hızı 0.05',
        'm4n': 'Sinir Ağı (ANN)',     'm4d': '128-64-32 katmanlı MLP; erken durdurma',
        'feat_title': 'En Önemli Klinik Göstergeler',
        'feat_sub':   '4 modelden ortalama önem skorları',
        'feat_names': ['Kreatinin', 'Lökosit (WBC)', 'Platelet', 'Total Bilirubin', 'Yaş'],
        'feat_cats':  ['Böbrek Fonk.', 'Enflamasyon', 'Koagülasyon', 'Karaciğer', 'Demografik'],
        'aki_section_title': 'Akut Böbrek Hasarı Nedir?',
        'aki_c1t': 'Tanım',
        'aki_c1p': 'AKI, böbrek fonksiyonunun saatler veya günler içinde ani azalmasıdır. YBÜ hastalarında en sık görülen komplikasyonlardan biridir.',
        'aki_c2t': 'Neden Önemli?',
        'aki_c2p': 'AKI, yoğun bakım ünitelerinde mortaliteyi önemli ölçüde artırır. Erken tanı ve müdahale hayat kurtarıcı olabilir.',
        'aki_c3t': 'Yapay Zeka',
        'aki_c3p': 'ML modelleri laboratuvar ve klinik verileri birleştirerek bireysel mortalite riskini tahmin eder.',
        'disclaimer_title': 'Önemli Uyarı',
        'disclaimer_full': 'Bu sistem yalnızca araştırma amaçlıdır. Klinik karar vermede kullanılmamalıdır. Tüm tahminler uzman klinisyen tarafından değerlendirilmelidir.',
        'proj_page_title': 'Araştırma Projesi',
        'proj_page_sub': 'DEU Hastanesi YBÜ kohortunda AKI mortalite tahmini',
        'proj_hero_badge': 'DEU Hastanesi · YBÜ Kohortu · İkili Sınıflandırma',
        'proj_hero_title': 'AKI Mortalite Tahmin Araştırması',
        'proj_hero_sub': 'DEU Hastanesi yoğun bakım ünitesi kohortunda dört makine öğrenmesi algoritması kullanılarak ICU mortalite riski tahmini gerçekleştirilmiştir.',
        'proj_s1': 'YBÜ Hastası', 'proj_s2': 'ML Modeli', 'proj_s3': 'En İyi AUC', 'proj_s4': 'Klinik Gösterge',
        'proj_dataset_title': 'Veri Seti',
        'proj_ds1': 'Toplam Hasta', 'proj_ds2': 'Eğitim/Test', 'proj_ds3': 'Ham Özellik', 'proj_ds4': 'Model Özelliği',
        'proj_survived': 'Sağkalım ~72%', 'proj_deceased': 'Mortalite ~28%',
        'proj_pipeline_title': 'Metodoloji Pipeline',
        'proj_pipe': [
            ('Veri Yükleme', 'PostgreSQL · deu_retro_clean tablosu'),
            ('EDA & Doğrulama', 'Hedef dağılımı · eksik değer analizi'),
            ('Ön İşleme', 'Kategorik kodlama · ID sütunu temizliği'),
            ('Stratifiye Bölme', '80% eğitim · 20% test · seed=42'),
            ('MICE Imputation', 'miceforest · 5 iterasyon · eğitim setine fit'),
            ('Normalizasyon', 'StandardScaler · eğitim setine fit'),
            ('Model Eğitimi', 'LR · RF · GB · ANN(MLP) · Değerlendirme'),
        ],
        'proj_algo_title': 'Makine Öğrenmesi Modelleri',
        'proj_metrics_title': 'Model Performans Karşılaştırması',
        'proj_th_model': 'Model', 'proj_best_model': 'En İyi',
        'proj_feat_title': 'En Önemli 15 Klinik Gösterge',
        'proj_feat_sub': '4 modelden ortalama permütasyon ve Gini önem skorları',
        'proj_feat_names': ['Lökosit (WBC)', 'AST', 'Kreatinin', 'Platelet', 'INR Plazma', 'Total Bilirubin', 'APTT Plazma', 'eGFR CKD-EPI', 'Yaş', 'Glukoz', 'Sodyum', 'PT Plazma', 'Kalsiyum', 'Klor', 'BUN'],
        'proj_conclusion_title': 'Temel Bulgular',
        'proj_findings': [
            'Gradient Boosting en yüksek AUC değerini (0.910) elde ederek diğer üç modeli geride bıraktı.',
            'Lökosit (WBC) ve Kreatinin, tüm modellerde en güçlü mortalite göstergeleri olarak öne çıktı.',
            'MICE yöntemi eksik klinik değerleri 5 iterasyonla doldurarak model kalitesini artırdı.',
            'Tüm modeller AUC > 0.86 değerine ulaştı; bu seçilen özellik setinin klinik geçerliliğini kanıtlar.',
        ],
        'proj_stack_title': 'Teknik Yığın',
    },
    'EN': {
        'nav_home': 'Home', 'nav_calc': 'Calculator',
        'nav_about': 'About', 'nav_project': 'Project',
        'theme_dark': 'Dark', 'theme_light': 'Light',
        'hero_badge': 'DEU Hospital · ICU Cohort · Research Tool',
        'hero_title': 'AKI Mortality Risk Calculator',
        'hero_sub': 'A clinical research tool combining four machine learning models to estimate mortality risk for AKI patients in intensive care units.',
        'hero_cta1': 'Calculate Risk',
        'hero_cta2': 'View Research',
        's1_val': '2,230', 's1_lbl': 'ICU Patients',
        's2_val': '4', 's2_lbl': 'ML Models',
        's3_val': '91%', 's3_lbl': 'Best AUC',
        's4_val': '15', 's4_lbl': 'Clinical Features',
        'feat1_title': 'Multi-Model Ensemble',
        'feat1_desc': 'Four ML algorithms (LR, RF, GB, ANN) evaluated together to produce robust risk estimates.',
        'feat2_title': 'Clinical Parameters',
        'feat2_desc': 'Analysis based on key laboratory values including Creatinine, WBC, Platelet, Total Bilirubin, and Age.',
        'feat3_title': 'Instant Results',
        'feat3_desc': 'Mortality probability and risk class calculated the moment you submit patient values.',
        'how_title': 'How It Works',
        'how1_title': 'Enter Values',
        'how1_desc': "Input the patient's laboratory measurements into the corresponding fields.",
        'how2_title': 'Analyze',
        'how2_desc': "Click 'Calculate Risk' — the models run in seconds.",
        'how3_title': 'Read Results',
        'how3_desc': 'Mortality probability, risk class, and an explanation appear on screen.',
        'calc_page_title': 'Mortality Risk Calculator',
        'calc_page_sub': 'Enter clinical laboratory values to estimate AKI mortality risk',
        'patient_data': 'Patient Parameters',
        'input_hint': 'Reference ranges shown via help icon on each field.',
        'predict_btn': 'Calculate Mortality Risk',
        'result_title': 'Prediction Result',
        'mortality_prob': 'Mortality Probability',
        'survival_prob': 'Survival Probability',
        'high': 'HIGH RISK',
        'moderate': 'MODERATE RISK',
        'low': 'LOW RISK',
        'high_msg': 'Patient has a high estimated AKI mortality risk. Urgent clinical evaluation is recommended.',
        'moderate_msg': 'Patient has a moderate estimated AKI mortality risk. Close clinical monitoring is recommended.',
        'low_msg': 'Patient has a low estimated AKI mortality risk. Routine clinical follow-up should continue.',
        'no_model': 'Model files not found. Please run the training pipeline first.',
        'err': 'Prediction error',
        'how_use_title': 'How to Use',
        'step1': 'Enter the clinical laboratory values in the left panel.',
        'step2': 'Click the "Calculate Mortality Risk" button.',
        'step3': 'The prediction result and risk class will appear here.',
        'top5': 'Top 5 Clinical Predictors',
        'kf_label': 'Key Input Values',
        'disclaimer': 'This tool is for research purposes only and must not be used for clinical decision-making. All predictions must be reviewed by a qualified clinician.',
        'fields': {
            'kreatinin':     ('Creatinine (mg/dL)',         0.1, 15.0, 0.1, 1.0,  'Normal: 0.6 – 1.2 mg/dL'),
            'wbc':           ('WBC / Leukocytes (10³/µL)',  0.0, 50.0, 0.1, 10.0, 'Normal: 4.0 – 11.0 × 10³/µL'),
            'plt':           ('Platelet Count (10³/µL)',     10,  500,  1,  200,   'Normal: 150 – 400 × 10³/µL'),
            'totalbilirubin':('Total Bilirubin (mg/dL)',     0.0, 20.0, 0.1, 0.8,  'Normal: 0.2 – 1.2 mg/dL'),
            'age':           ('Age (years)',                  18,  120,  1,   65,   ''),
        },
        'f1': 'WBC (Leukocytes)',  'f1_cat': 'Inflammation',
        'f2': 'Creatinine',        'f2_cat': 'Renal Func.',
        'f3': 'Platelet Count',    'f3_cat': 'Coagulation',
        'f4': 'Total Bilirubin',   'f4_cat': 'Hepatic',
        'f5': 'Age',               'f5_cat': 'Demographic',
        'about_page_title': 'About the System',
        'about_page_sub': 'Model architecture, dataset, and clinical background',
        'about_s1': 'ICU Patients', 'about_s2': 'ML Models',
        'about_s3': 'Mean AUC',     'about_s4': 'Features',
        'about_models_title': 'Machine Learning Models',
        'm1n': 'Logistic Regression', 'm1d': 'Interpretable linear model with Wald test p-values',
        'm2n': 'Random Forest',        'm2d': '200 decision trees with Gini importance scores',
        'm3n': 'Gradient Boosting',    'm3d': '200 estimators, learning rate 0.05',
        'm4n': 'Neural Network (ANN)', 'm4d': '128-64-32 layer MLP with early stopping',
        'feat_title': 'Top Clinical Predictors',
        'feat_sub':   'Averaged importance scores across all 4 models',
        'feat_names': ['Creatinine', 'WBC (Leukocytes)', 'Platelet Count', 'Total Bilirubin', 'Age'],
        'feat_cats':  ['Renal Func.', 'Inflammation', 'Coagulation', 'Hepatic', 'Demographic'],
        'aki_section_title': 'What is Acute Kidney Injury?',
        'aki_c1t': 'Definition',
        'aki_c1p': 'AKI is a sudden reduction in kidney function over hours to days — one of the most common complications in ICU patients.',
        'aki_c2t': 'Why It Matters',
        'aki_c2p': 'AKI significantly increases ICU mortality. Early diagnosis and intervention can be life-saving.',
        'aki_c3t': 'AI Approach',
        'aki_c3p': 'ML models combine laboratory and clinical data to estimate individual mortality risk.',
        'disclaimer_title': 'Important Notice',
        'disclaimer_full': 'This system was developed for research purposes only. It must not be used for clinical decision-making. All predictions must be reviewed by a qualified clinician.',
        'proj_page_title': 'Research Project',
        'proj_page_sub': 'AKI mortality prediction on the DEU Hospital ICU cohort',
        'proj_hero_badge': 'DEU Hospital · ICU Cohort · Binary Classification',
        'proj_hero_title': 'AKI Mortality Prediction Research',
        'proj_hero_sub': 'Four machine learning algorithms were applied to the DEU Hospital ICU cohort to predict in-hospital mortality risk for acute kidney injury patients.',
        'proj_s1': 'ICU Patients', 'proj_s2': 'ML Models', 'proj_s3': 'Best AUC', 'proj_s4': 'Clinical Features',
        'proj_dataset_title': 'Dataset',
        'proj_ds1': 'Total Patients', 'proj_ds2': 'Train/Test Split', 'proj_ds3': 'Raw Features', 'proj_ds4': 'Model Features',
        'proj_survived': 'Survived ~72%', 'proj_deceased': 'Deceased ~28%',
        'proj_pipeline_title': 'Methodology Pipeline',
        'proj_pipe': [
            ('Data Loading', 'PostgreSQL · deu_retro_clean table'),
            ('EDA & Validation', 'Target distribution · missing value analysis'),
            ('Preprocessing', 'Categorical encoding · ID column removal'),
            ('Stratified Split', '80% train · 20% test · seed=42'),
            ('MICE Imputation', 'miceforest · 5 iterations · fit on train'),
            ('Normalization', 'StandardScaler · fit on train set'),
            ('Model Training', 'LR · RF · GB · ANN(MLP) · Evaluation'),
        ],
        'proj_algo_title': 'Machine Learning Models',
        'proj_metrics_title': 'Model Performance Comparison',
        'proj_th_model': 'Model', 'proj_best_model': 'Best',
        'proj_feat_title': 'Top 15 Clinical Predictors',
        'proj_feat_sub': 'Averaged permutation and Gini importance scores across all 4 models',
        'proj_feat_names': ['WBC (Leukocytes)', 'AST', 'Creatinine', 'Platelet Count', 'INR Plasma', 'Total Bilirubin', 'APTT Plasma', 'eGFR CKD-EPI', 'Age', 'Glucose', 'Sodium', 'PT Plasma', 'Calcium', 'Chloride', 'BUN'],
        'proj_conclusion_title': 'Key Findings',
        'proj_findings': [
            'Gradient Boosting achieved the highest AUC of 0.910, outperforming all three other models on the hold-out test set.',
            'WBC (Leukocytes) and Creatinine emerged as the strongest mortality predictors across all four models.',
            'MICE imputation (5 iterations) effectively handled missing clinical values, improving overall model quality.',
            'All four models exceeded AUC 0.86, confirming the clinical validity of the selected feature set.',
        ],
        'proj_stack_title': 'Technical Stack',
    },
}

FEATURES = ['kreatinin', 'wbc', 'plt', 'totalbilirubin', 'age']

_PROJ_MODELS = [
    ('m1n', 'm1d', '86.5%', '82.1%', '0.714', '0.592', 86.5, '#0891b2', 'max_iter=1000 · C=1.0 · l2', False),
    ('m2n', 'm2d', '90.0%', '83.9%', '0.757', '0.637', 90.0, '#22c55e', 'n_estimators=200 · max_depth=20', False),
    ('m3n', 'm3d', '91.0%', '83.2%', '0.747', '0.623', 91.0, '#0e7490', 'n_estimators=200 · lr=0.05 · max_depth=5', True),
    ('m4n', 'm4d', '87.7%', '79.6%', '0.685', '0.538', 87.7, '#d97706', '128-64-32 · early_stopping · val=10%', False),
]
_PROJ_FI_VALS   = [11.0, 8.4, 8.2, 6.3, 4.7, 4.3, 3.3, 3.1, 2.9, 2.9, 2.9, 2.9, 2.6, 1.9, 1.8]
_PROJ_FI_COLORS = ['#0891b2','#22d3ee','#0891b2','#22c55e','#d97706','#d97706',
                   '#22d3ee','#0891b2','#22c55e','#d97706','#22d3ee','#d97706',
                   '#d97706','#22d3ee','#d97706']
_PROJ_METRICS_TABLE = [
    ('Logistic Regression', '0.865', '82.1%', '0.714', '64.9%', '0.592', '#0891b2', False),
    ('Random Forest',       '0.900', '83.9%', '0.757', '72.7%', '0.637', '#22c55e', False),
    ('Gradient Boosting',   '0.910', '83.2%', '0.747', '72.1%', '0.623', '#0e7490', True),
    ('ANN (MLP)',           '0.877', '79.6%', '0.685', '64.3%', '0.538', '#d97706', False),
]
_PROJ_STACK = ['Python 3.x', 'scikit-learn', 'PostgreSQL', 'miceforest',
               'pandas', 'NumPy', 'Streamlit', 'StandardScaler', 'joblib', 'SQLAlchemy', 'matplotlib', 'seaborn']


# ── Model loading ─────────────────────────────────────────────────────────────
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


# ── Animated SVG gauge ────────────────────────────────────────────────────────
def risk_gauge_html(pct: float, color: str) -> str:
    arc  = math.pi * 80
    fill = arc * min(pct, 100) / 100
    uid  = f"g{abs(int(pct * 137))}"
    return (
        '<div style="text-align:center;padding:12px 0 6px;">'
        f'<svg id="{uid}" viewBox="0 0 200 120" width="230" height="138">'
        '<defs>'
        f'<filter id="gw{uid}" x="-30%" y="-30%" width="160%" height="160%">'
        '<feGaussianBlur stdDeviation="3.5" result="blur"/>'
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
        '<style>'
        f'@keyframes fi{uid}{{from{{stroke-dasharray:0 {arc:.1f}}}to{{stroke-dasharray:{fill:.1f} {arc:.1f}}}}}'
        f'@keyframes pi{uid}{{from{{opacity:0;transform:scale(.88)}}to{{opacity:1;transform:scale(1)}}}}'
        f'#{uid}{{animation:pi{uid} .45s ease both}}'
        f'#ff{uid}{{animation:fi{uid} 1.3s cubic-bezier(.4,0,.2,1) .2s both}}'
        f'#nt{uid}{{animation:pi{uid} .4s ease .85s both;opacity:0}}'
        '</style>'
        '</defs>'
        f'<path d="M 20 100 A 80 80 0 0 1 180 100" stroke="rgba(0,0,0,0.07)" stroke-width="14" fill="none" stroke-linecap="round"/>'
        f'<path id="ff{uid}" d="M 20 100 A 80 80 0 0 1 180 100" stroke="{color}" stroke-width="14" fill="none" stroke-linecap="round" filter="url(#gw{uid})" stroke-dasharray="0 {arc:.1f}"/>'
        f'<g id="nt{uid}">'
        f'<text x="100" y="82" text-anchor="middle" font-family="\'Figtree\',sans-serif" font-size="30" font-weight="800" fill="{color}">{pct:.1f}%</text>'
        f'<text x="100" y="100" text-anchor="middle" font-family="\'Noto Sans\',sans-serif" font-size="7" font-weight="600" fill="rgba(0,0,0,0.3)" letter-spacing="2">MORTALITY RISK</text>'
        f'</g>'
        f'<text x="14" y="114" text-anchor="middle" font-family="\'Noto Sans\',sans-serif" font-size="8" fill="rgba(0,0,0,0.2)">0%</text>'
        f'<text x="186" y="114" text-anchor="middle" font-family="\'Noto Sans\',sans-serif" font-size="8" fill="rgba(0,0,0,0.2)">100%</text>'
        '</svg></div>'
    )


# ── Page renderers ────────────────────────────────────────────────────────────
def render_landing(T: dict) -> None:
    st.markdown(
        f'<div class="hero anim-in">'
        f'<div class="hero-badge">{T["hero_badge"]}</div>'
        f'<div class="hero-title">{T["hero_title"]}</div>'
        f'<div class="hero-sub">{T["hero_sub"]}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    cta1, cta2, _ = st.columns([2, 2, 6])
    with cta1:
        if st.button(T['hero_cta1'], use_container_width=True, key='cta_calc'):
            st.session_state.page = 'calculator'
            st.rerun()
    with cta2:
        if st.button(T['hero_cta2'], use_container_width=True, key='cta_proj'):
            st.session_state.page = 'project'
            st.rerun()

    st.markdown(
        f'<div class="stats-row anim-in-2">'
        f'<div class="stat-card"><div class="stat-val">{T["s1_val"]}</div><div class="stat-lbl">{T["s1_lbl"]}</div></div>'
        f'<div class="stat-card"><div class="stat-val">{T["s2_val"]}</div><div class="stat-lbl">{T["s2_lbl"]}</div></div>'
        f'<div class="stat-card"><div class="stat-val">{T["s3_val"]}</div><div class="stat-lbl">{T["s3_lbl"]}</div></div>'
        f'<div class="stat-card"><div class="stat-val">{T["s4_val"]}</div><div class="stat-lbl">{T["s4_lbl"]}</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div style="font-family:var(--ff-head);font-size:1.15rem;font-weight:800;color:var(--text);'
        f'margin:8px 0 16px;padding-top:8px;">{T["how_title"]}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="steps-row">'
        f'<div class="step-card"><div class="step-num">1</div>'
        f'<div class="step-title">{T["how1_title"]}</div><div class="step-desc">{T["how1_desc"]}</div></div>'
        f'<div class="step-card"><div class="step-num">2</div>'
        f'<div class="step-title">{T["how2_title"]}</div><div class="step-desc">{T["how2_desc"]}</div></div>'
        f'<div class="step-card"><div class="step-num">3</div>'
        f'<div class="step-title">{T["how3_title"]}</div><div class="step-desc">{T["how3_desc"]}</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )


def render_calculator(T: dict) -> None:
    st.markdown(
        f'<div class="section-header">'
        f'<div><div class="section-title">{T["calc_page_title"]}</div>'
        f'<div class="section-sub">{T["calc_page_sub"]}</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    model, scaler = load_model_and_preprocessors()
    if model is None:
        st.error(T['no_model'])
        return

    left, right = st.columns([1, 1], gap='large')

    with left:
        with st.container():
            st.markdown(
                f'<div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;'
                f'padding:20px 20px 4px;box-shadow:var(--shadow);margin-bottom:4px;">'
                f'<div class="card-title">{T["patient_data"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        st.markdown(
            '<style>[data-testid="stVerticalBlock"]>[data-testid="element-container"]:has(.card-title)+'
            '[data-testid="element-container"]{margin-top:-16px}</style>',
            unsafe_allow_html=True
        )
        st.caption(T['input_hint'])
        input_data: dict = {}
        for feat in FEATURES:
            lbl, mn, mx, step, default, ref = T['fields'][feat]
            input_data[feat] = st.number_input(
                lbl, min_value=float(mn), max_value=float(mx),
                value=float(default), step=float(step),
                **({'help': ref} if ref else {})
            )
        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        predict = st.button(T['predict_btn'], type='primary', use_container_width=True, key='predict_btn')
        st.markdown(
            f'<div class="disclaimer disclaimer-wrap">'
            f'<details open>'
            f'<summary>{T["disclaimer_title"]}</summary>'
            f'<div class="disc-body" style="margin-top:6px;">{T["disclaimer"]}</div>'
            f'</details>'
            f'</div>',
            unsafe_allow_html=True
        )

    with right:
        if not predict:
            feat_rows = ''.join(
                f'<div class="feat-row"><span class="feat-rank">{i+1}</span>'
                f'<span class="feat-name">{T[f"f{i+1}"]}</span></div>'
                for i in range(5)
            )
            st.markdown(
                f'<div class="card"><div class="card-title">{T["top5"]}</div>'
                f'{feat_rows}</div>',
                unsafe_allow_html=True
            )
        else:
            try:
                input_df = pd.DataFrame([input_data])
                if scaler is not None and hasattr(scaler, 'feature_names_in_'):
                    exp   = list(scaler.feature_names_in_)
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

                mp  = model.predict_proba(X_input)[0][1]
                pct = mp * 100
                sp  = 100 - pct

                if mp >= 0.7:
                    risk_key, color, badge, card_cls = 'high',     '#dc2626', 'badge-high',     'result-card-high'
                elif mp >= 0.4:
                    risk_key, color, badge, card_cls = 'moderate', '#d97706', 'badge-moderate', 'result-card-moderate'
                else:
                    risk_key, color, badge, card_cls = 'low',      '#059669', 'badge-low',      'result-card-low'

                gauge = risk_gauge_html(pct, color)

                st.markdown(
                    f'<div class="result-card {card_cls} anim-in">'
                    f'<div class="card-title">{T["result_title"]}</div>'
                    f'{gauge}'
                    f'<div style="text-align:center;margin:8px 0 16px;">'
                    f'<span class="risk-badge {badge}">{T[risk_key]}</span>'
                    f'</div>'
                    f'<div class="metric-pair">'
                    f'<div class="metric-box"><div class="metric-label">{T["mortality_prob"]}</div>'
                    f'<div class="metric-value" style="color:{color};">{pct:.1f}%</div></div>'
                    f'<div class="metric-box"><div class="metric-label">{T["survival_prob"]}</div>'
                    f'<div class="metric-value" style="color:#059669;">{sp:.1f}%</div></div>'
                    f'</div>'
                    f'<div class="prog-wrap">'
                    f'<div class="prog-labels"><span>0%</span><span>{pct:.1f}%</span><span>100%</span></div>'
                    f'<div class="prog-track"><div class="prog-fill" style="width:{pct:.1f}%;background:{color};"></div></div>'
                    f'</div>'
                    f'<div class="key-factors">'
                    f'<div class="kf-label">{T["kf_label"]}</div>'
                    f'<div class="kf-row"><span class="kf-name">{T["fields"]["kreatinin"][0]}</span><span class="kf-val">{input_data["kreatinin"]:.1f} mg/dL</span></div>'
                    f'<div class="kf-row"><span class="kf-name">{T["fields"]["wbc"][0]}</span><span class="kf-val">{input_data["wbc"]:.1f} ×10³/µL</span></div>'
                    f'<div class="kf-row"><span class="kf-name">{T["fields"]["plt"][0]}</span><span class="kf-val">{int(input_data["plt"])} ×10³/µL</span></div>'
                    f'</div>'
                    f'<p style="font-size:0.82rem;color:var(--sub);margin-top:14px;line-height:1.7;">{T[risk_key+"_msg"]}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"{T['err']}: {e}")


def render_about(T: dict) -> None:
    st.markdown(
        f'<div class="section-header">'
        f'<div><div class="section-title">{T["about_page_title"]}</div>'
        f'<div class="section-sub">{T["about_page_sub"]}</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="about-stats">'
        f'<div class="about-stat"><div class="about-stat-val">2,230</div><div class="about-stat-lbl">{T["about_s1"]}</div></div>'
        f'<div class="about-stat"><div class="about-stat-val">4</div><div class="about-stat-lbl">{T["about_s2"]}</div></div>'
        f'<div class="about-stat"><div class="about-stat-val">~89%</div><div class="about-stat-lbl">{T["about_s3"]}</div></div>'
        f'<div class="about-stat"><div class="about-stat-val">5</div><div class="about-stat-lbl">{T["about_s4"]}</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns([1, 1], gap='large')
    with col_a:
        aki_cards = ''.join(
            f'<div class="aki-card"><div class="aki-title">{t}</div><div class="aki-text">{p}</div></div>'
            for t, p in [(T['aki_c1t'], T['aki_c1p']), (T['aki_c2t'], T['aki_c2p']), (T['aki_c3t'], T['aki_c3p'])]
        )
        weights = [92, 85, 78, 71, 64]
        feat_bars = ''.join(
            f'<div class="fb-row">'
            f'<span class="fb-rank">{i+1}</span>'
            f'<div class="fb-info"><div class="fb-name">{nm}</div></div>'
            f'<div class="fb-track"><div class="fb-fill" style="width:{w}%;"></div></div>'
            f'<span class="fb-pct">{w}%</span>'
            f'</div>'
            for i, (nm, w) in enumerate(zip(T['feat_names'], weights))
        )
        st.markdown(
            f'<div class="card"><div class="card-title">{T["aki_section_title"]}</div>'
            f'<div class="aki-grid">{aki_cards}</div></div>'
            f'<div class="card"><div class="card-title">{T["feat_title"]}</div>'
            f'<p style="font-size:0.76rem;color:var(--sub);margin:-4px 0 14px;">{T["feat_sub"]}</p>'
            f'{feat_bars}</div>',
            unsafe_allow_html=True
        )

    with col_b:
        model_cards = ''.join(
            f'<div class="model-card"><div class="model-name">{T[nk]}</div>'
            f'<div class="model-desc">{T[dk]}</div>'
            f'<div class="model-auc-lbl">AUC</div><div class="model-auc-val">~{auc}%</div>'
            f'<div class="auc-track"><div class="auc-fill" style="width:{auc}%;"></div></div></div>'
            for nk, dk, auc in [('m1n','m1d',79),('m2n','m2d',82),('m3n','m3d',83),('m4n','m4d',80)]
        )
        st.markdown(
            f'<div class="card"><div class="card-title">{T["about_models_title"]}</div>'
            f'<div class="model-grid">{model_cards}</div></div>'
            f'<div class="card" style="background:#fffbeb;border-color:#fde68a;">'
            f'<div class="card-title" style="color:#d97706;">{T["disclaimer_title"]}</div>'
            f'<p style="font-size:0.81rem;color:#92400e;line-height:1.7;margin:0;">{T["disclaimer_full"]}</p>'
            f'</div>',
            unsafe_allow_html=True
        )


def render_project(T: dict, lang: str) -> None:
    st.markdown(
        f'<div class="section-header">'
        f'<div><div class="section-title">{T["proj_page_title"]}</div>'
        f'<div class="section-sub">{T["proj_page_sub"]}</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="proj-hero anim-in">'
        f'<div class="proj-hero-badge">{T["proj_hero_badge"]}</div>'
        f'<div class="proj-hero-title">{T["proj_hero_title"]}</div>'
        f'<div class="proj-hero-sub">{T["proj_hero_sub"]}</div>'
        f'<div class="proj-hero-stats">'
        f'<div class="proj-stat"><div class="proj-stat-val">2,230</div><div class="proj-stat-lbl">{T["proj_s1"]}</div></div>'
        f'<div class="proj-stat"><div class="proj-stat-val">4</div><div class="proj-stat-lbl">{T["proj_s2"]}</div></div>'
        f'<div class="proj-stat"><div class="proj-stat-val">91.0%</div><div class="proj-stat-lbl">{T["proj_s3"]}</div></div>'
        f'<div class="proj-stat"><div class="proj-stat-val">15</div><div class="proj-stat-lbl">{T["proj_s4"]}</div></div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns([1, 1], gap='large')
    with col_a:
        feat_chips = ''.join(
            f'<span class="proj-chip proj-chip-blue">{f}</span>'
            for f in (['Kreatinin','WBC','Platelet','Total Bilirubin','Yaş'] if lang == 'TR'
                      else ['Creatinine','WBC','Platelet','Total Bilirubin','Age'])
        )
        st.markdown(
            f'<div class="card"><div class="card-title">{T["proj_dataset_title"]}</div>'
            f'<div class="proj-ds-grid">'
            f'<div class="proj-ds-box"><div class="proj-ds-val">2,230</div><div class="proj-ds-lbl">{T["proj_ds1"]}</div></div>'
            f'<div class="proj-ds-box"><div class="proj-ds-val">80/20</div><div class="proj-ds-lbl">{T["proj_ds2"]}</div></div>'
            f'<div class="proj-ds-box"><div class="proj-ds-val">20+</div><div class="proj-ds-lbl">{T["proj_ds3"]}</div></div>'
            f'<div class="proj-ds-box"><div class="proj-ds-val">5</div><div class="proj-ds-lbl">{T["proj_ds4"]}</div></div>'
            f'</div>'
            f'<div style="font-size:0.65rem;font-weight:700;color:var(--sub);text-transform:uppercase;letter-spacing:.8px;margin:14px 0 6px;">{"Hesaplayıcı Özellikleri" if lang=="TR" else "Calculator Features"}</div>'
            f'<div class="proj-chips">{feat_chips}</div>'
            f'<div style="font-size:0.65rem;font-weight:700;color:var(--sub);text-transform:uppercase;letter-spacing:.8px;margin:10px 0 6px;">{"Hedef Dağılımı" if lang=="TR" else "Target Distribution"}</div>'
            f'<div class="proj-chips">'
            f'<span class="proj-chip proj-chip-green">{T["proj_survived"]}</span>'
            f'<span class="proj-chip proj-chip-red">{T["proj_deceased"]}</span>'
            f'</div></div>',
            unsafe_allow_html=True
        )

    with col_b:
        steps_html = ''.join(
            f'<div class="proj-pipe-step">'
            f'<div class="proj-pipe-num">{i+1}</div>'
            f'<div><div class="proj-pipe-txt">{label}</div><div class="proj-pipe-detail">{detail}</div></div>'
            f'</div>'
            for i, (label, detail) in enumerate(T['proj_pipe'])
        )
        st.markdown(
            f'<div class="card"><div class="card-title">{T["proj_pipeline_title"]}</div>'
            f'<div class="proj-pipeline">{steps_html}</div></div>',
            unsafe_allow_html=True
        )

    cards_html = ''.join(
        f'<div class="proj-model-card{"  proj-model-best" if best else ""}">'
        f'{"<div class=\"proj-best-badge\">" + T["proj_best_model"] + "</div>" if best else ""}'
        f'<div class="proj-model-name" style="color:{color};">{T[nk]}</div>'
        f'<div class="proj-model-desc">{T[dk]}</div>'
        f'<div class="proj-model-params">{params}</div>'
        f'<div class="proj-metrics-mini">'
        f'<div><div class="proj-mini-lbl">AUC</div><div class="proj-mini-val" style="color:{color};">{auc_s}</div></div>'
        f'<div><div class="proj-mini-lbl">ACC</div><div class="proj-mini-val">{acc}</div></div>'
        f'<div><div class="proj-mini-lbl">F1</div><div class="proj-mini-val">{f1}</div></div>'
        f'<div><div class="proj-mini-lbl">MCC</div><div class="proj-mini-val">{mcc}</div></div>'
        f'</div>'
        f'<div class="auc-track" style="margin-top:12px;">'
        f'<div class="auc-fill" style="width:{auc_f}%;background:{color};"></div></div>'
        f'</div>'
        for nk, dk, auc_s, acc, f1, mcc, auc_f, color, params, best in _PROJ_MODELS
    )
    st.markdown(
        f'<div class="card"><div class="card-title">{T["proj_algo_title"]}</div>'
        f'<div class="proj-model-grid">{cards_html}</div></div>',
        unsafe_allow_html=True
    )

    rows_html = ''.join(
        f'<tr class="{"proj-tr-best" if best else ""}">'
        f'<td class="proj-td-name" style="color:{color};">{name}</td>'
        f'<td class="proj-td-auc" style="color:{color};">{auc}</td>'
        f'<td>{acc}</td><td>{f1}</td><td>{rec}</td><td>{mcc}</td>'
        f'<td>{"<span class=\"proj-best-chip\">" + T["proj_best_model"] + "</span>" if best else ""}</td>'
        f'</tr>'
        for name, auc, acc, f1, rec, mcc, color, best in _PROJ_METRICS_TABLE
    )
    st.markdown(
        f'<div class="card"><div class="card-title">{T["proj_metrics_title"]}</div>'
        f'<div style="overflow-x:auto;">'
        f'<table class="proj-table"><thead><tr>'
        f'<th>{T["proj_th_model"]}</th><th>AUC</th><th>Accuracy</th>'
        f'<th>F1-Score</th><th>Recall</th><th>MCC</th><th></th>'
        f'</tr></thead><tbody>{rows_html}</tbody></table></div></div>',
        unsafe_allow_html=True
    )

    max_imp = _PROJ_FI_VALS[0]
    fi_rows = ''.join(
        f'<div class="proj-fi-row">'
        f'<div class="proj-fi-rank">{i+1}</div>'
        f'<div class="proj-fi-name">{name}</div>'
        f'<div class="proj-fi-track"><div class="proj-fi-fill" style="width:{imp/max_imp*100:.1f}%;background:{color};"></div></div>'
        f'<div class="proj-fi-pct" style="color:{color};">{imp:.1f}%</div>'
        f'</div>'
        for i, (name, imp, color) in enumerate(zip(T['proj_feat_names'], _PROJ_FI_VALS, _PROJ_FI_COLORS))
    )
    st.markdown(
        f'<div class="card"><div class="card-title">{T["proj_feat_title"]}</div>'
        f'<p style="font-size:0.74rem;color:var(--sub);margin:-6px 0 14px;">{T["proj_feat_sub"]}</p>'
        f'{fi_rows}</div>',
        unsafe_allow_html=True
    )

    col_c, col_d = st.columns([3, 2], gap='large')
    with col_c:
        findings_html = ''.join(
            f'<div class="proj-finding">'
            f'<div class="proj-finding-num">{i+1:02d}</div>'
            f'<div class="proj-finding-txt">{txt}</div>'
            f'</div>'
            for i, txt in enumerate(T['proj_findings'])
        )
        st.markdown(
            f'<div class="card"><div class="card-title">{T["proj_conclusion_title"]}</div>'
            f'{findings_html}</div>',
            unsafe_allow_html=True
        )
    with col_d:
        chips = ''.join(f'<span class="proj-stack-chip">{s}</span>' for s in _PROJ_STACK)
        st.markdown(
            f'<div class="card"><div class="card-title">{T["proj_stack_title"]}</div>'
            f'<div class="proj-stack-grid">{chips}</div></div>',
            unsafe_allow_html=True
        )


# ── Dark mode CSS injection ───────────────────────────────────────────────────
def inject_dark_css() -> None:
    st.markdown("""
<style>
:root{
  --bg:      #042f2e;
  --surface: #0d3b38;
  --surf2:   #134e4a;
  --border:  rgba(20,184,166,0.18);
  --bd-focus:rgba(34,211,238,0.5);
  --primary: #22d3ee;
  --p-hover: #67e8f9;
  --p-dim:   rgba(34,211,238,0.12);
  --p-glow:  rgba(34,211,238,0.25);
  --text:    #f0fdfa;
  --sub:     #99f6e4;
  --muted:   rgba(240,253,250,0.35);
  --success: #4ade80;
  --warn:    #fbbf24;
  --danger:  #f87171;
  --shadow:  0 1px 3px rgba(0,0,0,0.40),0 4px 16px rgba(0,0,0,0.32);
  --shadow-md:0 4px 12px rgba(0,0,0,0.45),0 12px 32px rgba(0,0,0,0.35);
}
[data-testid="stAppViewContainer"]{
  background:var(--bg)!important;
  background-image:
    linear-gradient(rgba(34,211,238,0.018) 1px,transparent 1px),
    linear-gradient(90deg,rgba(34,211,238,0.018) 1px,transparent 1px)!important;
  background-size:52px 52px!important;
}
.hero{background:linear-gradient(135deg,#042f2e 0%,#0891b2 55%,#22d3ee 100%)}
.disclaimer{background:rgba(217,119,6,0.08);border-color:rgba(217,119,6,0.25);color:#fbbf24}
.badge-high    {background:rgba(220,38,38,0.12);color:#f87171;border-color:rgba(248,113,113,0.3)}
.badge-moderate{background:rgba(217,119,6,0.12);color:#fbbf24;border-color:rgba(251,191,36,0.3)}
.badge-low     {background:rgba(5,150,105,0.12);color:#34d399;border-color:rgba(52,211,153,0.3)}
.result-card{background:var(--surface)}
.result-card-high    {border-top-color:#f87171}
.result-card-moderate{border-top-color:#fbbf24}
.result-card-low     {border-top-color:#34d399}
.proj-tr-best td{background:rgba(34,211,238,0.07)}
.proj-model-best{border-color:rgba(34,211,238,0.4)!important;background:rgba(34,211,238,0.06)!important}
.proj-best-badge,.proj-best-chip{background:rgba(34,211,238,0.1)!important;border-color:rgba(34,211,238,0.3)!important;color:#22d3ee!important}
.proj-hero{background:linear-gradient(135deg,rgba(8,145,178,0.1) 0%,rgba(34,211,238,0.06) 60%,transparent 100%);border-color:rgba(34,211,238,0.25)}
.proj-hero-badge{background:rgba(34,211,238,0.1);border-color:rgba(34,211,238,0.25);color:#22d3ee}
.proj-hero-title{color:var(--text)}
[data-baseweb="base-input"],[data-baseweb="input"]{background:var(--surf2)!important}
[data-testid="stNumberInput"]>div>div>input{background:var(--surf2)!important;color:var(--text)!important;border-color:var(--border)!important}
[data-testid="stNumberInput"] label{color:var(--sub)!important}
[data-testid="stNumberInput"] button{background:var(--surf2)!important;border-color:var(--border)!important;color:var(--text)!important}
[data-testid="stNumberInput"] button svg{fill:var(--text)!important;stroke:var(--text)!important}
.stButton>button{background:linear-gradient(135deg,#0e7490,#0891b2)!important}
[data-testid="stTabs"] [role="tablist"]{background:var(--surface)!important;border-color:var(--border)!important}
.card{background:var(--surface)!important;border-color:var(--border)!important}
.about-stat,.stat-card,.feature-card,.step-card,.proj-stat,.model-card,.aki-card{background:var(--surface)!important;border-color:var(--border)!important}
.surf2,.proj-ds-box,.metric-box,.fb-row:hover,.feat-row:hover{background:var(--surf2)!important}
.nav-bar{background:rgba(15,23,42,0.95);border-color:var(--border)}
::-webkit-scrollbar-track{background:var(--bg)!important}
</style>
""", unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if 'lang'  not in st.session_state: st.session_state.lang  = 'TR'
    if 'theme' not in st.session_state: st.session_state.theme = 'light'
    if 'page'  not in st.session_state: st.session_state.page  = 'landing'

    if st.session_state.theme == 'dark':
        inject_dark_css()

    T    = LANG[st.session_state.lang]
    page = st.session_state.page

    # ── Nav: desktop = single row | mobile = stacks via CSS ──
    # Brand is rendered as pure HTML (always full-width on mobile)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;padding:10px 0 6px;">'
        '<div style="width:36px;height:36px;background:linear-gradient(135deg,#0e7490,#0891b2);'
        'border-radius:9px;display:flex;align-items:center;justify-content:center;'
        'font-size:0.58rem;font-weight:800;color:#fff;flex-shrink:0;">AKI</div>'
        '<div><div style="font-size:0.94rem;font-weight:700;color:var(--text);">AKI Risk Calculator</div>'
        '<div style="font-size:0.65rem;color:var(--muted);">DEU Hospital · Research Tool</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

    # Nav buttons row — 4 equal + lang + theme  (CSS stacks on mobile)
    c_home, c_calc, c_about, c_proj, c_lang, c_theme = st.columns([1, 1, 1, 1, 1, 1.2])

    with c_home:
        if st.button(T['nav_home'],    key='nav_home',    use_container_width=True):
            st.session_state.page = 'landing';    st.rerun()
    with c_calc:
        if st.button(T['nav_calc'],    key='nav_calc',    use_container_width=True):
            st.session_state.page = 'calculator'; st.rerun()
    with c_about:
        if st.button(T['nav_about'],   key='nav_about',   use_container_width=True):
            st.session_state.page = 'about';      st.rerun()
    with c_proj:
        if st.button(T['nav_project'], key='nav_project', use_container_width=True):
            st.session_state.page = 'project';    st.rerun()
    with c_lang:
        other_lang = 'EN' if st.session_state.lang == 'TR' else 'TR'
        if st.button(other_lang, key='lang_toggle', use_container_width=True):
            st.session_state.lang = other_lang
            st.rerun()
    with c_theme:
        is_dark = st.session_state.theme == 'dark'
        theme_label = T['theme_light'] if is_dark else T['theme_dark']
        if st.button(theme_label, key='theme_toggle', use_container_width=True):
            st.session_state.theme = 'light' if is_dark else 'dark'
            st.rerun()

    st.markdown('<div style="height:6px;border-bottom:1px solid var(--border);margin-bottom:20px;"></div>',
                unsafe_allow_html=True)

    # ── Route ──
    if page == 'landing':
        render_landing(T)
    elif page == 'calculator':
        render_calculator(T)
    elif page == 'about':
        render_about(T)
    elif page == 'project':
        render_project(T, st.session_state.lang)


if __name__ == '__main__':
    main()
