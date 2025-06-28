import { useState, useRef, useEffect } from "react";
import "../styles/UserInput.css";
import { FaArrowUp } from "react-icons/fa";

function UserInput({ onSend}) {
	const [userInput, setUserInput] = useState("");
	const textareaRef = useRef(null);
	const initialHeightRef = useRef(null);

	useEffect(() => {
		if (textareaRef.current) {
			initialHeightRef.current = textareaRef.current.scrollHeight;
		}
	}, []);

	const handleSend = () => {
		if (onSend) onSend(userInput);
    	setUserInput("");

		if (textareaRef.current) {
			textareaRef.current.style.height = initialHeightRef.current
				? `${initialHeightRef.current}px`
				: "auto";
		}
	};

	const handleChange = (e) => {
		setUserInput(e.target.value);
		if (e.target.value.includes("\n") || e.target.value.length > 30) {
			e.target.style.height = "auto";
			e.target.style.height = `${e.target.scrollHeight}px`;
		} else if (initialHeightRef.current) {
			e.target.style.height = `${initialHeightRef.current}px`;
		}
	};

	return (
		<div className="user-input-container">
			<textarea
				ref={textareaRef}
				className="user-input-field"
				placeholder="Écris quelque chose..."
				value={userInput}
				onChange={handleChange}
				rows={1}
				onKeyDown={(e) => {
					if (e.key === "Enter" && !e.shiftKey) {
						e.preventDefault();
						handleSend();
					}
				}}
			/>
			<button className="send-button" onClick={handleSend}>
				<FaArrowUp />
			</button>
		</div>
	);
}

export default UserInput;
