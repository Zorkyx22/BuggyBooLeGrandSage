import './Chat.css';
import ChatBubbleArea from './ChatBubbleArea';

function Chat() {
  const chats = [["user","Bonjour"], ["assistant","Bonjour! Ça va?"], ["user","Bien sur! Et toi?"], ["assistnt","Moi je m'en sors. Comment va la famille?"], ["user","Très bien!"]]
  return (
    <div className="Chat">
      <header className='chat-header'>
        <ChatBubbleArea history={chats}/>
        <input className='user-input'></input>
      </header>
    </div>
  );
}

export default Chat;
