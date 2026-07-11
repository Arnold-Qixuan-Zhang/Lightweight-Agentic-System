export default function ExecutionTrace({ trace, result, error }) {
  if (error) {
    return (
      <section className="panel trace-panel">
        <h2>Execution Trace</h2>
        <p className="error-message">{error}</p>
      </section>
    );
  }

  if (!trace || trace.length === 0) {
    return (
      <section className="panel trace-panel">
        <h2>Execution Trace</h2>
        <p className="placeholder">Submit an instruction to see the agent steps.</p>
      </section>
    );
  }

  return (
    <section className="panel trace-panel">
      <h2>Execution Trace</h2>
      <ol className="trace-list">
        {trace.map((step) => (
          <li key={step.step}>
            <strong>Step {step.step}:</strong> {step.message}
          </li>
        ))}
      </ol>
      {result !== null && result !== undefined && (
        <div className="result-box">
          <h3>Result</h3>
          <pre>{formatResult(result)}</pre>
        </div>
      )}
    </section>
  );
}

function formatResult(result) {
  if (typeof result === "object") {
    return JSON.stringify(result, null, 2);
  }
  return String(result);
}
