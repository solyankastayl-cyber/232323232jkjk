# TA Engine — Full System PRD

## Project Overview
TA Engine - fund-grade decision-driven trading system with prediction engine, execution simulation, portfolio backtesting, risk management, multi-asset scaling, self-calibrating layer, controlled adaptive execution, policy guards, audit/rollback, Entry Timing Stack including Microstructure validation, Trading Terminal with Unified State Orchestrator, DATA VALIDATION LAYER, and **TIMEFRAME SELECTOR**.

## Current Version: Phase T4 - Timeframe Selector Complete

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRADING TERMINAL UI                       │
│    ┌────────────────────────────────────────────────────┐   │
│    │     TIMEFRAME: [ 1H ] [ 4H ] [ 1D ]                │   │
│    └────────────────────────────────────────────────────┘   │
│    ┌────────────────────────────────────────────────────┐   │
│    │   GET /api/terminal/state/{symbol}?timeframe=4H    │   │
│    │                SINGLE SOURCE OF TRUTH              │   │
│    │        + VALIDATION + TIMEFRAME AWARENESS          │   │
│    └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              TERMINAL STATE ORCHESTRATOR                     │
│              (all components get timeframe)                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │Decision │ │ Candles │ │Execution│ │Validation│           │
│  │   TF    │ │   TF    │ │   TF    │ │   TF    │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## What's Been Implemented

### 2026-04-02: Phase T4 — Timeframe Selector (COMPLETE)

**Backend Changes:**
- `terminal_state_engine.py`: Added timeframe as system parameter
- `terminal_state_routes.py`: Added `?timeframe=` query param
- `data_validator.py`: Added `validate_timeframe_consistency()`
- `reconciliation_engine.py`: Timeframe in validation response

**Frontend Changes:**
- `TradingTerminal.jsx`: Timeframe state, selector UI, badge in header
- `TradingChart.jsx`: Timeframe-aware candle fetching

**Timeframe Mapping (Coinbase):**
- 1H → 1h (168 candles = 7 days)
- 4H → 6h (120 candles = 30 days) *closest available*
- 1D → 1d (90 candles = 90 days)

**API:**
```
GET /api/terminal/state/BTCUSDT?timeframe=1H
GET /api/terminal/state/BTCUSDT?timeframe=4H (default)
GET /api/terminal/state/BTCUSDT?timeframe=1D
```

**Response includes:**
```json
{
  "timeframe": "4H",
  "execution": { "timeframe": "4H", ... },
  "validation": { "timeframe": "4H", ... }
}
```

### 2026-04-02: Phase T3 — Data Validation Layer (COMPLETE)
- Entry vs Market price check (20% threshold)
- Position vs Symbol check
- Mock data warnings
- Timeframe consistency validation

### Previous Phases (Completed)
- Phase T2: Terminal State Orchestrator
- Phase 5.1: Live Microstructure
- Phase 4.1-4.8.4: Entry Timing Stack
- Phase 3.1-3.4: Action Engine, Policy Guard, Audit/Rollback
- Phase 2.1-2.9: Prediction V2, Execution, Portfolio, Risk

## Test Results
- Phase T4: Backend 100%, Frontend 95%

## Prioritized Backlog

### P0 (Next Immediate)
1. **WebSocket Real-time** - Replace 3s polling with push
2. **Alert System** - Price near entry, validation errors, decision changes

### P1 Priority
1. MTF (Multi-Timeframe) analysis layer
2. Order lifecycle states
3. Real execution integration

### P2 Priority
1. Trading history view
2. Export/share functionality

## Tech Stack
- Backend: FastAPI + Python + aiohttp
- Database: MongoDB
- Frontend: React + Tailwind CSS + lightweight-charts
- Data: Coinbase API (live)

---
*Last Updated: 2026-04-02*
*Phase T4 Timeframe Selector COMPLETE*
