import React from 'react';
import './App.css';

function TimeChart({ values }) {

  const binTimestamp = (timestamp, level) => {
    if (level === 'day')
      return timestamp.substr(0, 10);
    if (level === 'month')
      return timestamp.substr(0, 7);
    if (level === 'year')
      return timestamp.substr(0, 4);
    throw Error(`unknown time level ${level}`);
  };

  const groupBy = (values, level = 'day') => {
    const bins = {};
    for (let timestamp in values) {
      let targetBin = binTimestamp(timestamp, level);
      bins[targetBin] = (bins[targetBin] || []).concat([values[timestamp]]);
    }
    return Object.entries(bins).sort((a, b) => a[0] > b[0] ? 1 : -1);
  };

  const sumBy = (values, level = 'day') => {
    return groupBy(values, level).map(
      ([k, vals]) => [k, vals.reduce((a, b) => a+b, 0)]);
  };


  return (
    <div className="TimeChart">
    This is a time chart:
    {sumBy(values, 'day').map(([k, v]) => <p key={k}>{k}: {v}</p>)}
    </div>
    );
  }

  export default TimeChart;
