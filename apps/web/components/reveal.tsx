"use client";
import { useEffect, useRef, useState } from "react";

/** Adds .in when scrolled into view (once). Content is visible without JS-motion (CSS default handles no-JS). */
export function Reveal({ children, delay = 0, as: Tag = "div", cls = "" }: {
  children: React.ReactNode; delay?: number; as?: "div" | "article" | "section" | "li"; cls?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.setProperty("--d", `${delay}s`);
    const io = new IntersectionObserver((es) => {
      es.forEach((e) => { if (e.isIntersecting) { el.classList.add("in"); io.disconnect(); } });
    }, { threshold: 0.08 });
    io.observe(el);
    const t = setTimeout(() => el.classList.add("in"), 2500); // safety: never trap content
    return () => { io.disconnect(); clearTimeout(t); };
  }, [delay]);
  return <Tag ref={ref as never} className={`reveal ${cls}`}>{children}</Tag>;
}

/** Animated KPI counter; renders final value immediately for reduced motion / no JS reliance. */
export function CountUp({ value, label }: { value: number; label: string }) {
  const [n, setN] = useState(0);
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) { setN(value); return; }
    let v = 0;
    const step = Math.max(1, Math.round(value / 24));
    const t = setInterval(() => { v += step; if (v >= value) { v = value; clearInterval(t); } setN(v); }, 40);
    return () => clearInterval(t);
  }, [value]);
  return <span aria-label={`${label}: ${value}`}><span aria-hidden>{n}</span><span className="sr">{value}</span></span>;
}
