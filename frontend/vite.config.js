import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // 5173 by hand, but an assigned port wins. Tooling that starts this server picks a
    // free port and passes it in PORT; hardcoding 5173 meant a stale process holding the
    // port silently sent the new server to 5174 while everything else still pointed at 5173.
    port: Number(process.env.PORT) || 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
});
