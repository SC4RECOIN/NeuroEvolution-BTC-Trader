import React from 'react';
import styled from 'styled-components';
import { Button, Slider, Row, Col, Checkbox,Popover } from 'antd';
import LineChart from './lineChart';
import ModelLayers from './hiddenLayers';

const TaBox = styled(Checkbox)`
  color: white;
`;

class ModelSetup extends React.Component {
  state = {
    modelIsTraining: false,
    loadingData: false,
    chartData: null,
    taData: null,
    sampleSize: 350,
    interval: 5,
    taKeys: [],
    hiddenLayers: []
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
    if (index > -1) {
      keys.splice(index, 1);
    } else {
      keys.push(taKey);
    }
    this.setState({taKeys: keys});
  }

  addLayer = (layer) => {
    if (layer.length !== 0) {
      let layers = this.state.hiddenLayers;
      layers.push(layer);
      this.setState({hiddenLayers: layers});
    }
  }

  removeLayer = () => {
    let layers = this.state.hiddenLayers;
    layers.pop();
    this.setState({hiddenLayers: layers});
  }

  fetchSample() {
    this.setState({loadingData: true});
    fetch('http://127.0.0.1:5000/data-sample-request', {
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
        this.setState({ 
          loadingData: false,
          chartData: data.closing,
          taData: data.ta
        })
      })
      .catch(e => console.log(`Error fetching sample segment: ${e}`))
  }
  
  startTraining() {
    this.setState({modelIsTraining: true});
    fetch('http://127.0.0.1:5000/start-training', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        'hiddenLayers': this.state.hiddenLayers,
        'taKeys': this.state.taKeys
      })
    })
      .then(r => r.json())
      .then(data => {
        console.log(data.message);
        this.setState({modelIsTraining: false});
      })
      .catch(e => {
        console.log(`Error fetching ta: ${e}`);
        this.setState({modelIsTraining: false});
      })
  }

  getTrainButton() {
    const button = (
      <Button 
        ghost
        disabled={!this.state.chartData || this.state.taKeys.length === 0 || this.state.hiddenLayers.length === 0}
        loading={this.state.modelIsTraining}
        style={{marginTop: "1em", color: "white"}}  
        onClick={() => this.startTraining()}
      >
        Train
      </Button> 
    )

    if (this.state.chartData === null) {
      return (
        <Popover title="Cannot start training" placement="topLeft" content="You need to get data segment for training">
          {button}
        </Popover>
      )
    } else if (this.state.taKeys.length === 0) {
      return (
        <Popover title="Cannot start training" placement="topLeft" content="You need to select TA for model inputs">
          {button}
        </Popover>
      )
    } else if (this.state.hiddenLayers.length === 0) {
      return (
        <Popover title="Cannot start training" placement="topLeft" content="You need to add hidden layers to your model">
          {button}
        </Popover>
      )
    }

    return button;
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
          <Col span={12}><Slider defaultValue={this.state.sampleSize} onChange={this.updateSampleSize} min={100} max={500}/></Col>
        </Row>
        <TaBox checked={this.state.interval === 1} onChange={() => this.updateInvBox(1)}>1min</TaBox>
        <TaBox checked={this.state.interval === 5} onChange={() => this.updateInvBox(5)}>5min</TaBox>
        <TaBox checked={this.state.interval === 15} onChange={() => this.updateInvBox(15)}>15min</TaBox>
        <TaBox checked={this.state.interval === 30} onChange={() => this.updateInvBox(30)}>30min</TaBox>
        <br/>
        <Button 
          ghost
          loading={this.state.loadingData}
          style={{marginTop: "1em"}}  
          onClick={() => this.fetchSample()}
        >
            Get Random Segment
        </Button>
        <hr style={{marginTop: "2em"}}/>
        <p style={{'fontSize': '1.6em'}}>Technical Analysis</p>
        <Row>
          <Col span={4}>
            <TaBox onChange={() => this.updateTa("ER")}>ER</TaBox><br/><br/>
            <TaBox onChange={() => this.updateTa("PPO")}>PPO</TaBox>
          </Col>
          <Col span={4}>
            <TaBox onChange={() => this.updateTa("STOCHRSI")}>STOCHRSI</TaBox><br/><br/>
            <TaBox onChange={() => this.updateTa("ADX")}>ADX</TaBox>
          </Col>
          <Col span={4}>
            <TaBox onChange={() => this.updateTa("RSI")}>RSI</TaBox><br/><br/>
            <TaBox onChange={() => this.updateTa("COPP")}>COPP</TaBox>
          </Col>
          <Col span={4}>
            <TaBox onChange={() => this.updateTa("CCI")}>CCI</TaBox><br/><br/>
            <TaBox onChange={() => this.updateTa("CHAIKIN")}>CHAIKIN</TaBox>
          </Col>
          <Col span={4}>
            <TaBox onChange={() => this.updateTa("FISH")}>FISH</TaBox><br/><br/>
          </Col>
        </Row>
        <hr style={{marginTop: "2em"}}/>
        <ModelLayers 
          addLayer={this.addLayer}
          removeLayer={this.removeLayer}
          layers={this.state.hiddenLayers}
        />
        <hr style={{marginTop: "2em"}}/>
        {this.getTrainButton()}
      </div>
    );
  }
}

export default ModelSetup;