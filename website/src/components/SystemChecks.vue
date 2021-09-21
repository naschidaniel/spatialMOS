<template>
  <ul class="list-group">
    <li class="list-group-item">Check</li>
    <li
      v-for="systemCheck in systemChecks"
      :key="systemCheck.name"
      class="list-group-item"
    >
      <span class="d-inline d-sm-inline d-md-none ml-1">
        <small>
          <span
            class="mr-1 badge rounded-pill mr-2"
            :class="systemCheck.isTooOld ? 'bg-success' : 'bg-danger'"
            title="{{ systemCheck.taskFinishedTime }}"
            >&nbsp;</span
          >
          {{ systemCheck.checkName }}
        </small>
      </span>
      <span class="d-none d-md-inline ml-2">
        <span
          class="d-none d-md-inline ml-2 mr-3 badge rounded-pill"
          :class="systemCheck.isTooOld ? 'bg-success' : 'bg-danger'"
          style="width: 60px"
          :title="`${systemCheck.taskFinishedTime} ${systemCheck.taskName}`"
        >
          {{ systemCheck.isTooOld ? "passed" : "failed" }}
        </span>
        <span class="mx-2">{{ systemCheck.checkName }}</span
        >&ndash;<small class="mx-2">{{
          formatDateTime(systemCheck.taskFinishedTime)
        }}</small>
      </span>
    </li>
  </ul>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { useSystemstatus } from "../store/systemstatus";
import { formatDateTime } from "../util/formatters";

export default defineComponent({
  name: "SystemChecks",
  setup() {
    const { systemChecks, systemstatus } = useSystemstatus();
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
