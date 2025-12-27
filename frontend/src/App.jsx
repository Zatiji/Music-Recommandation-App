// src/App.jsx
import { useRef, useState } from "react";
import ChatContainer from "./components/ChatContainer";
import UserInput from "./components/UserInput";
import "./styles/Containers.css";

function App() {
  const [messages, setMessages] = useState([]);
  const abortRef = useRef(null);

  const appendAssistantChunk = (id, chunk) => {
    setMessages(prev =>
      prev.map(m => (m.id === id ? { ...m, content: m.content + chunk } : m))
    );
  };

  const handleSendMessage = async (newMessage) => {
    if (!newMessage || !newMessage.trim()) return;

    // push the user message
    const userMsg = {
      id: crypto.randomUUID(),
      type: "user-message",
      content: newMessage,
    };
    setMessages(prev => [...prev, userMsg]);

    // create assistant placeholder (we'll stream into this)
    const assistantId = crypto.randomUUID();
    setMessages(prev => [...prev, { id: assistantId, type: "assistant", content: "" }]);

    // cancel any previous stream
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const response = await fetch("http://localhost:5001/generate-response", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "text/event-stream" },
        body: JSON.stringify({ message: newMessage }),
        signal: controller.signal,
      });

      if (!response.ok || !response.body) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      // Parse SSE frames: blocks separated by \n\n, each line may start with "data:"
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
            .map(line => (line.startsWith("data: ") ? line.slice(6) : line.slice(5))); // don't trim

          for (const d of dataLines) {
            try {
              const obj = JSON.parse(d);
              if (obj.done) {
                // finished
                continue;
              }
              if (typeof obj.delta === "string") {
                // JSON.parse already turned "\\n" into real "\n" — perfect for Markdown
                appendAssistantChunk(assistantId, obj.delta);
              }
            } catch {
              // fallback: treat as plain text
              appendAssistantChunk(assistantId, d);
            }
          }
        }
      }
    } catch (err) {
      console.error("Stream error:", err);
      appendAssistantChunk(assistantId, "\n[Error while streaming response]");
    } finally {
      abortRef.current = null;
    }
  };

  return (
    <div className="app-container">
      <ChatContainer messages={messages} />
      <UserInput onSend={handleSendMessage} />
    </div>
  );
}

export default App;