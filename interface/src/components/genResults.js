import React from 'react';
import { Row, Col } from 'antd';
import { genGenUpdate } from '../socket';

class Results extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      genData: "",
      generation: 0
    }

    genGenUpdate((err, data) => {
      console.log("Gen data received");
      this.setState({ 
        avgScore: data.results.average_score,
        bestScore: data.results.best_score,
        recordScore: data.results.record_score,
        generation: data.generation
      })
    });
  }

  render() {
    return (
      <div className="results">
        <Row>
          <Col span={4}>
            <p style={{marginTop: 30}}><b>Results</b></p>
            <p>Current generation: {this.state.generation}</p>
            <p>Average score: {this.state.avgScore}</p>
            <p>Best score: {this.state.bestScore}</p>
            <p>Record score: {this.state.recordScore}</p>
          </Col>
        </Row>
      </div>
    );
  }
}

export default Results;