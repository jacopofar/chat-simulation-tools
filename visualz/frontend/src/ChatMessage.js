import React from 'react';
import './ChatMessage.css';

function ChatMessage({ message }) {

  return (
    <div className="chat__message-box">
    <span className="chat__message-user">{message.user_print_name}</span>
    <time dateTime={message.timestamp}>{message.timestamp}</time>
    <p>{message.text}</p>
    <img className="chat__message-analysis" src={"/analyze?text=" + message.text + "&style=dep"}/>
    </div>
    );
  }

  export default ChatMessage;
