import './Chat.css';
import ChatBubble from './ChatBubble';

function ChatBubbleArea(props) {
    let chatHistory = props.history
  return (
    <div className="chat-bubble-area">
        {chatHistory.map((item)=><ChatBubble role={item[0]} text={item[1]}/>)}
    </div>
  );
}

export default ChatBubbleArea;