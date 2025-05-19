import { useState } from "react";
import ChatContainer from "./components/ChatContainer";
import UserInput from "./components/UserInput";
import "./styles/Containers.css"

function App() {
  const [messages, setMessages] = useState([]);

  const handleSendMessage = (newMessage) => {
    if (newMessage.trim() === "") return;
    setMessages([...messages, newMessage]);

	
  };

  return (
    <div className="app-container">
      <ChatContainer messages={messages} />
      <UserInput onSend={handleSendMessage} />
    </div>
  );
}

export default App;
