"use client";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { useFetch } from "../../hooks/hooks";
import { api } from "../../lib/api";

function Inner() {
  const sp = useSearchParams();
  const ids = (sp.get("ids") || "").split(",").map((s) => s.trim()).filter(Boolean).slice(0, 4);
  const cmp = useFetch(() => ids.length >= 2 ? api.compare(ids) : Promise.resolve(null), [sp.get("ids")]);
  if (ids.length < 2) return <div className="nb-card"><h1>COMPARE</h1><p>Add 2–4 datasets from Explore (COMPARE buttons deep-link here as <code>?ids=a,b</code>).</p></div>;
  if (cmp.loading) return <p role="status">Comparing…</p>;
  if (cmp.error) return <p className="warn">{String(cmp.error)}</p>;
  return (
    <div className="grid">
      <h1>COMPARE ({cmp.data.items.length})</h1>
      <p>Side-by-side source-declared facts. Search relevance is not dataset quality.</p>
      <table className="data">
        <thead><tr><th>Field</th>{cmp.data.items.map((i: Record<string, string>) => <th key={i.id}>{i.title}</th>)}</tr></thead>
        <tbody>
          {Object.keys(cmp.data.items[0]).filter((k) => k !== "title").map((k) => (
            <tr key={k}><th scope="row">{k}</th>{cmp.data.items.map((i: Record<string, string>) => <td key={i.id}>{i[k]}</td>)}</tr>
          ))}
        </tbody>
      </table>
      <ul>{cmp.data.notes.map((n: string, i: number) => <li key={i}>{n}</li>)}</ul>
      <p>{cmp.data.caveat}</p>
    </div>
  );
}
export default function Page() { return <Suspense fallback={<p>Loading…</p>}><Inner /></Suspense>; }
