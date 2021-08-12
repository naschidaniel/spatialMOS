<template>
  <div class="container">
    <h1>Vorhersagekarten</h1>
    <Predictions />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import Predictions from "../components/Predictions.vue";

export default defineComponent({
  name: "Vorhersagekarten",
  components: {
    Predictions,
  },
});
</script>
