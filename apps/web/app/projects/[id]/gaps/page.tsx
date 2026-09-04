"use client";
import Link from "next/link";

import { useFetch } from "../../../../hooks/hooks";
import { api } from "../../../../lib/api";

export default function Gaps({ params }: { params: { id: string } }) {
  const id = params.id;
  const g = useFetch(() => api.get(`/api/v1/projects/${id}/gaps`), [id]);
  const c = useFetch(() => api.get(`/api/v1/projects/${id}/compatibility`), [id]);
  if (g.loading) return <p>Evaluating gaps…</p>;
  if (g.error) return <p className="warn">{String(g.error)}</p>;
  return (
    <div className="grid">
      <h1>DATA GAP RADAR</h1>
      <p>{g.data.disclaimer}</p>
      {(g.data.requirements || []).map((r: Record<string, string>) => (
        <div className="nb-card" key={r.requirement_id} style={{ background: r.status === "COVERED" ? "var(--nb-green)" : r.status === "MISSING" ? "var(--nb-pink)" : "var(--nb-surface)" }}>
          <h3>{r.requirement_title} — {r.status}</h3>
          <p>{r.explanation}</p>
          <FindData project={id} req={r.requirement_id} />
        </div>
      ))}
      <h2>Compatibility detail</h2>
      {(c.data?.evaluations || []).slice(0, 10).map((e: Record<string, unknown>, i: number) => (
        <details className="nb-card" key={i}>
          <summary>{e.dataset_id as string} — {e.overall as string} (requirement {String(e.requirement_id)})</summary>
          <ul>{((e.checks as { rule: string; status: string; explanation: string }[]) || []).map((ch) => <li key={ch.rule}><strong>{ch.rule}: {ch.status}</strong> — {ch.explanation}</li>)}</ul>
          <p>{String(e.disclaimer)}</p>
        </details>
      ))}
      <p><Link href={`/projects/${id}/candidates`}>Candidate inbox →</Link></p>
    </div>
  );
}

function FindData({ project, req }: { project: string; req: string }) {
  async function run() {
    const r = await api.post(`/api/v1/projects/${project}/requirements/${req}/find-data`, {});
    alert(`Top candidate: ${r.internal_candidates?.[0]?.dataset_id || "none"} (search relevance). External leads go to the inbox.`);
  }
  return <button className="nb-btn secondary" onClick={run}>FIND DATA FOR GAP</button>;
}
