from setuptools import setup, find_packages

setup(
    name="mcp-content-library",
    version="0.1.0",
    description="MCP server for managing writing snippets and content library",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    py_modules=["server", "storage", "schemas", "search", "content_tools", "app", "server_http"],
    install_requires=[
        "mcp[cli]>=0.1.0",
        "starlette>=0.27.0",
        "uvicorn>=0.23.0",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "mcp-content-server=server:main",
        ],
    },
)
