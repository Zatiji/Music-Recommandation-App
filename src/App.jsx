import "./styles/App.css";
import reactLogo from "./assets/react.svg";
import React from "react";
import UserInput from "./components/UserInput";

function App() {
	return (
		<>
			<div class="app-container">
				<img
					src={reactLogo}
					alt="idle-image-container"
					className="idle-image"
				/>
        <UserInput />
			</div>
		</>
	);
}

export default App;
