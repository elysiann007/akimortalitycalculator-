"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import {
  BarChart3, TrendingUp, Activity, Award,
  CheckCircle, ChevronRight,
} from "lucide-react";
import CountUp from "@/components/CountUp";
import Link from "next/link";
import { useTranslation } from "@/lib/i18n";

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

const MODELS_STATIC = [
  { name: "Gradient Boosting", short: "GB", color: "#22d3ee", glow: "rgba(34,211,238,0.25)", bg: "rgba(34,211,238,0.06)", border: "rgba(34,211,238,0.18)", best: true,  metrics: { auc: 91.0, ca: 85.2, f1: 83.7, precision: 86.1, recall: 81.5, mcc: 0.681 } },
  { name: "Random Forest",     short: "RF",  color: "#818cf8", glow: "rgba(129,140,248,0.25)", bg: "rgba(129,140,248,0.06)", border: "rgba(129,140,248,0.18)", best: false, metrics: { auc: 89.2, ca: 83.4, f1: 81.2, precision: 84.5, recall: 78.1, mcc: 0.649 } },
  { name: "Neural Network (ANN)", short: "ANN", color: "#fb923c", glow: "rgba(251,146,60,0.25)", bg: "rgba(251,146,60,0.06)", border: "rgba(251,146,60,0.18)", best: false, metrics: { auc: 87.8, ca: 82.1, f1: 79.8, precision: 82.3, recall: 77.5, mcc: 0.628 } },
  { name: "Logistic Regression", short: "LR", color: "#34d399", glow: "rgba(52,211,153,0.25)", bg: "rgba(52,211,153,0.06)", border: "rgba(52,211,153,0.18)", best: false, metrics: { auc: 86.3, ca: 81.0, f1: 78.4, precision: 80.9, recall: 76.0, mcc: 0.608 } },
];

const TOP15 = [
  { name: "WBC / Leukocytes",  cat: "Inflammation",  score: 88, color: "#22d3ee" },
  { name: "AST",               cat: "Hepatic",        score: 81, color: "#818cf8" },
  { name: "Creatinine",        cat: "Renal Func.",    score: 79, color: "#22d3ee" },
  { name: "Platelet Count",    cat: "Coagulation",    score: 73, color: "#fb923c" },
  { name: "INR Plasma",        cat: "Coagulation",    score: 68, color: "#f472b6" },
  { name: "Total Bilirubin",   cat: "Hepatic",        score: 65, color: "#818cf8" },
  { name: "APTT Plasma",       cat: "Coagulation",    score: 60, color: "#f472b6" },
  { name: "eGFR CKD-EPI",      cat: "Renal Func.",    score: 58, color: "#22d3ee" },
  { name: "Age",               cat: "Demographic",    score: 53, color: "#34d399" },
  { name: "Glucose",           cat: "Metabolic",      score: 48, color: "#fbbf24" },
  { name: "Sodium",            cat: "Electrolyte",    score: 44, color: "#a78bfa" },
  { name: "PT Plasma",         cat: "Coagulation",    score: 41, color: "#f472b6" },
  { name: "Calcium",           cat: "Electrolyte",    score: 38, color: "#a78bfa" },
  { name: "Chloride",          cat: "Electrolyte",    score: 35, color: "#a78bfa" },
  { name: "BUN",               cat: "Renal Func.",    score: 32, color: "#22d3ee" },
];

const METRIC_KEYS = ["auc", "ca", "f1", "precision", "recall", "mcc"] as const;

export default function ModelsPage() {
  const { t } = useTranslation();

  const MODELS = MODELS_STATIC.map((m, i) => ({
    ...m,
    description: t.models.modelDescriptions[i],
  }));

  return (
    <div className="min-h-screen bg-[var(--bg)] pt-24 pb-20">
      {/* Header */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 mb-12">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-indigo-400/20 bg-indigo-400/5 mb-4">
            <BarChart3 className="w-3 h-3 text-indigo-400" />
            <span className="text-xs font-semibold text-indigo-400 tracking-wider uppercase">
              {t.models.badge}
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-3">
            {t.models.title1}{" "}
            <span className="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
              {t.models.title2}
            </span>
          </h1>
          <p className="text-slate-500 max-w-xl">
            {t.models.desc}
          </p>
        </motion.div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 space-y-8">
        {/* Model cards */}
        <div className="grid sm:grid-cols-2 gap-4">
          {MODELS.map((m, i) => (
            <ModelCard key={m.name} model={m} delay={i * 0.1} bestLabel={t.models.bestLabel} aucLabel={t.models.aucLabel} metricLabels={t.models.metricLabels} />
          ))}
        </div>

        {/* Metrics table */}
        <FadeUp>
          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.02] overflow-hidden">
            <div className="flex items-center justify-between p-5 border-b border-white/[0.06]">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-cyan-400" />
                <span className="text-sm font-semibold text-white">{t.models.tableTitle}</span>
              </div>
              <span className="text-xs text-slate-600">{t.models.threshold}</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/[0.06]">
                    <th className="text-left px-5 py-3 text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      {t.models.modelCol}
                    </th>
                    {METRIC_KEYS.map((k) => (
                      <th
                        key={k}
                        className="text-right px-4 py-3 text-xs font-semibold text-slate-600 uppercase tracking-wider"
                      >
                        {t.models.metricLabels[k]}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {MODELS.map((m) => (
                    <tr
                      key={m.name}
                      className="border-b border-white/[0.04] last:border-0 hover:bg-white/[0.02] transition-colors"
                    >
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-2">
                          <div
                            className="w-7 h-7 rounded-lg flex items-center justify-center text-[11px] font-black text-slate-900 flex-shrink-0"
                            style={{ background: m.color }}
                          >
                            {m.short}
                          </div>
                          <div>
                            <div className="text-white font-medium text-xs">{m.name}</div>
                            {m.best && (
                              <div className="text-[10px] text-amber-400 flex items-center gap-1">
                                <Award className="w-2.5 h-2.5" /> {t.models.bestLabel}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      {METRIC_KEYS.map((k) => {
                        const v = m.metrics[k];
                        return (
                          <td key={k} className="text-right px-4 py-4">
                            <span
                              className={`font-semibold tabular-nums text-sm ${
                                m.best && k === "auc" ? "text-cyan-400" : "text-slate-300"
                              }`}
                            >
                              {k === "mcc" ? v.toFixed(3) : `${v}%`}
                            </span>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </FadeUp>

        {/* Feature importance */}
        <FadeUp delay={0.1}>
          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.02] p-6">
            <div className="flex items-center gap-2 mb-6">
              <TrendingUp className="w-4 h-4 text-indigo-400" />
              <span className="text-sm font-semibold text-white">{t.models.featuresTitle}</span>
              <span className="ml-auto text-xs text-slate-600">{t.models.featuresSub}</span>
            </div>
            <div className="space-y-3">
              {TOP15.map((f, i) => (
                <FeatureBar key={f.name} feature={f} rank={i + 1} delay={i * 0.04} catLabel={t.models.cats[f.cat as keyof typeof t.models.cats] ?? f.cat} />
              ))}
            </div>
          </div>
        </FadeUp>

        {/* Key findings */}
        <FadeUp delay={0.15}>
          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.02] p-6">
            <div className="flex items-center gap-2 mb-5">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span className="text-sm font-semibold text-white">{t.models.findingsTitle}</span>
            </div>
            <div className="grid sm:grid-cols-2 gap-3">
              {t.models.findings.map((finding, i) => (
                <div
                  key={i}
                  className="flex items-start gap-3 p-4 rounded-xl border border-white/[0.05] bg-white/[0.02]"
                >
                  <div className="w-5 h-5 rounded-full bg-emerald-400/10 border border-emerald-400/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-[10px] font-bold text-emerald-400">{i + 1}</span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">{finding}</p>
                </div>
              ))}
            </div>
          </div>
        </FadeUp>

        {/* CTA */}
        <FadeUp delay={0.2} className="text-center pt-4">
          <Link
            href="/calculator"
            className="inline-flex items-center gap-2 px-6 py-3.5 bg-gradient-to-r from-cyan-500 to-cyan-400 text-slate-900 font-bold rounded-xl text-sm hover:shadow-[0_0_30px_rgba(34,211,238,0.4)] transition-all duration-200"
          >
            {t.models.ctaButton}
            <ChevronRight className="w-4 h-4" />
          </Link>
        </FadeUp>
      </div>
    </div>
  );
}

function ModelCard({
  model,
  delay,
  bestLabel,
  aucLabel,
  metricLabels,
}: {
  model: (typeof MODELS_STATIC)[0] & { description: string };
  delay: number;
  bestLabel: string;
  aucLabel: string;
  metricLabels: Record<string, string>;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-40px" });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 24 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.55, delay, ease: [0.16, 1, 0.3, 1] }}
      className="relative p-6 rounded-2xl border transition-all duration-300 hover:-translate-y-0.5"
      style={{
        background: model.bg,
        borderColor: model.border,
        boxShadow: model.best ? `0 0 30px ${model.glow}` : "none",
      }}
    >
      {model.best && (
        <div
          className="absolute top-3 right-3 flex items-center gap-1 px-2 py-1 rounded-full text-[10px] font-black text-slate-900 tracking-wider"
          style={{ background: model.color }}
        >
          <Award className="w-3 h-3" /> {bestLabel.toUpperCase()}
        </div>
      )}

      <div className="flex items-center gap-3 mb-5">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center text-xs font-black text-slate-900"
          style={{ background: model.color }}
        >
          {model.short}
        </div>
        <div>
          <div className="text-white font-bold text-sm">{model.name}</div>
          <div className="text-xs text-slate-600 mt-0.5">{model.description}</div>
        </div>
      </div>

      <div className="flex items-baseline gap-2 mb-4">
        <span className="text-4xl font-extrabold" style={{ color: model.color }}>
          <CountUp end={model.metrics.auc} decimals={1} suffix="%" />
        </span>
        <span className="text-xs text-slate-600">{aucLabel}</span>
      </div>

      <div className="grid grid-cols-3 gap-2">
        {(["ca", "f1", "precision"] as const).map((k) => (
          <div key={k} className="text-center p-2 rounded-lg bg-white/5">
            <div className="text-sm font-bold text-white">
              {model.metrics[k].toFixed(1)}%
            </div>
            <div className="text-[10px] text-slate-600">{metricLabels[k]}</div>
          </div>
        ))}
      </div>

      <div className="mt-4">
        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={inView ? { width: `${model.metrics.auc}%` } : {}}
            transition={{ duration: 1.2, delay: delay + 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="h-full rounded-full"
            style={{ background: model.color, boxShadow: `0 0 8px ${model.glow}` }}
          />
        </div>
      </div>
    </motion.div>
  );
}

function FeatureBar({
  feature,
  rank,
  delay,
  catLabel,
}: {
  feature: (typeof TOP15)[0];
  rank: number;
  delay: number;
  catLabel: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-20px" });

  return (
    <div ref={ref} className="flex items-center gap-3">
      <div className="w-6 h-6 rounded-full bg-white/5 flex items-center justify-center text-[10px] font-bold text-slate-600 flex-shrink-0">
        {rank}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-slate-300">{feature.name}</span>
            <span className="text-[10px] text-slate-700 px-1.5 py-0.5 rounded border border-white/[0.05] bg-white/[0.02]">
              {catLabel}
            </span>
          </div>
          <span className="text-xs font-bold tabular-nums" style={{ color: feature.color }}>
            {feature.score}
          </span>
        </div>
        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={inView ? { width: `${feature.score}%` } : {}}
            transition={{ duration: 0.8, delay, ease: [0.16, 1, 0.3, 1] }}
            className="h-full rounded-full"
            style={{ background: `linear-gradient(90deg, ${feature.color}60, ${feature.color})` }}
          />
        </div>
      </div>
    </div>
  );
}
