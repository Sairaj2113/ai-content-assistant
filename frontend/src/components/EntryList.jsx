const SUMMARY_LENGTH = 100;

function truncate(text, length) {
  return text.length > length ? `${text.slice(0, length).trimEnd()}…` : text;
}

export default function EntryList({ entries, loading, error, selectedId, onSelect }) {
  if (loading) return <p className="muted">Loading entries…</p>;
  if (error) return <p className="error">{error}</p>;
  if (entries.length === 0) return <p className="muted">No entries yet.</p>;

  return (
    <ul className="entry-list">
      {entries.map((entry) => (
        <li key={entry.id}>
          <button
            className={entry.id === selectedId ? "entry-item selected" : "entry-item"}
            onClick={() => onSelect(entry.id)}
          >
            <span className="entry-summary">{truncate(entry.summary, SUMMARY_LENGTH)}</span>
            <span className="tags">
              {entry.tags.map((tag) => (
                <span key={tag} className="tag">{tag}</span>
              ))}
            </span>
            <span className="muted small">{new Date(entry.created_at).toLocaleString()}</span>
          </button>
        </li>
      ))}
    </ul>
  );
}
