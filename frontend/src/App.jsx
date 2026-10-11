import { useEffect, useState } from "react";
import { listEntries } from "./api.js";
import EntryForm from "./components/EntryForm.jsx";
import EntryList from "./components/EntryList.jsx";
import EntryDetail from "./components/EntryDetail.jsx";

export default function App() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [listError, setListError] = useState("");
  const [selectedId, setSelectedId] = useState(null);

  useEffect(() => {
    listEntries()
      .then(setEntries)
      .catch((err) => setListError(err.message))
      .finally(() => setLoading(false));
  }, []);

  function handleCreated(entry) {
    // POST returns the full entry; the list only needs a short preview of the text.
    const { text, ...rest } = entry;
    setEntries((current) => [{ ...rest, preview: text.slice(0, 120) }, ...current]);
    setSelectedId(entry.id);
  }

  return (
    <div className="app">
      <h1>AI Content Assistant</h1>
      <div className="layout">
        <section className="column">
          <EntryForm onCreated={handleCreated} />
          <h2>Saved entries</h2>
          <EntryList
            entries={entries}
            loading={loading}
            error={listError}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        </section>
        <section className="column">
          {selectedId === null ? (
            <p className="muted">Select an entry to see the details.</p>
          ) : (
            <EntryDetail id={selectedId} onClose={() => setSelectedId(null)} />
          )}
        </section>
      </div>
    </div>
  );
}
