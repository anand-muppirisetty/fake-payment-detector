/// <reference types="vite/client" />

// This file tells TypeScript about Vite-injected globals like
// `import.meta.env.VITE_API_BASE_URL` (used in src/services/api.ts).
// Without it, `tsc` fails the build with:
//   "Property 'env' does not exist on type 'ImportMeta'"
