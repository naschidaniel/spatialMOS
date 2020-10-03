/* App.js */
import PropTypes from "prop-types";
import React, { Component } from "react";
import {
  Area,
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import CustomTooltip from "./CustomTooltip";

const propTypes = {
    data: PropTypes.string.isRequired,
};

export default class SimpleLineChart extends Component {
  static methodsAreOk() {
    return true;
  }

  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      steps: [],
    };
  }


  componentDidMount() {
    const { data } = this.props; // data === apiURL
    fetch(data)
      .then((res) => res.json())
      .then(
        (result) => {
          Object.values(result).forEach((v) => {
            // manipulation api request
            const addInformation = v
            addInformation.tooltip_label =
              `${v.valid_date  } + ${  v.valid_time}`;
            addInformation.spatialmos_min =
              Number(v.spatialmos_mean) -
              Number(v.spatialmos_spread);
            addInformation.spatialmos_max =
              Number(v.spatialmos_mean) +
              Number(v.spatialmos_spread);
            addInformation.spatialmos_range = [
              Number(v.spatialmos_max),
              Number(v.spatialmos_min),
            ];
            addInformation.unit = "°C";
          });
          this.setState({
            isLoaded: true,
            steps: result,
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

  render() {
    const { error, isLoaded, steps } = this.state;
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
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart
            data={steps}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="valid_date" />
            <YAxis unit={steps[0].unit} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              name="Mittelwert"
              type="monotone"
              dataKey="spatialmos_mean"
              stroke="#888888"
              activeDot={{ r: 8 }}
            />
            <Area
              name="Standardabweichung"
              type="monotone"
              dataKey="spatialmos_range"
              fill="#8884d8"
              opacity="0.3"
            />
          </ComposedChart>
        </ResponsiveContainer>
      );
    
  }
}

SimpleLineChart.propTypes = propTypes;
