# TA Engine — Full System PRD

## Project Overview
TA Engine - fund-grade decision-driven trading system with prediction engine, execution simulation, portfolio backtesting, risk management, multi-asset scaling, self-calibrating layer, controlled adaptive execution, policy guards, audit/rollback, Entry Timing Stack including Microstructure validation, and **Trading Terminal with Unified State Orchestrator**.

## Current Version: Phase T2 Complete

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRADING TERMINAL UI                       │
│                      /trading page                           │
│    ┌──────────────────────────────────────────────────┐     │
│    │        GET /api/terminal/state/{symbol}          │     │
│    │            SINGLE SOURCE OF TRUTH                │     │
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
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              INTERNAL SERVICES (RAW APIs)                    │
│  UI NEVER calls these directly - only orchestrator          │
├─────────────────────────────────────────────────────────────┤
│ /api/accounts/*     │ TR1 Account Manager      │ 12 endpoints│
│ /api/trades/*       │ TR3 Trade Monitor        │ 15 endpoints│
│ /api/risk/*         │ TR4 Risk Dashboard       │ 14 endpoints│
│ /api/control/*      │ TR5 Strategy Control     │ 18 endpoints│
│ /api/dashboard/*    │ TR6 Dashboard            │ 11 endpoints│
│ /api/reconciliation/*│ State Reconciliation    │ 15 endpoints│
│ /api/ops/capital/*  │ Capital Operations       │ 12 endpoints│
│ /api/ops/forensics/*│ Trade Forensics          │ 11 endpoints│
│ /api/ops/lifecycle/*│ Position Lifecycle       │ 10 endpoints│
│ /api/ops/positions/*│ Position Manager         │ 15 endpoints│
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  CORE TRADING STACK                          │
├─────────────────────────────────────────────────────────────┤
│  Entry Timing Stack (4.1-4.8.4) - COMPLETE                  │
│  Prediction Engine V2 - COMPLETE                            │
│  Portfolio/Risk/Adaptive - COMPLETE                         │
│  Live Microstructure (5.1) - COMPLETE (mock due to geo)     │
└─────────────────────────────────────────────────────────────┘
```

## What's Been Implemented

### 2026-04-02: Phase T2 — Terminal State Orchestrator (COMPLETE)

**Architecture Decision:**
- Frontend calls ONLY `/api/terminal/state/{symbol}`
- All other terminal APIs are INTERNAL
- Single source of truth for UI

**Files Created:**
```
/app/backend/modules/trading_terminal/terminal_state/
├── __init__.py
├── terminal_state_engine.py   # Unified orchestrator
└── terminal_state_routes.py   # Single API endpoint
```

**Unified State Response:**
```json
{
  "symbol": "BTCUSDT",
  "timestamp": "2026-04-02T17:15:00Z",
  "decision": {
    "action": "WAIT_MICRO",
    "confidence": 0.50,
    "direction": "NEUTRAL",
    "mode": "PASSIVE_LIMIT",
    "reasons": ["Using simulated data", "Waiting for confirmation"]
  },
  "execution": {
    "mode": "AGGRESSIVE",
    "size": 1.13,
    "entry": 65238.17,
    "stop": 63933.41,
    "target": 67521.51,
    "rr": 1.75,
    "execution_confidence": 0.88
  },
  "micro": {
    "source": "mock",
    "imbalance": -0.248,
    "spread": 1.83,
    "liquidity": "balanced",
    "state": "caution",
    "decision": "MICRO_CAUTION",
    "reasons": ["Waiting for confirmation"]
  },
  "position": {...},
  "portfolio": {...},
  "risk": {...},
  "strategy": {...},
  "system": {...}
}
```

**Frontend Refactored:**
- Single fetch to `/api/terminal/state/{symbol}`
- All blocks populated from unified response
- 3-second auto-refresh
- Symbol switcher

### Previous Phases (Completed)
- Phase 5.1: Live Microstructure (WebSocket + REST + Mock fallback)
- Phase 4.1-4.8.4: Entry Timing Stack
- Phase 3.1-3.4: Action Engine, Policy Guard, Audit/Rollback, Scheduler
- Phase 2.1-2.9: Prediction V2, Trade Setup, Execution, Portfolio, Risk, Calibration

## Registered Routes Summary

| Category | Routes | Endpoints | Status |
|----------|--------|-----------|--------|
| Terminal State | `/api/terminal/state/*` | 5 | ✅ UNIFIED API |
| Terminal Live | `/api/terminal/*` | 8 | ✅ Internal |
| Accounts | `/api/accounts/*` | 12 | ✅ Internal |
| Trades | `/api/trades/*` | 15 | ✅ Internal |
| Risk | `/api/risk/*` | 14 | ✅ Internal |
| Control | `/api/control/*` | 18 | ✅ Internal |
| Dashboard | `/api/dashboard/*` | 11 | ✅ Internal |
| Reconciliation | `/api/reconciliation/*` | 15 | ✅ Internal |
| Ops Capital | `/api/ops/capital/*` | 12 | ✅ Internal |
| Ops Forensics | `/api/ops/forensics/*` | 11 | ✅ Internal |
| Ops Lifecycle | `/api/ops/lifecycle/*` | 10 | ✅ Internal |
| Ops Positions | `/api/ops/positions/*` | 15 | ✅ Internal |
| Entry Timing | `/api/entry-timing/*` | ~40 | ✅ Core |
| Prediction | `/api/prediction/*` | 15 | ✅ Core |
| Portfolio | `/api/portfolio/*` | 10 | ✅ Core |

**Total: 200+ endpoints registered**

## Test Results
- Phase T2: Backend 100%, Frontend 100%, Integration 100%
- All 16 test cases passed

## Key Architecture Principles

### 1. Single Source of Truth
```
Frontend → /api/terminal/state/{symbol} → Orchestrator → Internal Services
```

### 2. Internal vs External APIs
- **External (UI calls):** Only `/api/terminal/state/*`
- **Internal (orchestrator calls):** All other terminal APIs

### 3. No Direct Service Calls
```
❌ Frontend → /api/risk/metrics
❌ Frontend → /api/positions/*
❌ Frontend → /api/decision/*

✅ Frontend → /api/terminal/state/{symbol}
```

## Prioritized Backlog

### P0 (Next Immediate)
1. **TradingView Chart Integration** - Embed real chart in Terminal
2. **Bind real services to orchestrator** - Connect risk/portfolio/positions

### P1 Priority
1. Deploy to non-restricted region for live Binance data
2. WebSocket push instead of polling
3. Real execution integration

### P2 Priority
1. Trading history view
2. Export/share functionality
3. Mobile responsiveness

## Tech Stack
- Backend: FastAPI + Python + aiohttp
- Database: MongoDB
- Frontend: React + Tailwind CSS
- Data: Binance API (mock due to geo-restriction)

---
*Last Updated: 2026-04-02*
*Phase T2 Terminal State Orchestrator COMPLETE*
