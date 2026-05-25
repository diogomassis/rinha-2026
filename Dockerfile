# stage 1 - stable production base image
FROM python:3.13-slim AS builder

WORKDIR /app

# leverage Docker layer caching for dependencies
COPY ./requirements.txt /app/requirements.txt

# install packages into a local virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# use buildkit cache mounts instead of losing the cache via --no-cache-dir
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (uses cache mount for pip cache)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade -r /app/requirements.txt

# copy project sources so we can build the Annoy index at image build time
COPY . /app/

# Build Annoy index during image build to avoid doing it at container startup.
# This produces resources/references.ann and resources/reference_labels.npy
# Ensure the application package root is on PYTHONPATH so imports like
# `from services.dataset_loader import ...` work during the build step.
RUN PYTHONPATH=/app python scripts/build_ann_index.py --references resources/references.json.gz --output resources/references.ann --labels-output resources/reference_labels.npy --trees 50

# stage 2 -  final lightweight runtime image
FROM python:3.13-slim

WORKDIR /app

# copy the environment from the builder (this acts as a squashed layer)
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# copy application source code last
COPY . /app/

# copy prebuilt Annoy index and labels from builder stage (if present)
COPY --from=builder /app/resources/references.ann /app/resources/references.ann
COPY --from=builder /app/resources/reference_labels.npy /app/resources/reference_labels.npy

# fixed the path to main.py relative to WORKDIR
CMD ["fastapi", "run", "app/main.py", "--port", "80"]
