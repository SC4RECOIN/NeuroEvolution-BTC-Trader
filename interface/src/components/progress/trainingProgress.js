import React from 'react';
import Results from './genResults';
import {
  ComposedChart, Line, Scatter, XAxis, YAxis, CartesianGrid, ResponsiveContainer
} from 'recharts';

import { genPriceUpdate } from '../../socket';

class TrainingProgress extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      chartData: null
    }

    genPriceUpdate((err, data) => {
      console.log("Data received");
      this.setState({ 
        chartData: data.generation_trades,
        generationBest: data.generation
      })
    });
  }

  render() {
    const data = this.state.chartData || [];

    return (
      <div className="panel">
        <div style={{overflowX: "scroll", overflowY: "hidden", marginBottom: "1.2em" }}>
          <div style={{ width: Math.max(data.length * 7, 1200), height: 400}}>
            <ResponsiveContainer>
            <ComposedChart 
              data={data}
              margin={{
                top: 10, right: 30, left: 0, bottom: 0
              }}
            >
              <CartesianGrid strokeDasharray="1" stroke="rgb(42,41,40)" />
              <XAxis />
              <YAxis domain={['dataMin', 'dataMax']}/>
              <Line type="linear" dataKey="price" stroke="#AFD275" dot={false} />
              <Scatter dataKey="buy" fill="green" />
              <Scatter dataKey="sell" fill="red" />
            </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
        <p>Overall best generation: {this.state.generationBest}</p>
        <Results />
      </div>
    );
  }
}

export default TrainingProgress;