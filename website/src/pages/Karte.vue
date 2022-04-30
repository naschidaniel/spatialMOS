<template>
  <div>
    <LeafletMap
      :overlay="spatialImage.overlay"
      :south-west="spatialImage.southWest"
      :north-east="spatialImage.northEast"
    />
  </div>
</template>

<script setup lang="ts">
import LeafletMap from "../components/LeafletMap.vue";
import { usePhotonApi } from "../store/usePhotonApi";
import { usePredictions } from "../store/usePredictions";

const { resetPhotonApiData } = usePhotonApi();
resetPhotonApiData();

const { spatialImage, fetchPrediction } = usePredictions();
fetchPrediction();
</script>
