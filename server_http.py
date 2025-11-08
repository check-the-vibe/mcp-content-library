"""HTTP runner for the MCP Content Library.

This script is deliberately lightweight so systemd, Docker and the
convenience `./start.sh` can invoke it with `python server_http.py`.

It will try to serve the Starlette `app` defined in `app.py` using
uvicorn. If that fails for any reason (uvicorn not installed or the
app module not present) it falls back to calling `mcp.run(...)` which
may be appropriate in some environments.
"""

import os
import traceback

# Preferred path: run the ASGI Starlette app in `app.py` with uvicorn.
try:
    from app import app  # the Starlette app instance
    has_app = True
except Exception:
    has_app = False

try:
    # Try to import uvicorn only when we plan to run it
    import uvicorn  # type: ignore
    has_uvicorn = True
except Exception:
    has_uvicorn = False


def _run_uvicorn():
    host = os.environ.get("MCP_HTTP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_HTTP_PORT", "8000"))
    # Run using the app object if available
    if has_app and has_uvicorn:
        uvicorn.run(app, host=host, port=port, log_level="info")
    elif has_app and not has_uvicorn:
        print("uvicorn is not installed. Install requirements: pip install -r requirements.txt")
        raise RuntimeError("uvicorn not available")
    else:
        raise RuntimeError("ASGI app not available (app.py missing or import failed)")


if __name__ == "__main__":
    # Primary: try to run uvicorn with the Starlette app from app.py.
    try:
        _run_uvicorn()
    except Exception:
        # Fallback: if we can't run uvicorn/app, try to run the MCP-runner
        print("Failed to start uvicorn/app — falling back to mcp.run if available.\n")
        traceback.print_exc()
        try:
            from server import mcp

            print("Attempting fallback: mcp.run(transport='streamable-http')")
            mcp.run(transport="streamable-http")
        except Exception:
            print("Fallback failed. Please ensure uvicorn is installed and app.py is present.")
            traceback.print_exc()
            raise

