import React, { Component } from "react";
import ReactDOM from "react-dom";
import { Map, TileLayer } from "react-leaflet";
import 'leaflet/dist/leaflet.css';

export default class Leafletmap extends Component {
  constructor(props) {
    super(props);
  
    this.state = {
    lat: 37.7749,
    lng: -122.4194,
    zoom: 13,
  };
  }
  render() {
    return (
      <Map
        center={[47, 12]}
        zoom={14}
        style={{ width: "50%", height: "900px" }}
      >
        <TileLayer
          attribution='&copy <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
      </Map>
    );
  }
}
const wrapper = document.getElementById("leaflet_map");
wrapper
  ? ReactDOM.render(
      <Leafletmap data='{"displayName": "haha", "lat": 11, "lon": 10}' />,
      wrapper
    )
  : false;
