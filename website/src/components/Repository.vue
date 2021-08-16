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
      Systeminfo:
      <a
        href="https://github.com/naschidaniel/spatialMOS/commits/main"
        target="_blank"
        rel="noreferrer"
        >{{ lastCommit }}</a
      >
    </p>
    <p>Updatetime: {{ updateTime }}</p>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { useSystemstatus } from "../store/systemstatus";

export default defineComponent({
  name: "Repository",
  setup() {
    const { lastCommit, updateTime } = useSystemstatus();
    return { lastCommit, updateTime };
  },
});
</script>
