#!/usr/bin/env bash
set -eu
cd /workspace/AI-HyperGenius
export UV_CACHE_DIR=/workspace/shared/uv-cache
uv sync --frozen
.venv/bin/python scripts/prepara_isolamento.py
