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
      Version: {{ formatDate(updateTime) }},
      <a
        href="https://github.com/naschidaniel/spatialMOS/commits/main"
        target="_blank"
        rel="noreferrer"
        >{{ lastCommit }}</a
      >
    </p>
  </div>
</template>

<script setup lang="ts">
import { useData } from "../store/useData";
import { formatDate } from "../util/formatters";

const { lastCommit, updateTime } = useData();
</script>
