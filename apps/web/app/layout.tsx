import type { Metadata } from "next";
import { Shell } from "../components/chrome";
import "leaflet/dist/leaflet.css";
import "./../styles/tokens.css";
import "./../styles/components.css";
import "./../styles/maps.css";
import "./../styles/charts.css";
import "./../styles/motion.css";
import "./../styles/app.css";

export const metadata: Metadata = {
  title: "INQETRA — Turn research questions into executable data plans",
  description: "UK-centred research-design studio and climate, environment, buildings and built-environment dataset hub.",
  openGraph: {
    title: "INQETRA — Turn research questions into executable data plans",
    description: "UK research-design studio + dataset hub: align questions, aims and methods to authoritative data, then export a reproducible data plan.",
    images: ["/img/brand/og-card.png"],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en-GB">
      <head>
        {/* motion layer hides .reveal only when JS runs; keeps content visible without JS */}
        <script dangerouslySetInnerHTML={{ __html: "document.documentElement.classList.add('js')" }} />
      </head>
      <body>
        <Shell>{children}</Shell>
      </body>
    </html>
  );
}
