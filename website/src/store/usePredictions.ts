import { reactive, computed, unref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { SpatialMosStep, SpatialMosImage, Predictions } from "../model";

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

export function usePredictions() {
  const route = useRoute();
  const router = useRouter();

  if (
    route.query?.parameter === "tmp_2m" ||
    route.query?.parameter === "rh_2m"
  ) {
    setParameter(route.query?.parameter);
  }
  if (route.query?.step && typeof route.query?.step === "string") {
    setStep(route.query.step);
  }
  if (route.query?.plot && typeof route.query?.plot === "string") {
    setPlot(route.query.plot);
  }

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
          router.push({
            query: {
              parameter: data[0].parameter,
              step: predictions.step,
              plot: predictions.plot,
            },
          });
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

  const spatialImage = computed(() => {
    if (selectedStep.value === undefined) {
      return { filename: "", overlay: "", northEast: [47, 11], southWest: [46, 9], height: 0, width: 0 };
    }
    return plot.value === "samos_spread"
      ? selectedStep.value.spatialmos_spread
      : plot.value === "nwp_mean"
      ? selectedStep.value.nwp_mean
      : plot.value === "nwp_spread"
      ? selectedStep.value.nwp_spread
      : selectedStep.value.spatialmos_mean;
  });

  const plot = computed(() => {
    return predictions.plot;
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
    } else {
      predictions.step = change;
    }
    router.push({
      query: {
        parameter: predictions.parameter,
        step: predictions.step,
        plot: predictions.plot,
      },
    });
  }

  function setParameter(change: string) {
    predictions.parameter = change;
    router.push({
      query: {
        parameter: change,
        step: predictions.step,
        plot: predictions.plot,
      },
    });
  }

  function setPlot(change: string) {
    predictions.plot = change;
    router.push({
      query: {
        parameter: predictions.parameter,
        step: predictions.step,
        plot: change,
      },
    });
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
    setPlot,
    spatialImage,
  };
}
