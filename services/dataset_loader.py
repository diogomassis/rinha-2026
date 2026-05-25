from __future__ import annotations

import gzip, ijson
import numpy as np

from functools import lru_cache
from pathlib import Path
from typing import Iterator

from models.vector.vector import VectorLabel

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESOURCES_DIR = PROJECT_ROOT / "resources"
DEFAULT_REFERENCES_PATH = RESOURCES_DIR / "references.json.gz"

def _to_vector_label(item: dict) -> VectorLabel:
    return VectorLabel(
        vector=[float(value) for value in item["vector"]],
        label=str(item["label"]),
    )

def iter_reference_dataset(references_path: Path | None = None) -> Iterator[VectorLabel]:
    path = references_path or DEFAULT_REFERENCES_PATH

    with gzip.open(path, "rb") as file:
        for item in ijson.items(file, "item"):
            yield _to_vector_label(item)

@lru_cache(maxsize=1)
def load_reference_dataset(references_path: str | None = None) -> list[VectorLabel]:
    path = Path(references_path) if references_path else DEFAULT_REFERENCES_PATH
    return list(iter_reference_dataset(path))


def load_training_arrays(
    references_path: str | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    dataset = load_reference_dataset(references_path)
    print(f"Loaded {len(dataset)} reference items")
    vectors = np.asarray([item.vector for item in dataset], dtype=np.float32)
    labels = np.asarray([0.0 if item.label == "legit" else 1.0 for item in dataset], dtype=np.float32)
    return vectors, labels
