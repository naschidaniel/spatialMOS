<template>
  <div class="container">
    <h1>systemstatus</h1>
    <h2 class="mt-4">Version</h2>
    <Repository />
    <h2 class="mt-4">Statuschecks</h2>
    <div v-if="systemstatus.isLoading" class="spinner-border" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <div v-else>
      <div v-if="systemstatus.isError" class="alert alert-danger" role="alert">
        Beim Laden der Datei '<a :href="url" target="_blank">{{ url }}</a
        >' ist folgender Fehler aufgetretten: {{ systemstatus.statusText }}
      </div>
      <SystemChecks v-else />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import Repository from "../components/Repository.vue";
import { useSystemstatus } from "../store/systemstatus";
import SystemChecks from "../components/SystemChecks.vue";

export default defineComponent({
  name: "Systemstatus",
  components: {
    Repository,
    SystemChecks,
  },
  setup() {
    const { systemstatus, fetchSystemChecks } = useSystemstatus();
    const url = "/systemstatus.json";
    fetchSystemChecks(url, { cache: "no-cache" });
    return { systemstatus, url, fetchSystemChecks };
  },
});
</script>
