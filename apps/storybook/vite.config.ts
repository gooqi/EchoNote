import path from "path";
import { defineConfig } from "vite";

export default defineConfig({
  resolve: {
    alias: {
      "@echonote/ui": path.resolve(__dirname, "../../packages/ui/src"),
      "@echonote/tiptap": path.resolve(__dirname, "../../packages/tiptap/src"),
      "@echonote/utils": path.resolve(__dirname, "../../packages/utils/src"),
    },
  },
});
