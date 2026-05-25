#!/usr/bin/env python3
"""Build an Annoy index from references.json.gz and save labels.

Usage:
    python scripts/build_ann_index.py --references resources/references.json.gz --output resources/references.ann

This script writes:
- resources/references.ann  (Annoy index file)
- resources/reference_labels.npy (labels as float32 array, 1.0 for fraud, 0.0 for legit)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from annoy import AnnoyIndex

from services.dataset_loader import iter_reference_dataset


def build_index(references_path: Path, output_index: Path, labels_output: Path, n_trees: int = 50, metric: str = "euclidean"):
    # determine dimensionality from first item
    it = iter_reference_dataset(references_path)
    first = next(it, None)
    if first is None:
        raise SystemExit("No items found in references file")
    dim = len(first.vector)

    index = AnnoyIndex(dim, metric)
    labels = []

    # add first
    index.add_item(0, first.vector)
    labels.append(1.0 if first.label == "fraud" else 0.0)

    for i, item in enumerate(it, start=1):
        index.add_item(i, item.vector)
        labels.append(1.0 if item.label == "fraud" else 0.0)

    print(f"Building Annoy index with {len(labels)} items, dim={dim}, trees={n_trees}...")
    index.build(n_trees)
    output_index.parent.mkdir(parents=True, exist_ok=True)
    index.save(str(output_index))
    np.save(labels_output, np.asarray(labels, dtype=np.float32))
    print(f"Saved index to {output_index} and labels to {labels_output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--references", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--labels-output", type=Path, default=Path("resources/reference_labels.npy"))
    parser.add_argument("--trees", type=int, default=50)
    args = parser.parse_args()
    build_index(args.references, args.output, args.labels_output, n_trees=args.trees)

if __name__ == "__main__":
    main()
