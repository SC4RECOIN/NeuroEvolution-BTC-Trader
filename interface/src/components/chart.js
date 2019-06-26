import React from 'react';
import { Slider, Row, Col, Button } from 'antd';
import {
  ComposedChart, Line, Scatter, XAxis, YAxis, CartesianGrid, ResponsiveContainer
} from 'recharts';

import { subscribeToTimer } from './../socket';

class Chart extends React.Component {
  constructor(props) {
    super(props);

    subscribeToTimer((err, data) => {
      this.setState({ 
        generation: data.generation 
      })
      console.log("socket event received");
  });
  }
    
  state = {
    generation: 0,
    loading: false,
    chartData: null,
    testSize: 20,
    testBack: true,
    botROI: "",
    holdROI: ""
  }

  updateTestSize = (e) => {
    this.setState({testSize: e})
  }

  sendTest = () => {
    this.setState({loading: true})
    fetch("http://localhost:5000/train", { 
      method: "POST",
      headers: {'content-type': 'application/json'},
      body: JSON.stringify({
        testSize: this.state.testSize/100,
        testBack: this.state.testBack
      })
    })
    .then(res => res.json())
    .then(res =>  {
      this.setState({
        loading: false,
        chartData: res.data,
        botROI: res.bot_roi,
        holdROI: res.holding_roi
      });
    })
    .catch(e => {
      console.log(`Error sending training request: ${e}`);
      this.setState({loading: false});
    })
  }

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
            <span style={{marginLeft: 4}}>Test size</span>
            <Slider defaultValue={20} onChange={this.updateTestSize}/>
            <Button style={{marginTop: "1em"}} ghost loading={this.state.loading} onClick={this.sendTest}>Train</Button>
          </Col>
        </Row>
        <Row>
          <Col span={12}>
            <p style={{marginTop: 30}}><b>Results</b></p>
            <p>Bot ROI: {this.state.botROI}%</p>
            <p>Hold ROI: {this.state.holdROI}%</p>
            <p>Generation: {this.state.generation}</p>
          </Col>
        </Row>
      </div>
    );
  }
}

export default Chart;