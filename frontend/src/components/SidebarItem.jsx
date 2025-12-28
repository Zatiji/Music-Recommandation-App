function SidebarItem({
  isActive,
  isEditing,
  editingValue,
  onSelect,
  onContextMenu,
  onEditValueChange,
  onCommit,
  onCancel,
  label,
}) {
  return (
    <button
      className={`session-item ${isActive ? "active" : ""}`}
      onClick={onSelect}
      onContextMenu={onContextMenu}
      title={label}
      disabled={isEditing}
    >
      {isEditing ? (
        <input
          className="session-title-input"
          value={editingValue}
          autoFocus
          onChange={onEditValueChange}
          onClick={(event) => event.stopPropagation()}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              onCommit();
            } else if (event.key === "Escape") {
              event.preventDefault();
              onCancel();
            }
          }}
          onBlur={onCommit}
        />
      ) : (
        <span className="session-title">{label}</span>
      )}
    </button>
  );
}

export default SidebarItem;
