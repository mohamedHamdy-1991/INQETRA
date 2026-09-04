"use client";
import Link from "next/link";
import { useFetch } from "../../hooks/hooks";
import { api } from "../../lib/api";

export default function Publishers() {
  const p = useFetch(() => api.publishers(), []);
  if (p.loading) return <p>Loading publishers…</p>;
  return (
    <div className="grid">
      <h1>PUBLISHERS</h1>
      <table className="data"><thead><tr><th>Publisher</th><th>Authority</th><th>Datasets</th></tr></thead>
        <tbody>{(p.data?.items || []).map((x: Record<string, string | number>) => (
          <tr key={String(x.name)}><td><Link href={`/datasets?publisher=${encodeURIComponent(String(x.name))}`}>{String(x.name)}</Link></td><td>{String(x.authority)}</td><td>{String(x.count)}</td></tr>
        ))}</tbody></table>
    </div>
  );
}
