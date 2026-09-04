"use client";
import { useState } from "react";
import { useFetch } from "../../../../hooks/hooks";
import { api } from "../../../../lib/api";

export default function Notes({ params }: { params: { id: string } }) {
  const id = params.id;
  const n = useFetch(() => api.project(id), [id]);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [type, setType] = useState("General");
  const [msg, setMsg] = useState("");
  return (
    <div className="grid">
      <h1>NOTEBOOK</h1>
      <div className="nb-card">
        <h2>New note (Markdown supported)</h2>
        <label className="f">Type<select value={type} onChange={(e) => setType(e.target.value)}>{["General", "Idea", "Method decision", "Dataset caveat", "Supervisor comment", "Meeting", "Result", "Limitation", "Future work", "Quotation", "Task"].map((t) => <option key={t}>{t}</option>)}</select></label>
        <label className="f">Title<input value={title} onChange={(e) => setTitle(e.target.value)} /></label>
        <label className="f">Body<textarea value={body} onChange={(e) => setBody(e.target.value)} rows={5} /></label>
        <button className="nb-btn" onClick={async () => { try { await api.post(`/api/v1/projects/${id}/notes`, { note_type: type, title, body }); setMsg("Saved."); window.location.reload(); } catch (e) { setMsg(String(e)); } }}>SAVE NOTE</button>
        {msg && <p role="status">{msg}</p>}
      </div>
      {(n.data?.notes || []).map((x: Record<string, string>) => (
        <article className="nb-card" key={x.id}><h3>[{x.note_type}] {x.title}</h3><p style={{ whiteSpace: "pre-wrap" }}>{x.body}</p></article>
      ))}
      <div className="nb-card">
        <h2>Researcher-entered result</h2>
        <ResultForm id={id} />
      </div>
    </div>
  );
}

function ResultForm({ id }: { id: string }) {
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [msg, setMsg] = useState("");
  return (
    <form onSubmit={async (e) => { e.preventDefault(); try { await api.post(`/api/v1/projects/${id}/results`, { title, body }); setMsg("Result saved. Abstracts may now cite it."); } catch (err) { setMsg(String(err)); } }}>
      <label className="f">Title<input value={title} onChange={(e) => setTitle(e.target.value)} /></label>
      <label className="f">Finding<textarea value={body} onChange={(e) => setBody(e.target.value)} rows={3} /></label>
      <button className="nb-btn" type="submit">SAVE RESULT</button>
      {msg && <p role="status">{msg}</p>}
    </form>
  );
}
