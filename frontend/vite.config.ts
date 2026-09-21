import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vite config — proxies /api to the FastAPI backend during local dev so the
// frontend can call relative paths without CORS friction.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
