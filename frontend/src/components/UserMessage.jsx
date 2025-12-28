import "../styles/MessageBase.css";
import "../styles/UserMessage.css";

function UserMessage({ text }) {
  return (
    <div className="message user-message">
      {text}
    </div>
  );
}

export default UserMessage;
