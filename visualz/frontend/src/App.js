import React, { Component } from 'react';
import './App.css';
import './ChatMessage';
import 'semantic-ui-css/semantic.min.css';
import GridLayout from 'react-grid-layout';
import { Form } from 'semantic-ui-react';
import axios from 'axios';
import ChatMessage from './ChatMessage';

class App extends Component {

  state = { searchKeyword: '', searchResults: null };

  handleChange = (e, { name, value }) => this.setState({ [name]: value });

  handleSubmit = () => {
    axios.get('/messages', {
      params: {
        query: this.state.searchKeyword
      }
    })
    .then( (response) => {
      this.setState({ searchResults: response.data})
    })
    console.log('submitted:', this.state.searchKeyword);
  };

  render() {
    let layout = [
      {i: 'a', x: 1, y: 0, w: 11, h: 2, static: true},
      {i: 'b', x: 1, y: 3, w: 10, h: 2, minW: 2, maxW: 10,  static: true},
      {i: 'c', x: 12, y: 0, w: 1, h: 2}
    ];
    return (
      <div className="App">
        <GridLayout className="layout" layout={layout} cols={12} rowHeight={30} width={1200}>
          <div className="search__text" key="a">
            <Form onSubmit={this.handleSubmit}>
              <Form.Input size='small' icon='search' placeholder='Search...' name='searchKeyword' onChange={this.handleChange} />
            </Form>
          </div>
          <div key="b">
          {this.state.searchResults != null &&
          <p className="search__result__description"><strong>{this.state.searchResults.length} results</strong> for "{this.state.searchKeyword}" </p>
          }
          {this.state.searchResults != null &&
          this.state.searchResults.map(r =>
           <ChatMessage key= {r.uuid} message={r}/>
          )
          }</div>
          <div key="c">placeholder 2</div>
        </GridLayout>
      </div>
      );
    }
  }

  export default App;
