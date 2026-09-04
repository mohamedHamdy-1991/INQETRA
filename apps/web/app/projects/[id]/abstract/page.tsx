"use client";
import { useState } from "react";
import { useFetch } from "../../../../hooks/hooks";
import { api } from "../../../../lib/api";

export default function Abstract({ params }: { params: { id: string } }) {
  const id = params.id;
  const t = useFetch(() => api.get(`/api/v1/projects/${id}/abstract/traces`), [id]);
  const [mode, setMode] = useState("proposal");
  const [limit, setLimit] = useState(250);
  const [draft, setDraft] = useState<Record<string, unknown> | null>(null);
  const [msg, setMsg] = useState("");
  return (
    <div className="grid">
      <h1>ABSTRACT BUILDER</h1>
      <p>Sentences draw from project objects only. Results require researcher-entered Result objects.</p>
      <div className="nb-card">
        <label className="f">Mode<select value={mode} onChange={(e) => setMode(e.target.value)}>{["proposal", "thesis", "journal", "conference", "grant", "extended", "plain"].map((m) => <option key={m}>{m}</option>)}</select></label>
        <label className="f">Word limit<input type="number" value={limit} onChange={(e) => setLimit(Number(e.target.value))} min={50} max={1000} /></label>
        <button className="nb-btn" onClick={async () => { try { setDraft(await api.post(`/api/v1/projects/${id}/abstract/draft`, { mode, word_limit: limit })); } catch (e) { setMsg(String(e)); } }}>DRAFT ABSTRACT</button>
        {msg && <p role="status">{msg}</p>}
      </div>
      {draft && (
        <article className="nb-card" style={{ background: "var(--nb-yellow)" }}>
          <h2>Draft ({String(draft.mode)})</h2>
          <p>{String(draft.text)}</p>
          <h3>Evidence trace</h3>
          <ul>{((draft.traces as { text: string; sources: string[] }[]) || []).map((tr, i) => <li key={i}>{tr.text} <em>← {tr.sources.join(", ")}</em></li>)}</ul>
        </article>
      )}
      <h2>History</h2>
      {(t.data?.items || []).map((d: Record<string, string>) => (
        <div className="nb-card" key={d.id}><h3>{d.mode} · {d.word_limit} words</h3><p>{d.text}</p></div>
      ))}
    </div>
  );
}
