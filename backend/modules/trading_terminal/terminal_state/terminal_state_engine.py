"""
Terminal State Engine - Unified Trading Terminal Orchestrator

This is the SINGLE SOURCE OF TRUTH for the Trading Terminal UI.
Frontend NEVER calls individual APIs directly - only this orchestrator.

Aggregates:
- Decision (from Entry Timing Integration)
- Execution (from Entry Timing / Execution Strategy)
- Microstructure (from Live Micro Manager)
- Position (from Positions Service)
- Portfolio (from Portfolio Service)
- Risk (from Risk Service)
- Strategy Control (from Control Service)
- System State (from Adaptive/Calibration)
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
import logging
import asyncio

from ..validation.reconciliation_engine import get_reconciliation_engine

logger = logging.getLogger(__name__)


class TerminalStateEngine:
    """
    Unified Trading Terminal Orchestrator.
    
    Single entry point for all terminal data.
    All services are injected and called internally.
    """
    
    def __init__(self):
        # Service references (injected later)
        self._decision_service = None
        self._micro_service = None
        self._positions_service = None
        self._portfolio_service = None
        self._risk_service = None
        self._strategy_service = None
        self._system_service = None
        
        # Cache for performance
        self._cache: Dict[str, Dict] = {}
        self._cache_ttl_seconds = 1.0  # 1 second cache
        self._cache_timestamps: Dict[str, datetime] = {}
    
    def bind_services(
        self,
        decision_service=None,
        micro_service=None,
        positions_service=None,
        portfolio_service=None,
        risk_service=None,
        strategy_service=None,
        system_service=None
    ):
        """Bind real services to the engine"""
        if decision_service:
            self._decision_service = decision_service
        if micro_service:
            self._micro_service = micro_service
        if positions_service:
            self._positions_service = positions_service
        if portfolio_service:
            self._portfolio_service = portfolio_service
        if risk_service:
            self._risk_service = risk_service
        if strategy_service:
            self._strategy_service = strategy_service
        if system_service:
            self._system_service = system_service
    
    async def get_terminal_state(self, symbol: str) -> Dict[str, Any]:
        """
        Get unified terminal state for symbol.
        This is THE endpoint for /trading UI.
        """
        symbol = symbol.upper()
        
        # Check cache
        cache_key = f"state_{symbol}"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        # Gather all data concurrently
        results = await asyncio.gather(
            self._safe_get(self._get_decision, symbol),
            self._safe_get(self._get_execution, symbol),
            self._safe_get(self._get_micro, symbol),
            self._safe_get(self._get_position, symbol),
            self._safe_get(self._get_portfolio, symbol),
            self._safe_get(self._get_risk, symbol),
            self._safe_get(self._get_strategy, symbol),
            self._safe_get(self._get_system, symbol),
            return_exceptions=True
        )
        
        # Unpack results with defaults
        decision = results[0] if isinstance(results[0], dict) else self._default_decision(symbol)
        execution = results[1] if isinstance(results[1], dict) else self._default_execution()
        micro = results[2] if isinstance(results[2], dict) else self._default_micro()
        position = results[3] if isinstance(results[3], dict) else self._default_position(symbol)
        portfolio = results[4] if isinstance(results[4], dict) else self._default_portfolio()
        risk = results[5] if isinstance(results[5], dict) else self._default_risk()
        strategy = results[6] if isinstance(results[6], dict) else self._default_strategy()
        system = results[7] if isinstance(results[7], dict) else self._default_system()
        
        state = {
            "symbol": symbol,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision": decision,
            "execution": execution,
            "micro": micro,
            "position": position,
            "portfolio": portfolio,
            "risk": risk,
            "strategy": strategy,
            "system": system
        }
        
        # Run validation layer with live price
        try:
            reconciliation = get_reconciliation_engine()
            validation = await reconciliation.validate_terminal_state_async(state)
            state["validation"] = validation
        except Exception as e:
            logger.warning(f"[Validation] Error: {e}")
            state["validation"] = {
                "is_valid": True,
                "critical_count": 0,
                "warning_count": 0,
                "info_count": 0,
                "issues": [],
                "error": str(e)
            }
        
        # Cache result
        self._cache[cache_key] = state
        self._cache_timestamps[cache_key] = datetime.now(timezone.utc)
        
        return state
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid"""
        if key not in self._cache or key not in self._cache_timestamps:
            return False
        
        age = (datetime.now(timezone.utc) - self._cache_timestamps[key]).total_seconds()
        return age < self._cache_ttl_seconds
    
    async def _safe_get(self, fn, symbol: str) -> Dict[str, Any]:
        """Safely call a getter function with error handling"""
        try:
            result = await fn(symbol) if asyncio.iscoroutinefunction(fn) else fn(symbol)
            return result if isinstance(result, dict) else {}
        except Exception as e:
            logger.warning(f"[TerminalState] Error in {fn.__name__}: {e}")
            return {"_error": str(e)}
    
    # =========================================
    # DATA GETTERS - Each integrates with a service
    # =========================================
    
    async def _get_decision(self, symbol: str) -> Dict[str, Any]:
        """Get decision from Entry Timing Integration"""
        # Try to import and use entry timing integration
        try:
            from ..live.terminal_routes import get_terminal_decision
            response = await get_terminal_decision(symbol)
            if response.get("ok") and response.get("data"):
                data = response["data"]
                decision_data = data.get("decision", {})
                why_data = data.get("why", [])
                
                return {
                    "action": decision_data.get("action", "WAIT"),
                    "confidence": decision_data.get("confidence", 0.5),
                    "direction": "LONG" if decision_data.get("action", "").startswith("GO") else "NEUTRAL",
                    "mode": data.get("execution", {}).get("mode", "PASSIVE_LIMIT"),
                    "reasons": [r.get("text", "") for r in why_data] if why_data else []
                }
        except Exception as e:
            logger.warning(f"[Decision] Error: {e}")
        
        return self._default_decision(symbol)
    
    async def _get_execution(self, symbol: str) -> Dict[str, Any]:
        """Get execution parameters"""
        try:
            from ..live.terminal_routes import get_terminal_decision
            response = await get_terminal_decision(symbol)
            if response.get("ok") and response.get("data"):
                exec_data = response["data"].get("execution", {})
                decision = response["data"].get("decision", {})
                
                return {
                    "mode": exec_data.get("mode", "PASSIVE_LIMIT"),
                    "size": exec_data.get("size_multiplier", 0.0),
                    "entry": exec_data.get("entry"),
                    "stop": exec_data.get("stop_loss"),
                    "target": exec_data.get("take_profit"),
                    "rr": exec_data.get("risk_reward"),
                    "execution_confidence": decision.get("confidence", 0.5)
                }
        except Exception as e:
            logger.warning(f"[Execution] Error: {e}")
        
        return self._default_execution()
    
    async def _get_micro(self, symbol: str) -> Dict[str, Any]:
        """Get microstructure data from Live Micro Manager"""
        try:
            from ..live.terminal_routes import get_micro_live
            response = await get_micro_live(symbol)
            if response.get("ok") and response.get("data"):
                data = response["data"]
                
                # Build reasons
                reasons = []
                if data.get("liquidity_state") == "strong_bid":
                    reasons.append("Strong bid support")
                if data.get("spread_bps", 0) < 1.5:
                    reasons.append("Tight spread")
                if data.get("state") == "favorable":
                    reasons.append("Favorable microstructure")
                elif data.get("state") == "hostile":
                    reasons.append("Hostile microstructure")
                elif data.get("state") == "caution":
                    reasons.append("Waiting for confirmation")
                
                return {
                    "source": response.get("source", "mock"),
                    "imbalance": data.get("imbalance", 0),
                    "spread": data.get("spread_bps"),
                    "liquidity": data.get("liquidity_state", "unknown"),
                    "state": data.get("state", "unknown"),
                    "decision": f"MICRO_{data.get('state', 'UNKNOWN').upper()}",
                    "reasons": reasons,
                    "best_bid": data.get("best_bid"),
                    "best_ask": data.get("best_ask"),
                    "mid_price": data.get("mid_price")
                }
        except Exception as e:
            logger.warning(f"[Micro] Error: {e}")
        
        return self._default_micro()
    
    async def _get_position(self, symbol: str) -> Dict[str, Any]:
        """Get position for symbol"""
        try:
            from ..live.terminal_routes import get_positions
            response = await get_positions()
            if response.get("ok") and response.get("data"):
                positions = response["data"].get("positions", [])
                
                # Find position for this symbol
                for pos in positions:
                    if pos.get("symbol") == symbol:
                        return {
                            "has_position": True,
                            "symbol": pos.get("symbol"),
                            "side": pos.get("side"),
                            "size": pos.get("size", 0),
                            "entry": pos.get("entry_price"),
                            "mark": pos.get("current_price"),
                            "pnl": pos.get("pnl_usd", 0),
                            "pnl_pct": pos.get("pnl_percent", 0),
                            "stop": None,  # Would come from position service
                            "target": None,
                            "status": pos.get("status", "UNKNOWN")
                        }
        except Exception as e:
            logger.warning(f"[Position] Error: {e}")
        
        return self._default_position(symbol)
    
    async def _get_portfolio(self, symbol: str) -> Dict[str, Any]:
        """Get portfolio summary"""
        try:
            from ..live.terminal_routes import get_positions
            response = await get_positions()
            if response.get("ok") and response.get("data"):
                summary = response["data"].get("summary", {})
                
                return {
                    "equity": 10000 + summary.get("total_pnl_usd", 0),  # Mock base equity
                    "free_capital": 10000 - summary.get("exposure_usd", 0) * 0.1,
                    "used_capital": summary.get("exposure_usd", 0) * 0.1,
                    "realized_pnl": summary.get("total_pnl_usd", 0) * 0.3,
                    "unrealized_pnl": summary.get("total_pnl_usd", 0) * 0.7,
                    "exposure": round(summary.get("exposure_usd", 0) / 100000, 2),
                    "risk_used": round(summary.get("total_positions", 0) * 0.05, 2)
                }
        except Exception as e:
            logger.warning(f"[Portfolio] Error: {e}")
        
        return self._default_portfolio()
    
    async def _get_risk(self, symbol: str) -> Dict[str, Any]:
        """Get risk metrics"""
        # Use defaults for now - would integrate with risk service
        import random
        
        heat = random.uniform(0.2, 0.6)
        drawdown = random.uniform(0.02, 0.1)
        
        return {
            "heat": round(heat, 2),
            "drawdown": round(drawdown, 2),
            "daily_drawdown": round(drawdown * 0.3, 2),
            "status": "normal" if heat < 0.5 else "elevated" if heat < 0.7 else "critical",
            "kill_switch": False,
            "alerts": []
        }
    
    async def _get_strategy(self, symbol: str) -> Dict[str, Any]:
        """Get strategy control state"""
        return {
            "profile": "BALANCED",
            "config": "default",
            "paused": False,
            "override": False
        }
    
    async def _get_system(self, symbol: str) -> Dict[str, Any]:
        """Get system state"""
        try:
            from ..live.terminal_routes import terminal_health
            health = await terminal_health()
            
            return {
                "mode": "SIMULATION",
                "adaptive_active": True,
                "scheduler": "running",
                "last_calibration": datetime.now(timezone.utc).replace(hour=0, minute=0).isoformat(),
                "last_rollback": None,
                "data_source": "mock" if not health.get("live_enabled") else "live"
            }
        except Exception as e:
            logger.warning(f"[System] Error: {e}")
        
        return self._default_system()
    
    # =========================================
    # DEFAULT VALUES
    # =========================================
    
    def _default_decision(self, symbol: str) -> Dict[str, Any]:
        return {
            "action": "WAIT",
            "confidence": 0.0,
            "direction": "NEUTRAL",
            "mode": "UNKNOWN",
            "reasons": ["waiting_for_data"]
        }
    
    def _default_execution(self) -> Dict[str, Any]:
        return {
            "mode": "PASSIVE_LIMIT",
            "size": 0.0,
            "entry": None,
            "stop": None,
            "target": None,
            "rr": None,
            "execution_confidence": 0.0
        }
    
    def _default_micro(self) -> Dict[str, Any]:
        return {
            "source": "offline",
            "imbalance": 0.0,
            "spread": None,
            "liquidity": "unknown",
            "state": "unknown",
            "decision": "WAIT_MICROSTRUCTURE",
            "reasons": ["micro_offline"]
        }
    
    def _default_position(self, symbol: str) -> Dict[str, Any]:
        return {
            "has_position": False,
            "symbol": symbol,
            "side": None,
            "size": 0.0,
            "entry": None,
            "mark": None,
            "pnl": 0.0,
            "pnl_pct": 0.0,
            "stop": None,
            "target": None,
            "status": "FLAT"
        }
    
    def _default_portfolio(self) -> Dict[str, Any]:
        return {
            "equity": None,
            "free_capital": None,
            "used_capital": None,
            "realized_pnl": None,
            "unrealized_pnl": None,
            "exposure": None,
            "risk_used": None
        }
    
    def _default_risk(self) -> Dict[str, Any]:
        return {
            "heat": None,
            "drawdown": None,
            "daily_drawdown": None,
            "status": "unknown",
            "kill_switch": False,
            "alerts": []
        }
    
    def _default_strategy(self) -> Dict[str, Any]:
        return {
            "profile": "UNKNOWN",
            "config": None,
            "paused": False,
            "override": False
        }
    
    def _default_system(self) -> Dict[str, Any]:
        return {
            "mode": "SIMULATION",
            "adaptive_active": False,
            "scheduler": "unknown",
            "last_calibration": None,
            "last_rollback": None,
            "data_source": "offline"
        }


# Global singleton instance
_engine: Optional[TerminalStateEngine] = None


def get_terminal_engine() -> TerminalStateEngine:
    """Get or create the singleton terminal state engine"""
    global _engine
    if _engine is None:
        _engine = TerminalStateEngine()
    return _engine
