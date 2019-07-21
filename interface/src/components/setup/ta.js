import React from 'react';
import styled from 'styled-components';
import { Row, Col, Checkbox } from 'antd';

const TaBox = styled(Checkbox)`
  color: white;
`;

class TA extends React.Component {
  render() {
    return (
      <div>
        <p style={{'fontSize': '1.6em'}}>Technical Analysis</p>
        <Row>
          <Col span={4}>
            <TaBox onChange={() => this.props.updateTa("ER")}>ER</TaBox><br/><br/>
            <TaBox onChange={() => this.props.updateTa("PPO")}>PPO</TaBox>
          </Col>
          <Col span={4}>
            <TaBox onChange={() => this.props.updateTa("STOCHRSI")}>STOCHRSI</TaBox><br/><br/>
            <TaBox onChange={() => this.props.updateTa("ADX")}>ADX</TaBox>
          </Col>
          <Col span={4}>
            <TaBox onChange={() => this.props.updateTa("RSI")}>RSI</TaBox><br/><br/>
            <TaBox onChange={() => this.props.updateTa("COPP")}>COPP</TaBox>
          </Col>
          <Col span={4}>
            <TaBox onChange={() => this.props.updateTa("CCI")}>CCI</TaBox><br/><br/>
            <TaBox onChange={() => this.props.updateTa("CHAIKIN")}>CHAIKIN</TaBox>
          </Col>
          <Col span={4}>
            <TaBox onChange={() => this.props.updateTa("FISH")}>FISH</TaBox><br/><br/>
          </Col>
        </Row>
      </div>
    )
  }
}

export default TA;