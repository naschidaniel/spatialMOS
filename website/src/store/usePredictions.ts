import { reactive, computed, unref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { SpatialMosStep, Predictions } from "../model";

const predictions: Predictions = reactive({
  analDate: "",
  steps: [],
  data: [],
  isError: false,
  isLoading: false,
  statusText: "",
  step: "6",
  parameter: "tmp_2m",
  plot: "samos_mean",
  url: "",
});

export function usePrediction() {
  const router = useRouter();

  async function fetchPrediction() {
    const url = `/media/${parameter.value}/spatialmosrun_${parameter.value}.json`;
    const options: Record<string, unknown> = { cache: "no-cache" };
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
          router.push({ path: "/", query: { parameter: data[0].parameter } });
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

  const plot = computed({
    get() {
      return predictions.plot;
    },
    set(value) {
      predictions.plot = value as string;
    },
  });

  function changeParameter(change: string) {
    setParameter(change);
    fetchPrediction();
  }

  const selectedStep = computed(() =>
    predictions.data?.find((s) => s.step === unref(predictions.step))
  );

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
    changeParameter,
    parameter,
    predictions,
    plot,
    fetchPrediction,
    selectedStep,
    setStep,
    setParameter,
  };
}