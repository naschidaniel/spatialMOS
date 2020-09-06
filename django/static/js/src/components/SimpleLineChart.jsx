/* App.js */
import PropTypes from "prop-types";
import React, { Component } from "react";
import ReactDOM from "react-dom";
import { DataExchangeString } from "../middleware/DataExchange.jsx";
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
import CustomTooltip from "./CustomTooltip.jsx";

export default class SimpleLineChart extends Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      steps: [],
    };
  }
  static get propTypes() {
    return {
      data: PropTypes.string,
    };
  }

  componentDidMount() {
    let apiUrl = this.props.data;
    fetch(apiUrl)
      .then((res) => res.json())
      .then(
        (result) => {
          for (const i in result) {
            result[i].tooltip_label =
              result[i].valid_date + " " + result[i].valid_time;
            result[i].spatialmos_min =
              Number(result[i].spatialmos_mean) -
              Number(result[i].spatialmos_spread);
            result[i].spatialmos_max =
              Number(result[i].spatialmos_mean) +
              Number(result[i].spatialmos_spread);
            result[i].spatialmos_range = [
              Number(result[i].spatialmos_max),
              Number(result[i].spatialmos_min),
            ];
            result[i].unit = "°C";
          }
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
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return (
        <div className="text-center" width="100%" height="400px">
          <div className="spinner-border" role="status">
            <span className="sr-only">Loading...</span>
          </div>
        </div>
      );
    } else {
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
}
const wrapper = document.getElementById("simple_line_chart");
const data = DataExchangeString(wrapper?.attributes?.data);
wrapper ? ReactDOM.render(<SimpleLineChart data={data} />, wrapper) : false;
