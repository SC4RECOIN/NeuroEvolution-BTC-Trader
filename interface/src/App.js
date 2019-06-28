import React from 'react';
import Chart from './components/chart';
import Parameters from './components/parameters';


class App extends React.Component {
  state = {
    activeHeader: 0,
    activeColor: "rgb(20, 20, 20)",
    unactiveColor: "rgb(32,31,30)"
  }

  setActivePage(activePage) {
    this.setState({activeHeader: activePage})
  }

  render() {
    const pageContent = [
      <Parameters />,
      <Chart />
    ]

    return (
      <div className="App">
        <div className="header">
          <span 
            className="header-item" 
            onClick={() => this.setActivePage(0)}
            style={{backgroundColor: this.state.activeHeader === 0 ? this.state.activeColor : this.state.unactiveColor}}
          >
              Training Parameters
          </span>
          <span 
            className="header-item" 
            onClick={() => this.setActivePage(1)}
            style={{backgroundColor: this.state.activeHeader === 1 ? this.state.activeColor : this.state.unactiveColor}}
          >
            Generation Best
          </span>
        </div>
        {pageContent[this.state.activeHeader]}
      </div>
    );
  }
}

export default App;
