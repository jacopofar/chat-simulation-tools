import React from 'react';
import './ChatMessage.css';

function ChatMessage({ message }) {

  return (
    <div className="chat__message-box">
    <p><span className="chat__message-user">{message.user_nick}</span>
    <time dateTime={message.timestamp}>{message.timestamp}</time></p>

    <p>{message.text}</p>
    </div>
    );
  }

  export default ChatMessage;
