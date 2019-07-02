import React from 'react';
import { Button, Slider, Row, Col, Checkbox } from 'antd';
import LineChart from './linechart';

class Parameters extends React.Component {
  state = {
    loading: false,
    loadingTA: false,
    chartData: null,
    ohlc: null,
    sampleSize: 200,
    interval: 1,
    taKeys: []
  }

  updateSampleSize = (e) => {
    this.setState({sampleSize: e});
  }

  updateInvBox = (idx) => {
    this.setState({interval: idx});
  }

  updateTa = (taKey) => {
    let keys = this.state.taKeys;
    const index = keys.indexOf(taKey);
    if (index > -1){
      keys.splice(index, 1);
    } else {
      keys.push(taKey);
      this.setState({taKeys: keys});
    }
  }

  fetchSample() {
    this.setState({loading: true});
    fetch('http://127.0.0.1:5000/sample-request', {
      headers: {'Content-Type': 'application/json'},
      method: 'POST',
      body: JSON.stringify({
        'sampleSize': this.state.sampleSize,
        'interval': this.state.interval
      })
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
        this.setState({ 
          loadingTA: false,
          taData: data.results
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
          <LineChart dataKey={["price"]} chartData={data} height={400}/>
          <LineChart dataKey={this.state.taKeys} chartData={ta} height={200}/>
        </div>
        <Row>
          <Col span={2}><p style={{marginTop: 7}}>Segment size:</p></Col>
          <Col span={12}><Slider defaultValue={200} onChange={this.updateSampleSize} min={100} max={500}/></Col>
        </Row>
        <Checkbox checked={this.state.interval === 1} onChange={() => this.updateInvBox(1)} style={{color: 'white'}}>1min</Checkbox>
        <Checkbox checked={this.state.interval === 5} onChange={() => this.updateInvBox(5)} style={{color: 'white'}}>5min</Checkbox>
        <Checkbox checked={this.state.interval === 15} onChange={() => this.updateInvBox(15)} style={{color: 'white'}}>15min</Checkbox>
        <Checkbox checked={this.state.interval === 30} onChange={() => this.updateInvBox(30)} style={{color: 'white'}}>30min</Checkbox>
        <br/>
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
            <Checkbox style={{color: 'white'}} onChange={() => this.updateTa("ER")}>ER</Checkbox><br/><br/>
            <Checkbox style={{color: 'white'}} onChange={() => this.updateTa("PPO")}>PPO</Checkbox>
          </Col>
          <Col span={4}>
            <Checkbox style={{color: 'white'}} onChange={() => this.updateTa("STOCHRSI")}>STOCHRSI</Checkbox><br/><br/>
            <Checkbox style={{color: 'white'}} onChange={() => this.updateTa("ADX")}>ADX</Checkbox>
            </Col>
          <Col span={4}>
            <Checkbox style={{color: 'white'}} onChange={() => this.updateTa("RSI")}>RSI</Checkbox><br/><br/>
            <Checkbox style={{color: 'white'}} onChange={() => this.updateTa("COPP")}>COPP</Checkbox>
          </Col>
          <Col span={4}>
            <Checkbox style={{color: 'white'}} onChange={() => this.updateTa("CCI")}>CCI</Checkbox><br/><br/>
            <Checkbox style={{color: 'white'}} onChange={() => this.updateTa("CHAIKIN")}>CHAIKIN</Checkbox>
          </Col>
          <Col span={4}>
            <Checkbox style={{color: 'white'}} onChange={() => this.updateTa("FISH")}>FISH</Checkbox><br/><br/>
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