"use client";
import { useFetch } from "../../hooks/hooks";
import { api } from "../../lib/api";

export default function Sources() {
  const s = useFetch(() => api.sources(), []);
  const h = useFetch(() => api.health(), []);
  return (
    <div className="grid">
      <h1>SOURCES</h1>
      <p>Controlled source registry. Harvesting originates here only — never indiscriminate scraping.</p>
      {h.data && <p role="status">Link health {h.data.checked_at_utc}: {h.data.reachable_record_count}/{h.data.record_count} reachable. {h.data.definition}</p>}
      <div className="grid cards">
        {(s.data?.items || []).map((x: Record<string, string>, i: number) => (
          <div className="nb-card" key={i}><h3>{x.source}</h3><p>Adapter: {x.adapter} · Trust: {x.trust} · Cadence: {x.cadence}</p><p><a href={x.homepage} target="_blank" rel="noreferrer">{x.homepage}</a></p><p>{x.notes}</p></div>
        ))}
      </div>
    </div>
  );
}
