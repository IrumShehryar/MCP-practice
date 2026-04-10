# Model Context Protocol (MCP) Practice

This repository is for hands-on learning, demos, and experiments with the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), a standard for passing context and enabling secure/structured LLM integrations.

## What’s in this repo

- **`mcp-remote-demo/`**
  - Contains a Python virtual environment and installed MCP packages (such as `mcp`, `pywin32`, `adodbapi`, and others).
  - Vendor code includes examples and class implementations for MCP servers and clients, protocol features, and authentication. (See the `mcp/server`, `mcp/client`, and related modules under `.venv/Lib/site-packages/mcp/`.)
  - You will find code for:
    - Setting up & running MCP servers (see classes like `FastMCP` and modules such as `session.py` and `request_context.py`).
    - Handling server-to-client and client-to-server requests, task management, protocol versioning, and authentication.
    - Experimental MCP request context and task support, validation helpers, and sample protocol implementations.

- **`weather/`**
  - Minimal Python project that declares a dependency on `mcp[cli]` and `httpx` in its `pyproject.toml`.
  - Serves as an example of installing and using the MCP library in a new project.

## What has been done

- The repo demonstrates:
  - Installation and local experimentation with the official MCP Python library and ecosystem tools.
  - Bootstrapping MCP-enabled Python environments for running example servers, exploring client APIs, and experimenting with MCP authentication and session handling.
  - Code review and exploration of internals, including examples of custom *request contexts*, *task handling*, and official [core MCP concepts](https://modelcontextprotocol.io/).

- No custom, user-authored (non-vendor) code implementing MCP protocol servers, resources, or tools was found here—the work focuses on integrating, running, and sandboxing existing MCP Python packages and examples.

## How to try it out

1. Navigate to `weather/` or `mcp-remote-demo/`.
2. Use your preferred Python environment. The MCP package is already listed as a dependency.
3. Review vendor code and examples in `.venv/Lib/site-packages/mcp/` for extensibility tips and hands-on protocol reference.

## References

- [MCP Documentation](https://modelcontextprotocol.io/)
- Python MCP package: https://github.com/modelcontextprotocol/python-sdk

---

**Note:** Most code under `mcp-remote-demo/.venv/Lib/site-packages/` is vendor code from installed MCP and related Python packages. For specifics, see the [mcp/server/experimental/request_context.py source](https://github.com/IrumShehryar/MCP-practice/blob/main/mcp-remote-demo/.venv/Lib/site-packages/mcp/server/experimental/request_context.py).

_Last updated: 2026-04-10. [More README/search](#)_
