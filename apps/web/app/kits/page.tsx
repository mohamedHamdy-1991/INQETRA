"use client";
import { useFetch } from "../../hooks/hooks";
import { api } from "../../lib/api";

export default function Kits() {
  const k = useFetch(() => api.kits(), []);
  if (k.loading) return <p>Loading kits…</p>;
  return (
    <div className="grid">
      <h1>RESEARCH KITS</h1>
      <p>Kits instantiate a research graph (questions, aims, methods, requirements) — not just a dataset list.</p>
      <div className="grid cards">
        {(k.data?.items || []).map((x: Record<string, unknown>) => (
          <div className="nb-card" key={x.slug as string}>
            <h3>{x.title as string}</h3>
            <p>{((x.questions as string[]) || []).join(" ")}</p>
            <p><strong>Methods:</strong> {((x.methods as string[]) || []).join(", ")}</p>
            <p><strong>Roles:</strong> {((x.required_roles as string[]) || []).join(", ")}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
