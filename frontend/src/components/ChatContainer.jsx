import UserMessage from "./UserMessage";
import reactLogo from "../assets/react.svg";
import { useEffect, useRef } from "react";
import "../styles/Containers.css"

function ChatContainer({ messages }) {
    const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages]);

  return ( 
    <div className={`chat-container ${messages.length === 0 ? "empty" : ""}`} ref={containerRef}>
      {messages.length === 0 ? (
        <img src={reactLogo} alt="idle-image-container" className="idle-image" />
      ) : (
        messages.map((msg, index) => (
          <UserMessage key={index} text={msg} />
        ))
      )}
    </div>
  );
}

export default ChatContainer;