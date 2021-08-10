<template>
  <div id="mapContainer"></div>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/no-explicit-any */
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// fix "Uncaught TypeError: this._map is null" when zooming
(L.Tooltip.prototype as any)._updatePosition = function () {
  if (!this._map || !this._latlng) return;
  var pos = this._map.latLngToLayerPoint(this._latlng);
  this._setPosition(pos);
};
(L.Tooltip.prototype as any)._animateZoom = function (e: any) {
  if (!this._map || !this._latlng) return;
  var pos = this._map._latLngToNewLayerPoint(this._latlng, e.zoom, e.center);
  this._setPosition(pos);
};

export default {
  name: "LeafletMap",
  data() {
    return {
      map: undefined,
      lat: 47.258502750000005,
      lon: 11.388483871855112,
      address:
        "29, Peter-Mayr-Straße, Wilten, Innsbruck, Tirol, 6020, Österreich",
    };
  },
  mounted() {
    this.map = L.map("mapContainer").setView([this.lat, this.lon], 16);
    L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(this.map);
    L.marker([this.lat, this.lon])
      .bindTooltip(this.address)
      .openTooltip()
      .addTo(this.map);
  },
};
</script>

<style scoped>
#mapContainer {
  width: 100%;
  height: 400px;
}
</style>
