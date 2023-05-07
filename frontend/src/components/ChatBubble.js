import './Chat.css';

function ChatBubble(props) {
  return (
    <div className={`chat-bubble ${props.role}`}>
        {props.text}
    </div>
  );
}

export default ChatBubble;