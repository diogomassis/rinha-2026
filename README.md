# Rinha 2026 — Fraud Detection

This repository contains an implementation for the Rinha de Backend 2026 challenge focused on fraud detection using vector search.

Purpose: evaluate a compact, efficient backend under CPU and memory limits.

Challenge: process transaction requests, compute fraud scores, and perform nearest-neighbour lookups with constrained resources.

## Solution summary

- **Approach:** combine lightweight feature normalization, a small vector model, and an ANN index for similarity search.
- **Goal:** high recall for known fraud patterns with low CPU and memory usage.

## Architecture

- **API:** minimal HTTP service accepting transaction requests and returning scores.
- **Vectorization:** feature extractor in `models/vector/vector.py` produces fixed-size vectors.
- **Index:** ANN index stored on disk and loaded into memory by `services/ann/ann_engine.py`.
- **Storage:** simple file-based resources under `resources/` for reproducibility.

## Design decisions

- **Simplicity:** prefer deterministic, explainable feature transforms over large models.
- **Performance:** memory-efficient vectors and lightweight ANN library to meet limits.
- **Reproducibility:** all resources and generation scripts are included (`data-generator/`, `scripts/`).

## Folder overview

- `app/` — application entrypoint and API.
- `models/` — feature definitions, normalization, and vector code.
- `services/` — ANN and vector engine implementations.
- `resources/` — static data: normalization rules and reference vectors.
- `data-generator/` — C generator for synthetic data and tools.
- `test/` — performance and smoke tests.

## Requirements

- Python 3.10+ (see `requirements.txt`).
- Build toolchain for the C data generator (gcc, make) if generating data.

## Run locally

1. Create a Python virtual environment and install requirements.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start the API (development):

```bash
fastapi dev
```

3. Run smoke tests from `test/` or use `docker-compose` where provided:

```bash
docker compose up --build
```

## Development notes

- Use `scripts/build_ann_index.py` to rebuild ANN indexes from generated vectors.
- Normalization rules live in `resources/normalization.json` and are applied in `models/normalization`.

## License

This project follows the license in the repository root.

## References

- Challenge: <https://github.com/zanfranceschi/rinha-de-backend-2026>
