/* App.js */
import PropTypes from "prop-types";
import React, { Component } from "react";
import ReactDOM from "react-dom";
import { DataExchangeString } from "../middleware/DataExchange.jsx"
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
            result[i].spatialmos_min =
              result[i].spatialmos_mean - result[i].spatialmos_spread;
            result[i].spatialmos_max =
              Number(result[i].spatialmos_mean) +
              Number(result[i].spatialmos_spread);
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
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="spatialmos_mean"
            stroke="#8884d8"
            activeDot={{ r: 8 }}
          />
          <Area
            type="monotone"
            dataKey="spatialmos_min"
            stackId="1"
            stroke="#8884d8"
          />
          <Area
            type="monotone"
            dataKey="spatialmos_max"
            fill="#8884d8"
            stroke="#8884d8"
            stackId="1"
          />
        </ComposedChart>
      </ResponsiveContainer>
    );
  }
}
const wrapper = document.getElementById("simple_line_chart");
const data = DataExchangeString(wrapper?.attributes?.data)
wrapper
  ? ReactDOM.render(
      <SimpleLineChart data={data} />,
      wrapper
    )
  : false;
