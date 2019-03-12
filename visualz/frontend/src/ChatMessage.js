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
    <time dateTime={message.timestamp}>{message.timestamp}</time>
    <p>{message.text}</p>
    {showDeptree &&
      <img className="chat__message-analysis" src={"/analyze?text=" + message.text + "&style=dep"}/>
    }
    <span onClick={toggleDepTree}>[Dependency tree]</span>
    </div>
    );
  }

  export default ChatMessage;
