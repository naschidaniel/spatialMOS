export type ImageSizes =
  | undefined
  | "2xs"
  | "xs"
  | "sm"
  | "md"
  | "lg"
  | "xl"
  | "2xl";

export type AvailableBoxSizes = {
  "2xs": 384;
  xs: 512;
  sm: 640;
  md: 768;
  lg: 1080;
  xl: 1280;
  "2xl": 1536;
};

export interface DataState {
  availableBoxSizes: AvailableBoxSizes;
  isWebpSupported: undefined | boolean;
}
