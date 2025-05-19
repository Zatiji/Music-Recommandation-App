import "../styles/Messages.css"

function UserMessage({ text }) {
  return (
    <div className="user-message">
      {text}
    </div>
  );
}

export default UserMessage;