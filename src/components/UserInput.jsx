import React from "react";
import { useState } from "react";
import "../styles/UserInput.css";
import { FaArrowUp } from "react-icons/fa";

function UserInput() {
	const [userInput, setUserInput] = useState("");

	const handleSend = () => {
		console.log("Envoyé :", userInput);
		setUserInput("");
	};

	const handleChange = (e) => {
		setUserInput(e.target.value);
		e.target.style.height = "auto";
		e.target.style.height = `${e.target.scrollHeight}px`;
	};

	return (
		<>
			<div class="user-input-container">
				<textarea
					class="user-input-field"
					type="text"
					placeholder="Écris quelque chose..."
					value={userInput}
					onChange={handleChange}
					rows={1}
				/>
				<button className="send-button" onClick={handleSend}>
					<FaArrowUp />
				</button>
			</div>
		</>
	);
}

export default UserInput;
