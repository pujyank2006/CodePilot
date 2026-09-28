
import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_BASE_URL;

function App() {
  const [status, setStatus] = useState("Connecting...");
  const [error, setError] = useState("");

  useEffect(() => {
    async function checkBackend() {
      try {
        const response = await fetch(
          `${API_URL}/api/v1/health`
        );

        if (!response.ok) {
          throw new Error("Backend request failed");
        }

        const data = await response.json();
        setStatus(data.status);
      } catch (err) {
        setError(err.message);
        setStatus("Disconnected");
      }
    }

    checkBackend();
  }, []);

  return (
    <main>
      <h1>CodePilot</h1>
      <p>Your AI-powered coding assistant.</p>

      <section>
        <h2>Backend status</h2>
        <p>{status}</p>
        {error && <p role="alert">{error}</p>}
      </section>
    </main>
  );
}

export default App;