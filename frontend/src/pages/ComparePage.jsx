import { useState } from "react";
import { compareTickers } from "../lib/api";

export default function ComparePage() {
  const [ticker1, setTicker1] = useState("NVDA");
  const [ticker2, setTicker2] = useState("AMD");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await compareTickers(ticker1, ticker2);
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
        <form className="inline-form" onSubmit={handleSubmit}>
          <label>
            <span>Ticker 1</span>
            <input value={ticker1} onChange={(event) => setTicker1(event.target.value.toUpperCase())} />
          </label>
          <label>
            <span>Ticker 2</span>
            <input value={ticker2} onChange={(event) => setTicker2(event.target.value.toUpperCase())} />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? "Comparing..." : "Compare"}
          </button>
        </form>
        {error ? <p className="error-banner">{error}</p> : null}
      </section>

      {result ? (
        <section className="panel wide-panel">
          <p className="eyebrow">Comparison</p>
          <h3>{result.ticker1} vs {result.ticker2}</h3>
          <div className="compare-table">
            <div className="compare-row compare-head">
              <span>Metric</span>
              <span>{result.ticker1}</span>
              <span>{result.ticker2}</span>
            </div>
            {(result.metrics || []).map((metric) => (
              <div key={metric.label} className="compare-row">
                <span>{metric.label}</span>
                <strong>{String(metric.ticker1_value ?? "N/A")}</strong>
                <strong>{String(metric.ticker2_value ?? "N/A")}</strong>
              </div>
            ))}
          </div>
        </section>
      ) : null}
    </section>
  );
}
