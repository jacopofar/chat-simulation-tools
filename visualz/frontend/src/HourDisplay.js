import React, { useState, useEffect } from 'react';
import './App.css';

function HourDisplay() {
  const [serverTime, setServerTime] = useState(null);

  useEffect(() => {
    fetch('/time')
    .then((response) => {
      response.json().then(setServerTime)
    })
    .catch(() => {
      setServerTime(222);
    });
  }, [])

  return (
    <div className="HourDisplay">
    Hello I am an Hour Display!
    <p>browser time: <time dateTime={new Date().toISOString()}>{new Date().toISOString()}</time></p>
    <p>server time: <time dateTime={serverTime}>{serverTime}</time></p>
    </div>
    );
  }

  export default HourDisplay;
