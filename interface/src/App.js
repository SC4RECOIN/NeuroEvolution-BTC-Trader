import React from 'react';
import TrainingProgress from './components/progress/trainingProgress';
import ModelSetup from './components/setup/modelSetup';
import { Carousel, Modal } from 'antd';
import { onConnectionError } from './socket'


class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      activeHeader: 0,
      modalVisible: false
    }

    onConnectionError(() => {
      console.log("Connection Error!");
      this.setState({modalVisible: true});
    });
  }

  setActivePage(activePage) {
    this.carousel.goTo(activePage);
    this.setState({activeHeader: activePage})
  }

  getTabColor(idx) {
    return this.state.activeHeader === idx ? "rgb(20, 20, 20)" : "rgb(32,31,30)";
  }

  handleOk = e => {
    this.setState({ modalVisible: false });
  };

  render() {
    return (
      <div className="App">
        <Modal
          title="Connection Error!"
          visible={this.state.modalVisible}
          onOk={this.handleOk}
          onCancel={this.handleOk}
        >
          <p>You need to start the python backend</p>
        </Modal>
        <div className="header">
          <span 
            className="header-item" 
            onClick={() => this.setActivePage(0)}
            style={{backgroundColor: this.getTabColor(0)}}
          >
            Training Parameters
          </span>
          <span 
            className="header-item" 
            onClick={() => this.setActivePage(1)}
            style={{backgroundColor: this.getTabColor(1)}}
          >
            Training Progress
          </span>
        </div>
        <Carousel ref={carousel => (this.carousel = carousel)}>
          <ModelSetup />
          <TrainingProgress />
        </Carousel>
      </div>
    );
  }
}

export default App;
