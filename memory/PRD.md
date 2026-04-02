# TA Engine — Full System PRD

## Project Overview
TA Engine - fund-grade decision-driven trading system с prediction engine, execution simulation, portfolio backtesting, risk management, multi-asset scaling, self-calibrating layer, controlled adaptive execution, policy guards, audit/rollback, и полный Entry Timing Stack включая Microstructure validation.

## System Architecture (Production Pipeline)

```
TA Intelligence + Fractal + Exchange Intelligence
                    ↓
        Prediction Engine V2 (WHAT)
                    ↓
        Trade Setup Generator
                    ↓
    ┌───────────────────────────────┐
    │    ENTRY TIMING STACK         │
    │                               │
    │  Entry Mode Selector (4.2)    │
    │         ↓                     │
    │  Execution Strategy (4.3)     │
    │         ↓                     │
    │  Entry Quality Score (4.4)    │
    │         ↓                     │
    │  MTF Layer (4.7)              │
    │    HTF (1D) permission        │
    │    MTF (4H) signal            │
    │    LTF (1H) timing            │
    │         ↓                     │
    │  Microstructure Entry (4.8)   │
    │    Liquidity risk             │
    │    Orderbook imbalance        │
    │    Absorption detection       │
    │    Sweep risk                 │
    │         ↓                     │
    │  Micro Weighting (4.8.3)      │
    │    Size multiplier            │
    │    Confidence modifier        │
    │    Execution modifier         │
    │         ↓                     │
    │  Final Integration (4.8.1)    │
    │    GO_FULL / GO_REDUCED /     │
    │    WAIT / WAIT_MICRO / SKIP   │
    └───────────────────────────────┘
                    ↓
        Execution Simulator (HOW)
                    ↓
        Portfolio Backtester
                    ↓
        Risk Metrics (HOW MUCH)
                    ↓
        Adaptive Layer (EVOLUTION)
```

## What's Been Implemented

### 2026-04-02: Phase 5.1 — Trading Terminal MVP
- **NEW:** Isolated Trading Terminal at `/trading` route
- **Password Gate:** Authentication layer (dev mode bypass)
- **UI Blocks:**
  - Decision Block (GO_FULL/GO_REDUCED/WAIT/SKIP + confidence)
  - Why Block (reasoning with strength badges)
  - Execution Block (mode, size, entry/SL/TP, R:R)
  - Microstructure Block (imbalance, spread, liquidity, state)
  - Positions Block (active trades with PnL)
- **Backend APIs:**
  - `/api/terminal/health` - Terminal health check
  - `/api/terminal/auth` - Authentication
  - `/api/terminal/decision/{symbol}` - Integrated decision output
  - `/api/terminal/positions` - Active positions
  - `/api/terminal/micro/live/{symbol}` - Live microstructure
- **Real-time:** 3-second polling for live updates
- **Symbol Support:** BTC/ETH/SOL

### Previous Phases (Completed)
- Core System (P0-P5 + P6): Scanner, Regime, Decision, Outcome, Calibration, Anti-Drift
- Phase 2.1-2.8: Prediction V2, Trade Setup, Execution Simulator, Portfolio, Risk, Multi-Asset (51 assets)
- Phase 2.9: Calibration Layer (94.7%)
- Phase 3.1: Action Application Engine (100%)
- Phase 3.2: Policy Guard Layer (96%)
- Phase 3.3: Audit / Rollback Layer (100%)
- Phase 3.4: Adaptive Scheduler (100%)
- Phase 4.1-4.8.4: Entry Timing Stack + Microstructure Weighting Validated

## Files Structure
```
/app/backend/modules/trading_terminal/
├── live/
│   ├── __init__.py
│   ├── micro_aggregator.py      # Microstructure features
│   └── terminal_routes.py       # Terminal API endpoints
├── auth/
├── live_execution/
├── microstructure_live/
├── decision_engine/
└── routes.py

/app/frontend/src/pages/trading/
├── index.jsx                    # Entry point with auth
└── components/
    ├── PasswordGate.jsx         # Auth overlay
    └── TradingTerminal.jsx      # Main terminal UI
```

## Key API Endpoints
- `POST /api/entry-timing/microstructure/evaluate` — Micro evaluation
- `POST /api/entry-timing/microstructure/validate/run` — A/B validation
- `POST /api/entry-timing/microstructure/weight/evaluate` — Weighting
- `POST /api/entry-timing/microstructure/weighting/validate/run` — A/B/C validation
- `POST /api/entry-timing/integration/evaluate` — Full stack decision
- `GET /api/terminal/decision/{symbol}` — Terminal decision
- `GET /api/terminal/positions` — Active positions

## Prioritized Backlog

### P0 (Next Immediate)
1. TradingView Chart integration in Terminal
2. Binance WebSocket connection for real-time data

### P1 Priority
1. Live orderbook feed integration (Binance WebSocket)
2. Real execution integration (connect to broker adapters)
3. Position management (open/close trades from terminal)

### P2 Priority
1. Alpha Factory
2. Additional timeframe support
3. Trading history view
4. Export/share functionality

### P3 Priority
1. Scale operations
2. Production deployment
3. Mobile responsiveness

## Tech Stack
- Backend: FastAPI + Python
- Database: MongoDB
- Frontend: React + Tailwind CSS
- Data: Binance API (planned)

## Test Results
- Phase 4.8.4: 21/21 tests passed
- Phase 5.1: Backend 100%, Frontend 95%

---
*Last Updated: 2026-04-02*
*Phase 5.1 Trading Terminal MVP COMPLETE*
