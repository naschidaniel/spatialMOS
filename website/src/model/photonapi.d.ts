export interface PhotonApi {
  url: string | undefined;
  isError: boolean;
  isEmpty: boolean;
  isLoading: boolean;
  statusText: string;
  lon: number | undefined;
  lat: number | undefined;
  city: string | undefined;
  street: string | undefined;
  housenumber: string | undefined;
}
