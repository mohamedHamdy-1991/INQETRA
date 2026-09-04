"use client";
import Link from "next/link";
import { useState } from "react";
import { api } from "../lib/api";
import { useFetch } from "../hooks/hooks";
import { CountUp, Reveal } from "../components/reveal";

const JOURNEY: [string, string][] = [
  ["01", "State the problem and the knowledge gap"],
  ["02", "Draft research questions"],
  ["03", "Align aims and objectives"],
  ["04", "Choose methodology and methods"],
  ["05", "List dataset requirements — variables, geography, scale"],
  ["06", "Fill the basket from the 751-record catalogue"],
  ["07", "Assign every dataset to an aim"],
  ["08", "Run compatibility + gap radar"],
  ["09", "Draft the evidence-traced abstract"],
  ["10", "Export the reproducible data plan"],
];

export default function Home() {
  const stats = useFetch(() => api.datasets({ limit: 1 }), []);
  const kits = useFetch(() => api.kits(), []);
  const health = useFetch(() => api.health(), []);
  const [rq, setRq] = useState("");
  const [msg, setMsg] = useState("");

  async function start(e: React.FormEvent) {
    e.preventDefault();
    if (!rq.trim()) { setMsg("Type a research question first — or use the guided wizard."); return; }
    try {
      const p = await api.createProject({ title: rq.slice(0, 80), problem: rq });
      window.location.href = `/projects/${p.id}/studio`;
    } catch (err) { setMsg(String(err)); }
  }

  return (
    <div className="grid home">
      {/* ── HERO ─────────────────────────────────────────────── */}
      <section className="hero home-hero" aria-labelledby="h1">
        <div>
          <nav className="pipe-chips" aria-label="How INQETRA works">
            <span className="chip">QUESTION</span><span className="pipe" aria-hidden="true">→</span>
            <span className="chip">METHOD</span><span className="pipe" aria-hidden="true">→</span>
            <span className="chip">DATA</span><span className="pipe" aria-hidden="true">→</span>
            <span className="chip">PLAN</span>
          </nav>
          <h1 id="h1" className="home-h1">
            TURN QUESTIONS<br />INTO{" "}
            <span className="hl-block">DATA&nbsp;PLANS.</span>
          </h1>
          <p className="lede">
            INQETRA turns a half-formed research idea into an executable data plan: authoritative UK
            datasets aligned to your aims and methods, gaps made explicit, and every claim traced to its source.
          </p>
          <form className="research-box" onSubmit={start}>
            <label className="sr" htmlFor="rq">Research question</label>
            <textarea id="rq" value={rq} onChange={(e) => setRq(e.target.value)}
              placeholder="What are you researching? Example: How do urban form and local weather influence overheating risk in UK dwellings?" />
            <button className="nb-btn orange" type="submit" style={{ background: "var(--nb-orange)" }}>START PROJECT →</button>
          </form>
          {msg && <p role="status">{msg}</p>}
          <p className="hero-ctas">
            <Link className="nb-btn violet" href="/projects/new" style={{ background: "var(--nb-violet)", color: "#fff" }}>GUIDED WIZARD →</Link>{" "}
            <Link className="nb-btn secondary" href="/projects">Start a Research Project</Link>{" "}
            <Link className="nb-btn secondary" href="/datasets">Explore Datasets</Link>
          </p>
        </div>
        <aside className="hero-media" aria-label="INQETRA at a glance">
          <div className="media-card pop-in">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/img/hero/hero-landing.png" alt="Illustration: city research data flowing into project cards" width={2000} height={1100} />
          </div>
          <div className="grid hero-kpis">
            <div className="nb-kpi"><span>DATASET CATALOGUE</span><strong><CountUp value={stats.data?.total ?? 751} label="Datasets" /></strong><p>Official links and provenance first.</p></div>
            <div className="nb-kpi" style={{ background: "var(--nb-cyan)" }}><span>RESEARCH LOGIC</span><strong>RQ↔AIM</strong><p>Questions, aims, methods, variables and datasets stay linked.</p></div>
          </div>
        </aside>
      </section>

      {/* ── INK STAT BAND ────────────────────────────────────── */}
      <section className="stat-band" aria-label="Catalogue facts">
        <div><strong><CountUp value={health.data?.record_count ?? 751} label="Datasets" /></strong><span>DATASETS</span></div>
        <div><strong><CountUp value={health.data?.reachable_record_count ?? 751} label="Reachable" /></strong><span>LINKS REACHABLE*</span></div>
        <div><strong><CountUp value={18} label="Domains" /></strong><span>DOMAINS</span></div>
        <div><strong><CountUp value={8} label="Research kits" /></strong><span>RESEARCH KITS</span></div>
      </section>
      <p className="fineprint">*Landing pages reachable at last link-health check. Reachability ≠ download access, licence permission or scientific fitness.</p>

      {/* ── JOURNEY ──────────────────────────────────────────── */}
      <section className="journey" aria-labelledby="jh">
        <div className="journey-head">
          <h2 id="jh">FROM HALF-FORMED IDEA<br />TO REPRODUCIBLE PLAN</h2>
          <p>INQETRA keeps your research logic as linked objects — not one long text field. Ten steps, each one stored, each one exportable.</p>
          <p><Link className="nb-btn orange" href="/projects/new" style={{ background: "var(--nb-orange)" }}>START THE GUIDED WIZARD →</Link></p>
        </div>
        <ol className="journey-board">
          {JOURNEY.map(([n, t], i) => (
            <Reveal as="li" key={n} delay={Math.min(i * 0.04, 0.3)} cls="journey-step">
              <span className="step-no" data-c={i % 6}>{n}</span>
              <span>{t}</span>
            </Reveal>
          ))}
        </ol>
      </section>

      {/* ── KITS ─────────────────────────────────────────────── */}
      <section aria-labelledby="kh">
        <h2 id="kh">START FROM A RESEARCH KIT</h2>
        <p>Eight ready-made research graphs — questions, aims, methods and requirements. One click creates the whole project.</p>
        <div className="kit-row">
          {((kits.data?.items || []) as Record<string, string>[]).map((k) => (
            <Reveal as="article" key={k.slug} cls="kit-card media-card">
              <Link href={`/kits/${k.slug}`} aria-label={`Open kit: ${k.title}`}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={`/img/kits/kit-${k.slug}.png`} alt="" width={800} height={450} loading="lazy" />
                <h3>{k.title}</h3>
                <span className="nb-btn secondary">OPEN KIT →</span>
              </Link>
            </Reveal>
          ))}
        </div>
        <p><Link className="nb-btn secondary" href="/kits">ALL EIGHT KITS →</Link></p>
      </section>

      {/* ── TRUST ────────────────────────────────────────────── */}
      <section className="trust" aria-labelledby="th">
        <div className="nb-card trust-copy">
          <h2 id="th">TRUST + PROVENANCE</h2>
          <p>Every dataset carries its publisher, <em>link_type</em>, <em>verification_state</em>, review date and landing-URL health.</p>
          <p>A working landing page does <strong>not</strong> prove download access, licence permission, scientific fitness or resolved metadata. Collection and search records stay labelled as such — never silently upgraded. Harvested material waits in a staging queue; nothing auto-publishes.</p>
          <p><Link className="nb-btn secondary" href="/methodology">READ THE DATA METHOD →</Link></p>
        </div>
        <div className="media-card trust-stickers">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/img/source/stickers-set.png" alt="INQETRA principles: evidence, 751 datasets, open, traceable, reproducible, UK" width={1200} height={800} loading="lazy" />
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────────── */}
      <section className="nb-card cta-final" aria-label="Start now">
        <div className="cta-media">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/img/banners/cta-start-project.png" alt="" aria-hidden="true" width={1600} height={600} />
          <div className="cta-overlay">
            <h2>YOUR DATA PLAN STARTS TODAY</h2>
            <p><Link className="nb-btn violet" href="/projects/new" style={{ background: "var(--nb-violet)", color: "#fff" }}>START A NEW PROJECT →</Link></p>
          </div>
        </div>
      </section>
    </div>
  );
}
