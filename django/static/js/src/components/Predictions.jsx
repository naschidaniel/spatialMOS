import React, { Component } from "react";
import ReactDOM from "react-dom";

export default class Predictions extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      availableSteps: [],
      error: null,
      isLoaded: false,
      parameter: {},
      steps: {},
      showStep: null
    };

    this.handleStepChange = this.handleStepChange.bind(this);
    this.increaseShowStep = this.increaseShowStep.bind(this);

  }

  componentDidMount() {
    fetch("/api/spatialmosrun/last/tmp_2m/")
    .then(res => res.json())
    .then(
      (result) => {
        console.log(result)
        this.setState({
          isLoaded: true,
          modelrun: result,
          availableSteps: result.steps.map(step => step.step),
          steps: result.steps,
          showStep: result.steps[0].step
        });
      },
      (error) => {
        this.setState({
          isLoaded: true,
          error
        });
      }
    )
  }

  increaseShowStep() {
    let next = (this.state.showStep !== this.state.availableSteps.length - 1) ? this.state.showStep + 1 : 0
    this.handleStepChange(next)
  }

  handleStepChange(index) {
    this.setState({
      showStep: index
    });
  }

  render() {
    const { availableSteps, error, isLoaded, modelrun, steps, showStep } = this.state;
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return <div>Loading...</div>;
    } else {
      return (
        <span>
          <img key={steps[showStep].step}
            src={ steps[showStep].filename_spatialmos_mean_md }
            srcSet=
              {`
                ${steps[showStep].filename_spatialmos_mean_sm} 640w, 
                ${steps[showStep].filename_spatialmos_mean_md } 900w, 
                ${steps[showStep].filename_spatialmos_mean_lg } 1024w
              `}
            alt={ modelrun.parameter_longname + " Vorhersage für " + steps[1].valid_date + " " + steps[1].valid_time }
            title={ modelrun.parameter_longname + " Vorhersage für " + steps[1].valid_date + " " + steps[1].valid_time }
            onClick={this.increaseShowStep}
          className="img-fluid" />
          <div className="d-flex flex-row bd-highlight mb-3">
            <div className="p-2 bd-highlight">Flex item 1</div>
            <div className="p-2 bd-highlight">Flex item 2</div>
            <div className="p-2 bd-highlight">Flex item 3</div>
          </div>
          <div className="list-inline">
            {availableSteps.map((value, index) => {
              let activeClassName = (index === showStep) ? 'list-inline-item active' : 'list-inline-item';
              return <span className={activeClassName} key={index} title={value} onClick={() => this.handleStepChange(index)}>{value}</span>
            })}
            </div>
        </span>
      );
    }
  }
}

const wrapper = document.getElementById("predictions_container");
wrapper ? ReactDOM.render(<Predictions />, wrapper) : false;