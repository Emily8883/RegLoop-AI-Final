import js from "@eslint/js";
import { FlatCompat } from "@eslint/eslintrc";
import { fileURLToPath } from "node:url";

const compat = new FlatCompat({
  baseDirectory: fileURLToPath(new URL(".", import.meta.url)),
});

const config = [
  js.configs.recommended,
  ...compat.extends("next/core-web-vitals"),
  {
    ignores: ["node_modules/", ".next/", "out/", "dist/"],
  },
  {
    rules: {
      "no-undef": "off",
      "no-unused-vars": "off",
    },
  },
];

export default config;
