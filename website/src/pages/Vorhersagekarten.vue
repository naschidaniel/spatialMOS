<template>
  <div class="container-lg">
    <h1>Vorhersagekarten</h1>
    <div>
      <PredictionsCarousel map="images" />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import PredictionsCarousel from "../components/PredictionsCarousel.vue";

export default defineComponent({
  name: "Vorhersagekarten",
  components: {
    PredictionsCarousel,
  },
});
</script>
