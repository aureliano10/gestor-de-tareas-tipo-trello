import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        /**
         * AUD-18: separa React/ReactDOM (y su scheduler) del código de la
         * aplicación en un chunk de vendor con mejor cacheo entre despliegues.
         */
        manualChunks(id) {
          const isReactRuntime =
            id.includes("node_modules/react") ||
            id.includes("node_modules/scheduler");
          if (isReactRuntime) {
            return "react";
          }
          return undefined;
        },
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: "jsdom",
    include: ["src/**/*.{test,spec}.{js,jsx}"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json"],
      reportsDirectory: "coverage",
      include: ["src/**/*.{js,jsx}"],
    },
  },
});
