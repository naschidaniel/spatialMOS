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
import { useRoute } from "vue-router";
import PredictionsCarousel from "../components/PredictionsCarousel.vue";
import { usePredictions } from "../store/usePredictions";

export default defineComponent({
  name: "Vorhersagekarten",
  components: {
    PredictionsCarousel,
  },
  setup() {
    const route = useRoute();
    const { setParameter, predictions, fetchPrediction, setStep, plot } =
      usePredictions();
    if (
      route.query?.parameter === "tmp_2m" ||
      route.query?.parameter === "rh_2m"
    ) {
      setParameter(route.query?.parameter);
      fetchPrediction();
    } else {
      fetchPrediction();
    }
    if (route.query?.step && typeof route.query?.step === "string") {
      setStep(route.query.step);
    }
    if (route.query?.plot && typeof route.query?.plot === "string") {
      plot.value = route.query.plot;
    }
    return { predictions };
  },
});
</script>
