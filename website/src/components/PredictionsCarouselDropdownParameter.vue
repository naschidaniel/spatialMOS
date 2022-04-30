<template>
  <div class="input-group">
    <label class="input-group-text" for="inputGroupSelectPlot"
      ><OutlineVariableIcon class="text-body" style="width: 1rem; height: 1rem"
    /></label>
    <select id="inputGroupSelectPlot" v-model="parameter" class="form-select">
      <option value="tmp_2m">Temperatur</option>
      <option value="rh_2m">Relative Luftfeuchte</option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { usePredictions } from "../store/usePredictions";
import OutlineVariableIcon from "./icons/OutlineVariableIcon.vue";

const { parameter } = usePredictions();
</script>
