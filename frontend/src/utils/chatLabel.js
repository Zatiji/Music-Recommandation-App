export function getChatLabel(chat) {
  const firstUserMessage = chat.messages.find(m => m.type === "user-message");
  const hasCustomTitle = chat.title && chat.title.trim() !== "" && chat.title !== "New chat";
  const rawLabel = hasCustomTitle
    ? chat.title
    : firstUserMessage?.content?.trim() || chat.title || "New chat";
  const singleLine = rawLabel.split("\n")[0];
  if (singleLine.length > 32) return `${singleLine.slice(0, 32)}...`;
  return singleLine;
}
