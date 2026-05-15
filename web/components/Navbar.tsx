"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, Menu, X, Zap } from "lucide-react";
import { cn } from "@/lib/utils";
import ThemeToggle from "@/components/ThemeToggle";

const links = [
  { href: "/", label: "Home" },
  { href: "/calculator", label: "Calculator" },
  { href: "/models", label: "Models" },
  { href: "/research", label: "Research" },
];

export default function Navbar() {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <motion.header
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className={cn(
          "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
          scrolled ? "backdrop-blur-xl border-b shadow-[0_1px_40px_rgba(0,0,0,0.15)]" : "bg-transparent"
        )}
        style={scrolled ? { background: "var(--nav-bg)", borderColor: "var(--border)" } : undefined}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative w-8 h-8">
              <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-cyan-400 to-indigo-500 opacity-20 group-hover:opacity-40 blur-sm transition-opacity" />
              <div className="relative w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-indigo-500 flex items-center justify-center">
                <Activity className="w-4 h-4 text-white" strokeWidth={2.5} />
              </div>
            </div>
            <div className="leading-none">
              <span className="text-sm font-bold tracking-wide" style={{ color: "var(--text)" }}>AKI</span>
              <span className="text-sm font-bold text-cyan-500 tracking-wide"> Predict</span>
              <div className="text-[10px] font-medium tracking-wider" style={{ color: "var(--muted)" }}>DEU HOSPITAL · RESEARCH</div>
            </div>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1">
            {links.map((link) => {
              const active = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    "relative px-4 py-2 text-sm font-medium rounded-lg transition-colors duration-200",
                    active ? "text-cyan-500" : "hover:text-cyan-500"
                  )}
                  style={!active ? { color: "var(--sub)" } : undefined}
                >
                  {active && (
                    <motion.div
                      layoutId="nav-pill"
                      className="absolute inset-0 rounded-lg border border-cyan-400/20"
                      style={{ background: "rgba(6,182,212,0.08)" }}
                      transition={{ type: "spring", bounce: 0.25, duration: 0.4 }}
                    />
                  )}
                  <span className="relative">{link.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Right: theme toggle + CTA */}
          <div className="hidden md:flex items-center gap-3">
            <ThemeToggle
              className="p-2 rounded-lg transition-colors duration-200 hover:bg-black/5 dark:hover:bg-white/5"
              style={{ color: "var(--sub)" } as React.CSSProperties}
            />
            <Link
              href="/calculator"
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-cyan-400 text-slate-900 text-sm font-bold rounded-lg hover:shadow-[0_0_20px_rgba(34,211,238,0.4)] transition-all duration-200 hover:scale-[1.02]"
            >
              <Zap className="w-3.5 h-3.5" />
              Calculate Risk
            </Link>
          </div>

          {/* Mobile: toggle + hamburger */}
          <div className="md:hidden flex items-center gap-1">
            <ThemeToggle
              className="p-2 rounded-lg transition-colors"
              style={{ color: "var(--sub)" } as React.CSSProperties}
            />
            <button
              onClick={() => setMobileOpen((v) => !v)}
              className="p-2 rounded-lg transition-colors"
              style={{ color: "var(--sub)" }}
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </motion.header>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="fixed top-16 inset-x-0 z-40 backdrop-blur-xl border-b md:hidden"
            style={{ background: "var(--mobile-nav-bg)", borderColor: "var(--border)" }}
          >
            <nav className="flex flex-col gap-1 p-4">
              {links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className={cn(
                    "px-4 py-3 text-sm font-medium rounded-xl transition-colors",
                    pathname === link.href
                      ? "text-cyan-500 border border-cyan-400/20"
                      : "hover:text-cyan-500"
                  )}
                  style={{
                    ...(pathname === link.href
                      ? { background: "rgba(6,182,212,0.08)" }
                      : { color: "var(--sub)" }),
                  }}
                >
                  {link.label}
                </Link>
              ))}
              <Link
                href="/calculator"
                onClick={() => setMobileOpen(false)}
                className="mt-2 px-4 py-3 text-sm font-bold rounded-xl bg-gradient-to-r from-cyan-500 to-cyan-400 text-slate-900 text-center"
              >
                Calculate Risk
              </Link>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
