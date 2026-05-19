import logging
import os
from dotenv import load_dotenv

# 1. Load env and setup OpenTelemetry BEFORE importing or initializing FastMCP
load_dotenv("../.env")
from otel_aspire import configure_aspire_dashboard

otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
configure_aspire_dashboard(endpoint=otlp_endpoint, service_name="calculator-mcp")

# 2. Now import FastMCP
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create the MCP server
mcp = FastMCP(
    name="Calculator",
    host="0.0.0.0",
    port=3001,
    stateless_http=True,
)

# Add your tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    logger.info(f"Calculator tool executing: adding {a} + {b}")
    return a + b

if __name__ == "__main__":
    logger.info("MCP server starting (HTTP mode on port 3001)")
    mcp.run(transport="streamable-http")
    logger.info("end process")