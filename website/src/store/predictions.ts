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
  steps: string[];
  data: SpatialMosStep[] | undefined;
  isError: boolean;
  statusText: string;
  step: string;
}

const predictions: Predictions = reactive({
  analDate: "",
  steps: [],
  data: undefined,
  isError: false,
  statusText: "",
  step: "6",
});

export function usePrediction() {
  async function fetchPrediction(
    url: string,
    options?: Record<string, unknown>
  ) {
    const res = await fetch(url, options);
    if (res.ok) {
      try {
        res.json().then((data: SpatialMosStep[]) => {
          predictions.analDate = data[0].anal_date;
          predictions.steps = Object.values(data).map((s) => s.step);
          predictions.statusText = res.statusText;
          predictions.isError = false;
          predictions.data = data;
        });
      } catch {
        predictions.isError = true;
        predictions.statusText = "Failed to convert Data";
      }
    } else {
      predictions.statusText = res.statusText;
      predictions.isError = true;
      throw new Error(res.statusText);
    }
  }

  const selectedStep = computed(() => {
    const data = predictions.data;
    if (data === undefined) {
      return [];
    }
    return data.find((s) => s.step === unref(predictions.step));
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

  return { predictions, fetchPrediction, selectedStep, setStep };
}
