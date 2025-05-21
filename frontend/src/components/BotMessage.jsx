import "../styles/Messages.css";
import reactLogo from "../assets/react.svg";

function BotMessage({ text }) {
	return (
		<>
			<div className="bot-message">{text}</div>
			<div className="image-in-bot-message">
				<img
					src={reactLogo}
					alt="image-in-bot-message"
					className="image-in-bot-message"
				/>
			</div>
		</>
	);
}

export default BotMessage;
