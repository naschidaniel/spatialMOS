<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
      <router-link class="navbar-brand" to="/">MOSes.tirol</router-link>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div id="navbarNav" class="collapse navbar-collapse">
        <ul class="navbar-nav">
          <li class="nav-item">
            <router-link class="nav-link active" aria-current="page" to="/"
              >Vorhersagekarten</router-link
            >
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/adresse"
              >Adressvorhersagen</router-link
            >
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/punktvorhersagen"
              >Punktvorhersagen</router-link
            >
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/projektbeschreibung"
              >Projektbeschreibung</router-link
            >
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/api">API</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/kontakt">Kontakt</router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script lang="ts">
import { defineComponent } from "vue";
export default defineComponent({});
</script>
