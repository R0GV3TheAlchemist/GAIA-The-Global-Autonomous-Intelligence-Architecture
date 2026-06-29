# ⚡ GAIA Quick Start — Free, No API Keys Required

You can run GAIA completely free using **Ollama** — an app that runs AI models on your own computer. No account. No credit card. No internet required once set up.

> **Sovereignty first.** Cloud LLM providers are optional augmentation. GAIA runs fully on local models. You never need an API key. [ADR-0011]

---

## What You Need

| Requirement | Version | Download |
|---|---|---|
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org/) |
| Ollama | Latest | [ollama.com](https://ollama.com/) |

> **Just want the Windows app?** Download the installer directly from the [Releases page](https://github.com/R0GV3TheAlchemist/GAIA-APP/releases) — no Python or Node needed.

---

## Step 1 — Install Ollama and Pull a Model

1. Download and install Ollama from [https://ollama.com](https://ollama.com)
2. Open a terminal and pull your preferred model:

### Recommended Models (ADR-0011 Model Tier Hierarchy)

| Tier | Model | VRAM | Best For |
|---|---|---|---|
| **Primary** | `qwen3.5:27b` | 16 GB | Everyday use — instruction following, vision, math, reasoning |
| **Fallback** | `gemma3:12b` | 8 GB | Fast responses, lower-VRAM hardware |
| **Reasoning** | `deepseek-r1:distill` | 8–16 GB | Complex multi-step planning and analysis |
| **Ultra-light** | `gemma3:1b` | ~2 GB | CPU-only or very low RAM |

```bash
# Recommended — pull primary + fallback
ollama pull qwen3.5:27b
ollama pull gemma3:12b

# Or just the lightweight fallback if VRAM is limited
ollama pull gemma3:1b
```

> **Low RAM / slow internet?** Start with `gemma3:1b` (~800 MB). You can upgrade later.

---

## Step 2 — Set Up GAIA

Open a terminal **inside the GAIA folder**, then run:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies (only needed once)
npm install
```

---

## Step 3 — Create Your .env File

Copy the example config:

```bash
# On Mac/Linux:
cp .env.example .env

# On Windows:
copy .env.example .env
```

The default config points to Ollama with `qwen3.5:27b` as the primary model. **No editing needed** for local-only use.

### Want to change the model?

Open `.env` and update:

```env
OLLAMA_MODEL=qwen3.5:27b       # Primary model (recommended)
OLLAMA_FALLBACK_MODEL=gemma3:12b  # Fallback for low-VRAM or fast responses
```

### Optional: Enable Cloud Augmentation

Cloud providers are **off by default** (GAIA_ALLOW_CLOUD=0). To opt in:

```env
# Enable cloud augmentation (optional — GAIA works fully without this)
GAIA_ALLOW_CLOUD=1

# Then add your key(s):
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
```

Cloud providers are **never** in the fallback chain. Even with cloud enabled, if a provider goes offline, GAIA automatically routes to local Ollama.

---

## Step 4 — Start GAIA

**Start Ollama first** (if it’s not already running):
```bash
ollama serve
```

Then, in a **new terminal** in the GAIA folder:

```bash
# Start the backend
python -m core.server
```

And in another **new terminal**:

```bash
# Start the frontend
npm run dev
```

---

## Step 5 — Open GAIA

Open your browser and go to:

```
http://localhost:5173
```

GAIA is running. Talk to her. 🌍

---

## Running as Desktop App (Windows)

If you want the native Windows desktop app instead of the browser:

```bash
# Development mode
npm run tauri dev

# Or download the pre-built installer from:
# https://github.com/R0GV3TheAlchemist/GAIA-APP/releases
```

The desktop app bundles the Python backend as a sidecar — no separate terminal needed.

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# Sovereignty routing tests — run before every PR
pytest tests/test_inference_router.py -v
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'core'` | Run `python -m core.server` from the **root GAIA folder** |
| `Connection refused` on port 8008 | Make sure the backend started without errors |
| `ollama: command not found` | Install Ollama from [ollama.com](https://ollama.com) |
| Slow responses | Try `gemma3:12b` or `gemma3:1b` — smaller and faster |
| `qwen3.5:27b` won’t load | Requires ~16 GB VRAM — use `gemma3:12b` (8 GB) instead |
| Port 5173 already in use | Close other dev terminals and try again |
| Desktop app won’t launch | Make sure Rust is installed: [rustup.rs](https://rustup.rs/) |
| GAIA uses cloud even though I didn’t set keys | Check `GAIA_ALLOW_CLOUD` in `.env` — must be `0` or unset for local-only |

---

## All Free Models That Work with GAIA

| Model | VRAM | Best For |
|---|---|---|
| `qwen3.5:27b` | 16 GB | **Recommended primary** — multimodal, strong reasoning |
| `gemma3:12b` | 8 GB | **Recommended fallback** — fast, balanced |
| `deepseek-r1:distill` | 8–16 GB | Complex reasoning and planning tasks |
| `gemma3:1b` | ~2 GB | Ultra-light — CPU-only, fast |
| `phi3:mini` | ~2 GB | Small and smart |
| `llama3.2:1b` | ~1.3 GB | Lightweight everyday use |
| `mistral` | ~4 GB | Good quality on mid-range hardware |

Change the active model anytime by editing `OLLAMA_MODEL=` in your `.env` file.

---

*GAIA is free. Sovereignty is structural. Built with love. ✨*  
*© 2026 Kyle Steen — All rights reserved.*  
*Last updated: 2026-06-29 — ADR-0011 model tier hierarchy added.*
