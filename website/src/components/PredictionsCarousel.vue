<template>
  <div>
    <!-- <div v-if="predictions.isLoading" class="spinner-border" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <div v-if="predictions.isError" class="alert alert-danger" role="alert">
      Beim Laden der Datei '<a :href="predictions.url" target="_blank">{{
        predictions.url
      }}</a
      >' ist folgender Fehler aufgetretten: {{ predictions.statusText }}
    </div> -->
    <div class="my-1 d-flex justify-content-end">
      <div class="col-auto">
        <div class="input-group mb-3">
          <label class="input-group-text" for="inputGroupSelectPlot"
            >Karten</label
          >
          <select
            id="inputGroupSelectPlot"
            class="form-select"
            @change="(event) => setPlot(event.target.value)"
          >
            <option value="samos_mean">SAMOS MEAN</option>
            <option value="samos_spread">SAMOS SPREAD</option>
            <option value="nwp_mean">NWP MEAN</option>
            <option value="nwp_spread">NWP SPREAD</option>
          </select>
        </div>
      </div>
    </div>
    <ResponsiveImage
      v-if="spatialImage.filename != '' && map === 'images'"
      image-class="pointer img-fluid"
      :image-href="spatialImage.filename"
      :image-height="spatialImage.height"
      :image-width="spatialImage.width"
      @click="setStep(+1)"
    />
    <LeafletMap
      v-if="map === 'leaflet'"
      :overlay="spatialImage.overlay"
      :south-west="spatialImage.southWest"
      :north-east="spatialImage.northEast"
    />
    <div class="mt-3 d-flex justify-content-between">
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
    <div class="d-flex justify-content-end mt-3">
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
    <table class="table mt-4">
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

<script lang="ts">
import { defineComponent } from "vue";
import { usePredictions } from "../store/usePredictions";
import LeafletMap from "./LeafletMap.vue";
import ResponsiveImage from "./ResponsiveImage.vue";
import SolidChevronLeftIcon from "./icons/SolidChevronLeftIcon.vue";
import SolidChevronRightIcon from "./icons/SolidChevronRightIcon.vue";

export default defineComponent({
  name: "PredictionsCarousel",
  components: {
    LeafletMap,
    ResponsiveImage,
    SolidChevronLeftIcon,
    SolidChevronRightIcon,
  },
  props: {
    map: { type: String, required: true },
  },
  setup() {
    const {
      plot,
      parameter,
      predictions,
      selectedStep,
      setStep,
      setPlot,
      changeParameter,
      spatialImage,
      fetchPrediction,
    } = usePredictions();
    fetchPrediction();
    return {
      plot,
      parameter,
      predictions,
      selectedStep,
      setStep,
      setPlot,
      changeParameter,
      spatialImage,
    };
  },
});
</script>
