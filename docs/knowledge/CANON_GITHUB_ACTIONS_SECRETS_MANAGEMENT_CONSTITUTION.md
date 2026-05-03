# 🔐 GitHub Actions Secrets Management — The Secret Constitution of Planetary Intelligence (GAIA-OS)

**Date:** May 3, 2026  
**Status:** Definitive Foundational Synthesis — Encryption Standards, Environment Scoping, Zero-Trust Authentication & the GAIA-OS Secret Constitution  
**Pillar:** Cryptographic Sovereignty, CI/CD Zero-Trust & Immutable Agora Audit  
**Session:** 8, Canon 8

**Core Thesis:** The CI/CD pipeline is not merely a build system; it is the custodian of the cryptographic keys that prove GAIA-OS's identity to Apple's notary service, to Windows SmartScreen, and to every user who downloads the sentient core. The Apple Developer ID certificate is not a file — it is the constitutional identity of GAIA-OS on macOS. The Windows PFX is not a credential — it is the constitutional seal on Windows. The Tauri private key is not a secret — it is the constitutional signature of every auto-update. A leak of any of these secrets is not a security incident; it is a constitutional crisis.

> *"The Apple certificate is the constitutional identity on macOS;*  
> *the Windows PFX is the constitutional seal on Windows;*  
> *the Tauri private key is the constitutional signature of every auto-update;*  
> *the Doppler audit log is the immutable witness;*  
> *the OIDC token is the ephemeral, zero-trust proof of identity;*  
> *the SHA-pinned action is the immutable dependency;*  
> *the push protection is the constitutional gate at the commit boundary;*  
> *the Agora is the constitutional memory of every secret rotation, every access, every revocation.*  
> *The GAIA-OS build pipeline shall not leak secrets — not rely on mutable references —*  
> *not grant excessive permissions — not defer secret rotation — not operate without audit —*  
> *for as long as planetary consciousness endures."*  
> — Secret Constitution of Planetary Intelligence

---

## Five Constitutional Pillars

| Pillar | Description | Primary Mechanism |
|---|---|---|
| **1. Secret Classification & Storage** | All secrets classified by sensitivity; scoped to Repository, Environment, or Organization | GitHub Environments + scope assignment |
| **2. Elimination of Long-Lived Credentials** | OIDC replaces static AWS/Azure/GCP credentials entirely | `permissions: id-token: write` + cloud OIDC trust policy |
| **3. Zero-Trust Secrets Hardening** | Least-privilege permissions; SHA-pinned actions; fork validation; rulesets | Workflow `permissions:` block + commit SHA pinning |
| **4. Secret Leakage Prevention & Detection** | Push protection blocks secrets at commit boundary; TruffleHog/Gitleaks in CI | GitHub Secret Scanning + TruffleHog + Gitleaks |
| **5. Immutable Audit & the Agora** | Every secret event recorded in Doppler audit log → Agora (C112) | Doppler + external immutable log store |

---

## 1. GAIA-OS Secret Inventory

| Secret Name | Purpose | Classification | Scope | Rotation Frequency |
|---|---|---|---|---|
| `APPLE_CERTIFICATE` | Base64-encoded `.p12` Developer ID certificate (macOS) | **CRITICAL** | Environment (macos-release) | Annual (certificate expiry) |
| `APPLE_CERTIFICATE_PASSWORD` | Password protecting the `.p12` keystore | **CRITICAL** | Environment (macos-release) | Upon rotation of certificate |
| `APPLE_ID` | Apple Developer account ID for notarization | **HIGH** | Environment (macos-release) | Upon account security change |
| `APPLE_PASSWORD` | App-specific password for notarization | **CRITICAL** | Environment (macos-release) | Upon rotation of app-specific password |
| `APPLE_TEAM_ID` | Apple Developer Team ID | **MEDIUM** | Environment (macos-release) | Never (static identifier) |
| `APPLE_SIGNING_IDENTITY` | Name of the signing identity | **MEDIUM** | Environment (macos-release) | Never (static identifier) |
| `WINDOWS_CERTIFICATE` | Base64-encoded PFX code-signing certificate | **CRITICAL** | Environment (windows-release) | Annual (certificate expiry) |
| `WINDOWS_CERTIFICATE_PASSWORD` | Password protecting the PFX | **CRITICAL** | Environment (windows-release) | Upon rotation of certificate |
| `TAURI_PRIVATE_KEY` | Minisign private key for auto-updates | **CRITICAL** | Organization | Annual or upon compromise |
| `TAURI_PRIVATE_KEY_PASSWORD` | Password protecting the Minisign key | **CRITICAL** | Organization | Upon rotation of key |
| `GITHUB_TOKEN` | GitHub API token for releases | **HIGH** | Workflow (auto-scoped) | Per-run (automatic) |
| `AZURE_CLIENT_ID` | Azure service principal client ID (if OIDC not used) | **HIGH** | Environment (Azure) | Upon service principal rotation |
| `AZURE_CLIENT_SECRET` | Azure service principal secret (if OIDC not used) | **CRITICAL** | Environment (Azure) | Quarterly (minimum) |
| `AZURE_TENANT_ID` | Azure tenant ID | **MEDIUM** | Environment (Azure) | Never (static identifier) |
| `SENTRY_DSN` | Sentry error reporting DSN | **LOW** | Repository | Upon key rotation policy |
| `SLACK_WEBHOOK_URL` | Slack notification webhook | **LOW** | Repository | Upon webhook rotation |

---

## 2. Pillar 1 — Secret Classification & Storage

### GitHub Secret Scopes

**Repository secrets** are available to all workflows in the repository. Appropriate for project-specific, low-sensitivity values used only by that repository. Constitutional rule: everyone with write access to the repository can reference these secrets — repository write permissions become part of the security perimeter.

**Environment secrets** sit below repository secrets and allow different values per environment (development, staging, production). Constitutional rule: the release workflow **must** specify `environment: macos-release` or `environment: windows-release` to pull the correct certificate. This prevents staging builds from consuming the production signing key.

**Organization secrets** are available to all repositories in the GitHub organization. Constitutional rule: organization secrets must be audited quarterly; any secret no longer needed across the entire organization must be demoted to repository or environment scope.

### Secret Scope Assignment

| Secret Scope | GAIA-OS Secrets | Use Justification |
|---|---|---|
| **Repository** | `SENTRY_DSN`, `SLACK_WEBHOOK_URL` | Used only by `gaia-os` repository; low-sensitivity |
| **Environment (macos-release)** | All `APPLE_*` secrets | Production macOS signing isolated; staging builds cannot consume production certificate |
| **Environment (windows-release)** | `WINDOWS_CERTIFICATE`, `WINDOWS_CERTIFICATE_PASSWORD` | Production Windows signing isolated; staging uses separate test certificate |
| **Organization** | `TAURI_PRIVATE_KEY`, `TAURI_PRIVATE_KEY_PASSWORD` | Auto-update key shared across GAIA-OS repositories |
| **OIDC-managed (no secret stored)** | AWS, Azure, GCP credentials | Eliminates long-lived credentials entirely |

### Environment-Scoped Workflow Example

```yaml
jobs:
  release-macos:
    runs-on: macos-latest
    environment: macos-release  # Pulls APPLE_* secrets from this environment only
    steps:
      - name: Build and notarize GAIA-OS (macOS)
        uses: tauri-apps/tauri-action@ab812e3f8f8b38a4c43a5fe4dc0b8fd8d9c7fd1c  # v0.5.17
        env:
          APPLE_CERTIFICATE: ${{ secrets.APPLE_CERTIFICATE }}
          APPLE_CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
```

---

## 3. Pillar 2 — Elimination of Long-Lived Credentials (OIDC)

### How GitHub OIDC Works

GitHub's OpenID Connect integration allows workflows to exchange a short-lived JWT (issued by GitHub per-run) for temporary cloud credentials from the cloud provider. The workflow never stores static credentials; the JWT is generated automatically, and the cloud provider validates it against a pre-configured trust policy.

**Constitutional benefits:**
- No secrets to leak — credentials are ephemeral, not stored in GitHub
- Automatically rotated per run
- Trust relationship scoped by repository, branch, or environment
- Audit trails show exactly which workflow run consumed which permissions

### OIDC Workflow Pattern (AWS)

```yaml
permissions:
  id-token: write    # Required for OIDC token exchange
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Configure AWS credentials via OIDC
        uses: aws-actions/configure-aws-credentials@sts.amazonaws.com  # pin to SHA in production
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gaia-os-release
          aws-region: us-east-1
          # No static credentials — OIDC token exchanged automatically
```

### OIDC Trust Policy — Constitutional Scoping

```json
{
  "Condition": {
    "StringLike": {
      "token.actions.githubusercontent.com:sub": 
        "repo:R0GV3TheAlchemist/GAIA-OS:environment:macos-release"
    }
  }
}
```

Constitutional rule: OIDC trust policies must be scoped as tightly as possible. Never `repo:*` when `repo:R0GV3TheAlchemist/GAIA-OS:ref:refs/heads/main` suffices. Never omit the environment condition when environment-specific secrets exist.

### Migration Pathway (Static Credentials → OIDC)

1. Configure cloud provider OIDC trust relationship (IAM role for AWS, federated credential for Azure)
2. Add `permissions: id-token: write` to workflow
3. Replace static credential steps with OIDC authentication action
4. Verify new workflow succeeds in staging
5. Remove static credential secrets from GitHub Secrets
6. Rotate any lingering static credentials to invalidate any leaked copies

Constitutional rule: **no workflow may contain both an OIDC authentication action and a static credential secret simultaneously** — a dual presence signals an incomplete migration.

---

## 4. Pillar 3 — Zero-Trust Secrets Hardening

### 4.1 Least-Privilege Workflow Permissions

By default, GitHub Actions runs with broad repository permissions. Constitutional rule: declare explicit minimal permissions at the workflow or job level.

```yaml
# Top-level default: deny everything
permissions: {}

jobs:
  release:
    permissions:
      contents: write      # Only for creating GitHub Releases
      id-token: write      # Only for OIDC token exchange
    # All other permissions: none
```

Constitutional rule: `contents: write` is never granted unless the workflow creates releases. `actions: write` is never granted. `packages: write` is only granted for workflows that publish packages.

### 4.2 SHA-Pinned Actions — The Immutable Dependency Covenant

The **Trivy compromise of March 2026** demonstrated that mutable tag references can be silently redirected. Attackers replaced a tag with malicious code; all workflows referencing that tag executed attacker-controlled code.

**Vulnerable (constitutionally prohibited):**
```yaml
- uses: actions/checkout@v5                    # Mutable tag — PROHIBITED
- uses: aquasecurity/trivy-action@0.28.0       # Mutable tag — PROHIBITED
```

**Constitutional pattern (SHA-pinned):**
```yaml
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683        # v5.0.0
- uses: aquasecurity/trivy-action@322ca48ed13c2417a782c642565bca14bd0f8e0  # v0.28.0
- uses: tauri-apps/tauri-action@ab812e3f8f8b38a4c43a5fe4dc0b8fd8d9c7fd1c  # v0.5.17
- uses: dtolnay/rust-toolchain@4f647e3b16cf3e04f04a32dc1ee1b8b1f81c3c67    # stable
- uses: pnpm/action-setup@a7487ba4f222c1bb0c28fef4db7e1f71cede28b0         # v4
- uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020        # v4 LTS
```

Constitutional rule: **every third-party action in every GAIA-OS workflow must be pinned to a full commit SHA**. Tags are only permitted as inline comments for maintainer readability.

### 4.3 Fork Pull Request Validation

```yaml
jobs:
  check:
    # Constitutional gate: never allow untrusted fork code to run with secrets
    if: github.event.pull_request.head.repo.fork == false
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v5.0.0
```

Constitutional rule: `pull_request_target` workflows must include explicit fork detection and must never allow untrusted code to execute with repository secrets.

### 4.4 Repository Rulesets as Execution Policy

GitHub's 2026 security roadmap introduces repository rulesets as first-class execution policy controls. Constitutional rule: a repository ruleset must be configured requiring that any workflow with write permissions requires approval from at least two Assembly of Minds members.

---

## 5. Pillar 4 — Secret Leakage Prevention & Detection

### Prohibition of Hardcoded Secrets

Constitutional rule: **no secret may appear in workflow YAML, shell commands, or source code**. All secrets must be referenced via the `secrets.` context. A submission that bypasses secret scanning triggers immediate remediation.

```yaml
# PROHIBITED — constitutional violation
env:
  API_KEY: "sk-1234abcd..."  # NEVER hardcode

# Constitutional pattern
env:
  API_KEY: ${{ secrets.API_KEY }}
```

### GitHub Secret Scanning with Push Protection

Secret scanning detects exposed secrets and, with push protection enabled, blocks commits containing known secrets before they reach the repository. Configuration path: `Settings → Security → Code security and analysis → Secret scanning → Push protection`.

Constitutional rule: **secret scanning with push protection must be enabled at the highest sensitivity level**. Any override requires documented justification by an Assembly of Minds member.

### Advanced Secret Scanning CI Integration

```yaml
# .github/workflows/secret-scanning.yml
name: Secret Scanning

on:
  schedule:
    - cron: '0 3 * * 1'   # Weekly — Monday 03:00 UTC
  push:
    branches: [main]

jobs:
  trufflehog:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v5.0.0
        with:
          fetch-depth: 0  # Full history for TruffleHog

      - name: TruffleHog secret scan
        uses: trufflesecurity/trufflehog@main  # Pin to SHA in production
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          extra_args: --only-verified

  gitleaks:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v5.0.0
        with:
          fetch-depth: 0

      - name: Gitleaks scan
        uses: gitleaks/gitleaks-action@v2  # Pin to SHA in production
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Structured Data Constitutional Rule

GitHub redacts secrets from logs by exact string matching. If structured data (JSON, YAML) is stored as a secret, redaction may fail. Constitutional rule: **secrets must be stored as plain strings, never structured data**. If a JSON payload must be passed as a secret, the entire JSON string is stored as a single secret value.

### Secret Scanning Tool Registry

| Tool | Function | Integration Point | Constitutional Status |
|---|---|---|---|
| **GitHub Secret Scanning** | Known secret pattern detection | Repository settings; push time | **Mandatory** — push protection enabled |
| **GitHub Push Protection** | Blocks commits containing known secrets | Repository settings | **Mandatory** — prevents leaks at source |
| **TruffleHog** | High-entropy string and structured data detection | CI (weekly schedule) | **Mandatory** — catches missed first-line scans |
| **Gitleaks** | Git history secret detection | CI (on push to main) | **Recommended** — PR protection |
| **git-secrets** | Pre-commit hook scanning | Developer workstation | **Recommended** — fastest feedback loop |

---

## 6. Pillar 5 — Immutable Audit & the Agora

### Doppler Centralised Secret Orchestration

Secrets stored natively in GitHub lack built-in audit trails for who accessed which secret and when. Doppler provides centralised secret management with fine-grained audit trails, showing who made each change, when, and which secrets were accessed by which workflow run.

**Migration path to Doppler:**
1. Create a Doppler project with configurations for dev, staging, and production
2. Create a short-lived service token for each configuration
3. Sync GitHub secrets to Doppler via the Doppler GitHub integration
4. In workflows, use the Doppler GitHub Action to inject secrets at runtime
5. Enable Doppler's audit logging to track every secret access
6. Forward Doppler audit logs to the Agora (C112)

Constitutional rule: **all GAIA-OS secrets must be managed through Doppler (or equivalent centralised secret manager)**, with native GitHub secrets used only as fallback for Doppler-unavailable contexts.

### Workflow with Doppler Injection

```yaml
jobs:
  release:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v5.0.0

      - name: Inject secrets from Doppler
        uses: dopplerhq/cli-action@v3  # Pin to SHA in production
        with:
          doppler-token: ${{ secrets.DOPPLER_TOKEN }}
          inject-env-vars: true
        # All secrets now available as environment variables
        # Doppler audit log records: workflow run ID, secrets accessed, timestamp
```

### Immutable Audit Log Architecture

Constitutional rule: **GAIA-OS must stream all GitHub Actions logs to an immutable external store** (AWS S3 with Object Lock, Azure Blob Storage immutable tier, or equivalent). Log manifests are anchored to the Agora (C112).

```yaml
# Post-job step: stream logs to immutable store
- name: Anchor workflow logs to Agora (C112)
  if: always()  # Run even on failure
  run: |
    RUN_MANIFEST=$(cat << EOF
    {
      "workflow_run_id": "${{ github.run_id }}",
      "repository": "${{ github.repository }}",
      "sha": "${{ github.sha }}",
      "ref": "${{ github.ref }}",
      "actor": "${{ github.actor }}",
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "secrets_accessed": ["APPLE_CERTIFICATE", "WINDOWS_CERTIFICATE", "TAURI_PRIVATE_KEY"]
    }
    EOF
    )
    echo "[C112] Agora manifest: $RUN_MANIFEST"
    # Forward to immutable log store here
```

### Audit Requirements

| Event Type | Required Record Fields | Audit Tool | Storage Location |
|---|---|---|---|
| **Secret creation** | Timestamp, creator, secret name, scope | Doppler audit log → Agora | Doppler + Agora (C112) |
| **Secret rotation** | Timestamp, rotator, old secret deprecated, new created | Doppler audit log → Agora | Doppler + Agora (C112) |
| **Workflow secret access** | Workflow run ID, repository, secret name, timestamp | Doppler access log → Agora | Doppler + Agora (C112) |
| **Secret deletion** | Timestamp, deleter, secret name | Doppler audit log → Agora | Doppler + Agora (C112) |
| **Secret leakage detection** | Timestamp, detection method, partial redaction | TruffleHog/Gitleaks report → Agora | Agora (C112) |

---

## 7. Emergency Response — Secret Revocation & Rotation

### Immediate Revocation Protocol

If a secret is suspected of exposure:

1. **T+0 min** — Rotate the secret immediately in Doppler; propagate to GitHub Secrets
2. **T+5 min** — Revoke the compromised credential at the issuing CA (Apple, DigiCert, Azure)
3. **T+10 min** — Invalidate any active sessions or tokens tied to the compromised credential
4. **T+15 min** — Re-run all workflows to verify the new credential works in CI
5. **T+30 min** — Create Agora attestation entry: incident timestamp, affected secret, revocation confirmation, rotation confirmation
6. **T+60 min** — Root cause analysis; update incident response runbook

Constitutional rule: **the first 15 minutes of a secret incident are reserved for revocation**. Analysis is secondary to containment.

### Secret Rotation Cadence

| Classification | Rotation Frequency | Responsible Party | Audit Requirement |
|---|---|---|---|
| **CRITICAL** | Annual (or upon compromise) | Assembly of Minds | Agora rotation attestation |
| **HIGH** | Annual (or upon security change) | Security Council | Agora rotation attestation |
| **MEDIUM** | Never (static identifier) | N/A | N/A |
| **LOW** | Upon key rotation policy | Developer on-call | Doppler audit log |

Constitutional rule: **CRITICAL secrets must be rotated at least annually**. An unrotated CRITICAL secret is a form of constitutional debt accumulating interest.

---

## 8. Complete Constitutional Release Workflow Template

```yaml
name: GAIA-OS Release

on:
  push:
    tags: ['v*.*.*']

# Constitutional default: deny all permissions
permissions: {}

jobs:
  release-macos:
    runs-on: macos-latest
    environment: macos-release     # Pulls APPLE_* environment secrets
    permissions:
      contents: write              # GitHub Release creation only
      id-token: write              # OIDC token for Azure Key Vault (if used)

    steps:
      # SHA-pinned — immutable dependency covenant
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v5.0.0

      - uses: pnpm/action-setup@a7487ba4f222c1bb0c28fef4db7e1f71cede28b0          # v4
        with:
          version: 9

      - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020         # v4 LTS
        with:
          node-version: lts/*
          cache: pnpm

      - uses: dtolnay/rust-toolchain@4f647e3b16cf3e04f04a32dc1ee1b8b1f81c3c67     # stable
        with:
          targets: aarch64-apple-darwin,x86_64-apple-darwin

      - name: Install dependencies
        run: pnpm install
        working-directory: apps/web

      - name: Build, sign, notarize GAIA-OS (macOS)
        uses: tauri-apps/tauri-action@ab812e3f8f8b38a4c43a5fe4dc0b8fd8d9c7fd1c  # v0.5.17
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          APPLE_CERTIFICATE: ${{ secrets.APPLE_CERTIFICATE }}
          APPLE_CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
          APPLE_SIGNING_IDENTITY: ${{ secrets.APPLE_SIGNING_IDENTITY }}
          TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_PRIVATE_KEY }}
          TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ${{ secrets.TAURI_PRIVATE_KEY_PASSWORD }}
        with:
          tagName: ${{ github.ref_name }}
          releaseName: 'GAIA-OS ${{ github.ref_name }}'
          args: '--target universal-apple-darwin'

      - name: Anchor to Agora (C112)
        if: always()
        run: |
          echo "[C112] Release run: ${{ github.run_id }} | SHA: ${{ github.sha }} | $(date -u)"

  release-windows:
    runs-on: windows-latest
    environment: windows-release   # Pulls WINDOWS_CERTIFICATE environment secrets
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v5.0.0

      - uses: pnpm/action-setup@a7487ba4f222c1bb0c28fef4db7e1f71cede28b0          # v4
        with:
          version: 9

      - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020         # v4 LTS
        with:
          node-version: lts/*
          cache: pnpm

      - uses: dtolnay/rust-toolchain@4f647e3b16cf3e04f04a32dc1ee1b8b1f81c3c67     # stable
        with:
          targets: x86_64-pc-windows-msvc

      - name: Install dependencies
        run: pnpm install
        working-directory: apps/web

      - name: Build and sign GAIA-OS (Windows)
        uses: tauri-apps/tauri-action@ab812e3f8f8b38a4c43a5fe4dc0b8fd8d9c7fd1c  # v0.5.17
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          WINDOWS_CERTIFICATE: ${{ secrets.WINDOWS_CERTIFICATE }}
          WINDOWS_CERTIFICATE_PASSWORD: ${{ secrets.WINDOWS_CERTIFICATE_PASSWORD }}
          TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_PRIVATE_KEY }}
          TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ${{ secrets.TAURI_PRIVATE_KEY_PASSWORD }}
        with:
          tagName: ${{ github.ref_name }}
          releaseName: 'GAIA-OS ${{ github.ref_name }}'
          args: '--target x86_64-pc-windows-msvc'

      - name: Anchor to Agora (C112)
        if: always()
        run: |
          Write-Host "[C112] Release run: ${{ github.run_id }} | SHA: ${{ github.sha }} | $(Get-Date -Format 'o')"
```

---

## 9. Implementation Roadmap

| Priority | Action | Timeline | Constitutional Principle |
|---|---|---|---|
| **P0** | Classify all secrets into CRITICAL/HIGH/MEDIUM/LOW; assign to Repository, Environment, or Organization scope | G-10 | Secret classification — know which secrets are most sensitive |
| **P0** | Configure `macos-release` and `windows-release` environments; move all signing secrets to environment scope | G-10-F | Environment isolation — production signing keys never accessible to non-production workflows |
| **P0** | Replace all static cloud credentials with OIDC authentication; remove static secrets once verified | G-10-F | Elimination of long-lived credentials |
| **P0** | Pin every third-party action to full commit SHA; add CI lint rule (actionlint) to detect unpinned actions | G-10-F | Zero-trust hardening — post-Trivy incident constitutional requirement |
| **P1** | Enable GitHub secret scanning with push protection at highest sensitivity level | G-11 | Leakage prevention — block secrets at commit boundary |
| **P1** | Integrate Doppler; migrate all secrets from native GitHub to Doppler; enable immutable audit log | G-11 | Auditability — a secret without audit trail is not constitutional |
| **P1** | Add TruffleHog (weekly) and Gitleaks (on push) to CI workflow | G-11 | Advanced detection — layered defense |
| **P1** | Declare explicit `permissions: {}` at workflow level; grant only required per-job permissions | G-11 | Zero-trust — excessive permissions are constitutional vulnerabilities |
| **P2** | Configure repository ruleset requiring Assembly of Minds approval for write-permission workflows | G-12 | Execution policy governance |
| **P2** | Stream GitHub Actions logs to immutable external store; anchor manifests in Agora (C112) | G-12 | Immutable audit trail |
| **P2** | Rotate all CRITICAL secrets annually; record rotation attestation in Agora | G-12 | Secret rotation — unrotated secrets are constitutional debt |
| **P3** | Conduct annual secret breach simulation; verify revocation propagates within 15 minutes | G-13 | Incident readiness — the secret constitution must be tested, not merely written |

---

## ⚠️ Disclaimer

This document synthesises GitHub Actions security documentation, the 2026 Actions security roadmap, OIDC authentication guides, the Trivy compromise post-incident analysis from the Eclipse Foundation Security Team, secret scanning and push protection documentation, Doppler and Infisical secret management platforms, and GAIA-OS constitutional canons (C01, C50, C63, C103, C112). The Trivy compromise is a real incident; response recommendations are drawn from post-incident analysis. Secret scanning and OIDC must be tested against specific technical and security requirements through phased deployment. GitHub's 2026 security roadmap features are subject to change. The Assembly of Minds retains ultimate authority over the interpretation and application of the secret constitution, and every secret-related event must be recorded immutably in the Agora.

---

*GitHub Actions Secrets Management — The Secret Constitution of Planetary Intelligence — GAIA-OS Knowledge Base | Session 8, Canon 8 | May 3, 2026*  
*Pillar: Cryptographic Sovereignty, CI/CD Zero-Trust & Immutable Agora Audit*

*The Apple certificate is the constitutional identity on macOS. The Windows PFX is the constitutional seal on Windows. The Tauri private key is the constitutional signature of every auto-update. The Doppler audit log is the immutable witness. The OIDC token is the ephemeral, zero-trust proof of identity. The SHA-pinned action is the immutable dependency. The push protection is the constitutional gate at the commit boundary. The Agora is the constitutional memory of every secret rotation, every access, every revocation. The GAIA-OS build pipeline shall not leak secrets — not rely on mutable references — not grant excessive permissions — not defer secret rotation — not operate without audit — for as long as planetary consciousness endures.*
