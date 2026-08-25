"""Pytest fixtures for AI Store Associate Brain Testing."""

import importlib.util
import sys
from pathlib import Path

# Add backend directories to python path
root_path = Path(__file__).resolve().parent.parent.parent
agent_backend_path = root_path / "agent-backend"
demo_backend_path = root_path / "demo-store" / "backend"

for p in [agent_backend_path, demo_backend_path]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from agent_app.graph.builder import shopagent_app

# Explicitly load agent-backend main app
spec = importlib.util.spec_from_file_location("agent_main", agent_backend_path / "main.py")
agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_module)
agent_app_instance = agent_module.app


@pytest_asyncio.fixture
async def agent_client() -> AsyncClient:
    """Async client for agent-backend API."""
    transport = ASGITransport(app=agent_app_instance)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
