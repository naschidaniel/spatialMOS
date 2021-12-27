declare module "*.vue" {
  import { DefineComponent } from "vue";
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/ban-types
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

interface ImportMetaEnv
  extends Readonly<Record<string, string | boolean | undefined>> {
  readonly VITE_APP_BUILDTIME: string;
  readonly VITE_APP_DEPENDENCIES: string;
  readonly VITE_APP_GITSHA: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
