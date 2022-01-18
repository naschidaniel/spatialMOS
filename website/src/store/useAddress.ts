import { ref, Ref, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";
import { usePhotonApi } from "./usePhotonApi";

const city: Ref<string> = ref("");
const postcode: Ref<string> = ref("");
const state: Ref<string> = ref("");
const street: Ref<string> = ref("");

export function useAddress() {
  const route = useRoute();
  const router = useRouter();
  const { fetchPhotonApiData } = usePhotonApi();

  function resetAddressForm(): void {
    city.value = "";
    postcode.value = "";
    state.value = "";
    street.value = "";
  }

  function submitAddressForm(): void {
    router.push({
      path: "adresse",
      query: {
        street: street.value,
        city: city.value,
        postcode: postcode.value,
        state: state.value,
      },
    });
    fetchPhotonApiData(city.value, postcode.value, state.value, street.value);
  }

  watchEffect(() => {
    if (
      route.query?.city != undefined &&
      typeof route.query?.city === "string"
    ) {
      city.value = route.query.city;
    } else {
      city.value = "";
    }

    if (
      route.query?.postcode != undefined &&
      typeof route.query?.postcode === "string"
    ) {
      postcode.value = route.query.postcode;
    } else {
      postcode.value = "";
    }

    if (
      route.query?.state != undefined &&
      typeof route.query?.state === "string"
    ) {
      state.value = route.query.state;
    } else {
      state.value = "";
    }

    if (
      route.query?.street != undefined &&
      typeof route.query?.street === "string"
    ) {
      street.value = route.query.street;
    } else {
      street.value = "";
    }
  });

  return {
    city,
    postcode,
    resetAddressForm,
    state,
    street,
    submitAddressForm,
  };
}
