"use client";
import { useEffect, useState } from "react";
import { api } from "../lib/api";

const DOMAIN_COLORS: Record<string, string> = {
  "Weather & Climate": "#12C8B0", "Climate Change": "#12C8B0", "Air Quality": "#12C8B0",
  "Environment": "#4BD14A", "Flooding & Hazards": "#12C8B0",
  "Buildings & Housing": "#FCDD28", "Building Performance": "#F36D30", "Energy & Carbon": "#F36D30",
  "Housing Vulnerability": "#FF4F85", "Planning & Development": "#8167F5",
  "Geospatial / GIS": "#8167F5", "Population & Demographics": "#FF4F85",
};

export function domainColor(domain = ""): string {
  return DOMAIN_COLORS[domain] || "#D8CCB9";
}

export function placeholder(title = "INQETRA", domain = ""): string {
  const initials = title.split(/\s+/).slice(0, 2).map((w) => w[0]).join("").toUpperCase() || "IN";
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360'><rect width='640' height='360' fill='${domainColor(domain)}'/><rect x='14' y='14' width='612' height='332' fill='none' stroke='#161616' stroke-width='6'/><text x='40' y='210' font-family='Arial Black,Arial' font-size='120' font-weight='900' fill='#161616'>${initials}</text><text x='40' y='280' font-family='monospace' font-size='26' font-weight='700' fill='#161616'>${domain || "UK DATASET"}</text></svg>`;
  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}

/** Local domain artwork path for a catalogue domain (empty when unmapped). */
export function domainArt(domain = ""): string {
  if (!domain) return "";
  const slug = domain.toLowerCase().replace(/&/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  return `/img/domains/domain-${slug}.png`;
}

/** Publisher-advertised preview image (hotlinked, never hosted) with local fallback. */
export function ThumbImg({ id, title, domain, height = 150 }: { id: string; title: string; domain?: string; height?: number }) {
  const art = domainArt(domain);
  const [src, setSrc] = useState<string>(art || placeholder(title, domain));
  const [note, setNote] = useState<string>("");
  useEffect(() => {
    let live = true;
    api.thumbnail(id).then((t) => {
      if (!live) return;
      if (t.image_url) setSrc(t.image_url);
      setNote(t.note || "");
    }).catch(() => { /* placeholder stands */ });
    return () => { live = false; };
  }, [id]);
  return (
    <figure className="thumb" style={{ margin: 0 }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={src} alt={`Preview for ${title}`} loading="lazy" referrerPolicy="no-referrer"
        style={{ width: "100%", height, objectFit: "cover", border: "2px solid var(--nb-ink)", background: "#fff" }}
        onError={(e) => {
          const img = e.target as HTMLImageElement;
          if (art && img.src.endsWith(art)) img.src = placeholder(title, domain);
        }} />
      {note && <figcaption title={note}>Preview: publisher-advertised or generated placeholder</figcaption>}
    </figure>
  );
}
