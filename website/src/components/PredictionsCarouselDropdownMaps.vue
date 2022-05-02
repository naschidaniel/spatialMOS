<template>
  <div class="input-group mb-1">
    <label class="input-group-text" for="inputGroupSelectPlot"
      ><OutlineMapIcon class="text-body" style="width: 1rem; height: 1rem"
    /></label>
    <select id="inputGroupSelectPlot" v-model="plot" class="form-select">
      <option value="samos_mean">SAMOS MEAN</option>
      <option value="samos_spread">SAMOS SPREAD</option>
      <option value="nwp_mean">NWP MEAN</option>
      <option value="nwp_spread">NWP SPREAD</option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { usePredictions } from "../store/usePredictions";
import OutlineMapIcon from "./icons/OutlineMapIcon.vue";

const { plot } = usePredictions();
</script>
