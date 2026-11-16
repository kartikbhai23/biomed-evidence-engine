import { useState } from "react";

type Citation = {
  document_id: string;
  title: string;
  excerpt: string;
  score: number;
};

type QueryResult = {
  answer: string;
  citations: Citation[];
  abstained: boolean;
  request_id: string;
  latency_ms: number;
};

export default function App() {
  const [question, setQuestion] = useState("What should be logged for an evidence assistant?");
  const [result, setResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);

  async function ask() {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/v1/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, top_k: 3 }),
      });
      setResult(await response.json());
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 820, margin: "48px auto", fontFamily: "system-ui", padding: 24 }}>
      <p style={{ letterSpacing: 1.5, textTransform: "uppercase", fontSize: 12 }}>
        Scientific AI / Evidence
      </p>
      <h1>Biomed Evidence Engine</h1>
      <p>Ask a question and inspect the exact evidence used by the system.</p>
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        rows={4}
        style={{ width: "100%", padding: 12 }}
      />
      <button onClick={ask} disabled={loading} style={{ marginTop: 12, padding: "10px 16px" }}>
        {loading ? "Retrieving..." : "Ask"}
      </button>

      {result && (
        <section style={{ marginTop: 32 }}>
          <h2>Answer</h2>
          <p>{result.answer}</p>
          <small>{result.latency_ms} ms · request {result.request_id.slice(0, 8)}</small>

          <h2>Evidence</h2>
          {result.citations.map((c) => (
            <article
              key={`${c.document_id}-${c.score}`}
              style={{ borderTop: "1px solid #ddd", padding: "14px 0" }}
            >
              <strong>{c.title}</strong>
              <p>{c.excerpt}</p>
            </article>
          ))}
        </section>
      )}
    </main>
  );
}
