"""
Terminal State Routes - Unified API for Trading Terminal

This is THE ONLY endpoint the /trading UI should call.
All other terminal APIs are INTERNAL.

Endpoints:
- GET /api/terminal/state/{symbol} - Full terminal state
- GET /api/terminal/state/{symbol}/health - Health check
- GET /api/terminal/state/{symbol}/decision - Decision only
- GET /api/terminal/state/{symbol}/micro - Microstructure only
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import Optional

from .terminal_state_engine import get_terminal_engine

router = APIRouter(prefix="/api/terminal/state", tags=["Terminal State Orchestrator"])


@router.get("/health")
async def state_orchestrator_health():
    """Health check for terminal state orchestrator"""
    return {
        "ok": True,
        "module": "terminal_state_orchestrator",
        "version": "1.0",
        "description": "Unified Trading Terminal API",
        "usage": "GET /api/terminal/state/{symbol}",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/{symbol}")
async def get_terminal_state(symbol: str):
    """
    GET UNIFIED TERMINAL STATE
    
    This is THE endpoint for /trading UI.
    Returns ALL data needed for the terminal in ONE call.
    
    Response includes:
    - decision: action, confidence, direction, mode, reasons
    - execution: mode, size, entry, stop, target, rr
    - micro: imbalance, spread, liquidity, state
    - position: current position for symbol
    - portfolio: equity, exposure, risk
    - risk: heat, drawdown, status, alerts
    - strategy: profile, paused, override
    - system: mode, adaptive, scheduler
    """
    symbol = symbol.upper()
    
    engine = get_terminal_engine()
    state = await engine.get_terminal_state(symbol)
    
    return {
        "ok": True,
        "data": state
    }


@router.get("/{symbol}/decision")
async def get_decision_only(symbol: str):
    """Get decision block only (lighter endpoint)"""
    symbol = symbol.upper()
    
    engine = get_terminal_engine()
    state = await engine.get_terminal_state(symbol)
    
    return {
        "ok": True,
        "symbol": symbol,
        "timestamp": state.get("timestamp"),
        "decision": state.get("decision"),
        "execution": state.get("execution")
    }


@router.get("/{symbol}/micro")
async def get_micro_only(symbol: str):
    """Get microstructure block only (lighter endpoint)"""
    symbol = symbol.upper()
    
    engine = get_terminal_engine()
    state = await engine.get_terminal_state(symbol)
    
    return {
        "ok": True,
        "symbol": symbol,
        "timestamp": state.get("timestamp"),
        "micro": state.get("micro")
    }


@router.get("/{symbol}/position")
async def get_position_only(symbol: str):
    """Get position block only"""
    symbol = symbol.upper()
    
    engine = get_terminal_engine()
    state = await engine.get_terminal_state(symbol)
    
    return {
        "ok": True,
        "symbol": symbol,
        "timestamp": state.get("timestamp"),
        "position": state.get("position"),
        "portfolio": state.get("portfolio")
    }


@router.get("/{symbol}/risk")
async def get_risk_only(symbol: str):
    """Get risk block only"""
    symbol = symbol.upper()
    
    engine = get_terminal_engine()
    state = await engine.get_terminal_state(symbol)
    
    return {
        "ok": True,
        "symbol": symbol,
        "timestamp": state.get("timestamp"),
        "risk": state.get("risk"),
        "strategy": state.get("strategy")
    }
