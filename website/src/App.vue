<template>
  <div>
    <NavigationMain />
    <main class="my-3">
      <router-view />
    </main>
    <NavigationFooter />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import NavigationMain from "./components/NavigationMain.vue";
import NavigationFooter from "./components/NavigationFooter.vue";

export default defineComponent({
  name: "App",
  components: {
    NavigationMain,
    NavigationFooter,
  },
});
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
