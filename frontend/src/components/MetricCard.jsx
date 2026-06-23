export function MetricCard({ label, value, accent = "amber" }) {
  return (
    <article className={`metric-card accent-${accent}`}>
      <p>{label}</p>
      <strong>{value ?? "N/A"}</strong>
    </article>
  );
}
