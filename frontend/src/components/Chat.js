import './Chat.css';

function Chat() {
  return (
    <div className="Chat">
      <header className='chat-header'>
        <div className='chat-timeline'>
          Les réponses vont apparaître ici
        </div>
        <input className='user-input'></input>
      </header>
    </div>
  );
}

export default Chat;
