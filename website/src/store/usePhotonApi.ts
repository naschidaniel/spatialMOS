import { reactive, computed, unref } from "vue";
import { PhotonApi } from "../model";
import { useAddress } from "./useAddress";

const photonApi: PhotonApi = reactive({
  isError: false,
  isLoading: false,
  isEmpty: false,
  lat: 47.259659,
  lon: 11.400375,
  statusText: "",
  url: undefined,
  city: undefined,
  street: undefined,
  housenumber: undefined,
});

export function usePhotonApi() {
  async function fetchPhotonApiData(
    city: string,
    postcode: string,
    state: string,
    street: string,
    options?: Record<string, unknown>
  ) {
    if (street === "" && city === "" && postcode === "") {
      photonApi.isError = false;
      photonApi.isEmpty = false;
      photonApi.lat = undefined;
      photonApi.lon = undefined;
      photonApi.statusText = "";
      photonApi.url = undefined;
      return;
    }
    const country = state === "Nordtirol" ? "Austria" : "Italy";
    const queryAddressString =
      `${street},${city},${postcode},${country}`.replace(",,", ",");
    const url = `https://photon.komoot.io/api/?q=${queryAddressString}&bbox=10,46.6,12.9,47.8&limit=1`;

    photonApi.isLoading = true;
    const res = await fetch(url, options);
    if (res.ok) {
      photonApi.url = url;
      try {
        res.json().then((data: Record<string, any>) => {
          if (data.features.length === 0) {
            photonApi.isEmpty = true;
            photonApi.url = url;
          } else {
            photonApi.lon = data.features[0].geometry.coordinates[0];
            photonApi.lat = data.features[0].geometry.coordinates[1];
            photonApi.isError = false;
            photonApi.statusText = res.statusText;
            photonApi.city = data.features[0].properties.city;
            photonApi.street = data.features[0].properties.street;
            photonApi.housenumber = data.features[0].properties.housenumber;
          }
        });
      } catch {
        photonApi.isError = true;
        photonApi.statusText =
          "Failed to convert Data from https://photon.komoot.io";
      }
    } else {
      photonApi.statusText = res.statusText;
      photonApi.isError = true;
    }
    photonApi.isLoading = false;
  }

  const point = computed((): [number, number] | undefined => {
    const lat = unref(photonApi.lat);
    const lon = unref(photonApi.lon);
    if (lat === undefined || lon === undefined) {
      return undefined;
    }
    return [lat, lon];
  });

  const lat = computed((): number | undefined => {
    return unref(photonApi.lat);
  });

  const lon = computed((): number | undefined => {
    return unref(photonApi.lon);
  });

  const tooltip = computed((): string => {
    const tooltip = [
      unref(photonApi.city),
      unref(photonApi.street),
      unref(photonApi.housenumber),
    ]
      .join(" ")
      .trim();
    return tooltip;
  });

  return {
    photonApi,
    lat,
    lon,
    tooltip,
    point,
    fetchPhotonApiData,
  };
}
