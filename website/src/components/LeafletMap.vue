<template>
  <div id="mapContainer" class="mapContainer">
    <div class="leaflet-top leaflet-right"></div>
    <div class="leaflet-bottom leaflet-left mb-3">
      <div class="leaflet-control">
        <PredictionsCarouselDropdownMaps />
        <PredictionsCarouselDropdownParameter />
      </div>
    </div>
    <div class="leaflet-bottom leaflet-right d-flex mb-3">
      <div class="ml-2 leaflet-control leaflet-bar">
        <a
          class="leaflet-control-spatialmos-next"
          type="button"
          @click="setStep(-1)"
        >
          <SolidChevronLeftIcon
            class="text-body"
            style="width: 1rem; height: 1rem"
          />
        </a>
      </div>
      <div class="mr-2 leaflet-control leaflet-bar">
        <a
          class="leaflet-control-spatialmos-pervious"
          type="button"
          @click="setStep(+1)"
        >
          <SolidChevronRightIcon
            class="text-body"
            style="width: 1rem; height: 1rem"
          />
        </a>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, unref, PropType } from "vue";
import SolidChevronLeftIcon from "./icons/SolidChevronLeftIcon.vue";
import SolidChevronRightIcon from "./icons/SolidChevronRightIcon.vue";
import PredictionsCarouselDropdownMaps from "./PredictionsCarouselDropdownMaps.vue";
import PredictionsCarouselDropdownParameter from "./PredictionsCarouselDropdownParameter.vue";

/* eslint-disable @typescript-eslint/no-explicit-any */
import "leaflet/dist/leaflet.css";
import { FeatureGroup, Tooltip, Marker, Map, Control } from "leaflet";
import L from "leaflet";

import { usePredictions } from "../store/usePredictions";
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
  components: {
    PredictionsCarouselDropdownMaps,
    SolidChevronLeftIcon,
    SolidChevronRightIcon,
    PredictionsCarouselDropdownParameter,
  },
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

  setup(props) {
    const { parameter, plot, setPlot, setStep, step } = usePredictions();
    const { latlon, lat, lon, tooltip } = usePhotonApi();
    const latidude =
      unref(lat) ||
      props.southWest[0] + (props.northEast[0] - props.southWest[0]) / 2;
    const longitude =
      unref(lon) ||
      props.southWest[1] + (props.northEast[1] - props.southWest[1]) / 2;

    return {
      latlon,
      latidude,
      longitude,
      parameter,
      plot,
      tooltip,
      setPlot,
      setStep,
      step,
    };
  },
  data() {
    return {
      map: undefined as unknown as Map,
      control: undefined as unknown as Control,
    };
  },
  watch: {
    latlon() {
      this.updateMarker();
    },
    overlay() {
      this.overlayLayer().addTo(this.map as Map);
    },
  },
  mounted() {
    this.map = L.map("mapContainer", {
      attributionControl: false,
      minZoom: 6,
      maxZoom: 13,
    }).setView([this.latidude, this.longitude], 9) as Map;

    const osm = L.tileLayer("https://{s}.tile.osm.org/{z}/{x}/{y}.png", {
      attribution:
        "<a href='https://www.openstreetmap.org' target='_blank' rel='noreferrer'>OpenStreetMap-Mitwirkende</a>",
    });

    const gelande = L.tileLayer(
      `https://maps.wien.gv.at/basemap/bmapgelaende/grau/google3857/{z}/{y}/{x}.jpeg`,
      {
        attribution:
          "<a href='https://basemap.at/' target='_blank' rel='noreferrer'>basemap.at</a>",
      }
    );

    const beschriftung = L.tileLayer(
      `https://maps.wien.gv.at/basemap/bmapoverlay/normal/google3857/{z}/{y}/{x}.png`,
      {
        pane: "markerPane",
      }
    );

    const baseLayers = {
      Gelände: gelande.addTo(this.map as Map),
      OpenStreetMap: osm,
    };

    const overlays = {
      Beschriftung: beschriftung,
    };
    this.overlayLayer().addTo(this.map as Map);
    this.control = L.control.layers(baseLayers, overlays);
    this.control.addTo(this.map as Map);
    this.updateMarker();
  },
  methods: {
    updateMarker(): void {
      if (this.latlon === undefined) {
        return;
      }
      const _latlng = L.latLng(this.latlon);
      this.map.setView(_latlng);
      const tooltip = this.tooltip;
      tooltip === ""
        ? new Marker(_latlng).addTo(this.map as Map)
        : new Marker(_latlng)
            .bindTooltip(tooltip)
            .openTooltip()
            .addTo(this.map as Map);
    },
    overlayLayer(): FeatureGroup {
      const overlayImageGroup = L.featureGroup([], {
        id: "spatialmosMaps",
        pane: "overlayPane",
      });
      if (this.overlay === "") return overlayImageGroup;
      this.map.eachLayer(
        (layer) => layer?.options?.id === "spatialmosMaps" && layer.remove()
      );
      const _southWest = L.latLng(this.southWest[0], this.southWest[1]);
      const _northEast = L.latLng(this.northEast[0], this.northEast[1]);
      const imageBounds = L.latLngBounds(_southWest, _northEast);
      const image = L.imageOverlay(this.overlay, imageBounds, {
        id: "spatialmosImage",
        pane: "overlayPane",
        className: "mix-blend-mode-multiply",
        opacity: 0.85,
      });

      if (this.map.attributionControl) {
        this.map.attributionControl.remove();
      }
      L.control
        .attribution({
          position: "bottomright",
          prefix: `<strong>${this.plot
            .replace("_", " ")
            .toUpperCase()}</strong> ${
            this.parameter === "tmp_2m" ? "Temperatur" : "Relative Luftfeuchte"
          }`,
        })
        .addAttribution(`Step: ${this.step}`)
        .addTo(this.map as Map);
      image.addTo(overlayImageGroup);
      return overlayImageGroup;
    },
  },
});
</script>

<style scoped>
.mapContainer {
  width: 100%;
  height: calc(100vh - 200px);
  background: #fff;
}

.mix-blend-mode-multiply {
  mix-blend-mode: multiply;
}

.leaflet-control-spatialmos-next,
.leaflet-control-spatialmos-pervious {
  font: bold 18px "Lucida Console", Monaco, monospace;
  text-indent: 1px;
}
</style>
