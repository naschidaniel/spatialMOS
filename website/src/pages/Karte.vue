<template>
  <div class="container-lg">
    <h1>Karte</h1>
    <PredictionsCarousel map="leaflet" />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import PredictionsCarousel from "../components/PredictionsCarousel.vue";

export default defineComponent({
  components: { PredictionsCarousel },
});
</script>
