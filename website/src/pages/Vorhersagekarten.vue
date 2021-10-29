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
      <Predictions v-else />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import Predictions from "../components/Predictions.vue";
import { usePrediction } from "../store/predictions";

export default defineComponent({
  name: "Vorhersagekarten",
  components: {
    Predictions,
  },
  setup() {
    const { parameter, predictions, fetchPrediction } = usePrediction();
    const url = `/media/${parameter.value}/spatialmosrun_${parameter.value}.json`;
    fetchPrediction(url, { cache: "no-cache" });
    return { predictions, fetchPrediction };
  },
});
</script>
