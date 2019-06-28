import React from 'react';
import { Button } from 'antd';

class Parameters extends React.Component {
  render() {
    return (
      <div className="panel">
        <p>This is the parameters panel</p>
        <Button style={{marginTop: "1em"}} ghost >Train</Button>
      </div>
    );
  }
}

export default Parameters;