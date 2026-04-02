# TA Engine — Full System PRD

## Project Overview
TA Engine - fund-grade decision-driven trading system with prediction engine, execution simulation, portfolio backtesting, risk management, multi-asset scaling, self-calibrating layer, controlled adaptive execution, policy guards, audit/rollback, Entry Timing Stack including Microstructure validation, Trading Terminal with Unified State Orchestrator, and **DATA VALIDATION LAYER**.

## Current Version: Phase T3 - Data Validation Layer Complete

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRADING TERMINAL UI                       │
│                      /trading page                           │
│    ┌──────────────────────────────────────────────────┐     │
│    │        GET /api/terminal/state/{symbol}          │     │
│    │            SINGLE SOURCE OF TRUTH                │     │
│    │         + VALIDATION LAYER (NEW)                 │     │
│    └──────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              TERMINAL STATE ORCHESTRATOR                     │
│                  (terminal_state_engine.py)                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │Decision │ │ Micro   │ │Position │ │Portfolio│           │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘           │
│       │           │           │           │                  │
│  ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌────┴────┐           │
│  │  Risk   │ │Strategy │ │ System  │ │Execution│           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│                     ↓                                        │
│  ┌──────────────────────────────────────────────────┐       │
│  │           DATA VALIDATION LAYER (NEW)            │       │
│  │   - Entry vs Market Price Check                  │       │
│  │   - Position vs Symbol Check                     │       │
│  │   - Mock vs Live Source Warning                  │       │
│  │   - Decision Confidence Validation               │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## What's Been Implemented

### 2026-04-02: Phase T3 — Data Validation Layer (COMPLETE)

**New Files Created:**
```
/app/backend/modules/trading_terminal/validation/
├── __init__.py
├── validation_types.py       # ValidationResult, ValidationSeverity
├── data_validator.py         # Core validation logic
└── reconciliation_engine.py  # Aggregates all validations
```

**Validation Checks:**
1. **ENTRY_PRICE_MISMATCH** - Entry deviates >20% from market (CRITICAL)
2. **POSITION_SYMBOL_MISMATCH** - Position symbol != terminal symbol (CRITICAL)
3. **SIMULATION_MODE** - Using mock/simulated data (WARNING)
4. **HIGH_CONFIDENCE_MOCK** - High confidence with simulated data (WARNING)
5. **INVALID_STOP_LEVEL** - Stop > Entry (CRITICAL)
6. **INVALID_TARGET_LEVEL** - Target < Entry (CRITICAL)

**Frontend Updates:**
- ValidationBlock component shows errors/warnings
- Chart now uses Coinbase live data
- Execution overlays (Entry, Stop, Target) visible on chart

**Validation Response:**
```json
{
  "validation": {
    "is_valid": true,
    "critical_count": 0,
    "warning_count": 2,
    "info_count": 3,
    "live_price": 66677.54,
    "price_source": "coinbase",
    "issues": [...]
  }
}
```

### Previous Phases (Completed)
- Phase T2: Terminal State Orchestrator
- Phase 5.1: Live Microstructure (WebSocket + REST + Mock fallback)
- Phase 4.1-4.8.4: Entry Timing Stack
- Phase 3.1-3.4: Action Engine, Policy Guard, Audit/Rollback, Scheduler
- Phase 2.1-2.9: Prediction V2, Trade Setup, Execution, Portfolio, Risk, Calibration

## Test Results
- Phase T3: Backend 100%, Frontend 100%, Integration 100%

## Prioritized Backlog

### P0 (Next Immediate)
1. **Timeframe Selector** - 1H / 4H / 1D for chart and analysis
2. **WebSocket Real-time** - Replace polling with push notifications

### P1 Priority
1. Deploy to non-restricted region for live Binance data
2. Real execution integration
3. Order lifecycle states (pending, filled, partial, cancelled)

### P2 Priority
1. Trading history view
2. Export/share functionality
3. Mobile responsiveness

## Tech Stack
- Backend: FastAPI + Python + aiohttp
- Database: MongoDB
- Frontend: React + Tailwind CSS + lightweight-charts
- Data: Coinbase API (live), Binance API (mock due to geo-restriction)

---
*Last Updated: 2026-04-02*
*Phase T3 Data Validation Layer COMPLETE*
