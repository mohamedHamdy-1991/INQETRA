"use client";
import Link from "next/link";
import { useEffect, useRef } from "react";
import { useFetch } from "../../hooks/hooks";
import { api } from "../../lib/api";

export default function MapPage() {
  const ref = useRef<HTMLDivElement>(null);
  const tax = useFetch(() => api.taxonomy(), []);
  const stats = useFetch(() => api.datasets({ limit: 1 }), []);
  useEffect(() => {
    let map: { remove: () => void } | null = null;
    (async () => {
      const L = await import("leaflet");
      if (!ref.current || (ref.current as HTMLElement).dataset.init) return;
      (ref.current as HTMLElement).dataset.init = "1";
      const m = L.map(ref.current as HTMLElement).setView([54.5, -2.5], 5);
      L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { attribution: "© OpenStreetMap contributors" }).addTo(m);
      // circleMarker: bundler-independent, no default icon assets needed
      L.circleMarker([53.8, -1.55], { radius: 9, color: "#161616", weight: 3, fillColor: "#FCDD28", fillOpacity: 1 })
        .addTo(m).bindPopup("Leeds — example study area");
      map = m as unknown as { remove: () => void };
    })();
    return () => { try { map?.remove(); } catch { /* noop */ } };
  }, []);
  const domains = ((tax.data?.domains || []) as string[]).slice(0, 12);
  return (
    <div className="grid">
      <h1>DATA MAP</h1>
      <p>The map is a discovery aid, never the only route. Coverage below comes from catalogue text, not live geometry.</p>
      <div ref={ref} className="inq-map-shell" role="application" aria-label="UK study-area map" style={{ minHeight: 420 }} />
      <section className="nb-card" aria-label="Dataset coverage summary">
        <h2>COVERAGE SUMMARY</h2>
        <p><strong>{stats.data?.total ?? "…"}</strong> catalogue records across <strong>{tax.data?.domains?.length ?? "…"}</strong> domains.</p>
        <nav aria-label="Domains" className="filters">
          {domains.map((d) => (
            <Link key={d} className="nb-btn secondary" href={`/datasets?domain=${encodeURIComponent(d)}`}>{d}</Link>
          ))}
        </nav>
        <p><Link className="nb-btn" href="/datasets/all">OPEN THE FULL A–Z CATALOGUE →</Link></p>
      </section>
      <p><Link className="nb-btn secondary" href="/datasets">Back to list search (always available)</Link></p>
    </div>
  );
}
