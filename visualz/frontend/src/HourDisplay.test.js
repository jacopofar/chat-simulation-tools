import React from 'react';
import ReactDOM from 'react-dom';
import HourDisplay from './HourDisplay';

let currentDate;

// trick from https://github.com/facebook/jest/issues/2234
beforeAll(() => {
  currentDate = new Date();

  const RealDate = Date;
  global.Date = jest.fn(() => new RealDate('2018-07-23T12:34:56'));
  Object.assign(Date, RealDate);
});

it('shows current time', () => {
  Date.now = jest.fn(() => new Date(Date.UTC(2017, 0, 1)).valueOf());
  const div = document.createElement('div');
  ReactDOM.render(<HourDisplay />, div);
  expect(div.querySelector('time').dateTime).toEqual('2018-07-23T10:34:56.000Z');
  ReactDOM.unmountComponentAtNode(div);
});
