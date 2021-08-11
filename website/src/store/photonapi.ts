import { reactive, computed, unref } from "vue";

export interface PhotonApi {
  url: string | undefined;
  isError: boolean;
  statusText: string;
  lon: number | undefined;
  lat: number | undefined;
}
const photonApi: PhotonApi = reactive({
  url: undefined,
  isError: false,
  statusText: "",
  lon: undefined,
  lat: undefined,
});

export function usePhotonApi() {
  async function fetchPhotonApiData(
    url: string,
    options?: Record<string, unknown>
  ) {
    if (url === undefined) {
      return;
    }
    const res = await fetch(url, options);
    if (res.ok) {
      photonApi.url = url;
      try {
        res.json().then((data: Record<string, any>) => {
          const coordinates = data.features[0].geometry.coordinates;
          photonApi.lon = coordinates[0];
          photonApi.lat = coordinates[1];
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
  }

  const point = computed(() => {
    const lat = unref(photonApi.lat);
    const lon = unref(photonApi.lon);
    console.log(lat);
    return [lat, lon];
  });

  return { photonApi, point, fetchPhotonApiData };
}
