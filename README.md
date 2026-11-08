# Reproducible checkout error

This is a real FastAPI application with a deliberate division-by-zero bug. It
exports an actual error span (including stack trace and code location) through OTLP
HTTP. It does not start or require a local observability stack; use SigNoz Cloud or
an existing collector.

From this repository root:

```bash
python3.12 -m venv /tmp/sherlock-checkout-venv
/tmp/sherlock-checkout-venv/bin/pip install -r examples/checkout/requirements.txt
# Set these for YOUR collector; do not commit the ingestion key.
export OTEL_EXPORTER_OTLP_ENDPOINT=https://ingest.YOUR-REGION.signoz.cloud:443
export OTEL_EXPORTER_OTLP_HEADERS='signoz-ingestion-key=YOUR_INGESTION_KEY'
# After committing and publishing this example to your GitHub repository:
export DEPLOYED_COMMIT=$(git rev-parse HEAD)
/tmp/sherlock-checkout-venv/bin/uvicorn examples.checkout.app:app --port 8200
```

In another terminal:

```bash
curl -i 'http://localhost:8200/checkout?quantity=2'  # 200, unit_price 60
curl -i 'http://localhost:8200/checkout?quantity=0'  # intentional 500
```

Wait a few seconds for export and ingestion. In SigNoz, find the
`sherlock-checkout` service and its error span. In Sherlock Live Mode enter the
GitHub URL containing this exact committed example and service `sherlock-checkout`.
Load errors, select the failed checkout trace, then investigate.

This repository is the deliberately faulty target for Sherlock, not the debugging assistant itself.

The expected diagnosis is the unchecked division in `unit_price`. A possible fix
is a positive-integer constraint on quantity, plus regression tests for zero,
negative and positive values. Sherlock suggests changes; it never applies them.
The example intentionally retains the bug for reproducibility.

If using a local collector, set `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318`
and omit the headers if your collector does not require authentication. The
SigNoz **query API key** used by Sherlock and **ingestion key** used by this example
are different credentials. Merely setting DEPLOYED_COMMIT does not publish code;
GitHub must already contain that commit. Never label uncommitted changes as a
verified deployment revision.
