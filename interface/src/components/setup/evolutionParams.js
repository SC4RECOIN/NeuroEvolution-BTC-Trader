import React from 'react';
import { Slider, Row, Col } from 'antd';

class EvolutionParams extends React.Component {
  render() {
    return (
      <div>
        <p style={{'fontSize': '1.6em'}}>Evolution Parameters</p>
        <Row>
          <Col span={10}><p style={{marginTop: 7}}>% Mutation Rate (weights):</p></Col>
          <Col span={12}><Slider defaultValue={this.props.defaults[0]} onChange={(e) => this.props.update({mrw: e})} min={1} max={20}/></Col>
        </Row>
        <Row>
          <Col span={10}><p style={{marginTop: 7}}>% Mutation Rate (bias):</p></Col>
          <Col span={12}><Slider defaultValue={this.props.defaults[1]} onChange={(e) => this.props.update({mrb: e})} min={1} max={20}/></Col>
        </Row>
        <Row>
          <Col span={10}><p style={{marginTop: 7}}>% Mutation Scale:</p></Col>
          <Col span={12}><Slider defaultValue={this.props.defaults[2]} onChange={(e) => this.props.update({ms: e})} min={10} max={60}/></Col>
        </Row>
        <Row>
          <Col span={10}><p style={{marginTop: 7}}>% Mutation Decay:</p></Col>
          <Col span={12}><Slider defaultValue={this.props.defaults[3]} onChange={(e) => this.props.update({md: e})} min={0} max={10}/></Col>
        </Row>
      </div>
    )
  }
}

export default EvolutionParams;