"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import {
  GitBranch, Database, Microscope, Brain, FlaskConical,
  BarChart3, TrendingUp, CheckCircle, Shield, Server,
  Activity,
} from "lucide-react";

function FadeUp({ children, delay = 0, className = "" }: { children: React.ReactNode; delay?: number; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-50px" });
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 28 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, delay, ease: [0.16, 1, 0.3, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

const PIPELINE = [
  {
    icon: <Database className="w-5 h-5" />,
    color: "#22d3ee",
    title: "Data Loading",
    desc: "PostgreSQL · deu_retro_clean table",
    detail: "Raw retrospective ICU data loaded directly from a local PostgreSQL instance. The table contains 2,230 patient records with 30+ raw features including demographics, vital signs, and laboratory measurements.",
  },
  {
    icon: <Microscope className="w-5 h-5" />,
    color: "#818cf8",
    title: "EDA & Validation",
    desc: "Target distribution · missing value analysis",
    detail: "Exploratory data analysis to verify target balance (~72% survived, ~28% deceased), identify missing value patterns, and detect anomalies. ID columns (row_id, patient_id, protocol_no) are automatically removed.",
  },
  {
    icon: <FlaskConical className="w-5 h-5" />,
    color: "#fb923c",
    title: "Preprocessing",
    desc: "Categorical encoding · feature selection",
    detail: "Categorical variables one-hot encoded. Non-predictive identifier columns removed. Feature matrix prepared with the deathflag target variable extracted separately.",
  },
  {
    icon: <GitBranch className="w-5 h-5" />,
    color: "#34d399",
    title: "Stratified Split",
    desc: "80% train · 20% test · seed = 42",
    detail: "Stratified train-test split preserves the class ratio in both sets. Fixed random seed (42) ensures full reproducibility. No data from the test set ever touches preprocessing fitting.",
  },
  {
    icon: <Brain className="w-5 h-5" />,
    color: "#f472b6",
    title: "MICE Imputation",
    desc: "miceforest · 5 iterations · fit on train",
    detail: "Multiple Imputation by Chained Equations via the miceforest library. The imputer is fit exclusively on training data (5 iterations) and then applied to both train and test sets — preventing data leakage.",
  },
  {
    icon: <TrendingUp className="w-5 h-5" />,
    color: "#fbbf24",
    title: "Feature Scaling",
    desc: "StandardScaler · fit on train set only",
    detail: "StandardScaler normalizes features to zero mean and unit variance. Fit on train set only, then applied to test set. Required for Logistic Regression and ANN; tree models use unscaled features.",
  },
  {
    icon: <BarChart3 className="w-5 h-5" />,
    color: "#22d3ee",
    title: "Model Training & Evaluation",
    desc: "LR · RF · GB · ANN · Metrics",
    detail: "Four models trained in parallel. Evaluated on held-out test set with AUC, Accuracy, F1, Precision, Recall, and MCC. Best model selected by AUC for the prediction interface.",
  },
];

const TECH = [
  { name: "Python 3.9+", role: "Runtime", icon: "🐍" },
  { name: "scikit-learn", role: "ML Models", icon: "🔬" },
  { name: "miceforest", role: "MICE Imputation", icon: "🧬" },
  { name: "PostgreSQL", role: "Data Source", icon: "🗄️" },
  { name: "pandas / NumPy", role: "Data Processing", icon: "📊" },
  { name: "matplotlib", role: "Visualizations", icon: "📈" },
  { name: "joblib", role: "Model Serialization", icon: "💾" },
  { name: "Streamlit", role: "Original Web UI", icon: "⚡" },
];

const STATS_GRID = [
  { label: "Total ICU Patients", value: "2,230" },
  { label: "Train / Test Split", value: "80% / 20%" },
  { label: "Raw Features", value: "30+" },
  { label: "Model Features", value: "15" },
  { label: "Survived", value: "~72%" },
  { label: "Deceased", value: "~28%" },
  { label: "MICE Iterations", value: "5" },
  { label: "Random Seed", value: "42" },
];

export default function ResearchPage() {
  return (
    <div className="min-h-screen bg-[var(--bg)] pt-24 pb-20">
      {/* Header */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 mb-12">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-emerald-400/20 bg-emerald-400/5 mb-4">
            <GitBranch className="w-3 h-3 text-emerald-400" />
            <span className="text-xs font-semibold text-emerald-400 tracking-wider uppercase">
              Research Project
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-3">
            AKI Mortality Prediction{" "}
            <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              Research
            </span>
          </h1>
          <p className="text-slate-500 max-w-xl">
            A comprehensive retrospective cohort study applying four machine learning models
            to predict in-hospital mortality risk in ICU patients with Acute Kidney Injury.
          </p>
        </motion.div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 space-y-8">
        {/* Hero stats */}
        <FadeUp>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {STATS_GRID.map((s) => (
              <div
                key={s.label}
                className="p-4 rounded-xl border border-white/[0.07] bg-white/[0.02] text-center"
              >
                <div className="text-lg font-bold text-white mb-1">{s.value}</div>
                <div className="text-xs text-slate-600">{s.label}</div>
              </div>
            ))}
          </div>
        </FadeUp>

        {/* What is AKI */}
        <FadeUp delay={0.05}>
          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.02] p-6">
            <div className="flex items-center gap-2 mb-5">
              <Activity className="w-4 h-4 text-cyan-400" />
              <span className="text-sm font-semibold text-white">What is Acute Kidney Injury?</span>
            </div>
            <div className="grid sm:grid-cols-3 gap-4">
              {[
                {
                  title: "Definition",
                  text: "AKI is a sudden reduction in kidney function over hours to days — one of the most frequent and severe complications in ICU patients.",
                  color: "#22d3ee",
                },
                {
                  title: "Why It Matters",
                  text: "AKI significantly increases ICU mortality. Early risk stratification enables timely intervention that can be life-saving.",
                  color: "#818cf8",
                },
                {
                  title: "AI Approach",
                  text: "Machine learning models combine laboratory and demographic data to estimate individual mortality risk, supporting clinical decision-making.",
                  color: "#34d399",
                },
              ].map((item) => (
                <div
                  key={item.title}
                  className="p-4 rounded-xl border border-white/[0.05] bg-white/[0.02]"
                >
                  <div className="text-sm font-bold mb-2" style={{ color: item.color }}>
                    {item.title}
                  </div>
                  <p className="text-xs text-slate-500 leading-relaxed">{item.text}</p>
                </div>
              ))}
            </div>
          </div>
        </FadeUp>

        {/* Pipeline */}
        <FadeUp delay={0.1}>
          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.02] p-6">
            <div className="flex items-center gap-2 mb-6">
              <GitBranch className="w-4 h-4 text-emerald-400" />
              <span className="text-sm font-semibold text-white">Methodology Pipeline</span>
            </div>
            <div className="relative">
              {/* Vertical line */}
              <div className="absolute left-5 top-5 bottom-5 w-px bg-white/[0.06]" />

              <div className="space-y-1">
                {PIPELINE.map((step, i) => (
                  <PipelineStep key={step.title} step={step} index={i} delay={i * 0.06} />
                ))}
              </div>
            </div>
          </div>
        </FadeUp>

        {/* Tech stack */}
        <FadeUp delay={0.12}>
          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.02] p-6">
            <div className="flex items-center gap-2 mb-5">
              <Server className="w-4 h-4 text-indigo-400" />
              <span className="text-sm font-semibold text-white">Technical Stack</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {TECH.map((t) => (
                <div
                  key={t.name}
                  className="flex items-center gap-3 p-3 rounded-xl border border-white/[0.05] bg-white/[0.02] hover:border-white/[0.09] transition-colors"
                >
                  <span className="text-xl">{t.icon}</span>
                  <div>
                    <div className="text-xs font-semibold text-white">{t.name}</div>
                    <div className="text-[10px] text-slate-600">{t.role}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </FadeUp>

        {/* Disclaimer */}
        <FadeUp delay={0.14}>
          <div className="rounded-2xl border border-amber-400/15 bg-amber-400/5 p-6">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-400/10 border border-amber-400/20 flex items-center justify-center flex-shrink-0">
                <Shield className="w-5 h-5 text-amber-400" />
              </div>
              <div>
                <div className="text-sm font-bold text-amber-400 mb-2">Important Notice</div>
                <p className="text-xs text-amber-400/70 leading-relaxed">
                  This system was developed exclusively for academic research purposes. It must not be used
                  for clinical decision-making, patient triage, or any medical diagnosis. All model outputs
                  are statistical estimates based on retrospective data and must be reviewed by a qualified
                  clinician before any action is taken. The authors accept no liability for clinical outcomes.
                </p>
                <div className="flex flex-wrap gap-3 mt-3">
                  {["Research use only", "Not CE/FDA cleared", "Requires clinical validation"].map(
                    (tag) => (
                      <div
                        key={tag}
                        className="flex items-center gap-1 text-[10px] text-amber-400/60"
                      >
                        <CheckCircle className="w-3 h-3" />
                        {tag}
                      </div>
                    )
                  )}
                </div>
              </div>
            </div>
          </div>
        </FadeUp>
      </div>
    </div>
  );
}

function PipelineStep({
  step,
  index,
  delay,
}: {
  step: (typeof PIPELINE)[0];
  index: number;
  delay: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-30px" });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, x: -16 }}
      animate={inView ? { opacity: 1, x: 0 } : {}}
      transition={{ duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] }}
      className="relative flex gap-4 pl-12 pb-6 last:pb-0 group"
    >
      {/* Circle on timeline */}
      <div
        className="absolute left-0 top-0 w-10 h-10 rounded-xl flex items-center justify-center text-white flex-shrink-0 z-10"
        style={{ background: `${step.color}18`, color: step.color, border: `1px solid ${step.color}30` }}
      >
        {step.icon}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0 pt-2">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-semibold text-white">{step.title}</span>
          <span className="text-xs text-slate-600 truncate">{step.desc}</span>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed group-hover:text-slate-500 transition-colors">
          {step.detail}
        </p>
      </div>

      {/* Step number */}
      <div className="flex-shrink-0 text-[10px] font-bold text-slate-700 pt-2.5">
        {String(index + 1).padStart(2, "0")}
      </div>
    </motion.div>
  );
}
