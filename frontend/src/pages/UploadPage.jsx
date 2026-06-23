import { useState } from "react";
import { uploadReport } from "../lib/api";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setError("Choose a PDF before uploading.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const response = await uploadReport(file);
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
          <label className="file-field">
            <span>Annual report PDF</span>
            <input
              type="file"
              accept="application/pdf"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
            />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? "Uploading..." : "Upload and Index"}
          </button>
        </form>
        {file ? <p className="body-copy">Selected file: {file.name}</p> : null}
        {error ? <p className="error-banner">{error}</p> : null}
      </section>

      {result ? (
        <section className="panel">
          <p className="eyebrow">Index Result</p>
          <ul className="detail-list">
            <li><span>Document ID</span><strong>{result.document_id}</strong></li>
            <li><span>Filename</span><strong>{result.filename}</strong></li>
            <li><span>Chunks Indexed</span><strong>{result.chunks_indexed}</strong></li>
            <li><span>Collection</span><strong>{result.collection_name}</strong></li>
          </ul>
        </section>
      ) : null}
    </section>
  );
}
