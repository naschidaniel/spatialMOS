import { reactive, computed, unref } from "vue";
import { PhotonApi } from "../model";

const photonApi: PhotonApi = reactive({
  isError: false,
  isLoading: false,
  isEmpty: false,
  lat: undefined,
  lon: undefined,
  statusText: "",
  url: undefined,
  city: undefined,
  street: undefined,
  housenumber: undefined,
});

export function usePhotonApi() {
  async function fetchPhotonApiData(
    url: string | undefined,
    options?: Record<string, unknown>
  ) {
    if (url === undefined) {
      photonApi.isError = false;
      photonApi.isEmpty = false;
      photonApi.lat = undefined;
      photonApi.lon = undefined;
      photonApi.statusText = "";
      photonApi.url = undefined;
      photonApi.city = undefined;
      photonApi.street = undefined;
      photonApi.housenumber = undefined;

      return;
    }
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

  return { photonApi, lat, lon, tooltip, point, fetchPhotonApiData };
}
