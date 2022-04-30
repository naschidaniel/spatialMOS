<template>
  <div>
    <NavigationMain />
    <main class="my-3">
      <router-view />
    </main>
    <NavigationFooter />
  </div>
</template>

<script setup lang="ts">
import NavigationMain from "./components/NavigationMain.vue";
import NavigationFooter from "./components/NavigationFooter.vue";
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a {
  text-decoration: none !important;
}

.pointer {
  cursor: pointer;
}
</style>
