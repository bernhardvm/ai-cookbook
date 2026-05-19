import logging
from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
# FIX: Import SimpleSpanProcessor for instant delivery
from opentelemetry.sdk.trace.export import SimpleSpanProcessor 
from opentelemetry.sdk._logs.export import SimpleLogRecordProcessor # Add this import

def configure_aspire_dashboard(endpoint: str, service_name: str = "addition-mcp"):
    resource = Resource.create({"service.name": service_name})

    # 1. Traces (Instant)
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(SimpleSpanProcessor(
        OTLPSpanExporter(endpoint=endpoint, insecure=True)
    ))
    trace.set_tracer_provider(tracer_provider)

    # 2. Metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=endpoint, insecure=True)
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # 3. Logs -> FIX: Change BatchLogRecordProcessor to SimpleLogRecordProcessor
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(SimpleLogRecordProcessor(
        OTLPLogExporter(endpoint=endpoint, insecure=True)
    ))
    set_logger_provider(logger_provider)

    # Hook it globally to the root logger at INFO level
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO) 
    
    if not any(isinstance(h, LoggingHandler) for h in root_logger.handlers):
        handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
        root_logger.addHandler(handler)
