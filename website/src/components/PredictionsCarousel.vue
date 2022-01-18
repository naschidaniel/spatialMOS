<template>
  <div>
    <div class="my-1 d-flex justify-content-end">
      <div class="col-auto">
        <div class="input-group mb-3">
          <label class="input-group-text" for="inputGroupSelectPlot"
            >Karten</label
          >
          <select id="inputGroupSelectPlot" v-model="plot" class="form-select">
            <option value="samos_mean">SAMOS MEAN</option>
            <option value="samos_spread">SAMOS SPREAD</option>
            <option value="nwp_mean">NWP MEAN</option>
            <option value="nwp_spread">NWP SPREAD</option>
          </select>
        </div>
      </div>
    </div>
    <ResponsiveImage
      v-if="spatialImage.filename != ''"
      image-class="pointer img-fluid"
      :image-href="spatialImage.filename"
      :image-height="spatialImage.height"
      :image-width="spatialImage.width"
      @click="setStep(+1)"
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
import { SpatialMosImage } from "../model";
import ResponsiveImage from "./ResponsiveImage.vue";
import SolidChevronLeftIcon from "./icons/SolidChevronLeftIcon.vue";
import SolidChevronRightIcon from "./icons/SolidChevronRightIcon.vue";

export default defineComponent({
  name: "PredictionsCarousel",
  components: {
    ResponsiveImage,
    SolidChevronLeftIcon,
    SolidChevronRightIcon,
  },
  setup() {
    const {
      parameter,
      predictions,
      plot,
      selectedStep,
      setStep,
      changeParameter,
    } = usePredictions();
    return {
      parameter,
      predictions,
      plot,
      selectedStep,
      setStep,
      changeParameter,
    };
  },
  computed: {
    spatialImage(): SpatialMosImage {
      if (this.selectedStep === undefined) {
        return { filename: "", height: 0, width: 0 };
      }
      return this.plot === "samos_spread"
        ? this.selectedStep.spatialmos_spread
        : this.plot === "nwp_mean"
        ? this.selectedStep.nwp_mean
        : this.plot === "nwp_spread"
        ? this.selectedStep.nwp_spread
        : this.selectedStep.spatialmos_mean;
    },
  },
});
</script>
