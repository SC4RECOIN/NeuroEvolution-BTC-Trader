import React from 'react';
import {
  ComposedChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer
} from 'recharts';

class LineChart extends React.Component {
  render() {
    const colors = [
      "#AFD275",
      "#C3073F",
      "#66FCF1",
      "#C5CBE3",
      "#FF652F",
      "#FFE400",
      "#DA7B93",
      "#17E9E0"
    ];
    const data = this.props.chartData || [];
    let lineGraphs = [];
    this.props.dataKey.forEach((key, idx) => {
      lineGraphs.push(
        <Line 
          key={idx.toString()} 
          type="linear" 
          dataKey={key} 
          stroke={colors[idx % colors.length]} 
          dot={false} 
      />)
    })

    return (
      <div style={{ width: Math.max(data.length * 5, 1200), height: 400}}>
        <ResponsiveContainer>
          <ComposedChart 
            data={data}
            margin={{
              top: 10, right: 30, left: 0, bottom: 0
            }}
          >
            {/* <CartesianGrid strokeDasharray="1" /> */}
            <XAxis />
            <YAxis domain={['dataMin', 'dataMax']}/>
            {lineGraphs}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    );
  }
}

export default LineChart;