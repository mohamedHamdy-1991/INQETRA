"use client";
import { useState } from "react";

export default function Settings() {
  const [provider, setProvider] = useState("");
  return (
    <div className="grid">
      <h1>SETTINGS</h1>
      <div className="nb-card">
        <h2>AI (optional, provider-neutral)</h2>
        <p>INQETRA works fully without AI. No keys are stored in the repo. To enable the gateway, set <code>INQETRA_AI_PROVIDER</code> on the API server.</p>
        <label className="f">Preferred provider (local note only)<input value={provider} onChange={(e) => setProvider(e.target.value)} placeholder="e.g. local / none" /></label>
      </div>
      <div className="nb-card"><h2>Accessibility</h2><p>Keyboard: Tab / Shift+Tab / Enter on all controls including matrix cells. Layouts verified at 1440/1024/768/390. Reduced motion respected. Minimum tap target 44px.</p></div>
    </div>
  );
}
