<template>
  <div>
    <div class="d-flex justify-content-center">
      <img class="img-fluid pointer" :src="imgHref" @click="setStep(+1)" />
    </div>
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
          <td>{{ predictions.parameter }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { usePrediction } from "../store/predictions";
import SolidChevronLeftIcon from "./icons/SolidChevronLeftIcon.vue";
import SolidChevronRightIcon from "./icons/SolidChevronRightIcon.vue";

export default defineComponent({
  name: "Predictions",
  components: {
    SolidChevronLeftIcon,
    SolidChevronRightIcon,
  },
  setup() {
    const {
      parameter,
      fetchPrediction,
      predictions,
      selectedStep,
      setStep,
      setParameter,
    } = usePrediction();
    return {
      parameter,
      fetchPrediction,
      predictions,
      selectedStep,
      setStep,
      setParameter,
    };
  },
  computed: {
    imgHref(): string {
      if (this.selectedStep === undefined) {
        return "";
      }
      const img = this.selectedStep.filename_spatialmos_mean;
      return `/media/${this.parameter}/images/${img}`;
    },
  },
  methods: {
    changeParameter(change: string) {
      this.setParameter(change);
      const url = `/media/${change}/spatialmosrun_${change}.json`;
      this.fetchPrediction(url);
      this.$router.push({ path: "/", query: { parameter: change } });
    },
  },
});
</script>
