import React from 'react';
import { Button, Slider, Row, Col, Checkbox } from 'antd';
import {
  ComposedChart, Line, Scatter, XAxis, YAxis, CartesianGrid, ResponsiveContainer
} from 'recharts';

class Parameters extends React.Component {
  state = {
    loading: false,
    loadingTA: false,
    chartData: null,
    ohlc: null,
    sampleSize: 200
  }

  updateSampleSize = (e) => {
    this.setState({sampleSize: e})
  }

  fetchSample() {
    this.setState({loading: true});
    fetch('http://127.0.0.1:5000/sample-request', {
      headers: {'Content-Type': 'application/json'},
      method: 'POST',
      body: JSON.stringify({'sampleSize': this.state.sampleSize})
    })
      .then(r => r.json())
      .then(data => {
        console.log("Sample data received");
        let chart = [];
        Object.keys(data.close).forEach((key) => {
          chart.push({'price': data.close[key]});
        });
        this.setState({ 
          loading: false,
          ohlc: data,
          chartData: chart
        })
      })
      .catch(e => console.log(`Error fetching sample segment: ${e}`))
  }

  fetchTA() {
    this.setState({loadingTA: true});
    fetch('http://127.0.0.1:5000/ta-request', {
      headers: {'Content-Type': 'application/json'},
      method: 'POST',
      body: JSON.stringify({'ohlcData': this.state.ohlc})
    })
      .then(r => r.json())
      .then(data => {
        let taChart = [];
        Object.keys(data).forEach((key) => {
          taChart.push({'rsi': data[key]});
        });
        this.setState({ 
          loadingTA: false,
          taData: taChart
        })
      })
      .catch(e => console.log(`Error fetching ta: ${e}`))
  }

  render() {
    const data = this.state.chartData || [];
    const ta = this.state.taData || [];

    return (
      <div className="panel">
        <div style={{overflowX: "scroll", overflowY: "hidden", marginBottom: "1.2em" }}>
          <div style={{ width: Math.max(data.length * 5, 1200), height: 400}}>
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
          <div style={{ width: Math.max(data.length * 3, 1200), height: 200}}>
            <ResponsiveContainer>
            <ComposedChart 
              data={ta}
              margin={{
                top: 10, right: 30, left: 0, bottom: 0
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis />
              <YAxis domain={['dataMin', 'dataMax']}/>
              <Line type="linear" dataKey="rsi" stroke="#8884d8" dot={false} />
            </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
        <Row>
          <Col span={2}>
            <p style={{marginTop: 7}}>Segment size:</p>
          </Col>
          <Col span={12}>
            <Slider defaultValue={200} onChange={this.updateSampleSize} min={100} max={500}/>
          </Col>
        </Row>
        <Button 
          ghost
          loading={this.state.loading}
          style={{marginTop: "1em"}}  
          onClick={() => this.fetchSample()}
        >
            Get Random Segment
        </Button>
        <hr style={{marginTop: "2em"}}/>
        <p style={{'fontSize': '1.6em'}}>Technical Analysis</p>
        <Row>
          <Col span={4}>
            <Checkbox style={{color: 'white'}}>RSI</Checkbox><br/><br/>
            <Checkbox style={{color: 'white'}}>PPO</Checkbox>
          </Col>
          <Col span={4}>
            <Checkbox style={{color: 'white'}}>MACD</Checkbox><br/><br/>
            <Checkbox style={{color: 'white'}}>ER</Checkbox>
            </Col>
          <Col span={4}>
            <Checkbox style={{color: 'white'}}>CCI</Checkbox><br/><br/>
            <Checkbox style={{color: 'white'}}>COPP</Checkbox>
          </Col>
        </Row>
        <br/>
        <Button 
          ghost
          loading={this.state.loadingTA}
          style={{marginTop: "1em"}}  
          onClick={() => this.fetchTA()}
        >
            Calculate TA
        </Button>
      </div>
    );
  }
}

export default Parameters;