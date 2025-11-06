from starlette.middleware.cors import CORSMiddleware
from server import mcp

# Use the MCP-provided Starlette app directly so its lifespan handlers run and
# the StreamableHTTP session manager is initialized on startup.
app = mcp.streamable_http_app()

# Ensure CORS allows OPTIONS preflight and exposes MCP session header
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)
