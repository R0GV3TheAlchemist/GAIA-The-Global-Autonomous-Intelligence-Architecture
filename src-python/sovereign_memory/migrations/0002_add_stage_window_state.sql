-- Migration 0002: Add stage_window_state table for WindowTracker (Stage Engine #63)
-- Applied by MigrationRunner; do not run manually.

CREATE TABLE IF NOT EXISTS stage_window_state (
    principal_id              TEXT PRIMARY KEY,
    days_forward_window_met   INTEGER NOT NULL DEFAULT 0,
    days_regression_window    INTEGER NOT NULL DEFAULT 0,
    last_evaluated_date       TEXT,
    updated_at                INTEGER NOT NULL
);
