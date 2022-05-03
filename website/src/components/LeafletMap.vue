<template>
  <div id="mapContainer" class="mapContainer">
    <div class="leaflet-control-spatialmos-headline-container">
      <div class="leaflet-control-spatialmos-headline">
        <strong>{{ plotName }}</strong> | {{ parameterName }} | Step: {{ step }}
      </div>
    </div>
    <div class="leaflet-bottom leaflet-left">
      <div class="leaflet-control">
        <PredictionsCarouselDropdownMaps />
        <PredictionsCarouselDropdownParameter />
      </div>
    </div>
    <a
      class="leaflet-bar leaflet-control-spatialmos-next"
      type="button"
      @click="setStep(+1)"
    >
      <SolidChevronRightIcon
        class="text-body"
        style="width: 1rem; height: 1rem"
      />
    </a>
    <a
      class="leaflet-bar leaflet-control-spatialmos-pervious"
      type="button"
      @click="setStep(-1)"
    >
      <SolidChevronLeftIcon
        class="text-body"
        style="width: 1rem; height: 1rem"
      />
    </a>
  </div>
</template>

<script setup lang="ts">
import SolidChevronLeftIcon from "./icons/SolidChevronLeftIcon.vue";
import SolidChevronRightIcon from "./icons/SolidChevronRightIcon.vue";
import PredictionsCarouselDropdownMaps from "./PredictionsCarouselDropdownMaps.vue";
import PredictionsCarouselDropdownParameter from "./PredictionsCarouselDropdownParameter.vue";

import "leaflet/dist/leaflet.css";

import { useLeafletMap } from "../store/useLeafletMap";
import { usePredictions } from "../store/usePredictions";

const { setStep, parameterName, step, plotName } = usePredictions();
useLeafletMap();
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
  text-indent: 1px;
  position: absolute;
  top: 50%;
  padding-top: 20px;
  padding-bottom: 20px;
  padding-left: 10px;
  padding-right: 10px;
  z-index: 1100;
  background: #fff;
}

.leaflet-control-spatialmos-next {
  right: 20px;
}
.leaflet-control-spatialmos-pervious {
  left: 20px;
}

.leaflet-control-spatialmos-headline-container {
  display: flex;
}

.leaflet-control-spatialmos-headline {
  font-size: large;
  padding: 10px;
  margin-left: auto;
  margin-right: auto;
  z-index: 600;
  background: #fff;
}

@media (max-width: 700px) {
  .leaflet-control-spatialmos-headline {
    font-size: small;
  }
}
</style>
