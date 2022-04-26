<template>
  <div class="container">
    <div id="mapContainer" class="mapContainer"></div>
  </div>
</template>

<script lang="ts">
import { defineComponent, unref, PropType } from "vue";

/* eslint-disable @typescript-eslint/no-explicit-any */
import "leaflet/dist/leaflet.css";
import { Map } from "leaflet/src/map";
import { Marker } from "leaflet/src/layer/marker/Marker";
import { Tooltip } from "leaflet/src/layer/Tooltip";
import L from "leaflet";

import { usePhotonApi } from "../store/usePhotonApi";

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

export default defineComponent({
  name: "LeafletMap",
  props: {
    overlay: { type: String, required: false, default: "" },
    southWest: {
      type: Array as PropType<number[]>,
      required: false,
      default: () => {
        return [undefined, undefined];
      },
    },
    northEast: {
      type: Array as PropType<number[]>,
      required: false,
      default: () => {
        return [undefined, undefined];
      },
    },
  },
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
    overlay() {
      this.loadOverlay();
    },
  },
  mounted() {
    const lat = unref(this.lat) || this.southWest[0] + (this.northEast[0] - this.southWest[0]) / 2;
    const lon = unref(this.lon) || this.southWest[1] + (this.northEast[1] - this.southWest[1]) / 2;
    if (!lat || !lon) {
      return;
    }
    console.log(lat, lon)
    this.map = L.map("mapContainer").setView([lat, lon], 6) as Map;
    L.tileLayer("https://{s}.tile.osm.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy <a href="https://osm.org/copyright">OpenStreetMap</a> contributors',
      minZoom: 7,
    }).addTo(this.map as Map);
    this.updateMarker();
    this.loadOverlay();
  },
  methods: {
    updateMarker(): void {
      if (this.point === undefined) {
        return;
      }
      const _latlng = L.latLng(this.point);
      this.map.setView(_latlng);
      const tooltip = this.tooltip;
      tooltip === ""
        ? new Marker(_latlng).addTo(this.map as Map)
        : new Marker(_latlng)
            .bindTooltip(tooltip)
            .openTooltip()
            .addTo(this.map as Map);
    },
    loadOverlay(): void {
      if (this.overlay === "") return;
      const southWest = L.latLng(this.southWest[0], this.southWest[1]);
      const northEast = L.latLng(this.northEast[0], this.northEast[1]);
      const imageBounds = L.latLngBounds(southWest, northEast);
      const image = L.imageOverlay(this.overlay, imageBounds, {
        pane: "tilePane",
        className: "mix-blend-mode-multiply",
      });
      image.addTo(this.map as Map);
    },
  },
});
</script>

<style scoped>
.mapContainer {
  width: 100%;
  height: 600px;
}

.mix-blend-mode-multiply {
  mix-blend-mode: multiply;
}
</style>
