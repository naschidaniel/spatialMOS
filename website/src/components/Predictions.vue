<template>
  <div>
    <div>Analyse Datum: {{ predictions.analDate }}</div>
    <img class="img-fluid pointer" :src="imgHref" @click="setStep(+1)" />
    <div>
      <span class="pointer" @click="setStep(-1)">back</span>
      <span v-for="s in predictions.steps" :key="s">
        <span
          class="pointer"
          :class="s === predictions.step ? 'text-danger' : ''"
          @click="setStep(s)"
          >{{ s }}</span
        >
      </span>
      <span class="pointer" @click="setStep(+1)">next</span>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { usePrediction } from "../store/predictions";

export default defineComponent({
  name: "Predictions",
  setup() {
    const { predictions, fetchPrediction, selectedStep, setStep } =
      usePrediction();
    fetchPrediction("/20210802_step_006.json");
    return { predictions, selectedStep, setStep };
  },
  computed: {
    imgHref() {
      const img = this.selectedStep?.filename_spatialmos_mean;
      return img ? `/images/${img}` : "";
    },
  },
});
</script>
