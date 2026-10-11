import { useEffect, useState } from "react";
import { getEntry } from "../api.js";

export default function EntryDetail({ id, onClose }) {
  const [entry, setEntry] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    // Ignore a slow response if the user has already picked another entry.
    let ignore = false;
    setEntry(null);
    setError("");
    getEntry(id)
      .then((data) => !ignore && setEntry(data))
      .catch((err) => !ignore && setError(err.message));
    return () => {
      ignore = true;
    };
  }, [id]);

  return (
    <article className="card">
      <div className="detail-header">
        <h2>Entry #{id}</h2>
        <button className="secondary" onClick={onClose}>Close</button>
      </div>

      {error && <p className="error">{error}</p>}
      {!entry && !error && <p className="muted">Loading…</p>}

      {entry && (
        <>
          <p className="muted small">{new Date(entry.created_at).toLocaleString()}</p>
          <h3>Summary</h3>
          <p>{entry.summary}</p>
          <div className="tags">
            {entry.tags.map((tag) => (
              <span key={tag} className="tag">{tag}</span>
            ))}
          </div>
          <h3>Original text</h3>
          <p className="original-text">{entry.text}</p>
        </>
      )}
    </article>
  );
}
