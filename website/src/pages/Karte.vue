<template>
  <div>
    <LeafletMap />
  </div>
</template>

<script setup lang="ts">
import LeafletMap from "../components/LeafletMap.vue";
import { usePhotonApi } from "../store/usePhotonApi";

const { resetPhotonApiData } = usePhotonApi();
resetPhotonApiData();
</script>
