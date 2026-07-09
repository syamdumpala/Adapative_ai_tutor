import type { NextConfig } from "next";

/**
 * Security headers applied to every response.
 *
 * The Content-Security-Policy below uses the "without nonces" strategy so that
 * static rendering keeps working (see
 * `node_modules/next/dist/docs/01-app/02-guides/content-security-policy.md`).
 * `'unsafe-inline'` is required for Next.js' hydration bootstrap scripts and
 * inline styles. To harden further (drop `'unsafe-inline'`), move to a
 * nonce-based CSP via a `proxy.ts` file — documented in
 * `docs/security/SECURITY.md`.
 */
const isDev = process.env.NODE_ENV === "development";

const cspDirectives = [
  "default-src 'self'",
  `script-src 'self' 'unsafe-inline'${isDev ? " 'unsafe-eval'" : ""}`,
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' blob: data:",
  "font-src 'self'",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'none'",
  `connect-src 'self'${isDev ? " ws: wss:" : ""}`,
];

if (!isDev) {
  cspDirectives.push("upgrade-insecure-requests");
}

const securityHeaders = [
  {
    key: "Content-Security-Policy",
    value: cspDirectives.join("; "),
  },
  {
    key: "Strict-Transport-Security",
    value: "max-age=63072000; includeSubDomains; preload",
  },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  {
    key: "Permissions-Policy",
    value: "camera=(), microphone=(), geolocation=(), interest-cohort=()",
  },
  { key: "X-DNS-Prefetch-Control", value: "off" },
  { key: "X-Permitted-Cross-Domain-Policies", value: "none" },
  { key: "Cross-Origin-Opener-Policy", value: "same-origin" },
  { key: "Cross-Origin-Resource-Policy", value: "same-origin" },
];

const nextConfig: NextConfig = {
  // Pin the workspace root to this app. Without it, Next walks up and picks the
  // monorepo root (it sees the root Husky `package-lock.json`), which makes
  // Turbopack resolve its build manifest in the wrong place ("Manifest file is
  // empty" on `next dev`). npm scripts run from `frontend/`, so cwd is correct.
  turbopack: { root: process.cwd() },
  // Do not leak the framework/version to clients.
  poweredByHeader: false,
  // Fail production builds on type errors instead of silently shipping.
  // (Next 16 removed the built-in `eslint` build step; linting runs via the
  // `lint` script and the pre-commit hook instead.)
  typescript: { ignoreBuildErrors: false },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: securityHeaders,
      },
    ];
  },
};

export default nextConfig;
