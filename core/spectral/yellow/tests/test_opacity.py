# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
import pytest
from core.spectral.yellow.opacity import (
    xanthosis_alert, mental_wound_recognition, illumination_marker,
    ares_athena_routing, apply_shadow_channel,
)


class TestInterruptFlagInvariant:
    def test_xanthosis_alert(self): assert xanthosis_alert({})["interrupt_flag"] is False
    def test_mental_wound(self): assert mental_wound_recognition({})["interrupt_flag"] is False
    def test_illumination_marker(self): assert illumination_marker({})["interrupt_flag"] is False
    def test_ares_athena(self): assert ares_athena_routing({})["interrupt_flag"] is False

    def test_apply_shadow_strips_true(self):
        r = apply_shadow_channel({}, {"interrupt_flag": True})
        assert r["_opacity_shadow"][0]["interrupt_flag"] is False


class TestIlluminationMarker:
    def test_no_history(self): assert illumination_marker({"intensity": 0.1})["illumination_detected"] is False

    def test_illumination_detected(self):
        history = [{"blocked": True}, {"intensity": 0.1}]
        current = {"coherent": True, "intensity": 0.7}
        assert illumination_marker(current, history=history)["illumination_detected"] is True


class TestApplyShadowChannel:
    def test_primary_not_mutated(self):
        p = {"key": "val"}
        copy = dict(p)
        apply_shadow_channel(p, {"x": 1})
        assert p == copy

    def test_shadow_appended(self):
        r = apply_shadow_channel({}, {"tag": "mind"})
        assert r["_opacity_shadow"][0]["tag"] == "mind"
