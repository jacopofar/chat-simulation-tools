import React, {useState} from 'react';
import './ChatMessage.css';

function ChatMessage({ message }) {
  const [showDeptree, setshowDeptree] = useState(false);
  const toggleDepTree = () => {
    setshowDeptree(!showDeptree);
  }
  return (
    <div className="chat__message-box">
    <span className="chat__message-user">{message.user_print_name}</span>
    <time className="chat__message-timestamp" dateTime={message.timestamp}>{message.timestamp}</time>
    <button className="chat__message-analysis-deptree" onClick={toggleDepTree}>See dependency tree</button>
    <p className="chat__message-text">{message.text}</p>
    {showDeptree &&
      <img className="chat__message-analysis" alt="dependency tree for the text" src={"/analyze?text=" + message.text + "&style=dep"}/>
    }
    </div>
    );
  }

  export default ChatMessage;
