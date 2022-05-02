<template>
  <div>
    <div
      v-if="predictions.isLoading"
      class="container-lg spinner-border"
      role="status"
    >
      <span class="visually-hidden">Loading...</span>
    </div>
    <div
      v-if="predictions.isError"
      class="container-lg alert alert-danger"
      role="alert"
    >
      Beim Laden der Datei '<a :href="predictions.url" target="_blank">{{
        predictions.url
      }}</a
      >' ist folgender Fehler aufgetretten: {{ predictions.statusText }}
    </div>
    <div
      v-if="props.map === 'images'"
      class="container-lg my-1 d-flex justify-content-end"
    >
      <div class="col-auto mb-3">
        <PredictionsCarouselDropdownMaps />
      </div>
    </div>
    <ResponsiveImage
      v-if="spatialImage.filename != '' && props.map === 'images'"
      image-class="pointer img-fluid"
      :image-href="spatialImage.filename"
      :image-height="spatialImage.height"
      :image-width="spatialImage.width"
      @click="setStep(+1)"
    />
    <LeafletMap
      v-if="props.map === 'leaflet'"
      :overlay="spatialImage.overlay"
      :south-west="spatialImage.southWest"
      :north-east="spatialImage.northEast"
    />
    <div class="container-lg mt-3 d-flex justify-content-between">
      <button class="btn btn-light" type="button" @click="setStep(-1)">
        <SolidChevronLeftIcon
          class="text-body"
          style="width: 1rem; height: 1rem"
        />
      </button>
      <div class="d-none d-xl-block d-xxl-block my-2">
        <span v-for="s in predictions.steps" :key="s">
          <span
            class="pointer m-1"
            :class="s === predictions.step ? 'text-danger' : ''"
            @click="setStep(s)"
            >{{ s }}</span
          >
        </span>
      </div>
      <div class="d-block d-xl-none d-xxl-none my-2">
        <span class="text-primary">Step: {{ predictions.step }}</span>
      </div>
      <button class="btn btn-light" type="button" @click="setStep(+1)">
        <SolidChevronRightIcon
          class="text-body"
          style="width: 1rem; height: 1rem"
        />
      </button>
    </div>
    <div class="container-lg d-flex justify-content-end mt-3">
      <button
        type="button"
        class="btn btn-outline-dark me-2"
        :class="parameter === 'tmp_2m' ? 'active' : ''"
        @click="changeParameter('tmp_2m')"
      >
        Temperatur
      </button>
      <button
        type="button"
        class="btn btn-outline-dark me-2"
        :class="parameter === 'rh_2m' ? 'active' : ''"
        @click="changeParameter('rh_2m')"
      >
        Relative Luftfeuchte
      </button>
    </div>
    <table class="container-lg table mt-4">
      <thead>
        <tr>
          <th scope="col">#</th>
          <th scope="col">Wert</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th scope="row">Analyse Datum</th>
          <td>{{ predictions.analDate }}</td>
        </tr>
        <tr>
          <th scope="row">Parameter</th>
          <td v-if="parameter === 'tmp_2m'">Temperatur</td>
          <td v-else>Relative Luftfeuchte</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from "vue";
import { usePredictions } from "../store/usePredictions";
import LeafletMap from "./LeafletMap.vue";
import ResponsiveImage from "./ResponsiveImage.vue";
import PredictionsCarouselDropdownMaps from "./PredictionsCarouselDropdownMaps.vue";
import SolidChevronLeftIcon from "./icons/SolidChevronLeftIcon.vue";
import SolidChevronRightIcon from "./icons/SolidChevronRightIcon.vue";

const props = defineProps({
  map: { type: String, required: true },
});

const {
  parameter,
  predictions,
  setStep,
  changeParameter,
  spatialImage,
  fetchPrediction,
} = usePredictions();
fetchPrediction();
</script>
