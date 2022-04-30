<template>
  <div ref="imageBox" class="">
    <img
      loading="lazy"
      :src="responsiveHref"
      :class="imageClass"
      :width="width"
      :height="height"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, defineProps, Ref, ref, watchEffect } from "vue";
import { useData } from "../store/useData";
import { ImageSizes } from "../model";

const props = defineProps({
  imageHref: { type: String, required: true },
  imageHeight: { type: Number, required: true },
  imageWidth: { type: Number, required: true },
  imageClass: { type: String, default: "", required: false },
});

// eslint-disable-next-line no-unused-vars
const { availableBoxSizes, canUseWebP, isWebpSupported, windowInnerWidth } =
  useData();

const width: Ref<undefined | number> = ref(undefined);
const height: Ref<undefined | number> = ref(undefined);
const imageSizeSelectedClass: Ref<undefined | ImageSizes> = ref(undefined);
const imageBox = ref(null);

const responsiveHref = computed(() => {
  if (props.imageHref === "") {
    console.warn(`The the entered props.imageHref is wrong ${props.imageHref}`);
    return "";
  }
  const extension = props.imageHref.split(".").reverse()[0];
  const filePostFix = `${imageSizeSelectedClass.value}.${extension}`;
  let responsiveUrl = props.imageHref.replace(
    `.${extension}`,
    `_${filePostFix}`
  );
  if (isWebpSupported.value) {
    responsiveUrl = responsiveUrl.replace(`.${extension}`, ".webp");
  }
  return responsiveUrl;
});

function getBestImageSize() {
  const imageBoxWidth = (imageBox as any)?.clientWidth;
  const devicePixelRatio = window?.devicePixelRatio > 1.5 ? 2 : 1;
  const imageSize = imageBoxWidth * devicePixelRatio;
  imageSizeSelectedClass.value =
    imageSize <= availableBoxSizes.value["2xs"]
      ? "2xs"
      : imageSize <= availableBoxSizes.value.xs
      ? "xs"
      : imageSize <= availableBoxSizes.value.sm
      ? "sm"
      : imageSize <= availableBoxSizes.value.md
      ? "md"
      : imageSize <= availableBoxSizes.value.lg
      ? "lg"
      : imageSize <= availableBoxSizes.value.xl
      ? "xl"
      : "2xl";
  width.value = availableBoxSizes.value[imageSizeSelectedClass.value];
  height.value = Math.round(
    availableBoxSizes.value[imageSizeSelectedClass.value] /
      (props.imageWidth / props.imageHeight)
  );
}
canUseWebP();
getBestImageSize();

// eslint-disable-next-line no-unused-vars
watchEffect((windowInnerWidth) => {
  getBestImageSize();
});
</script>
