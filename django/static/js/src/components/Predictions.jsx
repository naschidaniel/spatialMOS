import React, { Component } from "react";
import ReactDOM from "react-dom";

export default class Predictions extends React.Component {
  constructor() {
    super();

    this.state = {
      error: null,
      isLoaded: false,
      parameter: {},
      steps: {}
    };

    this.handleChange = this.handleChange.bind(this);
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
          steps: result.steps
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

  handleChange(event) {
    const { value } = event.target;
    this.setState(() => {
      return {
        value
      };
    });
  }

  render() {
    const { error, isLoaded, steps, modelrun } = this.state;
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return <div>Loading...</div>;
    } else {
      return (
        <span>
        {steps.map(step =>
          <img key={step.step}
            src={ step.filename_spatialmos_mean_md }
            srcSet=
              {`
                ${step.filename_spatialmos_mean_sm} 640w, 
                ${step.filename_spatialmos_mean_md } 900w, 
                ${step.filename_spatialmos_mean_lg } 1024w
              `}
            alt={ modelrun.parameter_longname + " Vorhersage für " + step.valid_date + " " + step.valid_time }
            title={ modelrun.parameter_longname + " Vorhersage für " + step.valid_date + " " + step.valid_time }
          className="img-fluid" />
        )}
      </span>
      );
    }
  }
}

const wrapper = document.getElementById("predictions_container");
wrapper ? ReactDOM.render(<Predictions />, wrapper) : false;