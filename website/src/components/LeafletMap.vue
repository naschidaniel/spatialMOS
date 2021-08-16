<template>
  <div class="container">
    <div id="mapContainer"></div>
  </div>
</template>

<script lang="ts">
import { unref } from "vue";
import { usePhotonApi } from "../store/photonapi";

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
  setup() {
    const { point } = usePhotonApi();
    return { point };
  },
  data() {
    return {
      map: undefined,
      activeLayer: undefined,
      tooltip:
        "29, Peter-Mayr-Straße, Wilten, Innsbruck, Tirol, 6020, Österreich",
    };
  },
  mounted() {
    const lat = unref(this.lat) || 47.258502750000005;
    const lon = unref(this.lon) || 11.388483871855112;
    this.map = L.map("mapContainer").setView([lat, lon], 16);

    this.activeLayer = L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(this.map);
    L.marker([lat, lon])
      .bindTooltip(this.tooltip)
      .openTooltip()
      .addTo(this.map);
  },
  watch: {
    point() {
      console.log("done watch");
      this.updateActiveBounds();
    },
  },
  methods: {
    updateActiveBounds() {
      if (this.point === undefined) {
        return;
      }
      this.map.setView(this.point);
      L.marker(this.point)
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
