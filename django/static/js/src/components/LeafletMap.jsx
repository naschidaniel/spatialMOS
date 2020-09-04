import React, { Component } from "react";
import ReactDOM from "react-dom";
import { Map, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

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
    const data = {
      "position": [47, 12],
      "displayName": "haha"
    }
    return (
      <Map
        center={data.position}
        zoom={14}
        style={{ width: "50%", height: "900px" }}
      >
        <TileLayer
          attribution='&copy <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={data.position}>
          <Popup>{data.displayName}</Popup>
        </Marker>
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
