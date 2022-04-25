<template>
  <div class="container-lg">
    <h1>Vorhersagekarten</h1>
    <div v-if="predictions.isLoading" class="spinner-border" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <div v-else>
      <div v-if="predictions.isError" class="alert alert-danger" role="alert">
        Beim Laden der Datei '<a :href="predictions.url" target="_blank">{{
          predictions.url
        }}</a
        >' ist folgender Fehler aufgetretten: {{ predictions.statusText }}
      </div>
      <PredictionsCarousel v-else />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import PredictionsCarousel from "../components/PredictionsCarousel.vue";
import { usePredictions } from "../store/usePredictions";

export default defineComponent({
  name: "Vorhersagekarten",
  components: {
    PredictionsCarousel,
  },
  setup() {
    const { predictions, fetchPrediction } = usePredictions();
    fetchPrediction();
    return { predictions };
  },
});
</script>
