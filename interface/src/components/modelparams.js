import React from 'react';
import { Row, Col, Input, Icon } from 'antd';

class ModelParams extends React.Component {
  state = {
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

  render() {
    return (
      <div>
        <p style={{'fontSize': '1.6em'}}>Model</p>
        <p>Add hidden layer</p>
        <Row style={{marginBottom: "2em"}}>
          <Col span={2}>
            <Input
              type="number"
              onChange={this.onChange}
              placeholder="size"
              style={{backgroundColor: "rgb(20, 20, 20)", color: "white"}}
            />
          </Col>
          <Col span={1}>
            <div className="add-layer"> 
              <Icon type="plus-square" onClick={this.addLayer}/>
            </div>
          </Col>
          <Col span={1}>
            <div className="remove-layer">
              <Icon type="minus-square" onClick={this.removeLayer}
              />
            </div>
          </Col>
        </Row>
        <Row>
          <p>Inputs: {this.props.numInputs}</p>
          <p>Hidden Layers: {this.state.hiddenLayers.join(', ')}</p>
          <p>Outputs: 2</p>
        </Row>
      </div>
    );
  }
}

export default ModelParams;