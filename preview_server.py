"""Emergent preview entrypoint: serves the AegisPay Orchestrator API + AG Grid
dashboard on a single origin (port 3000) so it is viewable at the preview URL."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "aegispay-system"))

from orchestrator_agent.agent import app  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

# Explicit API routes are already registered on `app`; mounting static at "/"
# only serves paths that don't match an existing route (dashboard HTML/JS/CSS).
app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "dashboard"), html=True), name="dashboard")
