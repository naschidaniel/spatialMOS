import { reactive, computed, unref } from "vue";
export interface SpatialMosStep {
  status: string;
  step: string;
  anal_date: string;
  valid_date: string;
  parameter: string;
  unit: string;
  prediction_json_file: string;
  filename_nwp_mean: string;
  filename_nwp_spread: string;
  filename_spatialmos_mean: string;
  filename_spatialmos_spread: string;
}

export interface Predictions {
  analDate: string;
  data: SpatialMosStep[] | undefined;
  isLoading: boolean;
  isError: boolean;
  statusText: string;
  step: string;
  steps: string[];
  parameter: string;
  url: string;
}

const predictions: Predictions = reactive({
  analDate: "",
  steps: [],
  data: undefined,
  isError: false,
  isLoading: false,
  statusText: "",
  step: "6",
  parameter: "tmp_2m",
  url: "",
});

export function usePrediction() {
  async function fetchPrediction(
    url: string,
    options?: Record<string, unknown>
  ) {
    predictions.url = url;
    predictions.isLoading = true;
    const res = await fetch(url, options);
    if (res.ok) {
      try {
        res.json().then((data: SpatialMosStep[]) => {
          predictions.analDate = data[0].anal_date;
          predictions.steps = Object.values(data).map((s) => s.step);
          predictions.statusText = res.statusText;
          predictions.isError = false;
          predictions.data = data;
          predictions.parameter = data[0].parameter;
        });
      } catch {
        predictions.isError = true;
        predictions.statusText = "Failed to convert Data";
      }
    } else {
      predictions.statusText = res.statusText;
      predictions.isError = true;
    }
    predictions.isLoading = false;
  }

  const parameter = computed(() => {
    return unref(predictions.parameter);
  });

  const selectedStep = computed(() => {
    return (
      predictions.data?.find((s) => s.step === unref(predictions.step)) ||
      undefined
    );
  });

  function setStep(change: string | number) {
    if (typeof change === "number") {
      const newIndex =
        predictions.steps.indexOf(unref(predictions.step)) + change;
      predictions.step =
        newIndex === predictions.steps.length
          ? predictions.steps[0]
          : newIndex === -1
          ? predictions.steps[predictions.steps.length - 1]
          : predictions.steps[newIndex];
      return;
    }
    predictions.step = change;
  }

  function setParameter(change: string) {
    predictions.parameter = change;
  }

  return {
    parameter,
    predictions,
    fetchPrediction,
    selectedStep,
    setStep,
    setParameter,
  };
}
