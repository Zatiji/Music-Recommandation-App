export async function streamChatResponse({
  message,
  sessionId,
  signal,
  onChunk,
  onCards,
  onDone,
}) {
  const response = await fetch("http://localhost:5001/generate-response", {
    method: "POST",
    headers: { "Content-Type": "application/json", "Accept": "text/event-stream" },
    body: JSON.stringify({ message, session_id: sessionId }),
    signal,
  });

  if (!response.ok || !response.body) {
    throw new Error(`HTTP ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    let idx;
    while ((idx = buffer.indexOf("\n\n")) !== -1) {
      const eventBlock = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);

      const dataLines = eventBlock
        .split(/\r?\n/)
        .filter(line => line.startsWith("data:"))
        .map(line => (line.startsWith("data: ") ? line.slice(6) : line.slice(5)));

      for (const line of dataLines) {
        try {
          const obj = JSON.parse(line);
          if (obj.done) {
            if (onDone) onDone();
            continue;
          }
          if (Array.isArray(obj.cards)) {
            if (onCards) onCards(obj.cards, obj.source || "lastfm");
            continue;
          }
          if (typeof obj.delta === "string") {
            onChunk(obj.delta);
          }
        } catch {
          onChunk(line);
        }
      }
    }
  }
}
