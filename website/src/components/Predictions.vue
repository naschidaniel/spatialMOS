<template>
  <div>
    <div>Analyse Datum: {{ predictions.analDate }}</div>
    <img class="img-fluid" :src="imgHref" />
    <div>
      <span v-for="s in predictions.steps" :key="s">
        <span @click="setStep(s)" class="pointer">{{ s }}</span>
      </span>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { usePrediction } from "../store/predictions"

export default defineComponent({
  name: "Predictions",
  setup() {
    const { predictions, fetchPrediction, selectedStep, setStep } = usePrediction();
    fetchPrediction('/20210802_step_006.json')
    return { predictions, selectedStep, setStep }
  },
  computed: {
    imgHref() {
      const img = this.selectedStep?.filename_spatialmos_mean
      return img ? `/images/${img}` : ''
    }
  }
});
</script>