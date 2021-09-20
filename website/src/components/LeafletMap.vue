<template>
  <div class="container">
    <div id="mapContainer"></div>
  </div>
</template>

<script lang="ts">
import { unref } from "vue";
import { usePhotonApi } from "../store/photonapi";

import * as L from "leaflet";

import "leaflet/dist/leaflet.css";
/* eslint-disable @typescript-eslint/no-explicit-any */
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
  setup() {
    const { point, lat, lon, tooltip } = usePhotonApi();
    return { point, lat, lon, tooltip };
  },
  data() {
    return {
      map: undefined as unknown as L.Map,
      activeLayer: undefined as unknown as L.TileLayer,
      marker: undefined as unknown as L.Marker,
      selectedLayer: undefined as unknown as L.LayerGroup,
    };
  },
  mounted() {
    const lat = unref(this.lat);
    const lon = unref(this.lon);
    const tooltip = unref(this.tooltip);
    this.map = new L.Map("mapContainer").setView([lat, lon], 16);

    this.activeLayer = new L.TileLayer(
      "http://{s}.tile.osm.org/{z}/{x}/{y}.png",
      {
        attribution:
          '&copy <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
      }
    ).addTo(this.map);
    this.updateActiveBounds();
  },
  watch: {
    point() {
      this.updateActiveBounds();
    },
  },
  methods: {
    updateActiveBounds(): void {
      if (this.point === undefined) {
        return;
      }
      const _latlng = L.latLng(this.point);
      this.map.setView(_latlng);
      this.marker = new L.Marker(_latlng)
        .bindTooltip(this.tooltip)
        .openTooltip()
        .addTo(this.map);
    },
  },
};
</script>

<style scoped>
#mapContainer {
  width: 100%;
  height: 400px;
}
</style>
