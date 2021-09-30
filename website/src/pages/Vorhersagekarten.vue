<template>
  <div class="container">
    <h1>Vorhersagekarten</h1>
    <div v-if="predictions.isLoading" class="spinner-border" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <div v-else>
      <div v-if="predictions.isError" class="alert alert-danger" role="alert">
        Beim Laden der Datei '<a :href="url" target="_blank">{{ url }}</a
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
    const url = "/media/tmp_2m/spatialmosrun_tmp_2m.json";
    const { predictions, fetchPrediction } = usePrediction();
    fetchPrediction(url, { cache: "no-cache" });
    return { url, predictions };
  },
});
</script>
