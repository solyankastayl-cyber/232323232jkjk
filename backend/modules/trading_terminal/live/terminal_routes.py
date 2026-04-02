"""
Trading Terminal API Routes
Provides live microstructure data and terminal state for the frontend
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import Dict, Optional
import random

from .micro_aggregator import get_mock_micro_data

router = APIRouter(prefix="/api/terminal", tags=["Trading Terminal"])


# Mock terminal state (in production, this would be stored in DB/Redis)
_terminal_state = {
    "authenticated": False,
    "password_hash": "terminal123"  # Simple dev password
}


@router.get("/health")
async def terminal_health():
    """Health check for trading terminal"""
    return {
        "ok": True,
        "module": "trading_terminal",
        "version": "5.1",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/auth")
async def terminal_auth(data: Dict):
    """
    Authenticate access to trading terminal.
    In dev mode, any password works.
    """
    password = data.get("password", "")
    
    # Dev mode: accept any non-empty password
    if password and len(password) >= 4:
        return {
            "ok": True,
            "authenticated": True,
            "message": "Access granted"
        }
    
    return {
        "ok": False,
        "authenticated": False,
        "message": "Invalid password"
    }


@router.get("/micro/live/{symbol}")
async def get_micro_live(symbol: str = "BTCUSDT"):
    """
    Get live microstructure data for symbol.
    Returns imbalance, spread, liquidity state, and overall micro assessment.
    """
    symbol = symbol.upper()
    
    micro = get_mock_micro_data(symbol)
    
    return {
        "ok": True,
        "data": micro
    }


@router.get("/decision/{symbol}")
async def get_terminal_decision(symbol: str = "BTCUSDT"):
    """
    Get integrated trading decision for symbol.
    Combines Entry Timing Stack output with Microstructure assessment.
    """
    symbol = symbol.upper()
    
    # Get microstructure data
    micro = get_mock_micro_data(symbol)
    
    # Mock decision from Entry Timing Stack
    decisions = ["GO_FULL", "GO_REDUCED", "WAIT", "WAIT_MICRO", "SKIP"]
    weights = [0.2, 0.25, 0.3, 0.15, 0.1]  # Realistic distribution
    
    # Adjust based on micro state
    if micro["state"] == "favorable":
        decision = random.choices(["GO_FULL", "GO_REDUCED"], weights=[0.7, 0.3])[0]
        confidence = micro["confidence"]
    elif micro["state"] == "hostile":
        decision = random.choices(["WAIT", "SKIP"], weights=[0.6, 0.4])[0]
        confidence = 0.3
    else:
        decision = random.choices(decisions, weights=weights)[0]
        confidence = random.uniform(0.5, 0.8)
    
    # Generate WHY reasons
    why_reasons = []
    if decision in ["GO_FULL", "GO_REDUCED"]:
        why_reasons = [
            {"text": "HTF aligned (Daily)", "strength": "strong"},
            {"text": "Breakout confirmed", "strength": "strong"},
            {"text": f"Micro: {micro['liquidity_state']}", "strength": "medium" if micro["state"] != "favorable" else "strong"}
        ]
        if micro["imbalance"] > 0.2:
            why_reasons.append({"text": f"Bid imbalance +{micro['imbalance']:.0%}", "strength": "strong"})
    else:
        why_reasons = [
            {"text": "Waiting for confirmation", "strength": "weak"},
            {"text": f"Spread elevated: {micro['spread_bps']:.1f}bps", "strength": "weak"},
        ]
        if micro["state"] == "hostile":
            why_reasons.append({"text": "Hostile microstructure", "strength": "weak"})
    
    # Execution parameters
    if decision == "GO_FULL":
        size_multiplier = round(1.0 + micro["confidence"] * 0.15, 2)
        execution_mode = "AGGRESSIVE"
    elif decision == "GO_REDUCED":
        size_multiplier = round(0.5 + micro["confidence"] * 0.3, 2)
        execution_mode = "NORMAL"
    else:
        size_multiplier = 0.0
        execution_mode = "PASSIVE_LIMIT"
    
    # Mock price levels (based on ~$65000 BTC)
    current_price = 65000 + random.uniform(-500, 500)
    
    return {
        "ok": True,
        "data": {
            "symbol": symbol,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision": {
                "action": decision,
                "confidence": round(confidence, 2)
            },
            "why": why_reasons,
            "execution": {
                "mode": execution_mode,
                "size_multiplier": size_multiplier,
                "entry": round(current_price, 2),
                "stop_loss": round(current_price * 0.98, 2),
                "take_profit": round(current_price * 1.035, 2),
                "risk_reward": 1.75
            },
            "micro": micro
        }
    }


@router.get("/positions")
async def get_positions():
    """
    Get current open positions.
    Mock data for development.
    """
    # Mock positions
    positions = [
        {
            "id": "pos_001",
            "symbol": "BTCUSDT",
            "side": "LONG",
            "size": 0.8,
            "entry_price": 64200.00,
            "current_price": 65100.00,
            "pnl_usd": 720.00,
            "pnl_percent": 1.12,
            "status": "ACTIVE",
            "opened_at": "2026-04-02T10:30:00Z"
        },
        {
            "id": "pos_002", 
            "symbol": "ETHUSDT",
            "side": "LONG",
            "size": 5.0,
            "entry_price": 3450.00,
            "current_price": 3520.00,
            "pnl_usd": 350.00,
            "pnl_percent": 2.03,
            "status": "ACTIVE",
            "opened_at": "2026-04-01T14:15:00Z"
        }
    ]
    
    total_pnl = sum(p["pnl_usd"] for p in positions)
    
    return {
        "ok": True,
        "data": {
            "positions": positions,
            "summary": {
                "total_positions": len(positions),
                "total_pnl_usd": round(total_pnl, 2),
                "exposure_usd": round(sum(p["size"] * p["current_price"] for p in positions), 2)
            }
        }
    }
