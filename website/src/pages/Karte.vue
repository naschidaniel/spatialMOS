<template>
  <div>
    <div class="container-lg">
      <h1>Karte</h1>
    </div>
    <PredictionsCarousel map="leaflet" />
  </div>
</template>

<script setup lang="ts">
import PredictionsCarousel from "../components/PredictionsCarousel.vue";
import { usePhotonApi } from "../store/usePhotonApi";
const { resetPhotonApiData } = usePhotonApi();
resetPhotonApiData();
</script>
