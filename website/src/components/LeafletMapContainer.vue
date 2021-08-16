<template>
  <div v-if="point !== undefined">
    <div v-if="photonApi.isLoading" class="spinner-border mt-4" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <div v-else class="mt-4">
      <div v-if="photonApi.isError" class="alert alert-danger" role="alert">
        Beim Laden der '<a :href="photonApi.url" target="_blank">{{
          photonApi.url
        }}</a
        >' ist folgender Fehler aufgetretten: {{ photonApi.statusText }}
      </div>
      <div v-else>
        <h2>Karte</h2>
        <LeafletMap />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { usePhotonApi } from "../store/photonapi";
import LeafletMap from "../components/LeafletMap.vue";

export default defineComponent({
  components: { LeafletMap },
  setup() {
    const { photonApi, point } = usePhotonApi();
    return { photonApi, point };
  },
});
</script>
