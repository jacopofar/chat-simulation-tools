import React, { Component } from 'react';
import './App.css';
import HourDisplay from './HourDisplay';
import TimeChart from './TimeChart';

class App extends Component {
  render() {
    const k = {
      '2019-02-13T16:07:04.370Z': 23,
      '2019-02-12T15:07:04.370Z': 15,
      '2019-02-11T15:07:04.370Z': 10,
      '2019-02-11T16:07:04.370Z': 10,
    };

    return (
      <div className="App">
        <header className="App-header">
          <HourDisplay/>
          <TimeChart values={k} level='day'/>
        </header>
      </div>
    );
  }
}

export default App;
