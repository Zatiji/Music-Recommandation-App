import { useState } from "react";
import ChatContainer from "./components/ChatContainer";
import UserInput from "./components/UserInput";
import "./styles/Containers.css"

function App() {
  const [messages, setMessages] = useState([]);

  const handleSendMessage = async (newMessage) => {
    if (newMessage.trim() === "") return;

    setMessages((prevMessages) => [
      ...prevMessages,
      { type: "user-message", content: newMessage }
    ]);

    try {
      const response = await fetch("http://localhost:5001/generate-response", { // -------- Local host hardcodé !!!
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: newMessage })
      });

      const data = await response.json();

      setMessages((prevMessages) => [
        ...prevMessages,
        { type: "assistant", content: data.response }
      ]);
    } catch (error) {
      console.error(" :", error);
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
