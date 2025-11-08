FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt setup.py ./
COPY storage.py schemas.py search.py content_tools.py server.py server_http.py app.py ./

# Install Python dependencies
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir -r requirements.txt

# Create storage directory
RUN mkdir -p /root/.mcp_snippets

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Set environment variables
ENV MCP_HTTP_HOST=0.0.0.0
ENV MCP_HTTP_PORT=8000
ENV MCP_SNIPPETS_ROOT=/root/.mcp_snippets

# Run the server
CMD ["python", "server_http.py"]
