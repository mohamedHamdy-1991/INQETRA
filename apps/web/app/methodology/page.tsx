import Link from "next/link";

export default function Methodology() {
  const fams: [string, string][] = [
    ["GIS / Spatial overlay", "Boundaries, exposure surfaces, overlay with housing stock. Evidence: boundary + exposure + built-environment roles."],
    ["Building simulation / Energy modelling", "Dwelling archetypes + weather files. Confirm temporal resolution and units on source pages."],
    ["Regression / Spatial regression", "Outcome + predictors + controls. Identifiers (LSOA/UPRN/postcode) decide join strategy."],
    ["Network analysis", "Streets, stops, timetables. Geometry/network roles required."],
    ["Monitoring / Sensors", "AURN, fixed sites. Point scale; check access and update frequency."],
  ];
  return (
    <div className="grid">
      <h1>METHODOLOGY LIBRARY</h1>
      <p>Educational guide — not prescriptive selection. Each method lists typical evidence requirements and caveats.</p>
      {fams.map(([t, d]) => <div className="nb-card" key={t}><h2>{t}</h2><p>{d}</p></div>)}
      <p><Link href="/projects">Apply in a project →</Link></p>
    </div>
  );
}
