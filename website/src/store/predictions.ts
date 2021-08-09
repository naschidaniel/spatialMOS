import { reactive, computed, unref } from "vue";

const predictions = reactive({
  analDate: '',
  steps: [],
  data: {},
  error: '',
  step: '6',
});


export function usePrediction() {
  async function fetchPrediction(url: string, options?: Object) {
    const res = await fetch(url, options);
    if (res.ok) {
      res.json().then(data => {
        predictions.analDate = data['6']['anal_date']  
        predictions.steps = Object.keys(data)
        predictions.data = data
      });
    } else {
      predictions.error = res.statusText
      throw new Error(res.statusText);
    }
  }

  const selectedStep = computed(() => {
    const step = unref(predictions.step)
    return unref(predictions.data[step])
  });

  function setStep(change: string){
    predictions.step = change
  };

  return { predictions, fetchPrediction, selectedStep, setStep}
}