import { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { RightPanel } from "@/components/RightPanel";
import { ScraperView } from "@/components/ScraperView";

const API_BASE = "http://localhost:8000";

interface ProcessResult {
  final_email: string;
  profile_data: string | null;
  target_url: string;
  run_id: string | null;
  email_sent_status: string | null;
}

function App() {
  const [activeNav, setActiveNav] = useState("scraper");
  const [url, setUrl] = useState("");
  const [email, setEmail] = useState("");
  const [apiToken, setApiToken] = useState("");
  const [headers, setHeaders] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ProcessResult | null>(null);

  const handleSubmit = async () => {
    if (!url.trim() || !email.trim()) return;

    setIsLoading(true);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE}/process`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_url: url, recipient_email: email }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Error en el pipeline");
      }

      const data: ProcessResult = await response.json();
      setResult(data);
    } catch (err) {
      console.error("Error:", err);
      alert(err instanceof Error ? err.message : "Error inesperado");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar activeItem={activeNav} onNavigate={setActiveNav} />

      <ScraperView
        url={url}
        onUrlChange={setUrl}
        email={email}
        onEmailChange={setEmail}
        onSubmit={handleSubmit}
        isLoading={isLoading}
        result={result}
      />

      <RightPanel
        apiToken={apiToken}
        onApiTokenChange={setApiToken}
        headers={headers}
        onHeadersChange={setHeaders}
        onSubmit={handleSubmit}
        isLoading={isLoading}
      />
    </div>
  );
}

export default App;
