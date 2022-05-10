<template>
  <div class="container-fluid d-lg-flex">
    <div class="my-3 me-3">
      <h1>Adresse</h1>
      <AddressForm />
      <h2 class="mt-4">Vorhersagen für ausgewählte Orte</h2>
      <ul class="list-group">
        <li class="list-group-item">
          <router-link
            :to="{
              path: '/adresse',
              query: {
                street: 'Peter-Mayr-Straße 29',
                city: 'Innsbruck',
                postcode: '6020',
                state: 'Nordtirol',
              },
            }"
            >Nordtirol, Innsbruck, Peter-Mayr-Straße 29</router-link
          >
        </li>
        <li class="list-group-item">
          <router-link
            :to="{
              path: '/adresse',
              query: {
                city: 'Wildschönau',
                state: 'Nordtirol',
              },
            }"
            >Nordtirol, Wildschönau</router-link
          >
        </li>
        <li class="list-group-item">
          <router-link
            :to="{
              path: '/adresse',
              query: {
                city: 'Bozen',
                state: 'Südtirol',
              },
            }"
            >Südtirol, Bozen</router-link
          >
        </li>
      </ul>
    </div>
    <div class="flex-grow-1"><LeafletMapContainer /></div>
  </div>
</template>

<script setup lang="ts">
import AddressForm from "../components/AddressForm.vue";
import LeafletMapContainer from "../components/LeafletMapContainer.vue";
</script>
