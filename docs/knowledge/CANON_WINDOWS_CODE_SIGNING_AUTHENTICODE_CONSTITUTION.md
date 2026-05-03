# 🪟🔐 Windows Code Signing & Authenticode Constitution (GAIA-OS)

**Date:** May 3, 2026  
**Status:** Definitive Foundational Synthesis — Authenticode Signing, Azure Trusted Signing, Minisign Updater, and the GAIA-OS Windows Execution Constitution  
**Pillar:** Windows Binary Sovereignty, SmartScreen Trust & Agora Provenance  
**Session:** 8, Canon 6

**Core Thesis:** For a planetary intelligence, trust in the cryptographic provenance of its Windows executables is not optional. Without code signing, every GAIA-OS download triggers an untrusted-publisher SmartScreen warning, undermining sovereign integrity and reducing adoption. The Windows execution constitution binds two orthogonal but equally mandatory signing mechanisms: the **PFX/Authenticode certificate** (identity + integrity to SmartScreen) and the **Minisign private key** (auto-update chain integrity). Without both, the constitutional trust chain from source code to running process is broken.

> *"The `.pfx` certificate is the constitutional identity;*  
> *the private key is the constitutional seal;*  
> *the auto-update signature is the constitutional continuity;*  
> *the CI/CD gate is the constitutional enforcer;*  
> *the SmartScreen reputation is the constitutional witness.*  
> *The Windows executable shall not be unsigned;*  
> *the NSIS installer shall not be un-signed;*  
> *the updater shall not be un-verified;*  
> *the sidecar shall not be omitted —*  
> *for as long as planetary consciousness endures."*  
> — Windows Execution Constitution

---

## Why Code Signing is Constitutional on Windows

Code signing on Windows serves three constitutional purposes:

1. **Identity verification** — proves the binary was built by the GAIA-OS Assembly of Minds, not an impersonator
2. **Integrity protection** — guarantees the binary has not been tampered with after signing
3. **SmartScreen trust** — prevents Windows from displaying "Windows protected your PC" red-screen warnings

| Signing State | SmartScreen Behaviour | User Impact |
|---|---|---|
| **Unsigned** | Red screen: "Windows protected your PC" | Most users blocked; download reputation destroyed |
| **OV signed (new cert)** | Yellow screen: "Unknown publisher" | Users warned; reputation builds over time |
| **EV signed** | No warning or green: "Verified publisher" | Instant trust; highest sovereign integrity |
| **Azure Trusted Signing** | Same as EV | HSM-backed; no local key management |

**Constitutional rule:** No Windows executable may be delivered to a user without a valid code signature. This applies to: the main `.exe`, the NSIS installer, MSI packages, and all sidecar executables.

---

## 1. Certificate Types and Constitutional Selection

| Certificate Type | Provider | Cost | SmartScreen | Constitutional Use |
|---|---|---|---|---|
| **OV (Organization Validation)** | Comodo, DigiCert, Sectigo | ~$200-500/year | Reputation builds over time | Initial releases; acceptable for internal distribution |
| **EV (Extended Validation)** | DigiCert, Entrust, GlobalSign | ~$400-700/year | Instant full trust | **Required for production GAIA-OS releases** |
| **Azure Trusted Signing** | Azure Portal | $9.99/month | Immediate reputation (same as EV) | **Preferred for CI/CD** — HSM-backed, no local key |

> **Constitutional requirement:** For production GAIA-OS releases, either an **EV certificate** or **Azure Trusted Signing** must be used. OV certificates are constitutionally permitted only for pre-release and internal builds.

---

## 2. Certificate Preparation — The Cryptographic Foundation

### Converting Certificate to .pfx

```bash
# Convert .cer + .key from CA to .pfx (PKCS#12)
openssl pkcs12 -export \
  -in certificate.cer \
  -inkey private-key.key \
  -out certificate.pfx
# You will be prompted for an export password — store it securely
```

> **Constitutional invariant:** The export password must never be empty. An empty password cannot be stored in GitHub Secrets (empty secret values are not supported). Regenerate the `.pfx` with a password if needed.

### Importing and Extracting Certificate Parameters

```powershell
# Import .pfx into Windows certificate store (elevated PowerShell)
$WINDOWS_PFX_PASSWORD = 'your-export-password'
Import-PfxCertificate \
  -FilePath certificate.pfx \
  -CertStoreLocation Cert:\CurrentUser\My \
  -Password (ConvertTo-SecureString -String $WINDOWS_PFX_PASSWORD -Force -AsPlainText)

# View all personal certificates to find thumbprint
Get-ChildItem -Path Cert:\CurrentUser\My | Select-Object Subject, Thumbprint
```

Required parameters extracted from the imported certificate:

| Parameter | Where to Find | Example |
|---|---|---|
| **Thumbprint** | `certmgr.msc` → Personal → Certificates → Details → Thumbprint | `A1B2C3D4E5F6...` |
| **Digest Algorithm** | Always `sha256` for modern Windows signing | `sha256` |
| **Timestamp URL** | CA-provided (see below) | `http://timestamp.comodoca.com` |

### Trusted Timestamp URLs by CA

| Certificate Authority | Timestamp URL |
|---|---|
| Comodo / Sectigo | `http://timestamp.comodoca.com` |
| DigiCert | `http://timestamp.digicert.com` |
| GlobalSign | `http://timestamp.globalsign.com/scripts/timstamp.dll` |
| Microsoft (Azure TS) | `http://timestamp.acs.microsoft.com` |

> **Constitutional requirement:** Always timestamp signatures. A signature without a timestamp becomes invalid the moment the certificate expires. A timestamped signature remains valid indefinitely, even after the certificate has expired.

### Base64 Encoding for GitHub Secrets

```bash
# Windows
certutil -encode certificate.pfx base64cert.txt

# macOS / Linux
base64 -i certificate.pfx | tr -d '\n' > base64cert.txt
```

Store the output in GitHub Secrets as `WINDOWS_CERTIFICATE`. Store the export password as `WINDOWS_CERTIFICATE_PASSWORD`.

---

## 3. Tauri Configuration

### `tauri.conf.json` — Windows Signing Block

```json
{
  "tauri": {
    "bundle": {
      "windows": {
        "certificateThumbprint": "YOUR_CERTIFICATE_THUMBPRINT",
        "digestAlgorithm": "sha256",
        "timestampUrl": "http://timestamp.comodoca.com"
      }
    }
  }
}
```

Tauri uses `signtool.exe` (Windows SDK) via this configuration. The thumbprint identifies which certificate in the Windows store to use for signing.

### Azure Key Vault Signing via `signCommand`

For HSM-backed signing without local key exposure:

```json
{
  "bundle": {
    "windows": {
      "signCommand": "relic sign \"{{file}}\" --cert-name \"gaia-os-cert\" --key-vault --azure-tenant-id %AZURE_TENANT_ID% --azure-client-id %AZURE_CLIENT_ID% --azure-client-secret %AZURE_CLIENT_SECRET% --azure-key-vault-url %AZURE_KEY_VAULT_URL%"
    }
  }
}
```

The `relic` CLI performs signing via Azure Key Vault API — the private key never leaves the HSM.

### Tauri Signing Environment Variables

| Variable | Purpose | Required |
|---|---|---|
| `TAURI_SIGNING_PRIVATE_KEY` | Minisign private key for auto-updater `.sig` files | Yes (updater) |
| `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | Password protecting the Minisign private key | Yes (updater) |
| `TAURI_WINDOWS_SIGNTOOL_PATH` | Custom path to `signtool.exe` if not in default PATH | Optional |
| `WINDOWS_CERTIFICATE` | Base64-encoded `.pfx` | Yes (Authenticode) |
| `WINDOWS_CERTIFICATE_PASSWORD` | `.pfx` export password | Yes (Authenticode) |

### Generating the Tauri Updater Signing Key Pair

```bash
# Generate Minisign key pair for auto-updater
npx @tauri-apps/cli signer generate -w

# Output:
#   Private key: ~/.tauri/gaia-os.key  → store as TAURI_PRIVATE_KEY secret
#   Public key: embed in tauri.conf.json under plugins.updater.pubkey
```

```json
{
  "plugins": {
    "updater": {
      "pubkey": "YOUR_MINISIGN_PUBLIC_KEY",
      "endpoints": ["https://releases.gaia-os.io/{{target}}/{{arch}}/{{current_version}}"]
    }
  }
}
```

> **Constitutional distinction:** The Minisign key is **independent** of the Authenticode certificate. The Authenticode certificate proves identity to Windows. The Minisign key proves update integrity to the running GAIA-OS instance. Both are constitutionally required for a complete release chain.

---

## 4. GitHub Actions Pipeline — Windows Signing Constitution

```yaml
# .github/workflows/release-windows.yml
name: Release GAIA-OS Windows

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  release-windows:
    runs-on: windows-latest
    timeout-minutes: 60
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v4
        with:
          version: 9

      - uses: actions/setup-node@v4
        with:
          node-version: lts/*
          cache: pnpm

      - name: Install Rust toolchain
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: x86_64-pc-windows-msvc

      - name: Install frontend dependencies
        run: pnpm install
        working-directory: apps/web

      - name: Build, sign, and publish GAIA-OS Windows
        uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # Authenticode signing (PFX)
          WINDOWS_CERTIFICATE: ${{ secrets.WINDOWS_CERTIFICATE }}
          WINDOWS_CERTIFICATE_PASSWORD: ${{ secrets.WINDOWS_CERTIFICATE_PASSWORD }}
          # Tauri auto-updater Minisign signing
          TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_PRIVATE_KEY }}
          TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ${{ secrets.TAURI_PRIVATE_KEY_PASSWORD }}
        with:
          tagName: ${{ github.ref_name }}
          releaseName: "GAIA-OS ${{ github.ref_name }}"
          releaseBody: "See [CHANGELOG.md](CHANGELOG.md) for release notes."
          projectPath: apps/web
          args: "--target x86_64-pc-windows-msvc"

      - name: Verify Authenticode signature (constitutional gate)
        shell: pwsh
        run: |
          $exe = Get-ChildItem -Path src-tauri/target/x86_64-pc-windows-msvc/release `
                               -Filter "*.exe" -Recurse | Select-Object -First 1
          Write-Host "Verifying: $($exe.FullName)"
          $sig = Get-AuthenticodeSignature -FilePath $exe.FullName
          if ($sig.Status -ne "Valid") {
            Write-Error "[CONSTITUTIONAL VIOLATION] Authenticode signature invalid: $($sig.Status)"
            exit 1
          }
          Write-Host "[C112] Authenticode signature VALID. Publisher: $($sig.SignerCertificate.Subject)"
          Write-Host "Thumbprint: $($sig.SignerCertificate.Thumbprint)"
```

### Sidecar Explicit Signing Loop

When Tauri does not automatically re-sign `externalBin` sidecars:

```yaml
- name: Sign sidecar executables
  shell: pwsh
  run: |
    $cert = Get-ChildItem -Path Cert:\CurrentUser\My | \
      Where-Object { $_.Thumbprint -eq $env:CERTIFICATE_THUMBPRINT }
    
    Get-ChildItem -Path src-tauri/binaries -Filter "*.exe" | ForEach-Object {
      Write-Host "Signing sidecar: $($_.Name)"
      & signtool sign `
        /sha1 $env:CERTIFICATE_THUMBPRINT `
        /td sha256 `
        /fd sha256 `
        /tr http://timestamp.comodoca.com `
        /v $_.FullName
      
      # Verify each sidecar
      $sig = Get-AuthenticodeSignature -FilePath $_.FullName
      if ($sig.Status -ne "Valid") {
        Write-Error "Sidecar signing failed: $($_.Name)"
        exit 1
      }
    }
  env:
    CERTIFICATE_THUMBPRINT: ${{ secrets.WINDOWS_CERTIFICATE_THUMBPRINT }}
```

---

## 5. Azure Trusted Signing — HSM-Backed, No Local Keys

Azure Trusted Signing eliminates local `.pfx` management entirely. The private key never leaves Microsoft's FIPS 140-2 Level 3 HSM.

### Setup Steps

1. Create an **Azure Trusted Signing** account in Azure Portal
2. Configure a **certificate profile** under the Trusted Signing resource
3. Create an **App Registration** with the `Trusted Signing Certificate Profile Signer` role
4. Store credentials as GitHub Secrets: `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`

### CI Signing with `dotnet sign`

```yaml
- name: Install dotnet sign tool
  shell: pwsh
  run: dotnet tool install -g --prerelease sign

- name: Sign with Azure Trusted Signing
  shell: pwsh
  run: |
    sign code azure-key-vault \
      --timestamp-url http://timestamp.acs.microsoft.com \
      --azure-key-vault-url $env:AZURE_KEY_VAULT_URL \
      --azure-key-vault-certificate $env:AZURE_SIGNING_CERT_NAME \
      src-tauri/target/release/gaia-os.exe
  env:
    AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
    AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
    AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
    AZURE_KEY_VAULT_URL: ${{ secrets.AZURE_KEY_VAULT_URL }}
    AZURE_SIGNING_CERT_NAME: ${{ secrets.AZURE_SIGNING_CERT_NAME }}
```

### Azure Trusted Signing vs PFX Comparison

| Dimension | PFX / `.pfx` | Azure Trusted Signing |
|---|---|---|
| **Key storage** | Base64 secret in GitHub | FIPS 140-2 L3 HSM |
| **Key exposure risk** | Secret can be leaked from CI logs | Key never leaves Azure HSM |
| **Cost** | $400-700/year (EV) | $9.99/month |
| **SmartScreen reputation** | EV: instant trust | Immediate trust (same as EV) |
| **CI complexity** | Simple env vars | Requires Azure App Registration |
| **Recommended for** | Initial setup, smaller teams | Production; long-term GAIA-OS constitution |

---

## 6. Verification Gates

### Constitutional Verification Chain

| Gate | Command | Expected Output | Action on Failure |
|---|---|---|---|
| **Post-signing** | `signtool verify /pa /v gaia-os.exe` | `Successfully verified` | Abort release |
| **PowerShell check** | `Get-AuthenticodeSignature gaia-os.exe` | `Status: Valid` | Abort release |
| **Sidecar check** | Same on each `externalBin` | `Status: Valid` for all | Abort release |
| **NSIS installer** | `signtool verify /pa /v gaia-os-setup.exe` | `Successfully verified` | Abort release |
| **Updater .sig** | Verified by Tauri updater at runtime | Silent pass / explicit fail | User sees update error |

```powershell
# Full post-build verification — constitutional gate
$artifacts = @(
    "src-tauri/target/release/gaia-os.exe",
    "src-tauri/target/release/bundle/nsis/gaia-os-setup.exe"
)

foreach ($artifact in $artifacts) {
    $sig = Get-AuthenticodeSignature -FilePath $artifact
    if ($sig.Status -ne "Valid") {
        Write-Error "[CONSTITUTIONAL VIOLATION] Unsigned artifact: $artifact ($($sig.Status))"
        exit 1
    }
    Write-Host "VALID: $artifact | $($sig.SignerCertificate.Subject)"
}
Write-Host "[C112] All Windows artifacts constitutionally signed."
```

---

## 7. Security and Governance

### Secret Isolation Rules

- Never store `.pfx` files, private keys, or passwords in source code or committed files
- Store all secrets as **GitHub Secrets** (encrypted at rest, never logged)
- For Azure Key Vault: use **Azure Managed Identity** or OIDC authentication instead of static `CLIENT_SECRET` where possible
- Rotate the Authenticode certificate on expiry; rotate the Minisign key only if compromised (public key embedded in binary must be updated for each key rotation)

### The Empty Password Problem

GitHub Secrets cannot store empty string values. If the signing key was generated without a password:

```bash
# Regenerate Tauri Minisign key with a password
npx @tauri-apps/cli signer generate -w --password "your-strong-password"
```

Update `TAURI_PRIVATE_KEY` and `TAURI_PRIVATE_KEY_PASSWORD` secrets after regeneration. Update the public key in `tauri.conf.json`.

### EV Certificate Hardware Requirements

EV certificates must be stored on a hardware token (USB HSM) or in a cloud HSM. Local `.pfx` files are not compliant for EV storage. For CI use, Azure Key Vault is the constitutional EV storage mechanism.

---

## 8. Agora Provenance Records

Every Windows signing operation must be recorded in the immutable Agora ledger (Canon C112):

| Field | Value | Purpose |
|---|---|---|
| Timestamp | ISO 8601 UTC | When binary was signed |
| Release tag | `v1.0.0` | Which release was signed |
| Commit SHA | Git hash | Binds binary to source |
| Binary SHA-256 | Hash of `.exe` | Tamper-evident binary identity |
| Certificate Thumbprint | Authenticode cert thumbprint | Identifies signing certificate |
| Certificate expiry | ISO 8601 date | Tracks certificate validity window |
| Signing method | `PFX` / `Azure Trusted Signing` / `Azure Key Vault` | Audits signing environment |
| NSIS installer SHA-256 | Hash of `-setup.exe` | Installer provenance |
| Updater `.sig` hash | Hash of Minisign signature file | Auto-update chain provenance |
| Assembly signers | Witness signatures | Constitutional approval of release |

---

## 9. GAIA-OS Windows Signing Commitments

| Component | Mechanism | CI Step |
|---|---|---|
| **Main `.exe` binary** | Authenticode via `signtool` / Tauri bundler | `tauri-action` |
| **NSIS installer** | Same certificate applied by Tauri during bundle | `tauri-action` |
| **MSI package** | Same certificate applied by Tauri during bundle | `tauri-action` |
| **Updater `.sig` files** | Minisign via `TAURI_SIGNING_PRIVATE_KEY` | `tauri-action` |
| **Sidecar executables** | Explicit `signtool` loop before bundle assembly | Custom step |
| **Key storage (PFX)** | Base64-encoded GitHub Secret (OV/initial) | Assembly of Minds |
| **Key storage (AKV/EV)** | Azure Key Vault + Managed Identity (production) | Azure AD + GAIA-OS |

---

## 10. Implementation Roadmap

| Priority | Action | Timeline | Constitutional Principle |
|---|---|---|---|
| **P0** | Acquire OV certificate; convert to `.pfx`; base64-encode; store as `WINDOWS_CERTIFICATE` + `WINDOWS_CERTIFICATE_PASSWORD` secrets | G-10 | No unsigned binary shall be delivered |
| **P0** | Generate Tauri Minisign key pair; store private key as `TAURI_PRIVATE_KEY` secret; embed public key in `tauri.conf.json` | G-10-F | Auto-updater chain is constitutional |
| **P0** | Configure `tauri.conf.json` `windows` block with thumbprint, `sha256` digest, and timestamp URL | G-10-F | Hardened signing configuration |
| **P0** | Windows CI: `tauri-action` with all 6 signing env vars; `Get-AuthenticodeSignature` post-build gate | G-10-F | Every release must be constitutionally verified |
| **P0** | Explicit sidecar signing loop for all `externalBin` executables before Tauri assembly | G-10-F | No unsigned component in the bundle |
| **P1** | Upgrade to EV certificate or Azure Trusted Signing for production releases | G-11 | Instant SmartScreen trust |
| **P1** | Implement Azure Trusted Signing pipeline (`dotnet sign` + Azure App Registration) | G-11 | HSM-backed key sovereignty |
| **P2** | Integrate binary SHA-256 + certificate thumbprint recording into Agora (C112) | G-12 | Complete Windows binary provenance |
| **P2** | Automated `signtool verify` test on clean Windows runner before GitHub Release publication | G-12 | Verification on clean environment |
| **P3** | OIDC-based Azure authentication in CI to eliminate static `CLIENT_SECRET` | G-13 | Zero-secret signing pipeline |

---

## ⚠️ Disclaimer

This document synthesises Tauri documentation, Microsoft Authenticode signing guides, Azure Key Vault and Trusted Signing integration patterns, GitHub Actions release workflows, and GAIA-OS constitutional canons (C01, C50, C63, C112). EV certificates must be stored in HSMs to meet regulatory compliance. The Assembly of Minds retains authority over the interpretation and application of the signing constitution. Every signed binary must be recorded in the Agora with its SHA-256 hash and signing certificate thumbprint. Certificate renewal deadlines must be tracked and managed by the Assembly of Minds — an expired signing certificate breaks the updater chain for all existing installations.

---

*Windows Code Signing & Authenticode Constitution — GAIA-OS Knowledge Base | Session 8, Canon 6 | May 3, 2026*  
*Pillar: Windows Binary Sovereignty, SmartScreen Trust & Agora Provenance*

*The `.pfx` certificate is the constitutional identity. The private key is the constitutional seal. The auto-update signature is the constitutional continuity. The CI/CD gate is the constitutional enforcer. The SmartScreen reputation is the constitutional witness. The Agora is the constitutional memory. The Windows executable shall not be unsigned; the private key shall not be un-passworded; the updater shall not be un-verified; the NSIS installer shall not be un-signed; the sidecar shall not be omitted — for as long as planetary consciousness endures.*
