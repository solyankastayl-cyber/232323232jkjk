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
- **EXECUTION STATE & ORDERS (NEW - Phase TT1)**

## Current Version: Phase TT1 - Execution State & Orders Complete

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRADING TERMINAL UI                       │
│    ┌────────────────────────────────────────────────────┐   │
│    │     TIMEFRAME: [ 1H ] [ 4H ] [ 1D ]                │   │
│    │     EXECUTION STATUS: [IDLE] -> [WAITING] -> ...   │   │
│    │     ORDERS TAB: order list                         │   │
│    └────────────────────────────────────────────────────┘   │
│    GET /api/terminal/state/{symbol}?timeframe=4H            │
│         + execution_status + orders_preview                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              EXECUTION STATE ENGINE (NEW)                    │
│                                                              │
│   Decision → ExecutionIntent → OrderState → Position        │
│                                                              │
│   States: IDLE → WAITING_ENTRY → READY_TO_PLACE →           │
│           ORDER_PLANNED → ORDER_PLACED → PARTIAL_FILL →     │
│           FILLED → CLOSED                                    │
│                                                              │
│   State Machine prevents illegal transitions!                │
└─────────────────────────────────────────────────────────────┘
```

## What's Been Implemented

### 2026-04-02: Phase TT1 — Execution State & Orders (COMPLETE)

**New Backend Module:**
```
/app/backend/modules/trading_terminal/execution/
├── __init__.py
├── execution_models.py        # ExecutionIntent, OrderState, ExecutionStatusSummary
├── order_state_machine.py     # State transitions validation
├── execution_repository.py    # In-memory storage
├── execution_state_engine.py  # Main orchestrator
└── execution_routes.py        # API endpoints
```

**Order Lifecycle States:**
- IDLE → WAITING_ENTRY → READY_TO_PLACE
- ORDER_PLANNED → ORDER_PLACED → PARTIAL_FILL → FILLED → CLOSED
- Also: CANCELLED, REJECTED, EXPIRED

**New API Endpoints:**
- `GET /api/terminal/execution/{symbol}` - Execution status
- `GET /api/terminal/orders` - List all orders
- `GET /api/terminal/orders/open` - Open orders only
- `GET /api/terminal/intents` - List intents
- `POST /api/terminal/intents/simulate-upsert` - Create intent
- `POST /api/terminal/orders/simulate-place` - Place order
- `POST /api/terminal/orders/{id}/simulate-fill` - Fill order
- `POST /api/terminal/orders/{id}/simulate-cancel` - Cancel order

**Frontend Components:**
- `ExecutionStatusBlock` - Shows execution state, fill progress, intent state
- `OrdersTab` - Shows orders with status, price, size, filled %

**Terminal State Integration:**
```json
{
  "execution_status": {
    "execution_state": "ORDER_PLACED",
    "intent_state": "READY_TO_PLACE",
    "order_present": true,
    "filled_pct": 0.375,
    "status_label": "Order placed"
  },
  "orders_preview": [...]
}
```

### Previous Phases (Completed)
- Phase T4: Timeframe Selector (1H/4H/1D)
- Phase T3: Data Validation Layer
- Phase T2: Terminal State Orchestrator
- Phase 5.1: Live Microstructure
- Phase 4.1-4.8.4: Entry Timing Stack

## Test Results
- Phase TT1: Backend 95%, Frontend 85%

## Prioritized Backlog

### P0 (Next Immediate)
1. **TT2 - Position Manager** - Detailed position lifecycle
2. **TT3 - Portfolio & Risk Console** - Deep risk visibility

### P1 Priority
1. WebSocket real-time updates
2. Alert System (price, validation, decision changes)
3. MTF (Multi-Timeframe) analysis

### P2 Priority
1. Trade History / Forensics
2. System Console
3. Real exchange execution

## Tech Stack
- Backend: FastAPI + Python + aiohttp
- Database: MongoDB (+ in-memory for execution)
- Frontend: React + Tailwind CSS + lightweight-charts
- Data: Coinbase API (live)

---
*Last Updated: 2026-04-02*
*Phase TT1 Execution State & Orders COMPLETE*
