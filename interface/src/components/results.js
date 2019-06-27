import React from 'react';
import { Row, Col } from 'antd';
import {  genGenUpdate } from './../socket';

class Results extends React.Component {
  constructor(props) {
    super(props);

    genGenUpdate((err, data) => {
      console.log("Gen data received");
      this.setState({ 
        genData: data.results,
        generation: data.generation
      })
    });
  }
    
  state = {
    genData: "",
    generation: 0
  }

  render() {
    return (
      <div className="results">
        <Row>
          <Col span={12}>
            <p style={{marginTop: 30}}><b>Results</b></p>
            <p>Current generation: {this.state.generation}</p>
            <p>{JSON.stringify(this.state.genData)}</p>
          </Col>
        </Row>
      </div>
    );
  }
}

export default Results;