<template>
  <div class="container-fluid">
    <h1>Adresse</h1>
    <AddressMap />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import AddressMap from "../components/AddressMap.vue";
export default defineComponent({
  components: { AddressMap },
});
</script>
