"""Expose the existing /api integration routes on the platform API service.

The dashboard and its SSE stream retain their existing single-origin entrypoint.
No duplicate application logic or provider credentials are introduced here.
"""
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
sys.path.insert(0, str(ROOT / 'aegispay-system'))

from orchestrator_agent.agent import app  # noqa: E402, F401