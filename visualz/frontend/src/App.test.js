import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';


// Date.now = jest.fn(() => new Date(Date.UTC(2017, 0, 1)).valueOf());

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<App />, div);
  ReactDOM.unmountComponentAtNode(div);
});
