import { useState } from "react";
import { analyzeTicker } from "../lib/api";
import { MetricCard } from "../components/MetricCard";

export default function DashboardPage() {
  const [ticker, setTicker] = useState("NVDA");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await analyzeTicker(ticker);
      setData(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="page-grid">
      <section className="panel hero-panel">
        <form className="inline-form" onSubmit={handleSubmit}>
          <label>
            <span>Ticker</span>
            <input value={ticker} onChange={(event) => setTicker(event.target.value.toUpperCase())} />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? "Analyzing..." : "Analyze Company"}
          </button>
        </form>
        {error ? <p className="error-banner">{error}</p> : null}
      </section>

      {data ? (
        <>
          <section className="panel wide-panel">
            <p className="eyebrow">Company</p>
            <h3>{data.company_name || data.ticker}</h3>
            <p className="body-copy">{data.business_summary || "No business summary available."}</p>
            <div className="metric-grid">
              <MetricCard label="Market Cap" value={data.market_cap} accent="blue" />
              <MetricCard label="Trailing P/E" value={data.trailing_pe} accent="sand" />
              <MetricCard label="Current Price" value={data.price_summary?.current_price} accent="green" />
              <MetricCard label="1M Change %" value={data.price_summary?.change_percent} accent="rose" />
            </div>
          </section>

          <section className="panel">
            <p className="eyebrow">AI View</p>
            <h3>{data.recommendation?.label || "N/A"}</h3>
            <p className="body-copy">{data.recommendation?.reasoning_summary}</p>
            <div className="signal-grid">
              <MetricCard label="Confidence" value={data.recommendation?.confidence} accent="amber" />
              <MetricCard label="Fundamentals" value={data.recommendation?.signals?.fundamentals} accent="blue" />
              <MetricCard label="Technicals" value={data.recommendation?.signals?.technicals} accent="green" />
              <MetricCard label="News" value={data.recommendation?.signals?.news_sentiment} accent="rose" />
            </div>
            <p className="micro-copy">{data.recommendation?.what_would_change_view}</p>
            <p className="micro-copy">{data.recommendation?.disclaimer}</p>
          </section>

          <section className="panel">
            <p className="eyebrow">Profile</p>
            <ul className="detail-list">
              <li><span>Ticker</span><strong>{data.ticker}</strong></li>
              <li><span>Sector</span><strong>{data.sector || "N/A"}</strong></li>
              <li><span>Industry</span><strong>{data.industry || "N/A"}</strong></li>
              <li><span>Website</span><strong>{data.website || "N/A"}</strong></li>
            </ul>
          </section>

          <section className="panel wide-panel">
            <p className="eyebrow">Recent News</p>
            <div className="news-list">
              {(data.recent_news || []).length ? (
                data.recent_news.map((item, index) => (
                  <article key={`${item.url || item.title}-${index}`} className="news-card">
                    <h4>{item.title}</h4>
                    <p>{item.source_name || "Unknown source"}</p>
                    {item.url ? (
                      <a href={item.url} target="_blank" rel="noreferrer">
                        Open article
                      </a>
                    ) : null}
                  </article>
                ))
              ) : (
                <p className="body-copy">No recent news available.</p>
              )}
            </div>
          </section>
        </>
      ) : null}
    </section>
  );
}
