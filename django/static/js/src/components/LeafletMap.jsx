import PropTypes from "prop-types";
import React, { Component } from "react";
import ReactDOM from "react-dom";
import { DataExchangeObject} from "../middleware/DataExchange.jsx"
import { Map, TileLayer, Marker, Popup } from "react-leaflet";

// require style and marker pngs
import "leaflet/dist/leaflet.css";
require("leaflet/dist/images/marker-icon-2x.png");
require("leaflet/dist/images/marker-icon.png");
require("leaflet/dist/images/marker-shadow.png");

export default class Leafletmap extends Component {
  constructor(props) {
    super(props);
  }
  static get propTypes() { 
    return { 
        data: PropTypes.object 
    }; 
  }

  render() {
    let data = this.props.data
    return (
      <Map
        center={[data.lat, data.lon]}
        zoom={14}
        style={{ width: "100%", height: "400px" }}
      >
        <TileLayer
          attribution='&copy <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={[data.lat, data.lon]}>
          <Popup>{data.display_name}</Popup>
        </Marker>
      </Map>
    );
  }
}
const wrapper = document.getElementById("leaflet_map");
const data = DataExchangeObject(wrapper?.attributes?.data);
wrapper
  ? ReactDOM.render(<Leafletmap data={data} />, wrapper)
  : false;
