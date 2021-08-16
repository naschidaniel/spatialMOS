<template>
  <div class="container">
    <h1>Adresse</h1>
    <AddressForm />
    <LeafletMapContainer />
    <h2 class="mt-4">Vorhersagen für Orte in Tirol</h2>
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
              street: '',
              city: 'Wildschönau',
              postcode: '',
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
              street: '',
              city: 'Bozen',
              postcode: '',
              state: 'Südtirol',
            },
          }"
          >Südtirol, Bozen</router-link
        >
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { usePhotonApi } from "../store/photonapi";
import AddressForm from "../components/AddressForm.vue";
import LeafletMapContainer from "../components/LeafletMapContainer.vue";

export default defineComponent({
  components: { AddressForm, LeafletMapContainer },
  setup() {
    const { photonApi } = usePhotonApi();
    return { photonApi };
  },
});
</script>
