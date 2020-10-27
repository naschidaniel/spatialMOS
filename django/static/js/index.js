import React from "react";
import ReactDOM from "react-dom";
import { DataExchangeObject, DataExchangeString } from "./src/util/DataExchange";
import LeafletMap from "./src/components/LeafletMap";
import SimpleLineChart from "./src/components/SimpleLineChart";
import Predictions from "./src/components/Predictions";
import "bootstrap/js/dist/collapse";

import "./style.css";
import "bootstrap/dist/css/bootstrap.min.css";

// LeafletMap
const leafletMapElement = document.getElementById("leaflet_map");
if (leafletMapElement !== null) {
  const data = DataExchangeObject(leafletMapElement?.attributes?.data);
  ReactDOM.render(
    <React.StrictMode>
      <LeafletMap data={data} />
    </React.StrictMode>,
    leafletMapElement
  );
}

// SimpleLineChart
const SimpleLineChartElement = document.getElementById("simple_line_chart");
if (SimpleLineChartElement !== null) {
  const data = DataExchangeString(SimpleLineChartElement?.attributes?.data);
  ReactDOM.render(
    <React.StrictMode>
      <SimpleLineChart data={data} />
    </React.StrictMode>,
    SimpleLineChartElement
  );
}

// SimpleLineChart
const PredictionsElement = document.getElementById("predictions_container");
if (PredictionsElement !== null) {
  const data = DataExchangeObject(PredictionsElement?.attributes?.data);
  ReactDOM.render(
    <React.StrictMode>
      <Predictions data={data} />
    </React.StrictMode>,
    PredictionsElement
  );
}
