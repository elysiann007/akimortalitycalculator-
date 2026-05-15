"use client";

import { useRef } from "react";
import Link from "next/link";
import { motion, useInView } from "framer-motion";
import {
  Activity, Brain, BarChart3, Zap, ArrowRight,
  Shield, FlaskConical, TrendingUp, ChevronRight,
  HeartPulse, Microscope, Database, GitBranch,
} from "lucide-react";
import ParticleField from "@/components/ParticleField";
import CountUp from "@/components/CountUp";
import { useTranslation } from "@/lib/i18n";

/* ─── Reusable fade-up wrapper ─── */
function FadeUp({
  children,
  delay = 0,
  className = "",
}: {
  children: React.ReactNode;
  delay?: number;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 32 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.65, delay, ease: [0.16, 1, 0.3, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ─── Stats data ─── */
const STATS_VALUES = [
  { value: 2230, suffix: "+" },
  { value: 4, suffix: "" },
  { value: 91, suffix: "%" },
  { value: 15, suffix: "" },
];

/* ─── Feature icon/style data (text from translations) ─── */
const FEATURE_STYLES = [
  { icon: <Brain className="w-5 h-5" />, color: "from-cyan-400 to-blue-500", bg: "rgba(34,211,238,0.08)", border: "rgba(34,211,238,0.18)" },
  { icon: <FlaskConical className="w-5 h-5" />, color: "from-indigo-400 to-purple-500", bg: "rgba(99,102,241,0.08)", border: "rgba(99,102,241,0.18)" },
  { icon: <Zap className="w-5 h-5" />, color: "from-amber-400 to-orange-500", bg: "rgba(251,191,36,0.08)", border: "rgba(251,191,36,0.18)" },
  { icon: <Shield className="w-5 h-5" />, color: "from-emerald-400 to-teal-500", bg: "rgba(16,185,129,0.08)", border: "rgba(16,185,129,0.18)" },
  { icon: <BarChart3 className="w-5 h-5" />, color: "from-rose-400 to-pink-500", bg: "rgba(244,63,94,0.08)", border: "rgba(244,63,94,0.18)" },
  { icon: <Database className="w-5 h-5" />, color: "from-violet-400 to-fuchsia-500", bg: "rgba(139,92,246,0.08)", border: "rgba(139,92,246,0.18)" },
];

/* ─── Pipeline icon data ─── */
const PIPELINE_ICONS = [
  <Database className="w-4 h-4" key="db" />,
  <Microscope className="w-4 h-4" key="mi" />,
  <GitBranch className="w-4 h-4" key="gb" />,
  <FlaskConical className="w-4 h-4" key="fl" />,
  <TrendingUp className="w-4 h-4" key="tu" />,
  <BarChart3 className="w-4 h-4" key="bc" />,
];

/* ─── Models ─── */
const MODELS = [
  { name: "Gradient Boosting", short: "GB", auc: 91.0, color: "#22d3ee", glow: "rgba(34,211,238,0.3)" },
  { name: "Random Forest",     short: "RF", auc: 89.2, color: "#818cf8", glow: "rgba(129,140,248,0.3)" },
  { name: "Neural Network",    short: "ANN", auc: 87.8, color: "#fb923c", glow: "rgba(251,146,60,0.3)" },
  { name: "Logistic Regression", short: "LR", auc: 86.3, color: "#34d399", glow: "rgba(52,211,153,0.3)" },
];

export default function HomePage() {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-[var(--bg)]">
      {/* ═══════════════════════════ HERO ═══════════════════════════ */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
        <ParticleField />

        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-cyan-400/5 blur-[120px]" />
          <div className="absolute bottom-1/3 right-1/4 w-80 h-80 rounded-full bg-indigo-500/8 blur-[100px]" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-cyan-400/3 blur-[150px]" />
        </div>

        <div
          className="absolute inset-0 pointer-events-none opacity-[0.03]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(34,211,238,1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(34,211,238,1) 1px, transparent 1px)
            `,
            backgroundSize: "60px 60px",
          }}
        />

        <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="inline-flex items-center gap-2 mb-8"
          >
            <div className="flex items-center gap-2 px-4 py-2 rounded-full border border-cyan-400/25 bg-cyan-400/5 backdrop-blur-sm">
              <span className="flex h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
              <span className="text-xs font-semibold text-cyan-400 tracking-widest uppercase">
                {t.home.heroBadge}
              </span>
            </div>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
            className="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight leading-[1.05] mb-6"
          >
            <span className="text-white">{t.home.heroTitle1}</span>
            <br />
            <span className="bg-gradient-to-r from-cyan-400 via-cyan-300 to-indigo-400 bg-clip-text text-transparent">
              {t.home.heroTitle2}
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="max-w-2xl mx-auto text-lg text-slate-400 leading-relaxed mb-10"
          >
            {t.home.heroSub1}{" "}
            <span className="text-white font-semibold">{t.home.heroSubBold}</span>{" "}
            {t.home.heroSub2}
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.45, ease: [0.16, 1, 0.3, 1] }}
            className="flex flex-wrap items-center justify-center gap-4"
          >
            <Link
              href="/calculator"
              className="group flex items-center gap-2 px-6 py-3.5 bg-gradient-to-r from-cyan-500 to-cyan-400 text-slate-900 font-bold rounded-xl text-sm hover:shadow-[0_0_30px_rgba(34,211,238,0.5)] transition-all duration-300 hover:scale-[1.03]"
            >
              <Zap className="w-4 h-4" />
              {t.home.heroCta1}
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <Link
              href="/models"
              className="flex items-center gap-2 px-6 py-3.5 border border-white/10 bg-white/5 text-white font-semibold rounded-xl text-sm hover:bg-white/10 hover:border-white/20 transition-all duration-200 backdrop-blur-sm"
            >
              <BarChart3 className="w-4 h-4 text-slate-400" />
              {t.home.heroCta2}
            </Link>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.7 }}
            className="mt-8 text-xs text-slate-600 flex items-center justify-center gap-2"
          >
            <Shield className="w-3 h-3" />
            {t.home.heroDisclaimer}
          </motion.p>
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
        >
          <span className="text-xs text-slate-600 tracking-widest uppercase">{t.home.scroll}</span>
          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
            className="w-px h-8 bg-gradient-to-b from-slate-600 to-transparent"
          />
        </motion.div>
      </section>

      {/* ═══════════════════════════ STATS ═══════════════════════════ */}
      <section className="relative py-24 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[var(--bg)] via-[var(--bg2)] to-[var(--bg)]" />
        <div className="relative max-w-6xl mx-auto px-4 sm:px-6">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {STATS_VALUES.map((s, i) => (
              <FadeUp key={i} delay={i * 0.1}>
                <div className="relative group p-6 rounded-2xl border border-white/[0.07] bg-white/[0.03] hover:border-cyan-400/20 hover:bg-cyan-400/[0.03] transition-all duration-300 text-center">
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-cyan-400/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                  <div className="text-4xl font-extrabold text-white mb-1 tracking-tight">
                    <CountUp end={s.value} suffix={s.suffix} />
                  </div>
                  <div className="text-sm font-semibold text-slate-300 mb-1">{t.home.statLabels[i]}</div>
                  <div className="text-xs text-slate-600">{t.home.statSublabels[i]}</div>
                </div>
              </FadeUp>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════ MODELS BAR ═══════════════════════════ */}
      <section className="relative py-24">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <FadeUp className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-indigo-400/20 bg-indigo-400/5 mb-4">
              <TrendingUp className="w-3 h-3 text-indigo-400" />
              <span className="text-xs font-semibold text-indigo-400 tracking-wider uppercase">{t.home.modelsBadge}</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              {t.home.modelsTitle1}{" "}
              <span className="bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">
                {t.home.modelsTitle2}
              </span>
            </h2>
            <p className="text-slate-500 max-w-xl mx-auto">
              {t.home.modelsDesc}
            </p>
          </FadeUp>

          <div className="grid sm:grid-cols-2 gap-4">
            {MODELS.map((m, i) => (
              <ModelBar key={m.name} model={m} delay={i * 0.12} aucLabel={t.home.aucLabel} />
            ))}
          </div>

          <FadeUp delay={0.5} className="mt-6 text-center">
            <Link
              href="/models"
              className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-cyan-400 transition-colors"
            >
              {t.home.modelsLink}
              <ChevronRight className="w-4 h-4" />
            </Link>
          </FadeUp>
        </div>
      </section>

      {/* ═══════════════════════════ FEATURES ═══════════════════════════ */}
      <section className="relative py-24 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-indigo-950/10 to-transparent" />
        <div className="relative max-w-6xl mx-auto px-4 sm:px-6">
          <FadeUp className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-cyan-400/20 bg-cyan-400/5 mb-4">
              <Activity className="w-3 h-3 text-cyan-400" />
              <span className="text-xs font-semibold text-cyan-400 tracking-wider uppercase">{t.home.featuresBadge}</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              {t.home.featuresTitle}
            </h2>
            <p className="text-slate-500 max-w-xl mx-auto">
              {t.home.featuresDesc}
            </p>
          </FadeUp>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {FEATURE_STYLES.map((f, i) => (
              <FadeUp key={i} delay={i * 0.08}>
                <div
                  className="group p-6 rounded-2xl border transition-all duration-300 hover:-translate-y-1"
                  style={{ background: f.bg, borderColor: f.border }}
                >
                  <div
                    className={`w-10 h-10 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center text-white mb-4 shadow-lg`}
                  >
                    {f.icon}
                  </div>
                  <h3 className="text-white font-semibold mb-2 text-sm">{t.home.featureTitles[i]}</h3>
                  <p className="text-slate-500 text-sm leading-relaxed">{t.home.featureDescs[i]}</p>
                </div>
              </FadeUp>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════════════════════ PIPELINE ═══════════════════════════ */}
      <section className="relative py-24">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <FadeUp>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-emerald-400/20 bg-emerald-400/5 mb-6">
                <GitBranch className="w-3 h-3 text-emerald-400" />
                <span className="text-xs font-semibold text-emerald-400 tracking-wider uppercase">{t.home.pipelineBadge}</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                {t.home.pipelineTitle1}{" "}
                <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                  {t.home.pipelineTitle2}
                </span>
              </h2>
              <p className="text-slate-500 leading-relaxed mb-8">
                {t.home.pipelineDesc}
              </p>
              <Link
                href="/research"
                className="inline-flex items-center gap-2 px-5 py-3 bg-white/5 border border-white/10 text-white font-semibold rounded-xl text-sm hover:bg-white/10 transition-all"
              >
                {t.home.pipelineLink}
                <ArrowRight className="w-4 h-4" />
              </Link>
            </FadeUp>

            <div className="space-y-3">
              {t.home.pipelineTitles.map((title, i) => (
                <FadeUp key={title} delay={i * 0.07}>
                  <div className="flex items-center gap-4 p-4 rounded-xl border border-white/[0.06] bg-white/[0.02] hover:border-white/10 transition-colors">
                    <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-white/5 border border-white/[0.08] flex items-center justify-center text-slate-400">
                      {PIPELINE_ICONS[i]}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-white">{title}</div>
                      <div className="text-xs text-slate-600 mt-0.5">{t.home.pipelineDescs[i]}</div>
                    </div>
                    <div className="flex-shrink-0 w-6 h-6 rounded-full border border-white/[0.06] flex items-center justify-center">
                      <span className="text-[10px] font-bold text-slate-600">{i + 1}</span>
                    </div>
                  </div>
                </FadeUp>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════ CTA BANNER ═══════════════════════════ */}
      <section className="relative py-24 overflow-hidden">
        <FadeUp className="max-w-4xl mx-auto px-4 sm:px-6 text-center">
          <div className="relative rounded-3xl border border-cyan-400/15 overflow-hidden p-12">
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-400/5 via-transparent to-indigo-500/5" />
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-px h-20 bg-gradient-to-b from-cyan-400/40 to-transparent" />

            <div className="relative z-10">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-400/20 to-indigo-500/20 border border-cyan-400/20 flex items-center justify-center mx-auto mb-6">
                <HeartPulse className="w-7 h-7 text-cyan-400" />
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                {t.home.ctaTitle}
              </h2>
              <p className="text-slate-500 max-w-lg mx-auto mb-8 leading-relaxed">
                {t.home.ctaDesc}
              </p>
              <Link
                href="/calculator"
                className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-cyan-500 to-cyan-400 text-slate-900 font-bold rounded-xl hover:shadow-[0_0_40px_rgba(34,211,238,0.5)] transition-all duration-300 hover:scale-[1.02]"
              >
                <Zap className="w-4 h-4" />
                {t.home.ctaButton}
                <ArrowRight className="w-4 h-4" />
              </Link>
              <p className="mt-4 text-xs text-slate-700">
                {t.home.ctaDisclaimer}
              </p>
            </div>
          </div>
        </FadeUp>
      </section>

      {/* ═══════════════════════════ FOOTER ═══════════════════════════ */}
      <footer className="border-t py-10" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-700">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400/40" />
            <span>{t.home.footerLeft}</span>
          </div>
          <div>{t.home.footerRight}</div>
        </div>
      </footer>
    </div>
  );
}

/* ─── Model bar component ─── */
function ModelBar({
  model,
  delay,
  aucLabel,
}: {
  model: (typeof MODELS)[0];
  delay: number;
  aucLabel: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-40px" });

  return (
    <div
      ref={ref}
      className="p-5 rounded-2xl border border-white/[0.06] bg-white/[0.02] hover:border-white/10 transition-all duration-300 group"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center text-xs font-black text-slate-900"
            style={{ background: model.color }}
          >
            {model.short}
          </div>
          <div>
            <div className="text-sm font-semibold text-white">{model.name}</div>
            <div className="text-xs text-slate-600">{aucLabel}</div>
          </div>
        </div>
        <div className="text-2xl font-extrabold" style={{ color: model.color }}>
          <CountUp end={model.auc} decimals={1} suffix="%" />
        </div>
      </div>
      <div className="h-2 bg-white/5 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={inView ? { width: `${model.auc}%` } : {}}
          transition={{ duration: 1.2, delay, ease: [0.16, 1, 0.3, 1] }}
          className="h-full rounded-full"
          style={{
            background: `linear-gradient(90deg, ${model.color}88, ${model.color})`,
            boxShadow: `0 0 12px ${model.glow}`,
          }}
        />
      </div>
    </div>
  );
}
