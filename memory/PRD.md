# TA Engine — Full System PRD

## Project Overview
TA Engine - fund-grade decision-driven trading system with full operational terminal including:
- Prediction Engine
- Execution Simulation
- Portfolio Backtesting  
- Risk Management
- Entry Timing Stack with Microstructure
- Trading Terminal with Unified State Orchestrator
- DATA VALIDATION LAYER
- TIMEFRAME SELECTOR
- EXECUTION STATE & ORDERS (TT1)
- **POSITION MANAGER (NEW - Phase TT2)**

## Current Version: Phase TT2 - Position Manager Complete

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRADING TERMINAL UI                       │
│                                                              │
│    DECISION → EXECUTION → ORDER → POSITION → PORTFOLIO      │
│         ↓          ↓        ↓        ↓           ↓          │
│      [Badge]    [Status]  [Tab]  [Block+Tab]  [Block]       │
│                                                              │
│    Position: OPEN | LONG 0.5 BTC | +$985 | GOOD             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              POSITION ENGINE (NEW - TT2)                     │
│                                                              │
│   Order FILLED → Position CREATED → Mark Updates → PnL      │
│                                                              │
│   Health Engine:                                             │
│   - GOOD: Normal operation                                   │
│   - WARNING: Near stop (<1%)                                 │
│   - CRITICAL: Stop breached                                  │
└─────────────────────────────────────────────────────────────┘
```

## What's Been Implemented

### 2026-04-02: Phase TT2 — Position Manager (COMPLETE)

**New Backend Module:**
```
/app/backend/modules/trading_terminal/positions/
├── __init__.py
├── position_models.py        # Position dataclass
├── position_repository.py    # In-memory storage
├── position_health_engine.py # GOOD/WARNING/CRITICAL
├── position_engine.py        # Main orchestrator
└── position_routes.py        # API endpoints
```

**Position Lifecycle:**
- OPENING → OPEN → SCALING → REDUCING → CLOSING → CLOSED

**Position Health:**
- **GOOD**: Normal operation
- **WARNING**: Within 1% of stop
- **CRITICAL**: Stop breached

**New API Endpoints:**
- `GET /api/terminal/positions` - List all positions
- `GET /api/terminal/positions/open` - Open positions only
- `GET /api/terminal/positions/history` - Closed positions
- `GET /api/terminal/positions/summary/{symbol}` - Position summary
- `POST /api/terminal/positions/simulate-open-from-order` - Create from order
- `POST /api/terminal/positions/{id}/simulate-mark` - Update mark price
- `POST /api/terminal/positions/{id}/simulate-close` - Close position
- `POST /api/terminal/positions/{id}/simulate-reduce` - Reduce size

**Frontend Components:**
- `PositionStatusBlock` - Shows position with PnL, health, levels

**Terminal State Integration:**
```json
{
  "position": {
    "has_position": true,
    "status": "OPEN",
    "side": "LONG",
    "size": 0.5,
    "entry_price": 65050,
    "mark_price": 67020,
    "unrealized_pnl": 985.0,
    "pnl_pct": 3.03,
    "health": "GOOD",
    "stop": 63500,
    "target": 68000
  },
  "positions_preview": [...]
}
```

### Previous Phases (Completed)
- Phase TT1: Execution State & Orders
- Phase T4: Timeframe Selector (1H/4H/1D)
- Phase T3: Data Validation Layer
- Phase T2: Terminal State Orchestrator
- Phase 5.1: Live Microstructure
- Phase 4.1-4.8.4: Entry Timing Stack

## Test Results
- Phase TT2: Backend 100%, Frontend 100%, Integration 100%

## Prioritized Backlog

### P0 (Next Immediate)
1. **TT3 - Portfolio & Risk Console** - Complete the chain
2. **WebSocket** - Real-time updates

### P1 Priority
1. Alert System (price, health, decision changes)
2. Trade History / Forensics
3. MTF (Multi-Timeframe) analysis

### P2 Priority
1. System Console
2. Real exchange execution
3. Manual position controls

## System Flow (Current)

```
Decision (GO_FULL)
    ↓
Execution Intent (READY_TO_PLACE)
    ↓
Order (ORDER_PLACED → FILLED)
    ↓
Position (OPEN, PnL, Health)
    ↓
Portfolio & Risk (TT3 - next)
```

## Tech Stack
- Backend: FastAPI + Python + aiohttp
- Database: MongoDB (+ in-memory for execution/positions)
- Frontend: React + Tailwind CSS + lightweight-charts
- Data: Coinbase API (live)

---
*Last Updated: 2026-04-02*
*Phase TT2 Position Manager COMPLETE*
