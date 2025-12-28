// src/App.jsx
import { useState } from "react";
import ChatContainer from "./components/ChatContainer";
import Sidebar from "./components/Sidebar";
import UserInput from "./components/UserInput";
import useChatSessions from "./hooks/useChatSessions";
import { streamChatResponse } from "./service/chatApi";
import "./styles/Containers.css";

function App() {
  const {
    chats,
    activeChat,
    activeChatId,
    setActiveChatId,
    appendAssistantChunk,
    appendUserMessage,
    createAssistantPlaceholder,
    clearActiveStream,
    setActiveStream,
    createNewChat,
    deleteChat,
    renameChat,
  } = useChatSessions();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

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

  const handleNewChat = () => {
    clearActiveStream();
    createNewChat();
  };

  const handleSelectChat = (chatId) => {
    if (chatId === activeChatId) return;
    clearActiveStream();
    setActiveChatId(chatId);
  };

  const handleDeleteChat = (chatId) => {
    clearActiveStream();
    deleteChat(chatId);
  };

  const handleRenameChat = (chatId, title) => {
    renameChat(chatId, title);
  };

  return (
    <div className="app-shell">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(prev => !prev)}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
        onRenameChat={handleRenameChat}
      />
      <div className="app-container">
        <ChatContainer messages={activeChat.messages} />
        <UserInput onSend={handleSendMessage} />
      </div>
    </div>
  );
}

export default App;
