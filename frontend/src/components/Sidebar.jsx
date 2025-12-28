import { useEffect, useState } from "react";
import { FaChevronLeft, FaChevronRight, FaPlus, FaTrash, FaPen } from "react-icons/fa";

function Sidebar({
  chats,
  activeChatId,
  isCollapsed,
  onToggleCollapse,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  onRenameChat,
}) {
  const [menuState, setMenuState] = useState({
    isOpen: false,
    x: 0,
    y: 0,
    chatId: null,
  });
  const [editingChatId, setEditingChatId] = useState(null);
  const [editingValue, setEditingValue] = useState("");

  const getChatLabel = (chat) => {
    const firstUserMessage = chat.messages.find(m => m.type === "user-message");
    const hasCustomTitle = chat.title && chat.title.trim() !== "" && chat.title !== "New chat";
    const rawLabel = hasCustomTitle
      ? chat.title
      : firstUserMessage?.content?.trim() || chat.title || "New chat";
    const singleLine = rawLabel.split("\n")[0];
    if (singleLine.length > 32) return `${singleLine.slice(0, 32)}...`;
    return singleLine;
  };

  useEffect(() => {
    if (!menuState.isOpen) return;
    const handleClose = () => setMenuState(prev => ({ ...prev, isOpen: false }));
    const handleKey = (event) => {
      if (event.key === "Escape") handleClose();
    };
    window.addEventListener("click", handleClose);
    window.addEventListener("keydown", handleKey);
    return () => {
      window.removeEventListener("click", handleClose);
      window.removeEventListener("keydown", handleKey);
    };
  }, [menuState.isOpen]);

  const handleContextMenu = (event, chatId) => {
    event.preventDefault();
    setMenuState({
      isOpen: true,
      x: event.clientX,
      y: event.clientY,
      chatId,
    });
  };

  const handleDeleteChat = () => {
    if (!menuState.chatId) return;
    onDeleteChat(menuState.chatId);
    setMenuState(prev => ({ ...prev, isOpen: false }));
  };

  const handleRenameRequest = () => {
    const chat = chats.find(item => item.id === menuState.chatId);
    if (!chat) return;
    setEditingChatId(chat.id);
    setEditingValue(chat.title && chat.title !== "New chat" ? chat.title : getChatLabel(chat));
    setMenuState(prev => ({ ...prev, isOpen: false }));
  };

  const handleRenameCommit = () => {
    if (!editingChatId) return;
    onRenameChat(editingChatId, editingValue);
    setEditingChatId(null);
    setEditingValue("");
  };

  const handleRenameCancel = () => {
    setEditingChatId(null);
    setEditingValue("");
  };

  return (
    <aside className={`sidebar ${isCollapsed ? "collapsed" : ""}`}>
      <div className="sidebar-header">
        <button className="sidebar-button" onClick={onNewChat} title="New chat">
          <FaPlus />
          {!isCollapsed && <span>New chat</span>}
        </button>
        <button
          className="sidebar-button ghost"
          onClick={onToggleCollapse}
          title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {isCollapsed ? <FaChevronRight /> : <FaChevronLeft />}
          {!isCollapsed && <span>Collapse</span>}
        </button>
      </div>
      <div className="session-list">
        {chats.map(chat => (
          <button
            key={chat.id}
            className={`session-item ${chat.id === activeChatId ? "active" : ""}`}
            onClick={() => onSelectChat(chat.id)}
            onContextMenu={(event) => handleContextMenu(event, chat.id)}
            title={getChatLabel(chat)}
            disabled={editingChatId === chat.id}
          >
            {editingChatId === chat.id ? (
              <input
                className="session-title-input"
                value={editingValue}
                autoFocus
                onChange={(event) => setEditingValue(event.target.value)}
                onClick={(event) => event.stopPropagation()}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    handleRenameCommit();
                  } else if (event.key === "Escape") {
                    event.preventDefault();
                    handleRenameCancel();
                  }
                }}
                onBlur={handleRenameCommit}
              />
            ) : (
              <span className="session-title">{getChatLabel(chat)}</span>
            )}
          </button>
        ))}
      </div>
      {menuState.isOpen && (
        <div
          className="session-menu"
          style={{ top: `${menuState.y}px`, left: `${menuState.x}px` }}
          role="menu"
        >
          <button className="session-menu-button" onClick={handleRenameRequest}>
            <FaPen />
            <span>Rename</span>
          </button>
          <button className="session-menu-button" onClick={handleDeleteChat}>
            <FaTrash />
            <span>Delete chat</span>
          </button>
        </div>
      )}
    </aside>
  );
}

export default Sidebar;
