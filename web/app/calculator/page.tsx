"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Activity, FlaskConical, Zap, AlertTriangle,
  CheckCircle, XCircle, Info, RotateCcw, ChevronDown,
  HeartPulse, Droplets, Thermometer, TrendingUp, Award,
  BarChart3, Database,
} from "lucide-react";
import { useTranslation } from "@/lib/i18n";

type Dataset = "deu" | "mimic";

/* ─── Types ─── */
interface Field {
  key: string;
  label: string;
  unit: string;
  min: number;
  max: number;
  step: number;
  default: number;
  normal: string;
  icon: React.ReactNode;
  color: string;
}

interface RiskResult {
  probability: number;
  survivalProb: number;
  riskLevel: "low" | "moderate" | "high";
  modelName: string;
  modelAuc: number;
  modelColor: string;
  dataset: Dataset;
}

/* ─── DEU model options ─── */
const DEU_MODEL_OPTIONS = [
  { id: "gb",  name: "Gradient Boosting",    short: "GB",  auc: 91.0, color: "#22d3ee", bg: "rgba(34,211,238,0.08)",   border: "rgba(34,211,238,0.25)",   best: true  },
  { id: "rf",  name: "Random Forest",        short: "RF",  auc: 89.2, color: "#818cf8", bg: "rgba(129,140,248,0.08)", border: "rgba(129,140,248,0.25)", best: false },
  { id: "ann", name: "Neural Network (ANN)", short: "ANN", auc: 87.8, color: "#fb923c", bg: "rgba(251,146,60,0.08)",   border: "rgba(251,146,60,0.25)",   best: false },
  { id: "lr",  name: "Logistic Regression",  short: "LR",  auc: 86.3, color: "#34d399", bg: "rgba(52,211,153,0.08)",  border: "rgba(52,211,153,0.25)",  best: false },
] as const;

/* ─── MIMIC model options (real metrics — RF is best) ─── */
const MIMIC_MODEL_OPTIONS = [
  { id: "rf",  name: "Random Forest",        short: "RF",  auc: 82.3, color: "#818cf8", bg: "rgba(129,140,248,0.08)", border: "rgba(129,140,248,0.25)", best: true  },
  { id: "gb",  name: "Gradient Boosting",    short: "GB",  auc: 80.3, color: "#22d3ee", bg: "rgba(34,211,238,0.08)",  border: "rgba(34,211,238,0.25)",  best: false },
  { id: "lr",  name: "Logistic Regression",  short: "LR",  auc: 79.1, color: "#34d399", bg: "rgba(52,211,153,0.08)", border: "rgba(52,211,153,0.25)", best: false },
  { id: "ann", name: "Neural Network (ANN)", short: "ANN", auc: 78.6, color: "#fb923c", bg: "rgba(251,146,60,0.08)",  border: "rgba(251,146,60,0.25)",  best: false },
] as const;

type ModelId = "gb" | "rf" | "ann" | "lr";

/* ─── DEU feature weights: [creatinine, wbc, platelet, bilirubin, age] ─── */
const DEU_WEIGHTS: Record<ModelId, [number, number, number, number, number]> = {
  gb:  [1.00, 1.00, 1.00, 1.00, 1.00],
  rf:  [0.90, 1.18, 1.08, 0.92, 0.92],
  ann: [0.95, 0.95, 0.93, 1.08, 1.09],
  lr:  [1.12, 0.85, 0.80, 0.90, 1.13],
};

/* ─── MIMIC feature weights (creatinine dominant; WBC less important) ─── */
const MIMIC_WEIGHTS: Record<ModelId, [number, number, number, number, number]> = {
  rf:  [1.40, 0.60, 0.85, 0.75, 0.80],
  gb:  [1.35, 0.62, 0.88, 0.78, 0.78],
  ann: [1.30, 0.65, 0.82, 0.80, 0.83],
  lr:  [1.25, 0.58, 0.78, 0.72, 0.85],
};

/* ─── Top-5 predictors per dataset ─── */
const DEU_PREDICTORS = [
  { w: 88 }, { w: 82 }, { w: 71 }, { w: 60 }, { w: 48 },
];
const MIMIC_PREDICTORS = [
  { w: 88 }, { w: 41 }, { w: 38 }, { w: 29 }, { w: 28 },
];

/* ─── Field static data ─── */
const FIELDS_STATIC = [
  { key: "creatinine", unit: "mg/dL",  min: 0.1, max: 15,  step: 0.1, default: 1.0, normal: "0.6 – 1.2", icon: <Droplets    className="w-4 h-4" />, color: "#22d3ee" },
  { key: "wbc",        unit: "10³/µL", min: 0,   max: 50,  step: 0.1, default: 10.0, normal: "4.0 – 11.0", icon: <FlaskConical className="w-4 h-4" />, color: "#818cf8" },
  { key: "platelet",   unit: "10³/µL", min: 10,  max: 500, step: 1,   default: 200, normal: "150 – 400",  icon: <Activity    className="w-4 h-4" />, color: "#fb923c" },
  { key: "bilirubin",  unit: "mg/dL",  min: 0,   max: 20,  step: 0.1, default: 0.8, normal: "0.2 – 1.2", icon: <Thermometer className="w-4 h-4" />, color: "#34d399" },
  { key: "age",        unit: "years",  min: 18,  max: 120, step: 1,   default: 65,  normal: "—",          icon: <HeartPulse  className="w-4 h-4" />, color: "#f472b6" },
];

/* ─── Risk config ─── */
const RISK_STATIC = {
  low:      { color: "#10b981", bg: "rgba(16,185,129,0.08)",  border: "rgba(16,185,129,0.25)",  glow: "rgba(16,185,129,0.2)",  Icon: CheckCircle },
  moderate: { color: "#f59e0b", bg: "rgba(245,158,11,0.08)",  border: "rgba(245,158,11,0.25)",  glow: "rgba(245,158,11,0.2)",  Icon: AlertTriangle },
  high:     { color: "#ef4444", bg: "rgba(239,68,68,0.08)",   border: "rgba(239,68,68,0.25)",   glow: "rgba(239,68,68,0.2)",   Icon: XCircle },
};

/* ─── Risk estimation ─── */
function computeRisk(values: Record<string, number>, modelId: ModelId, dataset: Dataset): RiskResult {
  const { creatinine, wbc, platelet, bilirubin, age } = values;
  const weights = dataset === "deu" ? DEU_WEIGHTS : MIMIC_WEIGHTS;
  const modelOptions = dataset === "deu" ? DEU_MODEL_OPTIONS : MIMIC_MODEL_OPTIONS;
  const [wCr, wWbc, wPlt, wBil, wAge] = weights[modelId];

  const crScore  = creatinine > 5 ? 35 : creatinine > 2.5 ? 22 : creatinine > 1.5 ? 12 : 3;
  const wbcScore = (wbc > 20 || wbc < 2) ? 25 : (wbc > 15 || wbc < 3.5) ? 15 : wbc > 11 ? 7 : 2;
  const pltScore = platelet < 50 ? 20 : platelet < 100 ? 12 : platelet < 150 ? 5 : 1;
  const bilScore = bilirubin > 5 ? 15 : bilirubin > 2 ? 8 : bilirubin > 1.2 ? 3 : 1;
  const ageScore = age > 80 ? 10 : age > 65 ? 6 : age > 50 ? 3 : 1;

  const score   = crScore * wCr + wbcScore * wWbc + pltScore * wPlt + bilScore * wBil + ageScore * wAge;
  const rawProb = Math.min(score / 105, 0.98);
  const prob    = Math.round(rawProb * 100 * 10) / 10;

  const riskLevel: "low" | "moderate" | "high" = prob >= 50 ? "high" : prob >= 25 ? "moderate" : "low";
  const model = modelOptions.find((m) => m.id === modelId)!;

  return {
    probability: prob,
    survivalProb: Math.round((100 - prob) * 10) / 10,
    riskLevel,
    modelName: model.name,
    modelAuc: model.auc,
    modelColor: model.color,
    dataset,
  };
}

export default function CalculatorPage() {
  const { t } = useTranslation();

  const FIELDS: Field[] = FIELDS_STATIC.map((f, i) => ({
    ...f,
    label: t.calculator.fieldLabels[i],
  }));

  const defaults: Record<string, number> = {};
  FIELDS.forEach((f) => (defaults[f.key] = f.default));

  const [dataset, setDataset]           = useState<Dataset>("deu");
  const [values, setValues]             = useState<Record<string, number>>(defaults);
  const [selectedModel, setSelectedModel] = useState<ModelId>("gb");
  const [result, setResult]             = useState<RiskResult | null>(null);
  const [loading, setLoading]           = useState(false);
  const [openInfo, setOpenInfo]         = useState<string | null>(null);

  const modelOptions  = dataset === "deu" ? DEU_MODEL_OPTIONS  : MIMIC_MODEL_OPTIONS;
  const predictors    = dataset === "deu" ? DEU_PREDICTORS     : MIMIC_PREDICTORS;
  const activeModel   = modelOptions.find((m) => m.id === selectedModel) ?? modelOptions[0];

  const handleDatasetSwitch = (ds: Dataset) => {
    setDataset(ds);
    setResult(null);
    const bestId = (ds === "deu" ? DEU_MODEL_OPTIONS : MIMIC_MODEL_OPTIONS).find((m) => m.best)!.id as ModelId;
    setSelectedModel(bestId);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    await new Promise((r) => setTimeout(r, 900));
    setResult(computeRisk(values, selectedModel, dataset));
    setLoading(false);
  };

  const handleReset = () => {
    setValues(defaults);
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-[var(--bg)] pt-24 pb-20">
      {/* Header */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 mb-12">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-cyan-400/20 bg-cyan-400/5 mb-4">
                <Zap className="w-3 h-3 text-cyan-400" />
                <span className="text-xs font-semibold text-cyan-400 tracking-wider uppercase">
                  {t.calculator.badge}
                </span>
              </div>
              <h1 className="text-3xl sm:text-4xl font-bold text-white mb-3">
                {t.calculator.title1}{" "}
                <span className="bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">
                  {t.calculator.title2}
                </span>
              </h1>
              <p className="text-slate-500 max-w-xl">{t.calculator.desc}</p>
            </div>

            {/* Dataset toggle */}
            <div className="flex-shrink-0">
              <div className="flex items-center gap-1 p-1 rounded-xl border border-white/[0.07] bg-white/[0.02]">
                {(["deu", "mimic"] as Dataset[]).map((ds) => {
                  const active = dataset === ds;
                  const label  = ds === "deu" ? t.calculator.datasetDeu : t.calculator.datasetMimic;
                  const sub    = ds === "deu" ? t.calculator.datasetDeuSub : t.calculator.datasetMimicSub;
                  return (
                    <button
                      key={ds}
                      type="button"
                      onClick={() => handleDatasetSwitch(ds)}
                      className="flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 text-left"
                      style={active ? { background: "rgba(34,211,238,0.10)" } : {}}
                    >
                      <Database className={`w-3.5 h-3.5 flex-shrink-0 ${active ? "text-cyan-400" : "text-slate-600"}`} />
                      <div>
                        <div className={`text-xs font-bold ${active ? "text-white" : "text-slate-600"}`}>{label}</div>
                        <div className="text-[10px] text-slate-700">{sub}</div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Main layout */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <form onSubmit={handleSubmit}>
          <div className="grid lg:grid-cols-[1fr_380px] gap-6">
            {/* ── Left: Inputs ── */}
            <div className="space-y-4">
              {/* Disclaimer */}
              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="flex items-start gap-3 p-4 rounded-xl border border-amber-400/15 bg-amber-400/5"
              >
                <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                <p className="text-xs text-amber-400/80 leading-relaxed">
                  <strong className="text-amber-400">{t.calculator.disclaimerBold}</strong>{" "}
                  {t.calculator.disclaimer}
                </p>
              </motion.div>

              {/* Model selector */}
              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 }}
                className="p-5 rounded-2xl border border-white/[0.07] bg-white/[0.02]"
              >
                <div className="flex items-center gap-2 mb-4">
                  <BarChart3 className="w-4 h-4 text-indigo-400" />
                  <span className="text-sm font-semibold text-white">{t.calculator.modelSelectTitle}</span>
                  <span className="ml-auto text-xs text-slate-600">{t.calculator.modelSelectSub}</span>
                </div>
                <AnimatePresence mode="wait">
                  <motion.div
                    key={dataset}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -6 }}
                    transition={{ duration: 0.2 }}
                    className="grid grid-cols-2 sm:grid-cols-4 gap-2"
                  >
                    {modelOptions.map((model) => {
                      const active = selectedModel === model.id;
                      return (
                        <button
                          key={model.id}
                          type="button"
                          onClick={() => { setSelectedModel(model.id as ModelId); setResult(null); }}
                          className="relative flex flex-col items-center gap-1.5 p-3 rounded-xl border transition-all duration-200 text-center"
                          style={active
                            ? { background: model.bg, borderColor: model.border }
                            : { background: "rgba(255,255,255,0.02)", borderColor: "rgba(255,255,255,0.07)" }}
                        >
                          {model.best && (
                            <div className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full flex items-center justify-center" style={{ background: model.color }}>
                              <Award className="w-2.5 h-2.5 text-slate-900" />
                            </div>
                          )}
                          <div
                            className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black"
                            style={{ background: active ? model.color : `${model.color}40` }}
                          >
                            <span style={{ color: active ? "#0f172a" : model.color }}>{model.short}</span>
                          </div>
                          <div className="text-[10px] font-semibold leading-tight" style={{ color: active ? model.color : "var(--sub)" }}>
                            {model.name}
                          </div>
                          <div
                            className="text-[9px] font-bold px-1.5 py-0.5 rounded-full"
                            style={active
                              ? { background: `${model.color}20`, color: model.color }
                              : { background: "rgba(255,255,255,0.04)", color: "var(--muted)" }}
                          >
                            AUC {model.auc}%
                          </div>
                        </button>
                      );
                    })}
                  </motion.div>
                </AnimatePresence>
              </motion.div>

              {/* Input grid */}
              <div className="grid sm:grid-cols-2 gap-4">
                {FIELDS.map((field, i) => (
                  <InputCard
                    key={field.key}
                    field={field}
                    value={values[field.key]}
                    delay={0.2 + i * 0.06}
                    onChange={(v) => setValues((prev) => ({ ...prev, [field.key]: v }))}
                    infoOpen={openInfo === field.key}
                    onToggleInfo={() => setOpenInfo((prev) => (prev === field.key ? null : field.key))}
                    normalRangeLabel={t.calculator.normalRange}
                  />
                ))}
              </div>

              {/* Submit / Reset */}
              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.55 }}
                className="flex gap-3"
              >
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 flex items-center justify-center gap-2 py-4 text-slate-900 font-bold rounded-xl text-sm transition-all duration-200 hover:scale-[1.01] disabled:opacity-60 disabled:cursor-not-allowed disabled:scale-100"
                  style={{
                    background: `linear-gradient(135deg, ${activeModel.color}, ${activeModel.color}cc)`,
                    boxShadow: loading ? "none" : `0 0 24px ${activeModel.color}40`,
                  }}
                >
                  {loading ? (
                    <>
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-4 h-4 border-2 border-slate-900/30 border-t-slate-900 rounded-full"
                      />
                      {t.calculator.analyzing}
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4" />
                      {t.calculator.calcBtn}
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={handleReset}
                  className="px-4 py-4 rounded-xl border border-white/10 bg-white/5 text-slate-400 hover:text-white hover:bg-white/10 transition-all"
                  title={t.calculator.resetTitle}
                >
                  <RotateCcw className="w-4 h-4" />
                </button>
              </motion.div>
            </div>

            {/* ── Right: Result panel ── */}
            <div className="space-y-4">
              <AnimatePresence mode="wait">
                {!result && !loading && (
                  <motion.div
                    key="empty"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="h-full min-h-[400px] rounded-2xl border border-white/[0.06] bg-white/[0.02] flex flex-col items-center justify-center gap-4 text-center p-8"
                  >
                    <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/[0.08] flex items-center justify-center">
                      <TrendingUp className="w-7 h-7 text-slate-600" />
                    </div>
                    <div>
                      <p className="text-slate-500 text-sm font-medium">{t.calculator.noPrediction}</p>
                      <p className="text-slate-700 text-xs mt-1">{t.calculator.noPredictionSub}</p>
                    </div>
                  </motion.div>
                )}

                {loading && (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0, scale: 0.97 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0 }}
                    className="h-full min-h-[400px] rounded-2xl border flex flex-col items-center justify-center gap-6 p-8"
                    style={{ borderColor: `${activeModel.color}30`, background: `${activeModel.color}05` }}
                  >
                    <div className="relative">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                        className="w-16 h-16 rounded-full border-2 border-transparent"
                        style={{ borderTopColor: activeModel.color, borderRightColor: `${activeModel.color}40` }}
                      />
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-xs font-black" style={{ color: activeModel.color }}>{activeModel.short}</span>
                      </div>
                    </div>
                    <div className="text-center">
                      <p className="text-white font-semibold text-sm">{t.calculator.runningAnalysis}</p>
                      <p className="text-slate-600 text-xs mt-1">{activeModel.name}…</p>
                    </div>
                  </motion.div>
                )}

                {result && !loading && (
                  <ResultPanel key="result" result={result} />
                )}
              </AnimatePresence>

              {/* Top predictors */}
              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="p-5 rounded-2xl border border-white/[0.06] bg-white/[0.02]"
              >
                <div className="flex items-center gap-2 mb-4">
                  <TrendingUp className="w-4 h-4 text-indigo-400" />
                  <span className="text-sm font-semibold text-white">{t.calculator.top5Title}</span>
                  {dataset === "mimic" && (
                    <span className="ml-auto text-[10px] text-indigo-400 border border-indigo-400/20 bg-indigo-400/5 px-1.5 py-0.5 rounded-full">MIMIC</span>
                  )}
                </div>
                <AnimatePresence mode="wait">
                  <motion.div
                    key={dataset}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    {predictors.map((p, i) => (
                      <div key={i} className="flex items-center gap-3 py-2.5 border-b border-white/[0.04] last:border-0">
                        <div className="w-6 h-6 rounded-full bg-white/5 flex items-center justify-center text-[10px] font-bold text-slate-500 flex-shrink-0">
                          {i + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs font-medium text-slate-300 truncate">{t.calculator.predictorNames[i]}</span>
                            <span className="text-[10px] text-slate-600 ml-2 flex-shrink-0">{t.calculator.predictorCats[i]}</span>
                          </div>
                          <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                            <div className="h-full rounded-full bg-gradient-to-r from-cyan-500/60 to-indigo-500/60" style={{ width: `${p.w}%` }} />
                          </div>
                        </div>
                      </div>
                    ))}
                  </motion.div>
                </AnimatePresence>
              </motion.div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

/* ─── Input card ─── */
function InputCard({
  field, value, delay, onChange, infoOpen, onToggleInfo, normalRangeLabel,
}: {
  field: Field; value: number; delay: number;
  onChange: (v: number) => void; infoOpen: boolean;
  onToggleInfo: () => void; normalRangeLabel: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] }}
      className="group p-5 rounded-2xl border border-white/[0.07] bg-white/[0.02] hover:border-white/10 transition-all duration-200"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `${field.color}20`, color: field.color }}>
            {field.icon}
          </div>
          <div>
            <div className="text-sm font-semibold text-white">{field.label}</div>
            <div className="text-xs text-slate-600">{field.unit}</div>
          </div>
        </div>
        <button type="button" onClick={onToggleInfo} className="text-slate-700 hover:text-slate-400 transition-colors">
          <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${infoOpen ? "rotate-180" : ""}`} />
        </button>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-700">{field.min}</span>
          <span className="text-xl font-bold tabular-nums" style={{ color: field.color }}>
            {value.toFixed(field.step < 1 ? 1 : 0)}
          </span>
          <span className="text-xs text-slate-700">{field.max}</span>
        </div>
        <input
          type="range" min={field.min} max={field.max} step={field.step} value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="w-full h-2 appearance-none cursor-pointer rounded-full"
          style={{
            background: `linear-gradient(to right, ${field.color} 0%, ${field.color} ${((value - field.min) / (field.max - field.min)) * 100}%, rgba(128,128,128,0.15) ${((value - field.min) / (field.max - field.min)) * 100}%, rgba(128,128,128,0.15) 100%)`,
            ["--thumb-color" as string]: field.color,
          }}
        />
        <input
          type="number" min={field.min} max={field.max} step={field.step} value={value}
          onChange={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v) && v >= field.min && v <= field.max) onChange(v); }}
          className="w-full bg-white/5 border border-white/[0.07] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-400/40 transition-colors text-center"
        />
      </div>

      <AnimatePresence>
        {infoOpen && field.normal !== "—" && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="mt-3 pt-3 border-t border-white/[0.05] flex items-start gap-2">
              <Info className="w-3.5 h-3.5 text-slate-600 flex-shrink-0 mt-0.5" />
              <p className="text-xs text-slate-600">
                {normalRangeLabel} <span className="text-slate-400 font-medium">{field.normal} {field.unit}</span>
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/* ─── Result panel ─── */
function ResultPanel({ result }: { result: RiskResult }) {
  const { t } = useTranslation();
  const cfg  = RISK_STATIC[result.riskLevel];
  const Icon = cfg.Icon;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96, y: 16 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="rounded-2xl border overflow-hidden"
      style={{ background: cfg.bg, borderColor: cfg.border, boxShadow: `0 0 40px ${cfg.glow}` }}
    >
      <div className="h-1 w-full" style={{ background: cfg.color }} />

      <div className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: `${cfg.color}20`, color: cfg.color }}>
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-black tracking-wider" style={{ color: cfg.color }}>
              {t.calculator.riskLabels[result.riskLevel]}
            </div>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className="text-[9px] font-black px-1.5 py-0.5 rounded" style={{ background: `${result.modelColor}20`, color: result.modelColor }}>
                {result.modelName.split(" ")[0]}
              </span>
              <span className="text-xs text-slate-600">{result.modelName} · AUC {result.modelAuc}%</span>
              <span className="text-[9px] text-slate-700 border border-white/[0.07] px-1.5 py-0.5 rounded">
                {result.dataset === "mimic" ? "MIMIC-III" : "DEU"}
              </span>
            </div>
          </div>
        </div>

        <div className="mb-6">
          <div className="flex items-baseline justify-between mb-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-widest">{t.calculator.mortalityProb}</span>
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-4xl font-extrabold tabular-nums"
              style={{ color: cfg.color }}
            >
              {result.probability.toFixed(1)}%
            </motion.span>
          </div>
          <div className="h-3 bg-white/5 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${result.probability}%` }}
              transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
              className="h-full rounded-full"
              style={{ background: `linear-gradient(90deg, ${cfg.color}60, ${cfg.color})`, boxShadow: `0 0 12px ${cfg.color}60` }}
            />
          </div>
          <div className="flex justify-between text-xs text-slate-700 mt-1">
            <span>0%</span><span>50%</span><span>100%</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-5">
          <div className="p-3 rounded-xl bg-white/5 text-center">
            <div className="text-xs text-slate-600 mb-1">{t.calculator.mortalityProbShort}</div>
            <div className="text-2xl font-bold" style={{ color: cfg.color }}>{result.probability.toFixed(1)}%</div>
          </div>
          <div className="p-3 rounded-xl bg-white/5 text-center">
            <div className="text-xs text-slate-600 mb-1">{t.calculator.survivalProbShort}</div>
            <div className="text-2xl font-bold text-emerald-400">{result.survivalProb.toFixed(1)}%</div>
          </div>
        </div>

        <div className="p-3 rounded-xl text-xs leading-relaxed" style={{ background: `${cfg.color}10`, color: cfg.color }}>
          {t.calculator.riskMessages[result.riskLevel]}
        </div>

        <div className="mt-4 flex items-start gap-2 p-3 rounded-xl bg-white/[0.03] border border-white/[0.05]">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400/70 flex-shrink-0 mt-0.5" />
          <p className="text-[11px] text-slate-700 leading-relaxed">{t.calculator.resultDisclaimer}</p>
        </div>
      </div>
    </motion.div>
  );
}
