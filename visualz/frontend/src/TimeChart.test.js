import React from 'react';
import ReactDOM from 'react-dom';
import TimeChart from './TimeChart';

it('Shows an empty placeholder in absence of values', () => {
  const div = document.createElement('div');
  ReactDOM.render(<TimeChart/>, div);
  expect(div.children[0].textContent).toEqual("This is a time chart:");
  expect(div.children.length).toEqual(1);
  ReactDOM.unmountComponentAtNode(div);
});

// skipped, yet to find a nice way to do the unit test
xit('Performs the sum', () => {
  const div = document.createElement('div');
  const component = ReactDOM.render(<TimeChart values={{}}/>, div).getInstance();
  console.log(component);
  component.groupBy({
    '2019-02-13T16:07:04.370Z': 23,
    '2019-02-12T15:07:04.370Z': 15,
    '2019-02-11T15:07:04.370Z': 10,
    '2019-02-11T16:07:04.370Z': 11,
  }).toEqual([])
})

it('Aggregates by day', () => {
  const k = {
    '2019-02-13T16:07:04.370Z': 23,
    '2019-02-12T15:07:04.370Z': 15,
    '2019-02-11T15:07:04.370Z': 10,
    '2019-02-11T16:07:04.370Z': 11,
  };
  const div = document.createElement('div');
  ReactDOM.render(<TimeChart values={k}/>, div);
  expect(div.children[0].children.length).toEqual(3);
  expect(div.children[0].children[0].textContent).toEqual('2019-02-11: 21');
  expect(div.children[0].children[1].textContent).toEqual('2019-02-12: 15');
  expect(div.children[0].children[2].textContent).toEqual('2019-02-13: 23');

  ReactDOM.unmountComponentAtNode(div);
});
