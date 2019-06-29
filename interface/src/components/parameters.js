import React from 'react';
import { Button } from 'antd';
import { requestSample } from './../socket';
import {
  ComposedChart, Line, Scatter, XAxis, YAxis, CartesianGrid, ResponsiveContainer
} from 'recharts';

class Parameters extends React.Component {
  state = {
    loading: false,
    chartData: null,
    ohlc: null
  }

  fetchSample() {
    this.setState({loading: true});
    requestSample((err, data) => {
      console.log("Sample data received");
      let chart = []
      data.close.forEach(d => chart.push({'price': d}))
      this.setState({ 
        loading: false,
        ohlc: data,
        chartData: chart
      })
    });
  }

  render() {
    const data = this.state.chartData || [];

    return (
      <div className="panel">
        <div style={{overflowX: "scroll", overflowY: "hidden", marginBottom: "1.2em" }}>
          <div style={{ width: data.length * 3, height: 400}}>
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
        </div>
        <Button 
          ghost
          loading={this.state.loading}
          style={{marginTop: "1em"}}  
          onClick={() => this.fetchSample()}>
            Get Random Segment
          </Button>
      </div>
    );
  }
}

export default Parameters;