<template>
  <div>
    <p>
      Github Repository:
      <a
        href="https://github.com/naschidaniel/spatialMOS"
        target="_blank"
        rel="noreferrer"
        >naschidaniel/spatialMOS</a
      >
    </p>
    <p>
      Version: {{ formatDate(updateTime) }}
      <a
        href="https://github.com/naschidaniel/spatialMOS/commits/main"
        target="_blank"
        rel="noreferrer"
        >{{ lastCommit }}</a
      >
    </p>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { useData } from "../store/useData";
import { formatDate } from "../util/formatters";

export default defineComponent({
  name: "Repository",
  setup() {
    const { lastCommit, updateTime } = useData();
    return { lastCommit, updateTime };
  },
  methods: {
    formatDate,
  },
});
</script>
