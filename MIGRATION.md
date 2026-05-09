# GAIA-OS — Web App Migration

This is the `web-app` branch. All Tauri-specific APIs have been
replaced with standard web equivalents. The app runs as a pure
Vite + React SPA.

## What Changed

| File | Change |
|---|---|
| `vite.config.ts` | Removed Tauri env vars; added `/api` proxy to `:8008` |
| `src/hooks/useAlignment.ts` | `invoke()` → `fetch('/api/alignment')` |
| `src/lib/ambientWidget.ts` | Replaces `AmbientOrb.ts` — localStorage + Pointer Events |
| `src/lib/api.ts` | New centralised fetch client with auth header injection |
| `index.html` | Removed Tauri script tags |

## What Did NOT Change

All 6 visual phases are identical to `main`:

- Phase 1 — CSS token foundation (`tokens.css`)
- Phase 2 — Runtime token injection (`applyAlignmentTheme.ts`)
- Phase 3 — GSAP breathing animation (`useBreathingAnimation.ts`)
- Phase 4 — Crystal Design Language (`crystal.css`)
- Phase 5 — ViritasPanel + ScoreSparkline
- Phase 6 — Three.js Ambient Field Visualiser

## Running in Dev

```bash
# 1. Start the Python backend
cd backend && uvicorn main:app --port 8008 --reload

# 2. Start the Vite dev server
npm run dev
# Opens http://localhost:3000
```

## Backend Endpoint Required

The frontend expects the Python backend to expose:

```
GET  /health
     → { "status": "ok" }

GET  /alignment?rmssd=<float|omit>
     → {
         "score":           number,   // 0–100
         "hrv_score":       number,   // 0–100
         "schumann_score":  number,   // 0–100
         "solar_kp":        number,
         "ui_tier":         "minimal" | "core" | "standard" | "full" | "vibrant",
         "last_updated":    string,   // ISO-8601 UTC
         "fallback_mode":   string    // empty when healthy
       }

POST /auth/register
     body: { email, username, password }
     → { access_token, user_id, username, email, role }

POST /auth/login
     body: { username, password }
     → { access_token, user_id, username, email, role }
```

## Production Build

```bash
npm run build
# Output: dist/
# Deploy dist/ to any static host (Vercel, Netlify, Cloudflare Pages)
# Route /api/* to the Python backend via reverse proxy
```

## Re-wrapping in Tauri (later)

When the web app is complete and stable, wrapping back into Tauri
for desktop distribution requires only:

1. Re-add `src-tauri/` from `main` branch
2. Point `tauri.conf.json` `devUrl` at `http://localhost:3000`
3. In `useAlignment.ts`, swap `fetch('/api/alignment')` back to
   `invoke('get_alignment_state')` (or keep HTTP — Tauri supports both)
4. `cargo tauri build`
