<template>
  <div class="container-lg">
    <h1>Systemstatus</h1>
    <VersionInformation class="mt-4" />
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

<script setup lang="ts">
import VersionInformation from "../components/VersionInformation.vue";
import { useSystemStatus } from "../store/useSystemStatus";
import SystemChecks from "../components/SystemChecks.vue";

const { systemstatus, fetchSystemStatus } = useSystemStatus();
const url = "/media/systemstatus.json";
fetchSystemStatus(url, { cache: "no-cache" });
</script>
