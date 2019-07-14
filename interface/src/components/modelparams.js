import React from 'react';
import { Row, Col, Input, Icon } from 'antd';

class ModelParams extends React.Component {
  state = {
    layerSize: ""
  }

  onChange = e => {
    this.setState({layerSize: e.target.value});
  };

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
              <Icon type="plus-square" onClick={() => this.props.addLayer(this.state.layerSize)}/>
            </div>
          </Col>
          <Col span={1}>
            <div className="remove-layer">
              <Icon type="minus-square" onClick={this.props.removeLayer}
              />
            </div>
          </Col>
        </Row>
        <p>Hidden Layers:</p>
        {this.props.layers.length === 0 ? <p style={{color: "red"}}>EMPTY</p> : <p>{this.props.layers.join(', ')}</p>}
      </div>
    );
  }
}

export default ModelParams;