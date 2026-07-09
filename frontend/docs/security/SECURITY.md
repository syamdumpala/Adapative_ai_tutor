# Frontend Security

This document describes the security controls implemented in the frontend, what
they protect against, and how to extend them safely.

## 1. HTTP security headers

Set for every response in [`../../next.config.ts`](../../next.config.ts) via
`headers()` on `source: "/:path*"`.

| Header                              | Value (summary)                        | Protects against                          |
| ----------------------------------- | -------------------------------------- | ----------------------------------------- |
| `Content-Security-Policy`           | see §2                                 | XSS, injection, clickjacking, mixed content |
| `Strict-Transport-Security`         | `max-age=63072000; includeSubDomains; preload` | Protocol downgrade / SSL stripping |
| `X-Frame-Options`                   | `DENY`                                 | Clickjacking (legacy fallback for CSP `frame-ancestors`) |
| `X-Content-Type-Options`            | `nosniff`                              | MIME-type sniffing                        |
| `Referrer-Policy`                   | `strict-origin-when-cross-origin`      | Referrer/URL leakage                      |
| `Permissions-Policy`                | camera/mic/geolocation/FLoC disabled   | Unwanted browser feature access           |
| `X-DNS-Prefetch-Control`            | `off`                                  | Passive DNS leakage                       |
| `X-Permitted-Cross-Domain-Policies` | `none`                                 | Adobe cross-domain policy abuse           |
| `Cross-Origin-Opener-Policy`        | `same-origin`                          | Cross-origin window attacks (XS-Leaks)    |
| `Cross-Origin-Resource-Policy`      | `same-origin`                          | Cross-origin resource inclusion           |

`poweredByHeader: false` also removes the `X-Powered-By: Next.js` fingerprint.

## 2. Content Security Policy (CSP)

Built in `next.config.ts`. Current directives:

```
default-src 'self';
script-src 'self' 'unsafe-inline' [ 'unsafe-eval' in dev only ];
style-src 'self' 'unsafe-inline';
img-src 'self' blob: data:;
font-src 'self';
object-src 'none';
base-uri 'self';
form-action 'self';
frame-ancestors 'none';
connect-src 'self' [ ws: wss: in dev only ];
upgrade-insecure-requests;   ( production only )
```

### Why `'unsafe-inline'` is currently allowed

We use the **"without nonces"** strategy (see
`node_modules/next/dist/docs/01-app/02-guides/content-security-policy.md`). Next.js
injects inline hydration scripts and inline styles; without a nonce these
require `'unsafe-inline'`. This keeps **static rendering** working. `'unsafe-eval'`
and dev websockets are only allowed in development (React dev tooling / HMR).

### Hardening roadmap (drop `'unsafe-inline'`)

To move to a strict, nonce-based CSP:

1. Add a `proxy.ts` (Next 16's replacement for `middleware.ts`) that generates a
   per-request nonce and sets `script-src 'self' 'nonce-…' 'strict-dynamic'`.
2. Opt affected pages into **dynamic rendering** (nonces disable static
   optimization / ISR / PPR — a real performance trade-off).
3. Read the nonce via `headers()` for any `<Script>` you add.

This is intentionally deferred; revisit when the app handles sensitive data.

### Adding a third-party origin

Never widen CSP blindly. When you must load an external script/style/image/API,
add its **exact** origin to the specific directive (e.g. `connect-src`,
`script-src`) — not a wildcard — and record it here with the reason.

### Fonts are self-hosted (no CSP change)

The Mira design links the Google Fonts CDN, but the app loads Bricolage
Grotesque, Hanken Grotesk and Space Mono via **`next/font/google`**
(`src/app/layout.tsx`). `next/font` downloads and self-hosts the files at build
time and serves them same-origin, so **no `fonts.googleapis.com` /
`fonts.gstatic.com` origin is needed** — `font-src 'self'` (and `style-src`)
stay unchanged, and there is no runtime request to Google. Prefer this pattern
over widening the CSP for any future web font.

## 3. Security linting

Enforced by [`../../eslint.config.mjs`](../../eslint.config.mjs):

- **`eslint-plugin-no-unsanitized`** — bans assignment to `innerHTML`/
  `outerHTML` and other unsanitized DOM sinks (DOM-XSS).
- **`eslint-plugin-security`** — flags `eval`-like calls, unsafe regex, non-literal
  `require`, etc. (`detect-object-injection` is disabled as too noisy for normal
  indexing; TypeScript covers that ground).
- Core rules: `no-eval`, `no-implied-eval`, `no-new-func`, `no-script-url`,
  `no-alert`.

In React, avoid `dangerouslySetInnerHTML`. If unavoidable, sanitize with a
vetted library and justify it in a code comment + here.

## 4. Secrets & environment variables

Template: [`../../.env.example`](../../.env.example). Rules:

- **`NEXT_PUBLIC_` = public.** Anything with this prefix is inlined into the
  browser bundle. **Never** put API keys, tokens, or passwords behind it.
- **Server-only secrets** have no `NEXT_PUBLIC_` prefix and are read only in
  Server Components / Route Handlers / Server Actions.
- Prefer a **server-side proxy** (Route Handler) between the browser and the
  backend so backend credentials never reach the client.
- `.env*` is git-ignored; only `.env.example` (no real values) is committed.

### Auth (when the API is wired)

The login/sign-up UI is built but **not connected** — the seam is
`src/features/auth/api.ts`. When wiring it:

- Call a **server-side route handler** (e.g. `/api/auth/*`), not the backend
  directly from the browser, so tokens/credentials stay off the client bundle.
- Prefer an **httpOnly, `Secure`, `SameSite` cookie** session over storing
  tokens in `localStorage` (XSS-readable).
- The client-side validation in `validation.ts` is **UX only** — always
  re-validate on the server.
- If the auth endpoint is a different origin, add its **exact** origin to
  `connect-src` in the CSP (§2) and record it there.

## 5. Type safety as a security control

Strict TypeScript (`tsconfig.json`) reduces a class of runtime bugs that become
security issues. `noUncheckedIndexedAccess` in particular forces handling of
possibly-undefined values. Keep `npm run typecheck` green.

## 6. Dependency hygiene

- Run `npm audit` periodically and before releases; triage high/critical issues.
- Pin/upgrade deliberately; review new dependencies before adding them.
- Keep `next` and `eslint-config-next` in lockstep (currently `16.2.10`).

## 7. Pre-ship security checklist

- [ ] No secret behind a `NEXT_PUBLIC_` variable; no secret hardcoded.
- [ ] Backend calls that use secrets run server-side, not in the client bundle.
- [ ] No `dangerouslySetInnerHTML` / raw `innerHTML` with unsanitized input.
- [ ] Any new external origin is added narrowly to CSP and documented in §2.
- [ ] User-controlled input is validated/escaped before use.
- [ ] `npm run lint` (incl. security rules) and `npm run typecheck` are green.
- [ ] `npm audit` reviewed; no unaddressed high/critical advisories.
- [ ] This file + `../history/HISTORY.md` updated if a control changed.
