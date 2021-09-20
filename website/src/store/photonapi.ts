import { reactive, computed, unref } from "vue";

export interface PhotonApi {
  url: string | undefined;
  isError: boolean;
  isLoading: boolean;
  statusText: string;
  lon: number | undefined;
  lat: number | undefined;
}
const photonApi: PhotonApi = reactive({
  isError: false,
  isLoading: false,
  lat: undefined,
  lon: undefined,
  statusText: "",
  url: undefined,
});

export function usePhotonApi() {
  async function fetchPhotonApiData(
    url: string,
    options?: Record<string, unknown>
  ) {
    if (url === undefined) {
      photonApi.isError = false;
      photonApi.lat = undefined;
      photonApi.lon = undefined;
      photonApi.statusText = "";
      photonApi.url = undefined;
      return;
    }
    photonApi.isLoading = true;
    const res = await fetch(url, options);
    if (res.ok) {
      photonApi.url = url;
      try {
        res.json().then((data: Record<string, any>) => {
          photonApi.lon = data.features[0].geometry.coordinates[0];
          photonApi.lat = data.features[0].geometry.coordinates[1];
          photonApi.isError = false;
          photonApi.statusText = res.statusText;
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

  const point = computed((): number[] | undefined => {
    const lat = unref(photonApi.lat);
    const lon = unref(photonApi.lon);
    if (lat === undefined || lon === undefined) {
      return undefined;
    }
    return [lat, lon];
  });

  const lat = computed((): number | undefined => {
    const lat = unref(photonApi.lat);
    return lat;
  });

  const lon = computed((): number | undefined => {
    const lon = unref(photonApi.lon);
    return lon;
  });

  const tooltip = computed((): string => {
    return "afdasdfadfdfadf";
  });

  return { photonApi, lat, lon, tooltip, point, fetchPhotonApiData };
}
