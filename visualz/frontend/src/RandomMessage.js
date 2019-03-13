import React, { Component } from 'react';
import './App.css';
import './ChatMessage';
import 'semantic-ui-css/semantic.min.css';
import axios from 'axios';
import ChatMessage from './ChatMessage';

class RandomMessage extends Component {
  state = {message: null };

  componentDidMount = () => {
    axios.get('/random_message')
    .then( (response) => {
      this.setState({ message: response.data})
    })
  };

  render() {
    return (
      <div className="RandomMessage">
      {this.state.message?
        <ChatMessage message={this.state.message}/>
        :'still loading...'}
      </div>
      );
    }
  }

  export default RandomMessage;
