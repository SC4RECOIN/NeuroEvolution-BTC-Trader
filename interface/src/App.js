import React from 'react';
import Chart from './components/chart';

function App() {
  return (
    <div className="App">
      <div className="header">
        <span className="header-item">Training Parameters</span>
        <span className="header-item">Generation Best</span>
        <span className="header-item">Overall Best</span>
      </div>
      <Chart />
    </div>
  );
}

export default App;
