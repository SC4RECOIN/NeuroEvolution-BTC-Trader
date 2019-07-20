import React from 'react';
import { Row, Col, Progress } from 'antd';
import { genGenUpdate, genGenProgress } from '../../socket';

class Results extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      generation: 0,
      progress: 0
    }

    genGenUpdate((err, data) => {
      console.log("Gen data received");
      this.setState({ 
        avgScore: data.results.average_score,
        bestScore: data.results.best_score,
        recordScore: data.results.record_score,
        generation: data.generation,
        hold: data.results.hold
      })
    });

    genGenProgress((err, data) => {
      this.setState({ 
        progress: data.progress
      })
    });
  }

  render() {
    return (
      <div className="results">
        <Progress percent={this.state.progress} status="active" />
        <p style={{marginTop: 30}}><b>Results</b></p>
        <Row>
          <Col span={4}>
            <p>Current generation: </p>
            <p>Average score: </p>
            <p>Best score: </p>
            <p>Record score: </p>
            <p>Hold ROI: </p>
          </Col>
          <Col span={4}>
            <p>{this.state.generation}</p>
            <p>{this.state.avgScore}%</p>
            <p>{this.state.bestScore}%</p>
            <p>{this.state.recordScore}%</p>
            <p>{this.state.hold}%</p>
          </Col>
        </Row>
      </div>
    );
  }
}

export default Results;