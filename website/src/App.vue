<template>
  <div>
    <Navigation />
    <main class="my-3">
      <router-view />
    </main>
    <Footer />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import Navigation from "./components/Navigation.vue";
import Footer from "./components/Footer.vue";

export default defineComponent({
  name: "App",
  components: {
    Navigation,
    Footer,
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
