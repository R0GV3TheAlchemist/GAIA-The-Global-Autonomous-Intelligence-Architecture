-- Migration 0003: Shadow Engine tables (Issue #67)
-- Applied by MigrationRunner; do not run manually.

-- Shadow archetype activation record (one row per principal, updated in place)
CREATE TABLE IF NOT EXISTS shadow_records (
    principal_id          TEXT PRIMARY KEY,
    active_archetype      TEXT NOT NULL DEFAULT 'none',
    -- archetypal values: none | orphan | martyr | wanderer | destroyer | wounded_healer
    shadow_intensity      REAL NOT NULL DEFAULT 0.0 CHECK (shadow_intensity BETWEEN 0.0 AND 1.0),
    dominant_emotion      TEXT NOT NULL DEFAULT 'neutral',
    is_volatile           INTEGER NOT NULL DEFAULT 0 CHECK (is_volatile IN (0,1)),
    low_energy_flag       INTEGER NOT NULL DEFAULT 0 CHECK (low_energy_flag IN (0,1)),
    mood_momentum         REAL NOT NULL DEFAULT 0.0,
    valence_trend         REAL NOT NULL DEFAULT 0.0,
    arc_stability         REAL NOT NULL DEFAULT 0.5,
    recommended_practice  TEXT,              -- short plaintext guidance string
    updated_at            INTEGER NOT NULL
);

-- Append-only log of shadow state changes (for Shadow Engine history)
CREATE TABLE IF NOT EXISTS shadow_transitions (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    principal_id          TEXT NOT NULL,
    from_archetype        TEXT NOT NULL,
    to_archetype          TEXT NOT NULL,
    transitioned_at       INTEGER NOT NULL,
    trigger_emotion       TEXT,
    shadow_intensity_at   REAL NOT NULL DEFAULT 0.0
);

CREATE INDEX IF NOT EXISTS idx_shadow_transitions_principal
    ON shadow_transitions (principal_id, transitioned_at DESC);
