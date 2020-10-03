import React from "react";
import PropTypes from "prop-types";
import { Map, TileLayer, Marker, Popup } from "react-leaflet";

// require style and marker pngs
import "leaflet/dist/leaflet.css";

require("leaflet/dist/images/marker-icon-2x.png");
require("leaflet/dist/images/marker-icon.png");
require("leaflet/dist/images/marker-shadow.png");



function LeafletMap(props) {
  const {data} = props;
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

LeafletMap.propTypes = {
  data: PropTypes.shape({ lat: PropTypes.number.isRequired, lon: PropTypes.number.isRequired, display_name: PropTypes.string.isRequired}).isRequired,
};

export default LeafletMap;
