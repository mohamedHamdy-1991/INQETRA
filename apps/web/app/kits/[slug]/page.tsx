"use client";
import Link from "next/link";
import { useState } from "react";
import { Reveal } from "../../../components/reveal";
import { useFetch } from "../../../hooks/hooks";
import { api } from "../../../lib/api";

export default function KitDetail({ params }: { params: { slug: string } }) {
  const slug = params.slug;
  const k = useFetch(() => api.kit(slug), [slug]);
  const [geo, setGeo] = useState("United Kingdom");
  const [msg, setMsg] = useState("");
  if (k.loading) return <p role="status">Loading kit…</p>;
  if (k.error || !k.data) return <p className="warn" role="alert">{String(k.error)}</p>;
  const d = k.data;
  async function instantiateKit() {
    try {
      const r = await api.instantiate(slug, { geography: geo });
      window.location.href = `/projects/${r.project_id}/studio`;
    } catch (e) { setMsg(String(e)); }
  }
  const list = (t: string, arr: string[]) => (
    <div className="nb-card"><h2>{t}</h2><ul>{(arr || []).map((x, i) => <li key={i}>{x}</li>)}</ul></div>
  );
  return (
    <div className="grid">
      <p><Link href="/kits">← Kits</Link></p>
      <h1>{d.title}</h1>
      <p>A kit instantiates a research graph — questions, aims, methods, requirements — not just a dataset list.</p>
      <div className="nb-card" style={{ padding: 0, overflow: "hidden" }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={`/img/kits/kit-${slug}.png`} alt={`${d.title} kit cover`} width={800} height={450}
          style={{ width: "100%", height: "auto", display: "block" }}
          onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
      </div>
      <div className="grid cards">
        <Reveal cls="nb-card">{list("Suggested questions", d.questions)}</Reveal>
        <Reveal cls="nb-card">{list("Aim templates", d.aims)}</Reveal>
        <Reveal cls="nb-card">{list("Methods", d.methods)}</Reveal>
        <Reveal cls="nb-card">{list("Required roles", d.required_roles)}</Reveal>
      </div>
      {d.recommended_domains && list("Recommended domains", d.recommended_domains)}
      <div className="nb-card pop-in">
        <h2>Use this kit</h2>
        <label className="f">Study geography<input value={geo} onChange={(e) => setGeo(e.target.value)} /></label>
        <button className="nb-btn" onClick={instantiateKit}>CREATE PROJECT FROM KIT →</button>
        {msg && <p role="status">{msg}</p>}
      </div>
    </div>
  );
}
