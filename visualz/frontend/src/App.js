import React, { Component } from 'react';
import './App.css';
import HourDisplay from './HourDisplay';

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <HourDisplay/>
        </header>
      </div>
    );
  }
}

export default App;
