import os
from datetime import datetime
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route
from server import mcp
from storage import get_all_content_count

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


def get_public_url():
    """Get the public URL for this server."""
    # Check if we're in GitHub Codespaces
    codespace_name = os.environ.get("CODESPACE_NAME")
    port_forwarding_domain = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN")
    
    if codespace_name and port_forwarding_domain:
        return f"https://{codespace_name}-8000.{port_forwarding_domain}"
    
    # Check if we're in Gitpod
    gitpod_workspace_url = os.environ.get("GITPOD_WORKSPACE_URL")
    if gitpod_workspace_url:
        workspace_url = gitpod_workspace_url.replace("https://", "")
        return f"https://8000-{workspace_url}"
    
    # Default to localhost
    return "http://localhost:8000"


async def homepage(request):
    """Friendly landing page for the MCP Content Library."""
    base_url = get_public_url()
    mcp_endpoint = f"{base_url}/mcp"
    
    # Count stored content
    try:
        content_count = get_all_content_count()
    except:
        content_count = 0
    
    # Get available tools from the MCP server
    tool_count = len(mcp._tools) if hasattr(mcp, '_tools') else 23
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MCP Content Library</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 800px;
                width: 100%;
                padding: 40px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 40px;
            }}
            .logo {{
                font-size: 60px;
                margin-bottom: 10px;
            }}
            h1 {{
                color: #667eea;
                font-size: 32px;
                margin-bottom: 10px;
            }}
            .subtitle {{
                color: #666;
                font-size: 16px;
            }}
            .status {{
                background: #f0fdf4;
                border: 2px solid #86efac;
                border-radius: 12px;
                padding: 20px;
                margin: 30px 0;
            }}
            .status-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 0;
                border-bottom: 1px solid #d1fae5;
            }}
            .status-item:last-child {{
                border-bottom: none;
            }}
            .status-label {{
                font-weight: 600;
                color: #166534;
            }}
            .status-value {{
                color: #15803d;
                font-family: 'Courier New', monospace;
            }}
            .section {{
                margin: 30px 0;
            }}
            .section-title {{
                font-size: 20px;
                font-weight: 600;
                color: #667eea;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .endpoint {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                font-family: 'Courier New', monospace;
                font-size: 14px;
            }}
            .endpoint-label {{
                color: #64748b;
                font-size: 12px;
                margin-bottom: 5px;
            }}
            .endpoint-url {{
                color: #667eea;
                word-break: break-all;
            }}
            .endpoint-url:hover {{
                text-decoration: underline;
            }}
            .quick-start {{
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .code-block {{
                background: #1e293b;
                color: #e2e8f0;
                padding: 15px;
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                overflow-x: auto;
                margin: 10px 0;
            }}
            .cli-section {{
                background: #f1f5f9;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
            }}
            .cli-title {{
                font-weight: 600;
                color: #475569;
                margin-bottom: 8px;
            }}
            .cli-command {{
                background: #1e293b;
                color: #86efac;
                padding: 10px;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                margin: 5px 0;
            }}
            .badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }}
            .badge-success {{
                background: #86efac;
                color: #166534;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e2e8f0;
                color: #64748b;
                font-size: 14px;
            }}
            a {{
                color: #667eea;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">📚</div>
                <h1>MCP Content Library</h1>
                <p class="subtitle">AI-Powered Content Management & Snippet Organization</p>
            </div>

            <div class="status">
                <div class="status-item">
                    <span class="status-label">🟢 Server Status</span>
                    <span class="badge badge-success">ONLINE</span>
                </div>
                <div class="status-item">
                    <span class="status-label">🔧 Available Tools</span>
                    <span class="status-value">{tool_count} tools</span>
                </div>
                <div class="status-item">
                    <span class="status-label">📦 Stored Content</span>
                    <span class="status-value">{content_count} items</span>
                </div>
                <div class="status-item">
                    <span class="status-label">⏰ Server Time</span>
                    <span class="status-value">{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</span>
                </div>
            </div>

            <div class="section">
                <div class="section-title">🔌 API Endpoints</div>
                <div class="endpoint">
                    <div class="endpoint-label">MCP Protocol Endpoint</div>
                    <a href="{mcp_endpoint}" class="endpoint-url">{mcp_endpoint}</a>
                </div>
                <div class="endpoint">
                    <div class="endpoint-label">Health Check</div>
                    <a href="/health" class="endpoint-url">{base_url}/health</a>
                </div>
            </div>

            <div class="section">
                <div class="section-title">🚀 Quick Start</div>
                <div class="quick-start">
                    <p style="margin-bottom: 15px; font-weight: 600;">Connect this server to your AI clients:</p>
                    
                    <div class="cli-section">
                        <div class="cli-title">Claude CLI</div>
                        <div class="cli-command">export CLAUDE_MCP_CONFIG=.claude/mcp_config.json</div>
                        <div class="cli-command">claude chat</div>
                    </div>

                    <div class="cli-section">
                        <div class="cli-title">Claude Desktop / VS Code</div>
                        <p style="font-size: 13px; color: #64748b; margin: 5px 0;">Add to your MCP config file:</p>
                        <div class="code-block">{{"mcpServers": {{"content-library": {{"type": "http", "url": "{mcp_endpoint}"}}}}}}</div>
                    </div>

                    <div class="cli-section">
                        <div class="cli-title">OpenAI Codex</div>
                        <div class="cli-command">pip install openai</div>
                        <div class="cli-command">export OPENAI_API_KEY='your-key'</div>
                        <p style="font-size: 12px; color: #64748b; margin-top: 8px;">
                            <a href="https://platform.openai.com/docs/guides/code" target="_blank">📖 OpenAI Docs</a>
                        </p>
                    </div>

                    <div class="cli-section">
                        <div class="cli-title">Qwen2.5-Coder (OpenCode)</div>
                        <div class="cli-command">pip install transformers torch</div>
                        <p style="font-size: 12px; color: #64748b; margin-top: 8px;">
                            <a href="https://github.com/QwenLM/Qwen2.5-Coder" target="_blank">📖 GitHub Repo</a>
                        </p>
                    </div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">📖 Documentation</div>
                <p style="margin: 10px 0;">
                    • <a href="https://github.com/check-the-vibe/mcp-content-library/blob/main/README.md">README.md</a><br>
                    • <a href="https://github.com/check-the-vibe/mcp-content-library/blob/main/CLAUDE.md">CLAUDE.md - Complete Guide</a><br>
                    • <a href="https://github.com/check-the-vibe/mcp-content-library">GitHub Repository</a>
                </p>
            </div>

            <div class="footer">
                <p>MCP Content Library • Open Source • MIT License</p>
                <p style="margin-top: 5px;">Made with ❤️ for AI-assisted writing</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


async def health_check(request):
    """Health check endpoint for monitoring."""
    try:
        content_count = get_all_content_count()
    except:
        content_count = 0
    
    return JSONResponse({
        "status": "healthy",
        "service": "mcp-content-library",
        "timestamp": datetime.utcnow().isoformat(),
        "mcp_endpoint": f"{get_public_url()}/mcp",
        "tools_available": len(mcp._tools) if hasattr(mcp, '_tools') else 23,
        "content_items": content_count
    })


# Add custom routes to the app
app.add_route("/", homepage, methods=["GET"])
app.add_route("/health", health_check, methods=["GET"])
