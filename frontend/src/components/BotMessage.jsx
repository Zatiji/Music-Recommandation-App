import "../styles/Messages.css"

function BotMessage({ text }) {
  return (
    <div className="bot-message">
      {text}
    </div>
  );
}

export default BotMessage;