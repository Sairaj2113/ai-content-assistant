import { useState } from "react";
import { createEntry } from "../api.js";

const MAX_LENGTH = 5000;

export default function EntryForm({ onCreated }) {
  const [text, setText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const tooLong = text.length > MAX_LENGTH;
  const canSubmit = text.trim() !== "" && !tooLong && !submitting;

  async function handleSubmit(event) {
    event.preventDefault();
    if (!canSubmit) return;
    setSubmitting(true);
    setError("");
    try {
      const entry = await createEntry(text);
      setText("");
      onCreated(entry);
    } catch (err) {
      // Keep the text in the box so the user can retry.
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <label htmlFor="entry-text">Text to summarize</label>
      <textarea
        id="entry-text"
        rows={8}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste an article, notes, or any text…"
        disabled={submitting}
      />
      <div className="form-footer">
        <span className={tooLong ? "counter over" : "counter"}>
          {text.length} / {MAX_LENGTH}
        </span>
        <button type="submit" disabled={!canSubmit}>
          {submitting ? "Generating summary…" : "Summarize"}
        </button>
      </div>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
