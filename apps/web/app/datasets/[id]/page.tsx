"use client";
import Link from "next/link";

import { Badges, Provenance } from "../../../components/chrome";
import { useBasket, useFetch } from "../../../hooks/hooks";
import { CAVEAT, api } from "../../../lib/api";

export default function Detail({ params }: { params: { id: string } }) {
  const id = params.id;
  const d = useFetch(() => api.dataset(id), [id]);
  const basket = useBasket();
  if (d.loading) return <p role="status">Loading dataset…</p>;
  if (d.error) return <p className="warn" role="alert">Not found: {d.error}</p>;
  const item = d.data.item;
  return (
    <div className="grid">
      <p><Link href="/datasets">← Explore</Link></p>
      <h1>{item.title}</h1>
      <Badges item={item} />
      <Provenance item={item} />
      <div className="nb-card">
        <h2>Overview</h2>
        <p><strong>Publisher:</strong> {item.publisher} ({item.authority_level}) · Portal: {item.source_portal}</p>
        <p><strong>Domain:</strong> {item.domain} / {item.subdomain}</p>
        <p><strong>Geography:</strong> {item.coverage} ({item.uk_nation}) · Scale: {item.spatial_scale}</p>
        <p><strong>Time:</strong> {item.temporal_resolution}</p>
        <p><strong>Roles:</strong> {item.research_roles} · <strong>Methods:</strong> {item.methods_supported}</p>
        <p><strong>Formats:</strong> {item.formats} · <strong>Access:</strong> {item.access_type} · <strong>Licence:</strong> {item.licence}</p>
        <p><strong>Variables:</strong> {item.variables || "Not listed in seed — check the landing page."}</p>
        <p><strong>Notes:</strong> {item.notes}</p>
      </div>
      <div className="nb-card">
        <h2>Access + Licence</h2>
        <p className="warn">Public availability does not imply reuse permission. Read the source licence before reuse or redistribution.</p>
        <p><a className="nb-btn" href={item.landing_url} target="_blank" rel="noreferrer">OPEN OFFICIAL LANDING PAGE</a></p>
      </div>
      <div className="nb-card">
        <h2>Provenance + Health</h2>
        <p>link_type: {item.link_type} · verification_state: {item.verification_state} · reviewed {item.last_catalogue_review}</p>
        <p>Health: {JSON.stringify(item.link_health)} · {CAVEAT}</p>
      </div>
      <p>
        <button className="nb-btn" onClick={() => basket.add(item.id)}>ADD TO BASKET</button>{" "}
        <Link className="nb-btn secondary" href={`/compare?ids=${item.id}`}>COMPARE</Link>
      </p>
      {d.data.related_ids?.length > 0 && (
        <div className="nb-card"><h2>Related</h2>
          <ul>{d.data.related_ids.map((r: string) => <li key={r}><Link href={`/datasets/${r}`}>{r}</Link></li>)}</ul>
        </div>
      )}
    </div>
  );
}
