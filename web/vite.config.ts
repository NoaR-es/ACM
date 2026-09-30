import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// ADR-019: la interfaz se compila dentro del paquete Python (src/acm/webui) y FastAPI la sirve en "/".
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    outDir: "../src/acm/webui",
    emptyOutDir: true,
    sourcemap: false,
    chunkSizeWarningLimit: 900,
  },
  server: {
    proxy: {
      "/api": { target: "http://127.0.0.1:8765", ws: true },
    },
  },
  test: {
    environment: "jsdom",
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
  },
});
