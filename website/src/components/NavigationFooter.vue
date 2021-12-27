<template>
  <footer class="page-footer font-small text-center blue mt-4">
    <span class="footer-copyright py-3"
      >©
      <router-link to="/">MOSes.tirol</router-link>
    </span>
    <span> ‒ </span>
    <span class="py-3">
      <router-link to="/impressum">Impressum</router-link>
    </span>
    <span> ‒ </span>
    <span class="py-3">
      <router-link to="/dsgvo">DSVGO</router-link>
    </span>
    <span> ‒ </span>
    <span class="py-3">
      <router-link to="/systemstatus">Systemstatus</router-link>
    </span>
  </footer>
</template>

<script lang="ts">
import { defineComponent } from "vue";
export default defineComponent({});
</script>
