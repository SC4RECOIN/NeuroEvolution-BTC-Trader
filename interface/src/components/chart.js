import React from 'react';
import { Row, Col, Button } from 'antd';
import {
  ComposedChart, Line, Scatter, XAxis, YAxis, CartesianGrid, ResponsiveContainer
} from 'recharts';

import { genPriceUpdate, genGenUpdate } from './../socket';

class Chart extends React.Component {
  constructor(props) {
    super(props);

    genPriceUpdate((err, data) => {
      console.log("Data received");
      this.setState({ 
        chartData: data.generation_trades,
        generationBest: data.generation
      })
    });

    genGenUpdate((err, data) => {
      console.log("Gen data received");
      this.setState({ 
        genData: data.results,
        generation: data.generation
      })
    });
  }
    
  state = {
    generationBest: 0,
    genData: "",
    generation: 0,
    loading: false,
    chartData: null,
    botROI: "",
    holdROI: ""
  }

  sendTest = () => {}

  render() {
    const data = this.state.chartData || [];

    return (
      <div className="chart">
        <Row>
          <div style={{overflowX: "scroll", overflowY: "hidden", marginBottom: "1.2em" }}>
            <div style={{ width: data.length * 3, height: 400}}>
              <ResponsiveContainer>
              <ComposedChart 
                data={data}
                margin={{
                  top: 10, right: 30, left: 0, bottom: 0
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis />
                <YAxis domain={['dataMin', 'dataMax']}/>
                <Line type="linear" dataKey="price" stroke="#8884d8" dot={false} />
                <Scatter dataKey="buy" fill="green" />
                <Scatter dataKey="sell" fill="red" />
              </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Row>
        <Row>
          <Col span={4}>
            <Button style={{marginTop: "1em"}} ghost loading={this.state.loading} onClick={this.sendTest}>Train</Button>
          </Col>
        </Row>
        <Row>
          <Col span={12}>
            <p style={{marginTop: 30}}><b>Results</b></p>
            <p>Overall best generation: {this.state.generationBest}</p>
            <p>Current generation: {this.state.generation}</p>
            <p>{JSON.stringify(this.state.genData)}</p>
          </Col>
        </Row>
      </div>
    );
  }
}

export default Chart;