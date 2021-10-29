<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container-lg">
      <router-link class="navbar-brand" to="/">MOSes.tirol</router-link>
      <button
        class="navbar-toggler"
        :class="isOpen ? 'collapsed' : ''"
        type="button"
        :aria-expanded="isOpen"
        aria-label="Toggle navigation"
        @click="toogleNavbar()"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" :class="isOpen ? 'show' : ''">
        <ul class="navbar-nav">
          <li class="nav-item" @click="toogleNavbar()">
            <router-link class="nav-link active" aria-current="page" to="/"
              >Vorhersagekarten</router-link
            >
          </li>
          <li class="nav-item" @click="toogleNavbar()">
            <router-link class="nav-link" to="/adresse"
              >Adressvorhersagen</router-link
            >
          </li>
          <li class="nav-item" @click="toogleNavbar()">
            <router-link class="nav-link" to="/punktvorhersagen"
              >Punktvorhersagen</router-link
            >
          </li>
          <li class="nav-item" @click="toogleNavbar()">
            <router-link class="nav-link" to="/projektbeschreibung"
              >Projektbeschreibung</router-link
            >
          </li>
          <li class="nav-item" @click="toogleNavbar()">
            <router-link class="nav-link" to="/api">API</router-link>
          </li>
          <li class="nav-item" @click="toogleNavbar()">
            <router-link class="nav-link" to="/kontakt">Kontakt</router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script lang="ts">
import { defineComponent } from "vue";
export default defineComponent({
  data() {
    return {
      isOpen: false,
    };
  },
  methods: {
    toogleNavbar() {
      this.isOpen = !this.isOpen;
    },
  },
});
</script>
