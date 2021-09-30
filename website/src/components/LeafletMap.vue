<template>
  <div class="container">
    <div id="mapContainer" class="mapContainer"></div>
  </div>
</template>

<script lang="ts">
import { unref } from "vue";

/* eslint-disable @typescript-eslint/no-explicit-any */
import "leaflet/dist/leaflet.css";
import { Map } from "leaflet/src/map";
import { Marker } from "leaflet/src/layer/marker/Marker";
import { TileLayer } from "leaflet/src/layer/tile/TileLayer";
import { Tooltip } from "leaflet/src/layer/Tooltip";
import { latLng } from "leaflet";

import { usePhotonApi } from "../store/photonapi";

// fix "Uncaught TypeError: this._map is null" when zooming
(Tooltip.prototype as any)._updatePosition = function () {
  if (!this._map || !this._latlng) return;
  var pos = this._map.latLngToLayerPoint(this._latlng);
  this._setPosition(pos);
};
(Tooltip.prototype as any)._animateZoom = function (e: any) {
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
      map: undefined as unknown as Map,
    };
  },
  watch: {
    point() {
      this.updateMarker();
    },
  },
  mounted() {
    const lat = unref(this.lat);
    const lon = unref(this.lon);
    this.map = new Map("mapContainer").setView([lat, lon], 16);

    new TileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(this.map);
    this.updateMarker();
  },
  methods: {
    updateMarker(): void {
      if (this.point === undefined) {
        return;
      }
      const _latlng = latLng(this.point);
      this.map.setView(_latlng);
      const tooltip = this.tooltip;
      tooltip === ""
        ? new Marker(_latlng).addTo(this.map as Map)
        : new Marker(_latlng)
            .bindTooltip(tooltip)
            .openTooltip()
            .addTo(this.map as Map);
    },
  },
};
</script>

<style scoped>
.mapContainer {
  width: 100%;
  height: 400px;
}
</style>
