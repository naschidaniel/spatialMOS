<template>
  <div class="container">
    <div v-if="photonApi.isEmpty" class="alert alert-danger" role="alert">
      Die Suchanfrage
      <a :href="photonApi.url" target="_balnk" rel="nofollow">{{
        photonApi.url
      }}</a>
      hat zu keinem Ergebniss geführt.
    </div>
    <form>
      <div class="row">
        <div class="col">
          <input
            v-model="street"
            class="form-control"
            placeholder="Straße und Hausnummer"
          />
        </div>
      </div>
      <div class="row">
        <div class="col-md-7 mt-2">
          <input v-model="city" class="form-control" placeholder="Ort" />
        </div>
        <div class="col-md-2 mt-2">
          <input
            v-model="postcode"
            class="form-control"
            placeholder="PLZ"
            maxlength="5"
          />
        </div>
        <div id="v-model-select" class="col-md-3 mt-2">
          <select v-model="state" class="form-select">
            <option>Nordtirol</option>
            <option>Südtirol</option>
          </select>
        </div>
      </div>
      <button
        class="btn btn-primary mt-2"
        @click.prevent="fetchPhotonApiData(queryAddressUrl)"
      >
        Submit
      </button>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { useData } from "../store/useData";

export default defineComponent({
  name: "AddressForm",
  setup() {
    const { photonApi, fetchPhotonApiData } = useData();
    return { photonApi, fetchPhotonApiData };
  },
  data() {
    return {
      street: "",
      city: "",
      postcode: "",
      state: "Nordtirol",
    };
  },
  computed: {
    queryAddressUrl(): string | undefined {
      if (this.street === "" && this.city === "" && this.postcode === "") {
        return undefined;
      }
      const country = this.state === "Nordtirol" ? "Austria" : "Italy";
      const queryAddressString =
        `${this.street},${this.city},${this.postcode},${country}`.replace(
          ",,",
          ","
        );
      return `https://photon.komoot.io/api/?q=${queryAddressString}&bbox=10,46.6,12.9,47.8&limit=1`;
    },
  },
});
</script>

<style scoped>
#mapContainer {
  width: 100%;
  height: 400px;
}
</style>
