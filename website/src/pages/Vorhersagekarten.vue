<template>
  <div class="container-lg my-3">
    <h1>Vorhersagekarten</h1>
    <div>
      <PredictionsCarousel map="images" />
    </div>
  </div>
</template>

<script setup lang="ts">
import PredictionsCarousel from "../components/PredictionsCarousel.vue";
</script>
