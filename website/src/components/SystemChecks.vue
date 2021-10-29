<template>
  <ul v-for="(group, key) in systemChecks" :key="key" class="list-group mt-4">
    <li class="list-group-item">
      <span v-if="key === 'hourly'" class="fw-bold">Stündlich</span>
      <span v-if="key === 'daily'" class="fw-bold">Täglich</span>
      <span v-if="key === 'weekly'" class="fw-bold">Wöchentlich</span>
    </li>
    <li
      v-for="systemCheck in group"
      :key="systemCheck.taskName"
      class="list-group-item"
    >
      <div class="container">
        <div class="row">
          <div class="col-1">
            <span
              class="mr-3 badge rounded-pill pointer"
              :class="
                systemCheck.failed
                  ? 'bg-danger'
                  : systemCheck.complete !== undefined && !systemCheck?.complete
                  ? 'bg-warning'
                  : 'bg-success'
              "
              :title="`${systemCheck.taskFinishedTime} ${systemCheck.taskName}`"
            >
              <span class="d-inline d-sm-inline d-md-none">&nbsp;</span>
              <span class="d-none d-md-inline">
                {{ systemCheck.failed ? "failed" : "passed" }}
              </span>
            </span>
          </div>
          <div class="col-11">
            <span class="ml-2"
              >{{ systemCheck.taskName
              }}<br class="d-inline d-sm-inline d-md-none" /><span
                class="d-none d-md-inline mx-2"
                >&ndash;</span
              > </span
            ><small>{{ formatDateTime(systemCheck.taskFinishedTime) }}</small>
          </div>
        </div>
      </div>
    </li>
  </ul>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { useData } from "../store/useData";
import { formatDateTime } from "../util/formatters";

export default defineComponent({
  name: "SystemChecks",
  setup() {
    const { systemChecks, systemstatus } = useData();
    return { systemChecks, systemstatus };
  },
  methods: {
    formatDateTime(date: string | undefined) {
      return date
        ? formatDateTime(Date.parse(date))
        : formatDateTime(undefined);
    },
  },
});
</script>
