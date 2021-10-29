export interface SpatialMosImage {
  filename: string;
  height: number;
  width: number;
}
export interface SpatialMosStep {
  status: string;
  step: string;
  anal_date: string;
  valid_date: string;
  parameter: string;
  unit: string;
  prediction_json_file: string;
  nwp_mean: SpatialMosImage;
  nwp_spread: SpatialMosImage;
  spatialmos_mean: SpatialMosImage;
  spatialmos_spread: SpatialMosImage;
}

export interface Predictions {
  analDate: string;
  data: SpatialMosStep[];
  isLoading: boolean;
  isError: boolean;
  statusText: string;
  step: string;
  steps: string[];
  parameter: string;
  plot: string;
  url: string;
}
