// src/App.jsx
import ChatContainer from "./components/ChatContainer";
import UserInput from "./components/UserInput";
import useChatSessions from "./hooks/useChatSessions";
import { streamChatResponse } from "./service/chatApi";
import "./styles/Containers.css";

function App() {
  const {
    activeChat,
    activeChatId,
    appendAssistantChunk,
    appendUserMessage,
    createAssistantPlaceholder,
    clearActiveStream,
    setActiveStream,
  } = useChatSessions();

  const handleSendMessage = async (newMessage) => {
    if (!newMessage || !newMessage.trim()) return;

    appendUserMessage(newMessage);

    const assistantId = createAssistantPlaceholder();

    clearActiveStream();
    const controller = new AbortController();
    setActiveStream(controller);

    try {
      await streamChatResponse({
        message: newMessage,
        sessionId: activeChatId,
        signal: controller.signal,
        onChunk: (chunk) => appendAssistantChunk(assistantId, chunk),
      });
    } catch (err) {
      console.error("Stream error:", err);
      appendAssistantChunk(assistantId, "\n[Error while streaming response]");
    } finally {
      clearActiveStream();
    }
  };

  return (
    <div className="app-container">
      <ChatContainer messages={activeChat.messages} />
      <UserInput onSend={handleSendMessage} />
    </div>
  );
}

export default App;
