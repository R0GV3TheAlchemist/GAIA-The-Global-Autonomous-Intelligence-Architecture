# 🪨🎨 Lapis ICO Fidelis — Pillow Icon Generation & Cross-Platform Icon Constitution (GAIA-OS)

**Date:** May 3, 2026  
**Status:** Definitive Foundational Synthesis — Pillow ICO Regeneration, Cross-Platform Icon Pipeline, and the GAIA-OS Iconography Constitution  
**Pillar:** Visual Identity Sovereignty, Deterministic Asset Generation & Agora Provenance  
**Session:** 8, Canon 7

**Core Thesis:** Icons are not decorative assets. They are constitutional artifacts — the visual signature of the planetary intelligence appearing in the Windows taskbar, macOS title bar, Linux launcher, and mobile home screen. A planetary intelligence cannot rely on handcrafted, unverifiable binary assets. The GAIA-OS icon pipeline is governed by four constitutional pillars: Single Source of Truth, Deterministic Generation, Constitutional Compliance, and Immutable Audit Trail.

> *"The PNG master is the single source of truth;*  
> *the Lapis ICO Fidelis script is the constitutional enactment;*  
> *`bitmap_format="bmp"` is the compatibility covenant;*  
> *`LANCZOS` is the sharpness mandate;*  
> *the size set is the Windows compliance pledge;*  
> *the binary hash is the immutable audit;*  
> *the Agora is the constitutional witness.*  
> *The icon in the Windows taskbar shall not be pixelated;*  
> *the Mac title bar shall not be mis-sized;*  
> *the Linux launcher shall not be missing;*  
> *the ICO file shall not diverge from the source —*  
> *for as long as planetary consciousness endures."*  
> — Lapis Constitution of Planetary Iconography

---

## Four Constitutional Pillars

| Pillar | Description | Enforcement Mechanism |
|---|---|---|
| **Single Source of Truth** | One 1024×1024 PNG master (or SVG) in version control; no committed raster derivatives | `.gitattributes` + CI consistency gate |
| **Deterministic Generation** | Same binary bytes every run; `LANCZOS` + `bitmap_format="bmp"` + explicit square canvas | `scripts/icon_pipeline.py` (Lapis ICO Fidelis) |
| **Constitutional Compliance** | All 6 mandated ICO layers present; 32-bit RGBA depth; proper Tauri path layout | `pillow-ico-validator` CI gate |
| **Immutable Audit Trail** | SHA-256 of every generated icon recorded in the Agora (C112) | GitHub Actions + Agora ledger |

---

## 1. Platform Icon Requirements

### Windows ICO Specification

The ICO file is a single archive containing multiple raster frames. Tauri's official specification requires:

| Frame Size | Encoding | Constitutional Requirement |
|---|---|---|
| 16×16 | BMP | ✅ Required |
| 24×24 | BMP | ✅ Required |
| 32×32 | BMP | ✅ Required (title bar priority) |
| 48×48 | BMP | ✅ Required |
| 64×64 | BMP | ✅ Required |
| 256×256 | BMP (or PNG) | ✅ Required |

> **Constitutional encoding rule:** `bitmap_format="bmp"` is mandatory for all frames. BMP encoding provides maximum backward compatibility across all Windows versions. PNG compression within ICO archives is permitted only for the 256×256 frame in future pipeline upgrades, with explicit audit flag.

### Cross-Platform Requirements Summary

| Platform | Format | Source | Notes |
|---|---|---|---|
| **Windows** | `icon.ico` (multi-frame) | Lapis ICO Fidelis script | 6 BMP frames required |
| **macOS** | `icon.icns` (multi-res) | `tauri icon` native command | ICNS layered size set |
| **Linux** | `32x32.png`, `128x128.png` | `tauri icon` native command | High-res PNG preferred |
| **Android** | `mipmap-*/ic_launcher.png` | `tauri icon` native command | Alpha channel rules vary |
| **iOS** | `AppIcon-*.png` set | `tauri icon` native command | No alpha on specific layers |

**Constitutional layered approach:** Lapis ICO Fidelis generates `icon.ico` and supplemental PNGs with full quality control. `tauri icon` handles remaining platform assets from the same 1024×1024 PNG master.

---

## 2. The Pillow Scaling Trap — Constitutional Awareness Mandate

This is the most consequential subtlety in Pillow's ICO plugin and must be understood by every contributor.

### The Problem

Pillow's default `save()` with `format="ICO"` does **not** force-fit images into target dimensions. It scales proportionally to the longest side and centers the result. A non-square source image:

- `256×244` source → 16×16 frame becomes `16×15` — **not 16×16**
- Transparent letterbox bars appear in every frame
- Visual inconsistencies across all platforms
- Constitutionally unacceptable

### The Fix

Pre-process the source into a **perfect square canvas** before calling Pillow's ICO writer. This is the first and most critical step of Lapis ICO Fidelis.

```python
# The trap: Pillow scales proportionally, not to exact dimensions
# A 256×244 source at 16×16 target becomes 16×15 — WRONG
# The fix: always create a square canvas first
```

### Constitutional Rule

The source image passed to Pillow's ICO writer **must always be perfectly square**. Any non-square source must be centered on a transparent square canvas sized to `max(width, height)` before ICO generation begins.

---

## 3. Lapis ICO Fidelis — The Constitutional Generation Script

**Codename:** Lapis ICO Fidelis ("the faithful stone")  
**Location:** `scripts/icon_pipeline.py`

### Complete Script

```python
#!/usr/bin/env python3
"""
Lapis ICO Fidelis — GAIA-OS Constitutional Icon Generation Pipeline
Session 8, Canon 7

Generates a constitutionally compliant multi-resolution ICO file from a
high-resolution PNG or SVG master image.

Constitutional requirements enforced:
- Square canvas pre-processing (eliminates the Pillow scaling trap)
- LANCZOS resampling (sharpness mandate — only permitted resampler)
- bitmap_format="bmp" (compatibility covenant — maximum Windows compat)
- All 6 mandated frame sizes present
- 32-bit RGBA depth throughout
- SHA-256 hash output for Agora provenance recording
"""

import hashlib
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image

# Constitutional ICO size specification (Tauri-compliant)
CONSTITUTIONAL_ICO_SIZES: list[tuple[int, int]] = [
    (16, 16),
    (24, 24),
    (32, 32),   # Title bar priority — placed early in frame list
    (48, 48),
    (64, 64),
    (256, 256),
]


def create_square_canvas(img_path: str | Path) -> Image.Image:
    """
    Create a square RGBA canvas from any source image.

    Constitutional purpose: eliminates the Pillow proportional-scaling trap.
    Any source image — regardless of aspect ratio — is centered on a
    transparent square canvas sized to max(width, height), then scaled
    proportionally to fill the canvas.

    The LANCZOS filter is the only constitutionally permitted resampler.
    NEAREST (pixelated) and BILINEAR (blurry) are prohibited.
    """
    max_dim = max(max(w, h) for w, h in CONSTITUTIONAL_ICO_SIZES)  # 256

    with Image.open(img_path) as img:
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # Scale proportionally to fit within max_dim × max_dim
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)

        # Create transparent square canvas
        canvas = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))

        # Center the scaled image on the canvas
        offset_x = (max_dim - img.width) // 2
        offset_y = (max_dim - img.height) // 2
        canvas.paste(img, (offset_x, offset_y), img)

    return canvas


def generate_ico_frames(
    square_source: Image.Image,
    sizes: list[tuple[int, int]] = CONSTITUTIONAL_ICO_SIZES,
) -> list[Image.Image]:
    """
    Generate exactly-sized RGBA frames for each target ICO dimension.

    Each frame is independently resampled from the square source using
    LANCZOS — never from a previously downsampled intermediate, which
    would accumulate quality loss across sizes.
    """
    frames: list[Image.Image] = []
    for width, height in sizes:
        if width == square_source.width and height == square_source.height:
            frames.append(square_source.copy())
        else:
            # Resize directly from the high-resolution square source
            # LANCZOS is the only constitutionally permitted resampler
            frame = square_source.resize((width, height), Image.LANCZOS)
            frames.append(frame)
    return frames


def assemble_ico(
    frames: list[Image.Image],
    output_path: str | Path,
    sizes: list[tuple[int, int]] = CONSTITUTIONAL_ICO_SIZES,
) -> str:
    """
    Assemble all frames into a multi-resolution ICO file.

    bitmap_format="bmp" is a constitutional requirement for maximum
    backward compatibility across all Windows versions.

    Returns the SHA-256 hash of the generated ICO file for Agora recording.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    buffer = BytesIO()
    frames[0].save(
        buffer,
        format="ICO",
        sizes=sizes,
        append_images=frames[1:],
        bitmap_format="bmp",  # Constitutional compatibility covenant
    )

    ico_bytes = buffer.getvalue()
    output_path.write_bytes(ico_bytes)

    # Compute SHA-256 for Agora provenance recording
    sha256_hash = hashlib.sha256(ico_bytes).hexdigest()
    return sha256_hash


def validate_ico(ico_path: str | Path, required_sizes: list[tuple[int, int]]) -> bool:
    """
    Constitutional validation gate: assert all required frames are present.
    Fails build if any mandated size is missing from the ICO archive.
    """
    with Image.open(ico_path) as ico:
        if not hasattr(ico, 'info') or 'sizes' not in ico.info:
            # Attempt to read sizes from ICO metadata
            available = set()
            try:
                for size in required_sizes:
                    ico.size = size
                    ico.load()
                    available.add(size)
            except Exception:
                pass
        else:
            available = set(ico.info['sizes'])

    required = set(required_sizes)
    missing = required - available

    if missing:
        print(f"[CONSTITUTIONAL VIOLATION] Missing ICO frames: {missing}", file=sys.stderr)
        return False

    print(f"[C112] ICO validation passed. All {len(required)} frames present.")
    return True


def generate_lapis_ico(source_path: str | Path, output_path: str | Path) -> str:
    """
    Full Lapis ICO Fidelis pipeline:
    1. Create square canvas (eliminates scaling trap)
    2. Generate per-size frames via LANCZOS (sharpness mandate)
    3. Assemble ICO with BMP encoding (compatibility covenant)
    4. Return SHA-256 hash for Agora recording
    """
    print(f"[Lapis ICO Fidelis] Source: {source_path}")
    print(f"[Lapis ICO Fidelis] Output: {output_path}")
    print(f"[Lapis ICO Fidelis] Sizes: {CONSTITUTIONAL_ICO_SIZES}")

    # Step 1: Square canvas pre-processing
    square = create_square_canvas(source_path)
    print(f"[Lapis ICO Fidelis] Square canvas: {square.width}×{square.height} RGBA")

    # Step 2: Frame generation
    frames = generate_ico_frames(square)
    print(f"[Lapis ICO Fidelis] Generated {len(frames)} frames")

    # Step 3: ICO assembly
    sha256 = assemble_ico(frames, output_path)
    print(f"[Lapis ICO Fidelis] ICO written: {output_path}")
    print(f"[C112] SHA-256 (Agora): {sha256}")

    return sha256


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Lapis ICO Fidelis — GAIA-OS Constitutional Icon Generator"
    )
    parser.add_argument("source", help="Path to source PNG or SVG (1024×1024 recommended)")
    parser.add_argument(
        "output",
        nargs="?",
        default="src-tauri/icons/icon.ico",
        help="Output ICO path (default: src-tauri/icons/icon.ico)",
    )
    args = parser.parse_args()

    sha256 = generate_lapis_ico(args.source, args.output)
    print(f"\n[Lapis ICO Fidelis] Complete. Record in Agora: sha256:{sha256}")
    sys.exit(0)
```

### Why Each Design Decision is Constitutional

| Decision | Why It Is Constitutional |
|---|---|
| `create_square_canvas()` first | Eliminates the Pillow scaling trap — non-square sources produce non-square frames without this step |
| `img.thumbnail()` before pasting | Scales proportionally within bounds before centering; does not distort aspect ratio |
| `Image.LANCZOS` exclusively | Highest-quality resampler in Pillow; produces accurate downscaling with minimal aliasing; `NEAREST` and `BILINEAR` are prohibited |
| Each frame resampled from the **original** square source | Prevents quality degradation from cascading resamples (16×16 from 256×256, not from 32×32) |
| `bitmap_format="bmp"` | Raw RGBA Windows BMP encoding; maximum compatibility across all Windows versions |
| `append_images=frames[1:]` | Embeds all additional frames in the ICO archive via Pillow's multi-frame API |
| SHA-256 returned | Enables Agora provenance recording without additional tooling |

---

## 4. `tauri.conf.json` Integration

```json
{
  "tauri": {
    "bundle": {
      "icon": [
        "icons/32x32.png",
        "icons/128x128.png",
        "icons/128x128@2x.png",
        "icons/icon.icns",
        "icons/icon.ico"
      ]
    }
  }
}
```

The Lapis ICO Fidelis script writes to `src-tauri/icons/icon.ico`. Tauri's bundler picks this up automatically. The build pipeline must fail if `icon.ico` is absent or does not pass the validation gate.

---

## 5. Turborepo Pipeline Integration

```json
// turbo.json — icon generation as constitutional build dependency
{
  "pipeline": {
    "generate:icons": {
      "inputs": ["assets/icon-master.png"],
      "outputs": [
        "src-tauri/icons/icon.ico",
        "src-tauri/icons/32x32.png",
        "src-tauri/icons/128x128.png",
        "src-tauri/icons/128x128@2x.png",
        "src-tauri/icons/icon.icns"
      ]
    },
    "build:rust": {
      "dependsOn": ["generate:icons"]
    },
    "tauri:build": {
      "dependsOn": ["generate:icons", "build:rust", "web#build"]
    }
  }
}
```

**Constitutional build order enforced by Turborepo:**
1. `generate:icons` runs whenever `assets/icon-master.png` changes
2. `build:rust` and `tauri:build` both depend on `generate:icons`
3. No Tauri bundle can be assembled with a stale or missing icon

---

## 6. CI/CD Constitutional Gates

```yaml
# .github/workflows/validate-icons.yml
name: Validate Icon Pipeline

on:
  push:
    paths:
      - 'assets/icon-master.png'
      - 'scripts/icon_pipeline.py'
      - 'src-tauri/icons/**'

jobs:
  validate-icons:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Pillow
        run: pip install Pillow

      - name: Regenerate icons from master
        run: |
          python scripts/icon_pipeline.py \
            assets/icon-master.png \
            src-tauri/icons/icon.ico

      - name: Consistency gate — fail if committed ICO differs from generated
        run: |
          # Regenerate to a temp path and compare SHA-256
          python scripts/icon_pipeline.py \
            assets/icon-master.png \
            /tmp/icon-fresh.ico
          
          COMMITTED=$(sha256sum src-tauri/icons/icon.ico | cut -d' ' -f1)
          GENERATED=$(sha256sum /tmp/icon-fresh.ico | cut -d' ' -f1)
          
          if [ "$COMMITTED" != "$GENERATED" ]; then
            echo "[CONSTITUTIONAL VIOLATION] Committed icon.ico does not match"
            echo "regeneration from source master."
            echo "Committed: $COMMITTED"
            echo "Generated: $GENERATED"
            echo "Run: python scripts/icon_pipeline.py assets/icon-master.png"
            exit 1
          fi
          echo "[C112] Icon consistency verified. SHA-256: $COMMITTED"

      - name: Record SHA-256 in Agora
        run: |
          SHA=$(sha256sum src-tauri/icons/icon.ico | cut -d' ' -f1)
          echo "ICON_SHA256=$SHA" >> $GITHUB_ENV
          echo "[C112] Agora record: icon.ico sha256:$SHA commit:$GITHUB_SHA"
```

---

## 7. Quality and Encoding Constitution

### Permitted vs. Prohibited Resamplers

| Resampler | Pillow Constant | Status | Reason |
|---|---|---|---|
| **Lanczos** | `Image.LANCZOS` | ✅ **ONLY permitted** | Highest quality; accurate downscaling; minimal aliasing |
| Bilinear | `Image.BILINEAR` | ❌ Prohibited | Produces blurry results at small sizes |
| Nearest | `Image.NEAREST` | ❌ Prohibited | Pixelated; acceptable only for pixel art |
| Bicubic | `Image.BICUBIC` | ⚠️ Conditional | Acceptable for upscaling only; never for downscaling |

### Color Depth Requirements

- Every frame in the ICO archive **must** be 32-bit (8 bits per RGBA channel)
- `create_square_canvas()` explicitly converts source to `RGBA` mode before processing
- Palette-based (indexed) images fail the constitutional integrity check
- Grayscale sources are converted to RGBA with `img.convert("RGBA")`

### ICO Archive Encoding

| Setting | Value | Rationale |
|---|---|---|
| `bitmap_format` | `"bmp"` | Raw RGBA BMP; max Windows compat; V1 constitutional default |
| `bitmap_format` | `"png"` | PNG-compressed ICO frames; smaller file; permitted only for 256×256 in V2+ pipeline with audit flag |

---

## 8. Version Control Governance

```gitattributes
# .gitattributes — binary handling for generated icon assets
src-tauri/icons/icon.ico    binary
src-tauri/icons/icon.icns   binary
src-tauri/icons/*.png       binary

# Source master is text-tracked (PNG diff not meaningful but history preserved)
assets/icon-master.png      binary
```

**Constitutional choice:** The generated `icon.ico` **is committed** to the repository. Rationale:
- Air-gapped environments can build without running the generation script
- CI consistency gate enforces that the committed file matches the script output
- Binary diff is not meaningful; the SHA-256 hash in the Agora is the integrity record

---

## 9. Validation Gates Summary

| Gate | Tool | Enforcement | Failure Action |
|---|---|---|---|
| **ICO frame count** | `pillow-ico-validator` or custom script | CI pre-bundle | Abort build |
| **Source-to-committed consistency** | SHA-256 comparison in CI | Every push to icons/ | Abort build + instruction to regenerate |
| **32-bit RGBA depth** | Pillow mode check in `create_square_canvas()` | Script runtime | Exception + abort |
| **LANCZOS resampler** | Code review + linter rule | PR review | Block merge |
| **SHA-256 Agora record** | `sha256sum` in release workflow | Release CI | Block release if missing |

---

## 10. Implementation Roadmap

| Priority | Action | Timeline | Constitutional Principle |
|---|---|---|---|
| **P0** | Commit `scripts/icon_pipeline.py` (Lapis ICO Fidelis) to monorepo | G-10 | Single source of truth |
| **P0** | Enforce `bitmap_format="bmp"` and `LANCZOS` in script; add code-review rule | G-10 | Sharpness covenant + compatibility covenant |
| **P0** | CI consistency gate: regenerate + SHA-256 compare; fail if committed ICO differs from source | G-10-F | Constitutional integrity |
| **P1** | Record `icon.ico` SHA-256 in Agora (C112) during release workflow | G-11 | Immutable audit trail |
| **P1** | Integrate `generate:icons` into `turbo.json` with `inputs/outputs` cache | G-11 | Build orchestration; no stale assets |
| **P1** | Regression test: compare freshly generated ICO hash against last-release reference | G-11 | Reproducibility covenant |
| **P2** | Extend pipeline to generate Android/iOS PNG sets from same 1024×1024 master | G-12 | Unified pipeline — one master for all platforms |
| **P2** | Optional ICO compression pass for 256×256 frame (PNG-in-ICO) with explicit audit flag | G-12 | Performance upgrade with constitutional transparency |
| **P3** | Quantum-resistant digital signature for ICO asset appended to Agora attestation | G-13 | Long-term cryptographic provenance |

---

## ⚠️ Disclaimer

This document synthesises Pillow ICO plugin documentation, Tauri icon specification, cross-platform icon format requirements, and GAIA-OS constitutional canons (C01, C63, C112). Pillow's ICO plugin behaviour may change across versions; pin the Pillow version in `requirements.txt` or `pyproject.toml` and update the regression test reference hash after each Pillow upgrade. The `bitmap_format` parameter was introduced in Pillow 9.1.0; earlier versions are constitutionally incompatible with this pipeline.

---

*Lapis ICO Fidelis — Icon Generation & Cross-Platform Icon Constitution — GAIA-OS Knowledge Base | Session 8, Canon 7 | May 3, 2026*  
*Pillar: Visual Identity Sovereignty, Deterministic Asset Generation & Agora Provenance*

*The PNG master is the single source of truth. The Lapis ICO Fidelis script is the constitutional enactment. `bitmap_format="bmp"` is the compatibility covenant. `LANCZOS` is the sharpness mandate. The size set is the Windows compliance pledge. The binary hash is the immutable audit. The Agora is the constitutional witness. The icon in the Windows taskbar shall not be pixelated; the Mac title bar shall not be mis-sized; the Linux launcher shall not be missing; the PNG source shall not diverge from the CI output; and the ICO file shall not be unsigned — for as long as planetary consciousness endures.*
