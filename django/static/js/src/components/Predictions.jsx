import React from "react";
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
      steps: {},
      showStep: null,
    };

    this.handleStepChange = this.handleStepChange.bind(this);
    this.increaseShowStep = this.increaseShowStep.bind(this);
    this.decreaseShowStep = this.decreaseShowStep.bind(this);
    this.onImgLoad = this.onImgLoad.bind(this);
  }

  componentDidMount() {
    this.fetchData("tmp_2m");
  }

  fetchData(parameter) {
    fetch(`/api/spatialmosrun/last/${parameter}/`)
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

  onImgLoad({ target: img }) {
    this.setState({
      dimensions: {
        height: img.offsetHeight,
        width: img.offsetWidth,
      },
    });
  }
  
  decreaseShowStep() {
    const { availableSteps, showStep } = this.state
    const index =
      showStep !== 0
        ? showStep - 1
        : availableSteps.length - 1;
    this.handleStepChange(index);
  }

  increaseShowStep() {
    const { availableSteps, showStep } = this.state
    const index =
      showStep !== availableSteps.length - 1
        ? showStep + 1
        : 0;
    this.handleStepChange(index);
  }

  handleStepChange(index) {
    this.setState({
      showStep: index,
    });
  }

  handleParameterChange(parameter) {
    this.fetchData(parameter);
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
      return (
        <div>
          Error:
          {error.message}
        </div>
);
    } if (!isLoaded) {
      return (
        <div className="text-center" width="100%" height="400px">
          <div className="spinner-border" role="status">
            <span className="sr-only">Loading...</span>
          </div>
        </div>
      );
    } 
      return (
        <div height={height} width={width} className="img-slider">
          {steps.map((step, index) => {
            const description = `${modelrun.parameter_longname} Vorhersage ${step.valid_date}  ${step.valid_time}`;
            const activeClassName =
              index === showStep ? "img-fluid active" : "d-none img-fluid";
            return (
              <span 
                onClick={this.increaseShowStep}
                role="button"
                key={step.step}
              >
                <img
                  className={activeClassName}
                  src={step.filename_spatialmos_mean_md}
                  onLoad={this.onImgLoad}
                  srcSet={`
            ${step.filename_spatialmos_mean_sm} 640w, 
            ${step.filename_spatialmos_mean_md} 900w, 
            ${step.filename_spatialmos_mean_lg} 1024w
            `}
                  alt={description}
                  title={description}
                />
              </span>
            );
          })}
          <div className="mt-3 d-none d-sm-none d-md-none d-lg-block">
            <div className="list-inline text-center">
              {availableSteps.map((value, index) => {
                const activeClassName =
                  index === showStep
                    ? "list-inline-item text-danger"
                    : "list-inline-item";
                return (
                  <span
                    className={activeClassName}
                    key={value}
                    title={value}
                    role="button"
                    onClick={() => this.handleStepChange(index)}
                  >
                    {value}
                  </span>
                );
              })}
            </div>
          </div>
          <div className="d-sm-block d-md-block d-lg-none">
            <div className="mt-3 img-navi d-flex justify-content-between">
              <button 
                className="btn btn-light"
                type="button"
                onClick={this.decreaseShowStep}
              >
                &#8249;
              </button>
              <span className="text-danger">
                Step:
                {steps[showStep].step}
              </span>
              <button
                className="btn btn-light"
                type="button"
                onClick={this.increaseShowStep}
              >
                &#8250;
              </button>
            </div>
          </div>
          <div className="dropdown show mt-2 text-right">
            <button className="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Parameter auswählen
            </button>

            <div className="dropdown-menu" aria-labelledby="dropdownMenuLink">
              <span className={`dropdown-item ${modelrun.parameter === "tmp_2m" ? "active" : ""}`} onClick={() => this.handleParameterChange('tmp_2m')} role="button">Temperatur</span>
              <span className={`dropdown-item ${modelrun.parameter === "rh_2m" ? "active" : ""}`} onClick={() => this.handleParameterChange('rh_2m')} role="button">Relative Luftfeuchte</span>
            </div>
          </div>
          <div className="mt-3">
            <table className="table table-sm">
              <tbody>
                <tr>
                  <th scope="row">Parmeter</th>
                  <td>{modelrun.parameter_longname}</td>
                </tr>
                <tr>
                  <th scope="row">Analysedatum</th>
                  <td>{modelrun.anal_date}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      );
    
  }
}
