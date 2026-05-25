# stage 1 - stable production base image
FROM python:3.13-slim AS builder

WORKDIR /app

# leverage Docker layer caching for dependencies
COPY ./requirements.txt /app/requirements.txt

# install packages into a local virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# use buildkit cache mounts instead of losing the cache via --no-cache-dir
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade -r /app/requirements.txt

# stage 2 -  final lightweight runtime image
FROM python:3.13-slim

WORKDIR /app

# copy the environment from the builder (this acts as a squashed layer)
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# copy application source code last
COPY . /app/

# fixed the path to main.py relative to WORKDIR
CMD ["fastapi", "run", "app/main.py", "--port", "80"]
