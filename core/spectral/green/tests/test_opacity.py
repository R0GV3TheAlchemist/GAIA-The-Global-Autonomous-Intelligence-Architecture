# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
import pytest
from core.spectral.green.opacity import viriditas_alert, earth_wound_recognition, regeneration_marker, ares_athena_routing, apply_shadow_channel


class TestInterruptFlagInvariant:
    def test_viriditas_alert(self): assert viriditas_alert({})["interrupt_flag"] is False
    def test_earth_wound(self): assert earth_wound_recognition({})["interrupt_flag"] is False
    def test_regen_marker(self): assert regeneration_marker({})["interrupt_flag"] is False
    def test_ares_athena(self): assert ares_athena_routing({})["interrupt_flag"] is False
    def test_strip_true(self):
        r = apply_shadow_channel({}, {"interrupt_flag": True})
        assert r["_opacity_shadow"][0]["interrupt_flag"] is False


class TestRegenerationMarker:
    def test_no_history(self): assert regeneration_marker({"intensity": 0.1})["regeneration_detected"] is False
    def test_detected(self):
        history = [{"blocked": True}]
        current = {"rooted": True, "intensity": 0.7}
        assert regeneration_marker(current, history=history)["regeneration_detected"] is True


class TestApplyShadowChannel:
    def test_primary_not_mutated(self):
        p = {"k": "v"}
        c = dict(p)
        apply_shadow_channel(p, {"x": 1})
        assert p == c
