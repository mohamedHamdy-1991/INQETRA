"use client";
import { useState } from "react";
import { useFetch } from "../../../../hooks/hooks";
import { api } from "../../../../lib/api";

export default function Candidates({ params }: { params: { id: string } }) {
  const id = params.id;
  const c = useFetch(() => api.get(`/api/v1/projects/${id}/candidates`), [id]);
  const [url, setUrl] = useState("");
  const [msg, setMsg] = useState("");
  return (
    <div className="grid">
      <h1>CANDIDATE INBOX</h1>
      <p>Candidates never auto-publish. Resolve → curate → catalogue review, with provenance + link health.</p>
      {(c.data?.items || []).map((x: Record<string, string>) => (
        <div className="nb-card" key={x.id}>
          <h3>{x.url || "(unresolved query)"} — {x.status}</h3>
          <p>{x.rationale} · Licence: {x.licence_state}</p>
          <label className="f">Resolve URL<input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://…" /></label>
          <button className="nb-btn secondary" onClick={async () => { try { await api.post(`/api/v1/candidates/${x.id}/resolve`, { url, source: x.source }); setMsg("Resolved."); window.location.reload(); } catch (e) { setMsg(String(e)); } }}>RESOLVE</button>{" "}
          <button className="nb-btn secondary" onClick={async () => { await api.post(`/api/v1/candidates/${x.id}/reject`, {}); window.location.reload(); }}>REJECT</button>{" "}
          <button className="nb-btn secondary" onClick={async () => { try { await api.post(`/api/v1/candidates/${x.id}/curate`, {}); setMsg("Curated — awaiting catalogue review."); window.location.reload(); } catch (e) { setMsg(String(e)); } }}>CURATE</button>
        </div>
      ))}
      {msg && <p role="status">{msg}</p>}
    </div>
  );
}
