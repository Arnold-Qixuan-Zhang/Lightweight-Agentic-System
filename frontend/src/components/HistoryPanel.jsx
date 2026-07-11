export default function HistoryPanel({ history, onSelect, onExport, loading }) {
  return (
    <section className="panel history-panel">
      <div className="history-header">
        <h2>History</h2>
        <button type="button" onClick={onExport} disabled={loading}>
          Export History
        </button>
      </div>

      {loading && <p className="placeholder">Loading history...</p>}

      {!loading && history.length === 0 && (
        <p className="placeholder">No tasks yet. Run your first instruction above.</p>
      )}

      {!loading && history.length > 0 && (
        <ul className="history-list">
          {history.map((record) => (
            <li key={record.id}>
              <button
                type="button"
                className="history-item"
                onClick={() => onSelect(record)}
              >
                <span className="history-instruction">{record.instruction}</span>
                <span className="history-meta">
                  {record.tool} · {formatDate(record.created_at)}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function formatDate(isoString) {
  try {
    return new Date(isoString).toLocaleString();
  } catch {
    return isoString;
  }
}
