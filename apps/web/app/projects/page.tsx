"use client";
import Link from "next/link";
import { useState } from "react";
import { useFetch } from "../../hooks/hooks";
import { api } from "../../lib/api";

export default function Projects() {
  const list = useFetch(() => api.projects(), []);
  const [title, setTitle] = useState("");
  const [msg, setMsg] = useState("");
  async function create(e: React.FormEvent) {
    e.preventDefault();
    try {
      const p = await api.createProject({ title: title || "Untitled project" });
      window.location.href = `/projects/${p.id}/studio`;
    } catch (err) { setMsg(String(err)); }
  }
  return (
    <div className="grid">
      <h1>MY PROJECTS</h1>
      <form className="nb-card" onSubmit={create}>
        <h2>New project</h2>
        <label className="f">Title<input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Overheating in Leeds terraces" /></label>
        <button className="nb-btn" type="submit">CREATE PROJECT</button>{" "}
        <Link className="nb-btn secondary" href="/projects/new">GUIDED WIZARD →</Link>
        {msg && <p role="status">{msg}</p>}
      </form>
      {list.loading && <p>Loading…</p>}
      <div className="grid cards">
        {(list.data?.items || []).map((p: Record<string, unknown>) => (
          <div className="nb-card" key={p.id as string}>
            <h3>{p.title as string}</h3>
            <p>RQs {(p.counts as Record<string, number>).questions} · Aims {(p.counts as Record<string, number>).aims} · Datasets {(p.counts as Record<string, number>).datasets}</p>
            <Link className="nb-btn" href={`/projects/${p.id}/studio`}>OPEN STUDIO</Link>
          </div>
        ))}
      </div>
    </div>
  );
}
