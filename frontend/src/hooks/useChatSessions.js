import { useEffect, useRef, useState, useCallback } from "react";

const STORAGE_KEY = "chat_sessions_v1";

function getInitialChats() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed;
      }
    }
  } catch {
    // ignore storage errors and fall back to default chat
  }
  return [
    {
      id: crypto.randomUUID(),
      title: "New chat",
      messages: [],
    },
  ];
}

export default function useChatSessions() {
  const [chats, setChats] = useState(getInitialChats);
  const [activeChatId, setActiveChatId] = useState(() => chats[0].id);
  const abortRef = useRef(null);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
    } catch {
      // ignore storage errors
    }
  }, [chats]);

  const activeChat = chats.find(chat => chat.id === activeChatId) || chats[0];

  const appendAssistantChunk = useCallback((id, chunk) => {
    setChats(prev =>
      prev.map(chat => {
        if (chat.id !== activeChatId) return chat;
        return {
          ...chat,
          messages: chat.messages.map(m =>
            m.id === id ? { ...m, content: m.content + chunk } : m
          ),
        };
      })
    );
  }, [activeChatId]);

  const appendUserMessage = useCallback((content) => {
    const userMsg = {
      id: crypto.randomUUID(),
      type: "user-message",
      content,
    };
    setChats(prev =>
      prev.map(chat =>
        chat.id === activeChatId
          ? { ...chat, messages: [...chat.messages, userMsg] }
          : chat
      )
    );
    return userMsg;
  }, [activeChatId]);

  const createAssistantPlaceholder = useCallback(() => {
    const assistantId = crypto.randomUUID();
    setChats(prev =>
      prev.map(chat =>
        chat.id === activeChatId
          ? {
              ...chat,
              messages: [...chat.messages, { id: assistantId, type: "assistant", content: "" }],
            }
          : chat
      )
    );
    return assistantId;
  }, [activeChatId]);

  const clearActiveStream = useCallback(() => {
    if (abortRef.current) abortRef.current.abort();
    abortRef.current = null;
  }, []);

  const setActiveStream = useCallback((controller) => {
    abortRef.current = controller;
  }, []);

  return {
    chats,
    activeChat,
    activeChatId,
    setActiveChatId,
    appendAssistantChunk,
    appendUserMessage,
    createAssistantPlaceholder,
    clearActiveStream,
    setActiveStream,
  };
}
