import { useState } from "react";

export default function InstructionInput({ onSubmit, loading }) {
  const [instruction, setInstruction] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    const trimmed = instruction.trim();
    if (!trimmed || loading) return;
    onSubmit(trimmed);
  };

  return (
    <form className="instruction-form" onSubmit={handleSubmit}>
      <label htmlFor="instruction">Enter your instruction</label>
      <textarea
        id="instruction"
        value={instruction}
        onChange={(e) => setInstruction(e.target.value)}
        placeholder='e.g. "convert hello world to uppercase" or "weather in Toronto"'
        rows={3}
        disabled={loading}
      />
      <button type="submit" disabled={loading || !instruction.trim()}>
        {loading ? "Running..." : "Run"}
      </button>
    </form>
  );
}
