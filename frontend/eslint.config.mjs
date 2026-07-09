import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";
import pluginSecurity from "eslint-plugin-security";
import pluginNoUnsanitized from "eslint-plugin-no-unsanitized";
import prettier from "eslint-config-prettier/flat";

/**
 * Frontend ESLint flat config.
 *
 * Layers (later entries win):
 *   1. Next.js core-web-vitals + TypeScript presets.
 *   2. Security guardrails (eslint-plugin-security, eslint-plugin-no-unsanitized).
 *   3. Code-quality guardrails (size/complexity limits) — source files only.
 *   4. Prettier compatibility (disables stylistic rules that fight the formatter).
 *
 * The numeric limits below are the enforced "Balanced" tier. See
 * `docs/architecture/STRUCTURE.md` and `RULES.md` for the rationale and how to
 * tune them.
 */
const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,

  // --- Security guardrails ---------------------------------------------------
  pluginSecurity.configs.recommended,
  pluginNoUnsanitized.configs.recommended,
  {
    name: "frontend/security-overrides",
    rules: {
      // Extremely noisy for normal `obj[key]` access; keep off and rely on
      // TypeScript + the more targeted rules below.
      "security/detect-object-injection": "off",
    },
  },

  // --- Code-quality guardrails (source only) ---------------------------------
  {
    name: "frontend/quality-limits",
    files: ["src/**/*.{ts,tsx,js,jsx,mjs,cjs}"],
    rules: {
      "max-lines": [
        "error",
        { max: 200, skipBlankLines: true, skipComments: true },
      ],
      "max-lines-per-function": [
        "error",
        { max: 50, skipBlankLines: true, skipComments: true, IIFEs: true },
      ],
      complexity: ["error", 10],
      "max-depth": ["error", 4],
      "max-params": ["error", 4],
      "max-nested-callbacks": ["error", 3],
      "max-statements": ["warn", 20],

      // Correctness / hygiene guardrails.
      eqeqeq: ["error", "always"],
      "no-var": "error",
      "prefer-const": "error",
      "no-console": ["warn", { allow: ["warn", "error"] }],
      "no-alert": "error",
      "no-eval": "error",
      "no-implied-eval": "error",
      "no-new-func": "error",
      "no-script-url": "error",
      "no-param-reassign": "error",
    },
  },

  // --- Prettier (must stay last) ---------------------------------------------
  prettier,

  globalIgnores([
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    "node_modules/**",
    "docs/**",
    "public/**",
  ]),
]);

export default eslintConfig;
