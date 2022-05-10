<template>
  <div>
    <div v-if="photonApi.isLoading" class="spinner-border mt-4" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <div v-else>
      <div v-if="photonApi.isError" class="alert alert-danger" role="alert">
        Beim Laden der '<a :href="photonApi.url" target="_blank">{{
          photonApi.url
        }}</a
        >' ist folgender Fehler aufgetretten: {{ photonApi.statusText }}
      </div>
      <div v-else>
        <LeafletMap />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePhotonApi } from "../store/usePhotonApi";
import LeafletMap from "../components/LeafletMap.vue";

const { photonApi } = usePhotonApi();
</script>
