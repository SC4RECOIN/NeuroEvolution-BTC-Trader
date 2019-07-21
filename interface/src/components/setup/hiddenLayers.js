import React from 'react';
import { Row, Col, InputNumber, Icon } from 'antd';

class ModelLayers extends React.Component {
  state = {
    layerSize: ""
  }

  onChange = value => {
    this.setState({layerSize: value});
  };

  render() {
    return (
      <div>
        <p style={{'fontSize': '1.6em'}}>Model</p>
        <p>Add hidden layer</p>
        <Row style={{marginBottom: "2em"}}>
          <Col span={6}>
            <InputNumber 
              onChange={this.onChange}
              placeholder="size"
              style={{backgroundColor: "rgb(20, 20, 20)", color: "white"}}
            />
          </Col>
            <span className="add-layer"> 
              <Icon type="plus-square" onClick={() => this.props.addLayer(this.state.layerSize)}/>
            </span>
            <span className="remove-layer">
              <Icon type="minus-square" onClick={this.props.removeLayer}/>
            </span>
        </Row>
        <p>Hidden Layers:</p>
        {this.props.layers.length === 0 ? <p style={{color: "red"}}>EMPTY</p> : <p>{this.props.layers.join(', ')}</p>}
      </div>
    );
  }
}

export default ModelLayers;