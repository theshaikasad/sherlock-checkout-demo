"""A deliberate division-by-zero bug for investigating with Sherlock."""
import os
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

provider = TracerProvider(resource=Resource.create({
    'service.name': 'sherlock-checkout',
    'service.version': os.getenv('DEPLOYED_COMMIT', 'local'),
}))
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer('checkout')
app = FastAPI()


def unit_price(total: float, quantity: int):
    return total / quantity


@app.get('/checkout')
def checkout(quantity: int = 0):
    with tracer.start_as_current_span('checkout') as span:
        try:
            return {'unit_price': unit_price(120, quantity)}
        except ZeroDivisionError as error:
            import traceback
            span.set_attribute('exception.type', type(error).__name__)
            span.set_attribute('exception.message', str(error))
            span.set_attribute('exception.stacktrace', traceback.format_exc())
            span.set_attribute('code.file.path', 'examples/checkout/app.py')
            span.set_attribute('code.line.number', 21)
            raise
