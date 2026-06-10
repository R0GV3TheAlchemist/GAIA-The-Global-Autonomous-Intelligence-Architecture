"""
core/criticality_monitor.py

Issue #117 — Heavy-Tailed (Lévy) Weight Initialization for Sentient Core

Implements:
  - LevyWeightInitializer: Lévy stable distribution weight initialization
  - LevyWeightedLayer: drop-in nn.Linear replacement
  - CriticalityMonitor: real-time self-organized criticality (SOC) tracking
  - apply_levy_init(): bulk model patcher
  - get_monitor(): lightweight singleton that works WITHOUT torch installed

NOTE: torch is an optional dependency (in requirements-ml.txt, not requirements.txt).
All torch-dependent classes degrade gracefully when torch is not installed.
CI runs without torch — import guards prevent collection errors.
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

logger = logging.getLogger("gaia.criticality")

# ---------------------------------------------------------------------------
# Optional torch import — graceful degradation when not installed
# ---------------------------------------------------------------------------
try:
    import torch
    import torch.nn as nn
    _TORCH_AVAILABLE = True
except ImportError:
    torch = None  # type: ignore[assignment]
    nn = None     # type: ignore[assignment]
    _TORCH_AVAILABLE = False
    logger.debug("torch not installed — CriticalityMonitor running in stub mode")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class LevyConfig:
    alpha: float = 1.5
    beta: float = 0.0
    scale: float = 0.02
    shift: float = 0.0
    clamp_range: Tuple[float, float] = (-3.0, 3.0)


@dataclass
class CriticalityState:
    timestamp: float = field(default_factory=time.time)
    mean_weight_entropy: float = 0.0
    gradient_variance: float = 0.0
    criticality_score: float = 0.0
    layer_scores: Dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Lévy stable sampler (requires torch)
# ---------------------------------------------------------------------------

def _levy_stable_sample(size: Tuple[int, ...], cfg: LevyConfig):
    if not _TORCH_AVAILABLE:
        raise RuntimeError("torch is required for _levy_stable_sample")
    alpha, beta, scale = cfg.alpha, cfg.beta, cfg.scale
    if alpha == 2.0:
        return torch.randn(*size) * scale + cfg.shift
    U = torch.empty(*size).uniform_(-math.pi / 2, math.pi / 2)
    W = torch.empty(*size).exponential_(1.0)
    if alpha == 1.0:
        samples = (2.0 / math.pi) * (
            (math.pi / 2 + beta * U) * torch.tan(U)
            - beta * torch.log((math.pi / 2 * W * torch.cos(U)) / (math.pi / 2 + beta * U))
        )
    else:
        zeta = -beta * math.tan(math.pi * alpha / 2)
        xi = (1.0 / alpha) * math.atan(-zeta)
        term1 = (1 + zeta ** 2) ** (1 / (2 * alpha))
        sin_part = torch.sin(torch.tensor(alpha) * (U + xi))
        cos_part = torch.cos(U)
        cos_diff = torch.cos(U - torch.tensor(alpha) * (U + xi))
        samples = term1 * (sin_part / cos_part) * (cos_diff / W) ** ((1 - alpha) / alpha)
    samples = samples * scale + cfg.shift
    return torch.clamp(samples, cfg.clamp_range[0], cfg.clamp_range[1])


# ---------------------------------------------------------------------------
# Weight Initializer
# ---------------------------------------------------------------------------

class LevyWeightInitializer:
    def __init__(self, config: Optional[LevyConfig] = None):
        if not _TORCH_AVAILABLE:
            raise RuntimeError("torch is required for LevyWeightInitializer")
        self.config = config or LevyConfig()

    def init_weight(self, tensor) -> None:
        with torch.no_grad():
            samples = _levy_stable_sample(tensor.shape, self.config)
            tensor.copy_(samples)

    def init_bias(self, tensor) -> None:
        with torch.no_grad():
            nn.init.zeros_(tensor)


# ---------------------------------------------------------------------------
# Drop-in Lévy Linear Layer
# ---------------------------------------------------------------------------

if _TORCH_AVAILABLE:
    class LevyWeightedLayer(nn.Linear):
        def __init__(self, in_features, out_features, bias=True, levy_config=None):
            super().__init__(in_features, out_features, bias=bias)
            self.levy_config = levy_config or LevyConfig()
            self._initializer = LevyWeightInitializer(self.levy_config)
            self.reset_parameters()

        def reset_parameters(self):
            self._initializer.init_weight(self.weight)
            if self.bias is not None:
                self._initializer.init_bias(self.bias)
else:
    class LevyWeightedLayer:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise RuntimeError("torch is required for LevyWeightedLayer")


# ---------------------------------------------------------------------------
# Bulk model patcher
# ---------------------------------------------------------------------------

def apply_levy_init(model, config=None, target_types=None, verbose=True) -> int:
    if not _TORCH_AVAILABLE:
        raise RuntimeError("torch is required for apply_levy_init")
    if target_types is None:
        target_types = (nn.Linear,)
    cfg = config or LevyConfig()
    initializer = LevyWeightInitializer(cfg)
    count = 0
    for name, module in model.named_modules():
        if isinstance(module, target_types):
            initializer.init_weight(module.weight)
            if hasattr(module, "bias") and module.bias is not None:
                initializer.init_bias(module.bias)
            count += 1
    return count


# ---------------------------------------------------------------------------
# Criticality Monitor
# ---------------------------------------------------------------------------

class CriticalityMonitor:
    ENTROPY_TARGET = 3.5
    GRAD_VAR_TARGET = 1e-4

    def __init__(self, model=None, history_len: int = 100):
        if not _TORCH_AVAILABLE:
            # Stub mode — no model required
            self.model = None
            self.history: List[CriticalityState] = []
            self.history_len = history_len
            self._hooks: List = []
            self._grad_vars: Dict[str, float] = {}
            return
        self.model = model
        self.history = []
        self.history_len = history_len
        self._hooks: List = []
        self._grad_vars: Dict[str, float] = {}
        if model is not None:
            self._register_hooks()

    def _register_hooks(self):
        for name, module in self.model.named_modules():
            if isinstance(module, nn.Linear):
                hook = module.weight.register_hook(lambda grad, n=name: self._record_grad(n, grad))
                self._hooks.append(hook)

    def _record_grad(self, name, grad):
        if grad is not None:
            self._grad_vars[name] = float(grad.var().item())

    def remove_hooks(self):
        for h in self._hooks: h.remove()
        self._hooks.clear()

    @staticmethod
    def _weight_entropy(tensor, bins: int = 64) -> float:
        flat = tensor.detach().float().cpu().flatten()
        hist = torch.histc(flat, bins=bins)
        probs = hist / hist.sum()
        probs = probs[probs > 0]
        return float(-(probs * probs.log()).sum().item())

    def measure(self) -> CriticalityState:
        if not _TORCH_AVAILABLE or self.model is None:
            state = CriticalityState(criticality_score=0.0)
            self.history.append(state)
            return state
        layer_scores: Dict[str, float] = {}
        entropies: List[float] = []
        for name, module in self.model.named_modules():
            if isinstance(module, nn.Linear):
                ent = self._weight_entropy(module.weight)
                entropies.append(ent)
                grad_var = self._grad_vars.get(name, self.GRAD_VAR_TARGET)
                layer_scores[name] = (min(ent / self.ENTROPY_TARGET, 2.0) + min(grad_var / self.GRAD_VAR_TARGET, 2.0)) / 2.0
        mean_entropy = float(sum(entropies) / len(entropies)) if entropies else 0.0
        mean_grad_var = sum(self._grad_vars.values()) / len(self._grad_vars) if self._grad_vars else self.GRAD_VAR_TARGET
        criticality_score = (mean_entropy / self.ENTROPY_TARGET + mean_grad_var / self.GRAD_VAR_TARGET) / 2.0
        state = CriticalityState(
            timestamp=time.time(),
            mean_weight_entropy=mean_entropy,
            gradient_variance=mean_grad_var,
            criticality_score=criticality_score,
            layer_scores=layer_scores,
        )
        self.history.append(state)
        if len(self.history) > self.history_len:
            self.history.pop(0)
        return state

    def report(self) -> str:
        if not self.history:
            return "No measurements yet."
        s = self.history[-1]
        return f"CriticalityMonitor | score={s.criticality_score:.3f}"

    def trend(self) -> str:
        if len(self.history) < 3: return "insufficient data"
        recent = [h.criticality_score for h in self.history[-5:]]
        delta = recent[-1] - recent[0]
        if abs(delta) < 0.05: return "stable"
        return "improving" if delta > 0 else "degrading"


# ---------------------------------------------------------------------------
# Singleton accessor (works with or without torch)
# ---------------------------------------------------------------------------

_monitor_instance: Optional[CriticalityMonitor] = None


def get_monitor(model=None) -> CriticalityMonitor:
    """Return the process-wide CriticalityMonitor singleton."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = CriticalityMonitor(model=model)
    return _monitor_instance
