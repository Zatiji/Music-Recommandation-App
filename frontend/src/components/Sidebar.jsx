import { FaChevronLeft, FaChevronRight, FaPlus } from "react-icons/fa";

function Sidebar({
  chats,
  activeChatId,
  isCollapsed,
  onToggleCollapse,
  onNewChat,
  onSelectChat,
}) {
  const getChatLabel = (chat) => {
    const firstUserMessage = chat.messages.find(m => m.type === "user-message");
    const rawLabel = firstUserMessage?.content?.trim() || chat.title || "New chat";
    const singleLine = rawLabel.split("\n")[0];
    if (singleLine.length > 32) return `${singleLine.slice(0, 32)}...`;
    return singleLine;
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
            title={getChatLabel(chat)}
          >
            <span className="session-title">{getChatLabel(chat)}</span>
          </button>
        ))}
      </div>
    </aside>
  );
}

export default Sidebar;
