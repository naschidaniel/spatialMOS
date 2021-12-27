import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { readFileSync } from "fs";
import { execSync } from "child_process";

const packages = JSON.parse(
  readFileSync("./package.json", { encoding: "utf8" })
);

const dependencies = Object.keys(packages.dependencies)
  .map((dependency) =>
    JSON.parse(
      readFileSync(`node_modules/${dependency}/package.json`, {
        encoding: "utf8",
      })
    )
  )
  .map(({ name, version, license }) => ({
    name,
    version,
    license,
  }))
  .sort((a, b) => a.name.localeCompare(b.name));

process.env.VITE_APP_DEPENDENCIES = JSON.stringify(dependencies);

process.env.VITE_APP_GITSHA = execSync("git rev-parse --short HEAD", {
  encoding: "utf8",
}).trim();

process.env.VITE_APP_BUILDTIME = new Date().toISOString();

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      "/media": {
        target: "https://moses.tirol/",
        changeOrigin: true,
      },
    },
    cors: true,
  },
});
