declare module "*.vue" {
  import { DefineComponent } from "vue";
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/ban-types
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

declare namespace NodeJS {
  interface ProcessEnv {
    VITE_APP_CURRENT_GIT_SHA: string;
    VITE_APP_VUE_APP_UPDATETIME: string;
  }
}

interface ImportMeta {
  env: {
    VITE_APP_CURRENT_GIT_SHA: string;
    VITE_APP_VUE_APP_UPDATETIME: string;
  };
}
