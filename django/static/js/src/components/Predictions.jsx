import React from "react";
import ReactDOM from "react-dom";
import "./Predictions.css";

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
      showNextStep: null,
    };

    this.handleStepChange = this.handleStepChange.bind(this);
    this.increaseShowStep = this.increaseShowStep.bind(this);
    this.decreaseShowStep = this.decreaseShowStep.bind(this);
    this.onImgLoad = this.onImgLoad.bind(this);
  }

  componentDidMount() {
    fetch("/api/spatialmosrun/last/tmp_2m/")
      .then((res) => res.json())
      .then(
        (result) => {
          this.setState({
            isLoaded: true,
            modelrun: result,
            availableSteps: result.steps.map((step) => step.step),
            steps: result.steps,
            showStep: 0,
            showNextStep: 1,
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

  decreaseShowStep() {
    let index =
      this.state.showStep !== 0
        ? this.state.showStep - 1
        : this.state.availableSteps.length - 1;
    this.handleStepChange(index);
  }

  increaseShowStep() {
    let index =
      this.state.showStep !== this.state.availableSteps.length - 1
        ? this.state.showStep + 1
        : 0;
    this.handleStepChange(index);
  }

  handleStepChange(index) {
    let nextIndex =
      this.state.showNextStep !== this.state.availableSteps.length - 1
        ? this.state.showNextStep + 1
        : 0;
    this.setState({
      showStep: index,
      showNextStep: nextIndex,
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
      showNextStep,
      dimensions,
    } = this.state;
    const { width, height } = dimensions;
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return (
        <div className="text-center" width={width}>
          <div className="spinner-border" role="status">
            <span className="sr-only">Loading...</span>
          </div>
        </div>
      );
    } else {
      return (
        <div height={height} width={width} className="img-slider">
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
            className="img-fluid active"
          />
          <div className="mt-3 d-none d-sm-none d-md-block">
            <div className="list-inline text-center">
              {availableSteps.map((value, index) => {
                let activeClassName =
                  index === showStep
                    ? "list-inline-item text-danger"
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
          <div className="d-sm-block d-md-none">
            <div className="mt-3 img-navi d-flex justify-content-between">
              <a class="bg-dark text-white" onClick={this.decreaseShowStep}>
                &#8249;
              </a>
              <span class="bg-dark text-white">Step: {steps[showStep].step}</span>
              <a class="bg-dark text-white" onClick={this.increaseShowStep}>
                &#8250;
              </a>
            </div>
          </div>
          <img
            src={steps[showNextStep].filename_spatialmos_mean_md}
            width="1"
            height="1"
            className="d-none"
            srcSet={`
            ${steps[showNextStep].filename_spatialmos_mean_sm} 640w, 
            ${steps[showNextStep].filename_spatialmos_mean_md} 900w, 
            ${steps[showNextStep].filename_spatialmos_mean_lg} 1024w
          `}
          />
        </div>
      );
    }
  }
}

const wrapper = document.getElementById("predictions_container");
wrapper ? ReactDOM.render(<Predictions />, wrapper) : false;
