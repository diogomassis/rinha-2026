from __future__ import annotations

import numpy as np

from pathlib import Path
from annoy import AnnoyIndex

EXPECTED_INPUT_SIZE = 14
NEAREST_NEIGHBORS = 5


class AnnEngine:
    def __init__(self, ann_index: AnnoyIndex, reference_labels: np.ndarray, threshold: float = 0.6, k: int = NEAREST_NEIGHBORS):
        self.ann_index = ann_index
        self.reference_labels = reference_labels.astype(np.float32)
        self.threshold = threshold
        self.k = k

    @classmethod
    def load(cls, references_path: str | Path, threshold: float = 0.6, k: int = NEAREST_NEIGHBORS) -> "AnnEngine":
        path = Path(references_path)
        if not path.exists():
            raise FileNotFoundError(f"Reference dataset not found at {path}.")

        # Expect index and labels to be prebuilt in the same resources folder
        resources_dir = path.parent
        index_path = resources_dir / "references.ann"
        labels_path = resources_dir / "reference_labels.npy"

        if not index_path.exists() or not labels_path.exists():
            raise FileNotFoundError(f"Annoy index or labels not found. Run scripts/build_ann_index.py to build them.\nMissing: {index_path if not index_path.exists() else ''} {labels_path if not labels_path.exists() else ''}")

        # load labels
        labels = np.load(labels_path)
        dim = EXPECTED_INPUT_SIZE
        ann = AnnoyIndex(dim, "euclidean")
        ann.load(str(index_path))
        print(f"ANN engine: loaded Annoy index from {index_path} with {len(labels)} labels.")
        return cls(ann_index=ann, reference_labels=labels, threshold=threshold, k=k)

    def predict_proba(self, vector: list[float] | np.ndarray) -> float:
        vec = list(map(float, vector))
        if len(vec) != EXPECTED_INPUT_SIZE:
            raise ValueError(f"ANN expects {EXPECTED_INPUT_SIZE} input features, got {len(vec)}")

        nearest = self.ann_index.get_nns_by_vector(vec, self.k, include_distances=False)
        if not nearest:
            return 0.0
        fraud_probability = float(np.mean(self.reference_labels[nearest]))
        return fraud_probability

    def predict(self, vector: list[float] | np.ndarray) -> tuple[bool, float]:
        fraud_score = self.predict_proba(vector)
        approved = fraud_score < self.threshold
        return approved, fraud_score
