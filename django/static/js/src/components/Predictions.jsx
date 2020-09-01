import React from "react";
import ReactDOM from "react-dom";

export default class Predictions extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      availableSteps: [],
      dimensions: {
        height: "555",
        width: "100%",
      },
      error: null,
      isLoaded: false,
      parameter: {},
      steps: {},
      showStep: null,
    };

    this.handleStepChange = this.handleStepChange.bind(this);
    this.increaseShowStep = this.increaseShowStep.bind(this);
    this.onImgLoad = this.onImgLoad.bind(this);
  }

  componentDidMount() {
    fetch(
      "https://cors-anywhere.herokuapp.com/https://moses.tirol/api/spatialmosrun/last/tmp_2m/"
    )
      .then((res) => res.json())
      .then(
        (result) => {
          this.setState({
            isLoaded: true,
            modelrun: result,
            availableSteps: result.steps.map((step) => step.step),
            steps: result.steps,
            showStep: 0,
          });
        },
        (error) => {
          this.setState({
            isLoaded: true,
            error,
          });
        }
      );
  }

  increaseShowStep() {
    let next =
      this.state.showStep !== this.state.availableSteps.length - 1
        ? this.state.showStep + 1
        : 0;
    this.handleStepChange(next);
  }

  handleStepChange(index) {
    this.setState({
      showStep: index,
    });
  }

  onImgLoad({ target: img }) {
    this.setState({
      dimensions: {
        height: img.offsetHeight,
        width: img.offsetWidth,
      },
    });
  }

  render() {
    const {
      availableSteps,
      error,
      isLoaded,
      modelrun,
      steps,
      showStep,
      dimensions,
    } = this.state;
    const { width, height } = dimensions;
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return (
        <div className="text-center border" width={width}>
          <div className="spinner-border" role="status">
            <span className="sr-only">Loading...</span>
          </div>
        </div>
      );
    } else {
      return (
        <div height={height} width={width}>
          <img
            key={steps[showStep].step}
            src={steps[showStep].filename_spatialmos_mean_md}
            onLoad={this.onImgLoad}
            srcSet={`
                ${steps[showStep].filename_spatialmos_mean_sm} 640w, 
                ${steps[showStep].filename_spatialmos_mean_md} 900w, 
                ${steps[showStep].filename_spatialmos_mean_lg} 1024w
              `}
            alt={
              modelrun.parameter_longname +
              " Vorhersage für " +
              steps[1].valid_date +
              " " +
              steps[1].valid_time
            }
            title={
              modelrun.parameter_longname +
              " Vorhersage für " +
              steps[1].valid_date +
              " " +
              steps[1].valid_time
            }
            onClick={this.increaseShowStep}
            height={height}
            width={width}
            className="img-fluid"
          />
          <div className="list-inline text-center">
            {availableSteps.map((value, index) => {
              let activeClassName =
                index === showStep
                  ? "list-inline-item active"
                  : "list-inline-item";
              return (
                <span
                  className={activeClassName}
                  key={index}
                  title={value}
                  onClick={() => this.handleStepChange(index)}
                >
                  {value}
                </span>
              );
            })}
          </div>
        </div>
      );
    }
  }
}

const wrapper = document.getElementById("predictions_container");
wrapper ? ReactDOM.render(<Predictions />, wrapper) : false;
