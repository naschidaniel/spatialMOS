import { computed, onMounted, onUnmounted, reactive, ref, Ref } from "vue";
import { DataState, AvailableBoxSizes } from "../model";

const windowInnerWidth: Ref<undefined | number> = ref(undefined);
const windowInnerHeight: Ref<undefined | number> = ref(undefined);
const state: DataState = reactive({
  availableBoxSizes: {
    "2xs": 384,
    xs: 512,
    sm: 640,
    md: 768,
    lg: 1080,
    xl: 1280,
    "2xl": 1536,
  } as AvailableBoxSizes,
  isWebpSupported: undefined,
});

export function useData() {
  const availableBoxSizes = computed(() => state.availableBoxSizes);
  const isWebpSupported = computed(() => state.isWebpSupported);

  const updateTime = computed((): number => {
    return new Date(import.meta.env.VITE_APP_BUILDTIME).getTime();
  });

  const lastCommit = computed((): string => {
    return import.meta.env.VITE_APP_GITSHA;
  });

  function canUseWebP() {
    if (state.isWebpSupported !== undefined) {
      return;
    }
    const isFirefoxVersionSupported =
      parseInt(navigator.userAgent?.split("Firefox/")[1]) >= 65.0;
    if (isFirefoxVersionSupported) {
      state.isWebpSupported = isFirefoxVersionSupported;
      return;
    }
    const elem = document.createElement("canvas");
    if (elem.getContext && elem.getContext("2d")) {
      state.isWebpSupported =
        elem.toDataURL("image/webp").indexOf("data:image/webp") === 0;
      return;
    }
    state.isWebpSupported = false;
  }

  onMounted(() => {
    window.addEventListener("resize", setDimensions);
  });

  onUnmounted(() => {
    window.removeEventListener("resize", setDimensions);
  });

  function setDimensions() {
    windowInnerWidth.value = window.innerWidth;
    windowInnerHeight.value = window.innerHeight;
  }

  return {
    availableBoxSizes,
    canUseWebP,
    isWebpSupported,
    lastCommit,
    updateTime,
    windowInnerWidth,
  };
}
