import React from 'react';
import { Button, Row, Col, Input, Icon } from 'antd';

class ModelParams extends React.Component {
  state = {
    modelIsTraining: false,
    hiddenLayers: [],
    layerSize: ""
  }

  onChange = e => {
    this.setState({layerSize: e.target.value});
  };

  addLayer = () => {
    let layers = this.state.hiddenLayers;
    layers.push(this.state.layerSize);
    if (this.state.layerSize !== "") {
      this.setState({hiddenLayers: layers});
    }
  }

  removeLayer = () => {
    let layers = this.state.hiddenLayers;
    layers.pop();
    this.setState({hiddenLayers: layers});
  }

  startTraining() {
    this.setState({modelIsTraining: true});
    fetch('http://127.0.0.1:5000/start-training')
      .then(r => r.json())
      .then(data => console.log(data.message))
      .catch(e => console.log(`Error fetching ta: ${e}`))
  }

  render() {
    return (
      <div>
        <p style={{'fontSize': '1.6em'}}>Model</p>
        <p>Add hidden layer</p>
        <Row>
          <Col span={2}>
            <Input
              type="number"
              onChange={this.onChange}
              placeholder="size"
              style={{backgroundColor: "rgb(20, 20, 20)", color: "white"}}
            />
          </Col>
          <Col span={1}>
            <div className="layerIcon" style={{color: "green"}}> 
              <Icon 
                type="plus-square" 
                onClick={this.addLayer}
              />
            </div>
          </Col>
          <Col span={1}>
            <div className="layerIcon" style={{color: "red"}}>
              <Icon 
                type="minus-square" 
                onClick={this.removeLayer}
              />
            </div>
          </Col>
        </Row>
        <Button 
          ghost
          loading={this.state.modelIsTraining}
          style={{marginTop: "1em"}}  
          onClick={() => this.startTraining()}
        >
          Train
        </Button>
      </div>
    );
  }
}

export default ModelParams;