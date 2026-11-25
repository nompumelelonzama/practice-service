# ---- Stage 1: builder (has pip and build tooling) ----
FROM python:3.14-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: runtime (only what we need to run) ----
FROM python:3.14-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Patch OS packages (fixes the zlib finding)
RUN apt-get update && apt-get upgrade -y --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd --system --uid 10001 --no-create-home appuser

WORKDIR /app
COPY --from=builder /install /usr/local
COPY main.py ./

# No package manager in the runtime image
RUN pip uninstall -y pip

USER 10001
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]