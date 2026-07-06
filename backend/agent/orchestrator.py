# backend/agent/orchestrator.py
"""
InnerVoice v4.0 — Orchestrator shim
This module is kept for backward compatibility.
All orchestration logic now lives in backend/agent/reasoning_loop.py.
"""
import logging
logger = logging.getLogger(__name__)
logger.info("orchestrator.py loaded — orchestration delegated to reasoning_loop.py")
