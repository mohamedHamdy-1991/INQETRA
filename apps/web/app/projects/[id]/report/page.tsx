"use client";
import Link from "next/link";

import { useFetch } from "../../../../hooks/hooks";
import { api } from "../../../../lib/api";

export default function Report({ params }: { params: { id: string } }) {
  const id = params.id;
  const r = useFetch(() => api.get(`/api/v1/projects/${id}/report-model`), [id]);
  const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  if (r.loading) return <p>Loading report…</p>;
  if (r.error) return <p className="warn">{String(r.error)}</p>;
  const m = r.data;
  return (
    <div className="grid">
      <h1>RESEARCH DATA PLAN — {m.project.title}</h1>
      <p>Generated {m.generated_at} · {m.provenance}</p>
      <section className="nb-card"><h2>Questions</h2><ul>{m.questions.map((q: Record<string, string>) => <li key={q.id}>{q.text}</li>)}</ul></section>
      <section className="nb-card"><h2>Aims</h2><ul>{m.aims.map((a: Record<string, string>) => <li key={a.id}>{a.title}: {a.statement}</li>)}</ul></section>
      <section className="nb-card"><h2>Inventory</h2><ul>{m.inventory.map((i: Record<string, Record<string, string>>) => <li key={i.basket.id}>{i.dataset.id} — {i.dataset.title} · {i.dataset.landing_url}</li>)}</ul></section>
      <p>
        <Link className="nb-btn orange" href={`/projects/${id}/report/print`} style={{ background: "var(--nb-orange)" }}>EXPORT PDF (NEO-BRUTALIST) →</Link>{" "}
        <a className="nb-btn" href={`${API}/api/v1/projects/${id}/export?format=markdown`} download>DOWNLOAD MARKDOWN</a>{" "}
        <a className="nb-btn secondary" href={`${API}/api/v1/projects/${id}/export?format=json`} download>DOWNLOAD JSON</a>
      </p>
    </div>
  );
}
