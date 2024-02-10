import React, { useState } from "react";
import CircularProgress from "@mui/material/CircularProgress";
import "./Chat.css";

const serverBaseUrl = "http://localhost:8000";

function Chat() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
const [loading, setLoading] = useState(false);

  const handleUserInput = (e) => {
    setUserInput(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessages(messages => [...messages, { text: userInput, user: true }]);
    var response = await sendToApi(userInput);
    setMessages(messages => [...messages, { text: response.response, user: false }]);
    setUserInput("");
    setLoading(false);
  };

const sendToApi = async (message) => {
  const requestOptions = {
    method: "POST",
    headers: { "Content-Type": "application/json; charset=utf-8" },
    body: JSON.stringify({ conversation: messages.map((message) => { return { "role": message.user ? "user" : "assistant", "content": message.text } }).concat({ "role": "user", "content": message }) }),
  };
  const response = await fetch(`${serverBaseUrl}/ask`, requestOptions);
  return response.json();
};

  return (
    <div className="Chat">
      <div className="chat-timeline">
        {messages.map((message, index) => (
          <div key={index} className={message.user ? "user-message" : "assistant-message"}>
            <span className={message.user ? "user-message-head" : "assistant-message-head"}>{message.user ? "Vous" : "Buggy Boo Le Grand Sage"}</span>
            <hr className="message-bar"/>
            <span>{message.text}</span>
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="user-input-form">
        <input
          className="user-input"
          type="text"
          value={userInput}
          onChange={handleUserInput}
          placeholder="Type your message here..."
          disabled={loading}
        />
        <button type="submit">{loading ? <CircularProgress size={24} /> : "Send"}</button>
      </form>
    </div>
  );
}

export default Chat;