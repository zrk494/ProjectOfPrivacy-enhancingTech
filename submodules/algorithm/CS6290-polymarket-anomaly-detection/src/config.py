from __future__ import annotations

# =========================
# Core pipeline parameters
# =========================

BUCKET_SECONDS = 60

# Activity anomaly scoring
ACTIVITY_WINDOW = 60
ACTIVITY_QUANTILE = 0.98
ACTIVITY_SCORE_MODE = "sum"

# Batch / output defaults
TOP_K_BUCKETS = 10
TOP_K_EVENTS = 10