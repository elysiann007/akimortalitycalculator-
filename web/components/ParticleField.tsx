"use client";

import { useEffect, useRef } from "react";

interface Particle {
  x: number; y: number;
  vx: number; vy: number;
  r: number;
  opacity: number;
  pulse: number;
  pulseSpeed: number;
}

const COUNT = 45;
const CONNECT_DIST = 100;
const CONNECT_DIST_SQ = CONNECT_DIST * CONNECT_DIST;
const FPS_CAP = 30;
const FRAME_INTERVAL = 1000 / FPS_CAP;

export default function ParticleField() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resize();
    window.addEventListener("resize", resize, { passive: true });

    // Cache color in a ref — avoid DOM query every frame
    let color = document.documentElement.getAttribute("data-theme") === "light"
      ? "8,145,178" : "34,211,238";
    const observer = new MutationObserver(() => {
      color = document.documentElement.getAttribute("data-theme") === "light"
        ? "8,145,178" : "34,211,238";
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

    const particles: Particle[] = Array.from({ length: COUNT }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      r: Math.random() * 1.5 + 0.5,
      opacity: Math.random() * 0.5 + 0.1,
      pulse: Math.random() * Math.PI * 2,
      pulseSpeed: Math.random() * 0.02 + 0.005,
    }));

    let frame: number;
    let lastTime = 0;

    const draw = (now: number) => {
      frame = requestAnimationFrame(draw);
      if (now - lastTime < FRAME_INTERVAL) return;
      lastTime = now;

      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);

      // Update + draw dots
      for (let i = 0; i < COUNT; i++) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.pulse += p.pulseSpeed;

        if (p.x < 0) p.x = w;
        else if (p.x > w) p.x = 0;
        if (p.y < 0) p.y = h;
        else if (p.y > h) p.y = 0;

        const alpha = p.opacity * (0.7 + 0.3 * Math.sin(p.pulse));
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${color},${alpha})`;
        ctx.fill();
      }

      // Draw connections — squared distance avoids sqrt in the hot rejection path
      ctx.lineWidth = 0.5;
      for (let i = 0; i < COUNT; i++) {
        for (let j = i + 1; j < COUNT; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dSq = dx * dx + dy * dy;
          if (dSq < CONNECT_DIST_SQ) {
            // Only call sqrt for the ~5–10% of pairs that actually connect
            const alpha = (1 - Math.sqrt(dSq) / CONNECT_DIST) * 0.12;
            ctx.strokeStyle = `rgba(${color},${alpha})`;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }
    };

    frame = requestAnimationFrame(draw);

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", resize);
      observer.disconnect();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none"
      style={{ opacity: 0.6, willChange: "transform" }}
    />
  );
}
