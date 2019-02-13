import React from 'react';
import ReactDOM from 'react-dom';
import TimeChart from './TimeChart';


it('shows current time', () => {
  const div = document.createElement('div');
  ReactDOM.render(<TimeChart />, div);
  //TODO write a real test
  expect(div).toEqual(<div><div class="TimeChart">This is a time chart:</div></div>);
  ReactDOM.unmountComponentAtNode(div);
});
