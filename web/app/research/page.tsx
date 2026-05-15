"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import {
  GitBranch, Database, Microscope, Brain, FlaskConical,
  BarChart3, TrendingUp, CheckCircle, Shield, Server,
  Activity,
} from "lucide-react";
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

const PIPELINE_ICONS = [
  { icon: <Database className="w-5 h-5" />, color: "#22d3ee" },
  { icon: <Microscope className="w-5 h-5" />, color: "#818cf8" },
  { icon: <FlaskConical className="w-5 h-5" />, color: "#fb923c" },
  { icon: <GitBranch className="w-5 h-5" />, color: "#34d399" },
  { icon: <Brain className="w-5 h-5" />, color: "#f472b6" },
  { icon: <TrendingUp className="w-5 h-5" />, color: "#fbbf24" },
  { icon: <BarChart3 className="w-5 h-5" />, color: "#22d3ee" },
];

const AKI_COLORS = ["#22d3ee", "#818cf8", "#34d399"];

const STATS_VALUES = ["2,230", "80% / 20%", "30+", "15", "~72%", "~28%", "5", "42"];

const TECH_ITEMS = [
  { name: "Python 3.9+", icon: "🐍" },
  { name: "scikit-learn", icon: "🔬" },
  { name: "miceforest", icon: "🧬" },
  { name: "PostgreSQL", icon: "🗄️" },
  { name: "pandas / NumPy", icon: "📊" },
  { name: "matplotlib", icon: "📈" },
  { name: "joblib", icon: "💾" },
  { name: "Streamlit", icon: "⚡" },
];

export default function ResearchPage() {
  const { t } = useTranslation();

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
              {t.research.badge}
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-3">
            {t.research.title1}{" "}
            <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              {t.research.title2}
            </span>
          </h1>
          <p className="text-slate-500 max-w-xl">
            {t.research.desc}
          </p>
        </motion.div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 space-y-8">
        {/* Hero stats */}
        <FadeUp>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {STATS_VALUES.map((value, i) => (
              <div
                key={i}
                className="p-4 rounded-xl border border-white/[0.07] bg-white/[0.02] text-center"
              >
                <div className="text-lg font-bold text-white mb-1">{value}</div>
                <div className="text-xs text-slate-600">{t.research.statsLabels[i]}</div>
              </div>
            ))}
          </div>
        </FadeUp>

        {/* What is AKI */}
        <FadeUp delay={0.05}>
          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.02] p-6">
            <div className="flex items-center gap-2 mb-5">
              <Activity className="w-4 h-4 text-cyan-400" />
              <span className="text-sm font-semibold text-white">{t.research.akiTitle}</span>
            </div>
            <div className="grid sm:grid-cols-3 gap-4">
              {t.research.akiCards.map((item, i) => (
                <div
                  key={item.title}
                  className="p-4 rounded-xl border border-white/[0.05] bg-white/[0.02]"
                >
                  <div className="text-sm font-bold mb-2" style={{ color: AKI_COLORS[i] }}>
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
              <span className="text-sm font-semibold text-white">{t.research.pipelineTitle}</span>
            </div>
            <div className="relative">
              <div className="absolute left-5 top-5 bottom-5 w-px bg-white/[0.06]" />
              <div className="space-y-1">
                {t.research.pipeline.map((step, i) => (
                  <PipelineStep
                    key={step.title}
                    step={step}
                    index={i}
                    delay={i * 0.06}
                    iconData={PIPELINE_ICONS[i]}
                  />
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
              <span className="text-sm font-semibold text-white">{t.research.techTitle}</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {TECH_ITEMS.map((item, i) => (
                <div
                  key={item.name}
                  className="flex items-center gap-3 p-3 rounded-xl border border-white/[0.05] bg-white/[0.02] hover:border-white/[0.09] transition-colors"
                >
                  <span className="text-xl">{item.icon}</span>
                  <div>
                    <div className="text-xs font-semibold text-white">{item.name}</div>
                    <div className="text-[10px] text-slate-600">{t.research.techRoles[i]}</div>
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
                <div className="text-sm font-bold text-amber-400 mb-2">{t.research.disclaimerTitle}</div>
                <p className="text-xs text-amber-400/70 leading-relaxed">
                  {t.research.disclaimerText}
                </p>
                <div className="flex flex-wrap gap-3 mt-3">
                  {t.research.disclaimerTags.map((tag) => (
                    <div
                      key={tag}
                      className="flex items-center gap-1 text-[10px] text-amber-400/60"
                    >
                      <CheckCircle className="w-3 h-3" />
                      {tag}
                    </div>
                  ))}
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
  iconData,
}: {
  step: { title: string; desc: string; detail: string };
  index: number;
  delay: number;
  iconData: { icon: React.ReactNode; color: string };
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
      <div
        className="absolute left-0 top-0 w-10 h-10 rounded-xl flex items-center justify-center text-white flex-shrink-0 z-10"
        style={{ background: `${iconData.color}18`, color: iconData.color, border: `1px solid ${iconData.color}30` }}
      >
        {iconData.icon}
      </div>

      <div className="flex-1 min-w-0 pt-2">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-semibold text-white">{step.title}</span>
          <span className="text-xs text-slate-600 truncate">{step.desc}</span>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed group-hover:text-slate-500 transition-colors">
          {step.detail}
        </p>
      </div>

      <div className="flex-shrink-0 text-[10px] font-bold text-slate-700 pt-2.5">
        {String(index + 1).padStart(2, "0")}
      </div>
    </motion.div>
  );
}
