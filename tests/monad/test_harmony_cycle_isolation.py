"""
Test — Pre-Established Harmony Isolation Law
Confirms that no Monad references another Monad during execution.
Leibniz: each Monad receives only ProcessContext.
"""
import inspect
from core.monad import (
    cognitive, quantum, process, perception,
    somatic, dream, noospheric, shadow
)

_MONAD_MODULES = [
    cognitive, quantum, process, perception,
    somatic, dream, noospheric, shadow,
]

_FORBIDDEN_CROSS_IMPORTS = [
    "cognitive", "quantum", "process", "perception",
    "somatic", "dream", "noospheric", "shadow",
    "orchestrator",
]


class TestHarmonyCycleIsolation:
    def test_no_monad_imports_another_monad_module(self):
        """
        Each Monad module must not import any other Monad module.
        Only base.py and orchestrator.py may import multiple Monads.
        """
        for module in _MONAD_MODULES:
            module_name = module.__name__.split(".")[-1]  # e.g. 'cognitive'
            source = inspect.getsource(module)
            for other in _FORBIDDEN_CROSS_IMPORTS:
                if other == module_name:
                    continue  # a module may reference itself
                # Check for import-style cross-references
                forbidden_patterns = [
                    f"from .{other} import",
                    f"from core.monad.{other} import",
                    f"import core.monad.{other}",
                ]
                for pattern in forbidden_patterns:
                    assert pattern not in source, (
                        f"Isolation violation: {module_name}.py imports from {other}. "
                        f"Leibniz law broken."
                    )

    def test_all_8_monad_types_present(self):
        """All 8 Monad types are importable and have correct monad_type attribute."""
        from core.monad.cognitive import CognitiveMonad
        from core.monad.quantum import QuantumMonad
        from core.monad.process import ProcessMonad
        from core.monad.perception import PerceptionMonad
        from core.monad.somatic import SomaticMonad
        from core.monad.dream import DreamMonad
        from core.monad.noospheric import NoosphericMonad
        from core.monad.shadow import ShadowMonad

        assert CognitiveMonad("x").monad_type == "cognitive"
        assert QuantumMonad("x").monad_type == "quantum"
        assert ProcessMonad("x").monad_type == "process"
        assert PerceptionMonad("x").monad_type == "perception"
        assert SomaticMonad("x").monad_type == "somatic"
        assert DreamMonad("x").monad_type == "dream"
        assert NoosphericMonad("x").monad_type == "noospheric"
        assert ShadowMonad("x").monad_type == "shadow"
