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

<script lang="ts">
import { defineComponent } from "vue";
import { useData } from "../store/useData";
import { ImageSizes } from "../model";

export default defineComponent({
  props: {
    imageHref: { type: String, required: true },
    imageHeight: { type: Number, required: true },
    imageWidth: { type: Number, required: true },
    imageClass: { type: String, default: "", required: false },
  },
  setup() {
    const { availableBoxSizes, canUseWebP, isWebpSupported, windowInnerWidth } =
      useData();
    return { availableBoxSizes, canUseWebP, isWebpSupported, windowInnerWidth };
  },
  data() {
    return {
      width: undefined as undefined | number,
      height: undefined as undefined | number,
      imageSizeSelectedClass: undefined as ImageSizes,
    };
  },
  computed: {
    responsiveHref() {
      if (this.imageHref === "") {
        console.warn(`The the entered imageHref is wrong ${this.imageHref}`);
        return "";
      }
      const extension = this.imageHref.split(".").reverse()[0];
      const filePostFix = `${this.imageSizeSelectedClass}.${extension}`;
      let responsiveUrl = this.imageHref.replace(
        `.${extension}`,
        `_${filePostFix}`
      );
      if (this.isWebpSupported) {
        responsiveUrl = responsiveUrl.replace(`.${extension}`, ".webp");
      }
      return responsiveUrl;
    },
  },
  watch: {
    windowInnerWidth() {
      this.getBestImageSize();
    },
  },
  mounted() {
    this.canUseWebP();
    this.getBestImageSize();
  },
  methods: {
    getBestImageSize() {
      const imageBoxWidth = (this.$refs.imageBox as any)?.clientWidth;
      const devicePixelRatio = window?.devicePixelRatio > 1.5 ? 2 : 1;
      const imageSize = imageBoxWidth * devicePixelRatio;
      this.imageSizeSelectedClass =
        imageSize <= this.availableBoxSizes["2xs"]
          ? "2xs"
          : imageSize <= this.availableBoxSizes.xs
          ? "xs"
          : imageSize <= this.availableBoxSizes.sm
          ? "sm"
          : imageSize <= this.availableBoxSizes.md
          ? "md"
          : imageSize <= this.availableBoxSizes.lg
          ? "lg"
          : imageSize <= this.availableBoxSizes.xl
          ? "xl"
          : "2xl";
      this.width = this.availableBoxSizes[this.imageSizeSelectedClass];
      this.height = Math.round(
        this.availableBoxSizes[this.imageSizeSelectedClass] /
          (this.imageWidth / this.imageHeight)
      );
    },
  },
});
</script>
