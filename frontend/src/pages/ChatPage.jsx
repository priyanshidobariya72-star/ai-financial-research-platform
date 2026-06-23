import { useState } from "react";
import { askQuestion } from "../lib/api";

export default function ChatPage() {
  const [query, setQuery] = useState("What risks are mentioned in the annual report?");
  const [k, setK] = useState(4);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await askQuestion(query, Number(k));
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="page-grid">
      <section className="panel wide-panel">
        <form className="stack-form" onSubmit={handleSubmit}>
          <label>
            <span>Question</span>
            <textarea rows="6" value={query} onChange={(event) => setQuery(event.target.value)} />
          </label>
          <label>
            <span>Top K Chunks</span>
            <input type="number" min="1" max="10" value={k} onChange={(event) => setK(event.target.value)} />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? "Running workflow..." : "Ask"}
          </button>
        </form>
        {error ? <p className="error-banner">{error}</p> : null}
      </section>

      {result ? (
        <>
          <section className="panel wide-panel">
            <p className="eyebrow">Answer</p>
            <p className="body-copy">{result.answer}</p>
          </section>
          <section className="panel">
            <p className="eyebrow">Citations</p>
            <div className="citation-list">
              {(result.citations || []).length ? (
                result.citations.map((citation, index) => (
                  <article key={`${citation.chunk_id || citation.source}-${index}`} className="citation-card">
                    <strong>{citation.source}</strong>
                    <span>Page {citation.page || "N/A"}</span>
                    <code>{citation.chunk_id || "No chunk id"}</code>
                  </article>
                ))
              ) : (
                <p className="body-copy">No citations returned.</p>
              )}
            </div>
          </section>
        </>
      ) : null}
    </section>
  );
}
