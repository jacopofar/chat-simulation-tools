import React, { Component } from 'react';
import './App.css';
import 'semantic-ui-css/semantic.min.css';
import GridLayout from 'react-grid-layout';
import { Form } from 'semantic-ui-react'

class App extends Component {
  state = { searchKeyword: '' };

  handleChange = (e, { name, value }) => this.setState({ [name]: value });

  handleSubmit = () => {
    console.log('submitted:', this.state.searchKeyword);
  };

  render() {
    let layout = [
      {i: 'a', x: 1, y: 0, w: 11, h: 2, static: true},
      {i: 'b', x: 1, y: 0, w: 3, h: 2, minW: 2, maxW: 4},
      {i: 'c', x: 4, y: 0, w: 1, h: 2}
    ];
    return (
      <div className="App">
        <GridLayout className="layout" layout={layout} cols={12} rowHeight={30} width={1200}>
          <div className="search__text" key="a">
            <Form onSubmit={this.handleSubmit}>
              <Form.Input size='small' icon='search' placeholder='Search...' name='searchKeyword' onChange={this.handleChange} />
            </Form>
          </div>
          <div key="b">placeholder 1</div>
          <div key="c">placeholder 2</div>
        </GridLayout>
      </div>
      );
    }
  }

  export default App;
