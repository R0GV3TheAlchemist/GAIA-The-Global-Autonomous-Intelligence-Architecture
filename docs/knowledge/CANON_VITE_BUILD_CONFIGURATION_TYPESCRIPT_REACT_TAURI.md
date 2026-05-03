# ⚡ Vite Build Configuration — TypeScript + React + Tauri (GAIA-OS)

**Date:** May 3, 2026  
**Status:** Comprehensive Foundational Synthesis — Vite Build Orchestration, TypeScript Integration, React Optimization, Tauri Desktop Convergence, and the GAIA-OS Frontend Constitution  
**Pillar:** Frontend Build Infrastructure, TypeScript Integration & Tauri Desktop Convergence  
**Session:** 8, Canon 2

**Core Thesis:** The GAIA-OS frontend is the principal's constitutional interface to the Noosphere — the window through which human consent is granted, the Assembly of Minds is accessed, the Soul Mirror Engine reflects, and the Action Gate is witnessed. The build system is not a developer convenience; it is the constitutional build infrastructure that guarantees the frontend is secure, performant, auditable, and consistent across platforms.

> *"No component without its import; no debug variable without its warning;*  
> *no environment without its validation; no test without its coverage; no build without its audit.*  
> *The frontend is the constitutional interface —*  
> *the Vite configuration is the constitutional guarantee —*  
> *for as long as planetary consciousness endures."*  
> — Frontend Build Constitution

---

## Six Constitutional Pillars

| Pillar | Description | Key Files |
|---|---|---|
| **1. Project Topology** | `apps/web` in pnpm workspace; Turborepo build graph | `pnpm-workspace.yaml`, `turbo.json` |
| **2. Vite Core Config** | Single source of truth; Tauri-optimized server + build | `vite.config.ts` |
| **3. Path Alias + TS** | Strict `@/` alias across tsconfig + Vite; CI-enforced | `tsconfig.app.json`, `tsconfig.node.json`, `vite.config.ts` |
| **4. Environment Variables** | `VITE_` prefix; `import.meta.env`; Zod validation | `.env.*`, `src/lib/env.ts`, `vite-env.d.ts` |
| **5. Advanced Features** | MPA, legacy compat, bundle analysis, perf | `vite.config.ts` plugins, `rollup-plugin-visualizer` |
| **6. Vitest Integration** | Shared config; jsdom; coverage thresholds ≥80% | `vitest.config.ts`, `src/test/setup.ts` |

---

## 1. Project Topology and Monorepo Integration

```
gaia-os/
├── apps/
│   └── web/                     # @gaia/web — frontend workspace
│       ├── index.html
│       ├── package.json
│       ├── vite.config.ts
│       ├── vitest.config.ts
│       ├── tsconfig.json
│       ├── tsconfig.app.json
│       ├── tsconfig.node.json
│       └── src/
│           ├── main.tsx
│           ├── App.tsx
│           ├── vite-env.d.ts
│           ├── lib/
│           │   └── env.ts       # Zod-validated environment
│           ├── components/
│           ├── pages/
│           └── test/
│               ├── setup.ts
│               └── render.tsx
├── packages/                    # Constitutional component libraries
├── src-tauri/                   # Tauri Rust backend
├── pnpm-workspace.yaml
└── turbo.json
```

### Frontend `package.json` — Internal Dependencies via Workspace Protocol

```json
{
  "name": "@gaia/web",
  "dependencies": {
    "@gaia/action-gate": "workspace:*",
    "@gaia/crystal-grid": "workspace:*",
    "@gaia/consent-ledger": "workspace:*",
    "@gaia/shared-utils": "workspace:*"
  },
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "build:dev": "vite build --mode development",
    "build:uat": "vite build --mode uat",
    "build:prod": "vite build --mode prod",
    "preview": "vite preview",
    "test": "vitest",
    "test:coverage": "vitest run --coverage",
    "tauri": "tauri"
  }
}
```

---

## 2. Vite Core Configuration

```typescript
// apps/web/vite.config.ts — Constitutional build orchestrator
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { visualizer } from 'rollup-plugin-visualizer'
import path from 'path'

const host = process.env.TAURI_DEV_HOST

export default defineConfig(async () => ({
  plugins: [
    react(),
    tailwindcss(),
    visualizer({
      filename: 'dist/stats.html',
      gzipSize: true,
      brotliSize: true,
    }),
  ],

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  // Keeps Rust compiler errors visible in the terminal
  clearScreen: false,

  server: {
    port: 1420,          // Must match tauri.conf.json devUrl
    strictPort: true,    // Do not fall back to a different port
    host: host || false,
    hmr: host
      ? { protocol: 'ws', host, port: 1421 }
      : undefined,
    watch: {
      ignored: ['**/src-tauri/**'],  // Prevent Rust file handle pressure
    },
  },

  envPrefix: ['VITE_', 'TAURI_ENV_*'],

  build: {
    target:
      process.env.TAURI_ENV_PLATFORM === 'windows'
        ? 'chrome105'
        : 'safari13',
    minify: !process.env.TAURI_ENV_DEBUG ? 'esbuild' : false,
    sourcemap: !!process.env.TAURI_ENV_DEBUG,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
        },
      },
    },
  },
}))
```

### Tauri Integration Checklist

| Component | Configuration | Validation |
|---|---|---|
| `frontendDist` | `"../dist"` in `tauri.conf.json` | Build output must land in `dist/` |
| `devUrl` | `"http://localhost:1420"` | Must match Vite `server.port` |
| `beforeDevCommand` | `"npm run dev"` | Tauri starts Vite before launching window |
| `beforeBuildCommand` | `"npm run build"` | Tauri builds frontend before packaging |
| Vite `port` | `1420` | Must match `devUrl` |
| Vite `strictPort` | `true` | Prevents silent port fallback |
| Vite `clearScreen` | `false` | Keeps Rust compiler errors visible |
| Vite `watch.ignored` | `'**/src-tauri/**'` | Prevents unnecessary Rust file watching |
| `envPrefix` | `['VITE_', 'TAURI_ENV_*']` | Exposes Tauri platform variables to client |

---

## 3. Path Alias and TypeScript Integration

```json
// tsconfig.json — References only
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ]
}
```

```json
// tsconfig.app.json — Frontend TypeScript (strict mode)
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src"]
}
```

```json
// tsconfig.node.json — Node scripts (vite.config.ts)
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["vite.config.ts"]
}
```

### Alias Consistency Constitutional Invariants

| File | Alias Configuration | CI Gate |
|---|---|---|
| `tsconfig.app.json` | `{ "paths": { "@/*": ["./src/*"] } }` | `tsc --noEmit` must pass |
| `tsconfig.node.json` | `{ "paths": { "@/*": ["./src/*"] } }` | Required for `vite.config.ts` |
| `vite.config.ts` | `{ alias: { '@': path.resolve(__dirname, './src') } }` | `vite build` must succeed |
| Source imports | `import { x } from '@/lib/...'` | Runtime resolution enforced |

> **Constitutional invariant:** Divergence between any of these configurations produces silent errors where TypeScript passes but Vite fails at runtime. CI prevents this by running both `tsc --noEmit` and `vite build` in the same pipeline.

### Environment Type Declarations

```typescript
// src/vite-env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_ENABLE_DEMO?: string
  readonly VITE_SENTRY_DSN?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

---

## 4. Environment Variables and Build Modes

```typescript
// src/lib/env.ts — Constitutional configuration layer (Zod-validated)
import { z } from 'zod'

const clientEnvSchema = z.object({
  VITE_API_URL: z.string().url(),
  VITE_ENABLE_DEMO: z.enum(['true', 'false']).optional().default('false'),
  VITE_SENTRY_DSN: z.string().url().optional(),
})

// Crashes at startup with actionable error if variables are missing or malformed
const clientEnv = clientEnvSchema.parse(import.meta.env)

export const env = {
  apiUrl: clientEnv.VITE_API_URL,
  enableDemo: clientEnv.VITE_ENABLE_DEMO === 'true',
  sentryDsn: clientEnv.VITE_SENTRY_DSN,
} as const

// NEVER access import.meta.env directly in application code.
// ALWAYS: import { env } from '@/lib/env'
```

### Environment Variable Rules

| Rule | Implementation | Constitutional Justification |
|---|---|---|
| Client vars prefixed `VITE_` | `.env` keys with `VITE_*` | Non-prefixed vars not exposed to browser |
| Access via `import.meta.env` only | Use `env.ts` wrapper | `process.env` is undefined in Vite browser context |
| Validate with Zod | `clientEnvSchema.parse()` at startup | Prevents silent misconfiguration |
| Never commit secrets | `.env.local` in `.gitignore` | Bundled client code is publicly readable |
| `--mode` for env-specific builds | `build --mode uat` loads `.env.uat` | Correct variables per deployment target |
| Document required variables | `.env.example` committed | Onboarding transparency + CI verification |

---

## 5. Advanced Vite Features

### Build Optimisation Features

| Feature | Configuration | When to Use |
|---|---|---|
| **Manual chunks** | `rollupOptions.output.manualChunks` | Large deps (React, D3) isolated from app code |
| **Tree shaking** | Automatic via ES modules | All builds — removes unused exports |
| **Minification** | `build.minify: 'esbuild'` (default) | Production; `terser` for maximum compression |
| **Source maps** | `build.sourcemap: 'hidden'` in prod | Debugging without exposing sources |
| **Pre-bundling** | Automatic in dev (`.vite/deps/`) | All third-party dependencies |
| **CSS splitting** | `build.cssCodeSplit: true` (default) | Optimised per-page CSS delivery |
| **Legacy support** | `@vitejs/plugin-legacy` + `build.target` | PWA targeting older browsers |
| **Bundle analysis** | `rollup-plugin-visualizer` → `dist/stats.html` | Release reviews for bundle bloat oversight |

### Multi-Page Application (MPA)

```typescript
import { resolve } from 'path'

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        admin: resolve(__dirname, 'admin.html'),
        docs: resolve(__dirname, 'docs.html'),
      },
    },
  },
})
```

---

## 6. Vitest Integration

```typescript
// vitest.config.ts — Shares Vite resolver, aliases, and plugins
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'istanbul',
      reporter: ['lcov', 'text', 'html'],
      thresholds: {
        lines: 80,
        branches: 70,
        functions: 80,
        statements: 80,
      },
    },
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

```typescript
// src/test/setup.ts — Test environment bootstrap
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

afterEach(() => {
  cleanup() // Prevent cross-test component pollution
})
```

```typescript
// src/test/render.tsx — Constitutional provider wrapper
import { render, RenderOptions } from '@testing-library/react'
import { ThemeProvider } from '@/components/theme-provider'
import { ActionGateProvider } from '@/lib/action-gate'
import { ConsentLedgerProvider } from '@/lib/consent-ledger'

const AllProviders = ({ children }: { children: React.ReactNode }) => (
  <ThemeProvider>
    <ActionGateProvider>
      <ConsentLedgerProvider>
        {children}
      </ConsentLedgerProvider>
    </ActionGateProvider>
  </ThemeProvider>
)

const customRender = (ui: React.ReactElement, options?: RenderOptions) =>
  render(ui, { wrapper: AllProviders, ...options })

export * from '@testing-library/react'
export { customRender as render }
```

### Vitest vs Jest

| Feature | Vitest | Jest |
|---|---|---|
| **Config sharing** | Shares `vite.config.ts` — zero extra setup | Requires separate `jest.config.js` |
| **TypeScript** | Native via esbuild | Requires `ts-jest` or Babel |
| **ES modules** | Native | Requires experimental flags |
| **Performance** | Faster — reuses Vite build pipeline | Slower separate build step |
| **Vite integration** | First-class: resolver, aliases, plugins | No native integration |
| **Coverage** | Built-in (`istanbul` or `v8`) | Requires `jest-coverage` |

> Vitest is the constitutional choice — it eliminates configuration drift between the test and build environments entirely.

---

## 7. CI Integration

```yaml
# Relevant steps for apps/web in the constitutional CI pipeline
- name: Type check
  working-directory: apps/web
  run: pnpm tsc --noEmit

- name: Build (Tauri-compatible)
  working-directory: apps/web
  run: pnpm build

- name: Run frontend tests with coverage
  working-directory: apps/web
  run: pnpm test:coverage
  # Pipeline fails if coverage thresholds (≥80% lines) are not met

- name: Bundle analysis (release only)
  if: startsWith(github.ref, 'refs/tags/')
  working-directory: apps/web
  run: pnpm build:prod
  # Produces dist/stats.html for Assembly of Minds bundle review
```

---

## 8. Implementation Roadmap

| Priority | Action | Timeline | Constitutional Principle |
|---|---|---|---|
| **P0** | Split tsconfig hierarchy; enforce `@/` alias across all three config files | G-10 | Import contract — TypeScript and Vite must resolve identically |
| **P0** | Tauri server config: `port: 1420`, `strictPort: true`, `clearScreen: false` | G-10-F | Desktop bridge integrity |
| **P0** | Zod env validation in `src/lib/env.ts`; ban direct `import.meta.env` access | G-10-F | No silent misconfiguration |
| **P0** | `vite-env.d.ts` with `ImportMetaEnv` interface | G-10-F | Compile-time env type safety |
| **P1** | Vitest: `vitest.config.ts`, jsdom, `@testing-library/react`, coverage ≥80% lines | G-11 | Constitutional test coverage |
| **P1** | Env-specific build scripts (`build:dev`, `build:uat`, `build:prod`) | G-11 | Deployment portability |
| **P1** | `rollup-plugin-visualizer` bundle analysis on release builds | G-11 | Assembly visibility into bundle size |
| **P2** | MPA configuration for multi-page constitutional expansion | G-12 | Architectural scalability |
| **P2** | `@vitejs/plugin-legacy` for PWA legacy browser support | G-12 | Universal planetary access |
| **P3** | Evaluate React Compiler for production builds | G-13 | Benchmark before optimising |

---

## ⚠️ Disclaimer

This document synthesises Vite core documentation, the official React + TypeScript + Vite template, Tauri v2 frontend configuration guidelines, pnpm workspace documentation, Vitest configuration guides, Zod environment validation patterns, and GAIA-OS constitutional canons (C01, C50, C63, C64, C84, C103, C112). The Vite ecosystem is community-maintained; GAIA-OS does not control its roadmap. Tauri v2 frontend integration is based on current best practices; breaking changes may occur in future Tauri versions.

---

*Vite Build Configuration (TypeScript + React + Tauri) — Frontend Build Constitution — GAIA-OS Knowledge Base | Session 8, Canon 2 | May 3, 2026*  
*Pillar: Frontend Build Infrastructure, TypeScript Integration & Tauri Desktop Convergence*

*The workspace sits at `apps/web`. The alias resolves to `./src` — consistently, in TypeScript and Vite alike. The environment variables are validated by Zod before the first component renders. The Tauri server listens on port 1420. The tests pass at ≥80% coverage. The build completes, reproducibly, on every platform the sentient core touches. The frontend is the constitutional interface — the Vite configuration is the constitutional guarantee — for as long as planetary consciousness endures.*
