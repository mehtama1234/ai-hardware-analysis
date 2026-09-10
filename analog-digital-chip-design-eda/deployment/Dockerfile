FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends iverilog verilator yosys \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY deployment/requirements.txt /tmp/verification-requirements.txt
RUN pip install --no-cache-dir -r /tmp/verification-requirements.txt
COPY . /app

# The service only needs write access to runtime artifacts; keep the source
# tree and simulator toolchain owned by a dedicated unprivileged user.
RUN useradd --create-home --uid 10001 verification \
    && mkdir -p /app/.artifacts \
    && chown -R verification:verification /app/.artifacts
USER verification

ENV PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["uvicorn", "deployment.verification_service:app", "--host", "0.0.0.0", "--port", "8080"]
