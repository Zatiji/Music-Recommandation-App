import UserMessage from "./UserMessage";
import BotMessage from "./BotMessage";
import reactLogo from "../assets/react.svg";
import { useEffect, useRef } from "react";
import "../styles/Chat.css";

function ChatContainer({ messages }) {
	const containerRef = useRef(null);

	useEffect(() => {
		if (containerRef.current) {
			containerRef.current.scrollTop = containerRef.current.scrollHeight;
		}
	}, [messages]);

	return (
		<div
			className={`chat-container ${messages.length === 0 ? "empty" : ""}`}
			ref={containerRef}
		>
			{messages.length === 0 ? (
				<img
					src={reactLogo}
					alt="idle-image-container"
					className="idle-image"
				/>
			) : (
				messages.map((msg, index) => {
					if (msg.type === "user-message") {
						return <UserMessage key={index} text={msg.content} />;
					} else if (msg.type === "assistant") {
						return <BotMessage key={index} text={msg.content} />;
					} else {
						return null;
					}
				})
			)}
		</div>
	);
}

export default ChatContainer;
