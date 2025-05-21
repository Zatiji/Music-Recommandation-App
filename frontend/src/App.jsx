import { useState } from "react";
import ChatContainer from "./components/ChatContainer";
import UserInput from "./components/UserInput";
import "./styles/Containers.css"

function App() {
  const [messages, setMessages] = useState([]);

  const handleSendMessage = (newMessage) => {
  if (newMessage.trim() === "") return;

  const botResponse = "hahaHshdgufiuasdciyadvyiadvaiyudvakuyvaksuvadskvadkuvbadkvakhvbadhkvbdhkvbadhkvbadkhbadykgvadyivas !!"; // Mettre la méthode GPT ici

  setMessages((prevMessages) => [
    ...prevMessages,
    { type: "user-message", content: newMessage },
    { type: "bot-message", content: botResponse }
  ]);
};

  return (
    <div className="app-container">
      <ChatContainer messages={messages} />
      <UserInput onSend={handleSendMessage} />
    </div>
  );
}

export default App;
