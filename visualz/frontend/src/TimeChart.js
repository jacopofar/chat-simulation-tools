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
    return bins;
  };

  const sumBy = (values, level = 'day') => {
    const aggregated = groupBy(values, level);
    const retVal = {};
    for (let ts in aggregated) {
      retVal[ts] = aggregated[ts].reduce((a,b) => a+b, 0);
    }
    return Object.entries(retVal);
  };


  return (
    <div className="TimeChart">
    This is a time chart:
    {sumBy(values, 'day').map(([k, v]) => <p key={k}>{k}: {v}</p>)}
    </div>
    );
  }

  export default TimeChart;
