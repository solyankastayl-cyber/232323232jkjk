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

## Completed Phases

### Core System (P0-P5 + P6)
- Scanner, Regime, Decision, Outcome, Calibration, Anti-Drift, Historical Backtest

### Phase 2.1-2.8: Prediction & Portfolio Pipeline
- Prediction V2, Trade Setup, Execution Simulator, Portfolio, Risk, Multi-Asset (51 assets)

### Phase 2.9: Calibration Layer (94.7%)
### Phase 3.1: Action Application Engine (100%)
### Phase 3.2: Policy Guard Layer (96%)
### Phase 3.3: Audit / Rollback Layer (100%)
### Phase 3.4: Adaptive Scheduler (100%)

### Phase 4.1: Wrong Early Diagnostic Engine (100%)
### Phase 4.2: Entry Mode Selector — 7 modes (100%)
### Phase 4.3: Entry Execution Strategy — 7 strategies (100%)
### Phase 4.4: Entry Quality Score — 8 factors (100%)
### Phase 4.5: Entry Timing Integration — GO/WAIT/SKIP (100%)
### Phase 4.6: Wrong Early Re-Measurement — 55%→17% (100%)
### Phase 4.7: MTF Entry Timing — HTF+LTF+Alignment, 11 modes (100%)

### Phase 4.8: Microstructure Entry Layer (100% — 20/20)
- LiquidityEngine, OrderbookEngine, ImbalanceEngine, AbsorptionEngine, SweepDetector
- 6 decisions: ENTER_NOW, ENTER_REDUCED, WAIT_LIQUIDITY_CLEAR, WAIT_SWEEP, WAIT_MICRO_CONFIRMATION, SKIP_HOSTILE_SPREAD

### Phase 4.8.1: Microstructure Integration (100%)
- MicrostructureMergeEngine — timing + micro → unified decision
- GO_FULL (timing+micro aligned), WAIT_MICROSTRUCTURE (micro block)
- Backward compatible without micro data

### Phase 4.8.2: Microstructure A/B Validation (100% — 21/21)
- MicrostructureABTester — same trades, base vs micro pipeline
- MicroMetricsEngine — win_rate, PnL, PF, expectancy, MAE/MFE
- MicroImpactAnalyzer — avoided_bad, missed_good, net_edge
- **Result**: net_edge=79, wrong_early 15.5%→0%, stop_outs 20.5%→0%

### Phase 4.8.3: Microstructure Weighting (100%)
- MicroSizeModifier — 0.0x to 1.15x position size
- MicroConfidenceModifier — confidence boost/penalty
- MicroExecutionModifier — AGGRESSIVE/NORMAL/PASSIVE_LIMIT
- Strong micro: 1.15x size, GO_FULL | Weak micro: 0.6x size, GO_REDUCED

### Phase 4.8.4: A/B/C Weighting Validation (100%)
- Three-way: Base vs Filter vs Weighting on identical dataset
- **VERDICT: CASE_1_IDEAL — KEEP_WEIGHTING**
- Filter > Base: win_rate +46%, WE -15.5%, SO -20.5%
- Weighting > Filter: size-adj PnL +12%, upgraded_wins=29, oversized_losses=1

## Files Structure
```
/app/backend/modules/entry_timing/
├── diagnostics/                 # 4.1
├── mode_selector/               # 4.2
├── execution_strategy/          # 4.3
├── quality/                     # 4.4
├── integration/                 # 4.5 + 4.8.1
│   ├── entry_governor.py
│   ├── entry_decision_builder.py
│   ├── entry_timing_integration.py
│   ├── microstructure_merge_engine.py
│   └── entry_timing_routes.py
├── backtest/                    # 4.6
├── mtf/                         # 4.7
│   ├── htf_analyzer.py
│   ├── ltf_refinement_engine.py
│   ├── mtf_alignment_engine.py
│   ├── mtf_decision_engine.py
│   └── mtf_routes.py
└── microstructure/              # 4.8
    ├── liquidity_engine.py
    ├── orderbook_engine.py
    ├── imbalance_engine.py
    ├── absorption_engine.py
    ├── sweep_detector.py
    ├── microstructure_decision_engine.py
    ├── microstructure_routes.py
    ├── validation/              # 4.8.2
    │   ├── micro_ab_tester.py
    │   ├── micro_metrics_engine.py
    │   ├── micro_impact_analyzer.py
    │   ├── micro_backtest_runner.py
    │   └── micro_validation_routes.py
    ├── weighting/               # 4.8.3
    │   ├── micro_size_modifier.py
    │   ├── micro_confidence_modifier.py
    │   ├── micro_execution_modifier.py
    │   ├── micro_weighting_engine.py
    │   └── micro_weighting_routes.py
    └── validation_weighting/    # 4.8.4
        ├── micro_weighting_ab_runner.py
        ├── micro_weighting_metrics.py
        ├── micro_weighting_impact.py
        ├── micro_weighting_comparator.py
        └── micro_weighting_routes.py
```

## Key API Endpoints
- `POST /api/entry-timing/microstructure/evaluate` — Micro evaluation
- `POST /api/entry-timing/microstructure/validate/run` — A/B validation
- `POST /api/entry-timing/microstructure/weight/evaluate` — Weighting
- `POST /api/entry-timing/microstructure/weighting/validate/run` — A/B/C validation
- `POST /api/entry-timing/integration/evaluate` — Full stack decision
- `POST /api/entry-timing/mtf/decide/mock/{scenario}` — MTF decisions

## Key System Rules
1. No Future Leakage
2. Deterministic (rule-based, no ML in simulation)
3. Correctness First
4. Self-analyzing: knows where it works/fails
5. Timing-aware: decides WHEN to enter
6. MTF-aware: HTF permission + LTF timing
7. Microstructure-aware: local execution safety
8. Validated: A/B/C proven edge

## Backlog / Next Steps

### P1 Priority
1. Dashboard UI for Entry Timing Stack
2. Live orderbook feed integration (Binance WebSocket)

### P2 Priority
1. Alpha Factory
2. Additional timeframe support
3. Full Dashboard UI

### P3 Priority
1. Scale operations
2. Production deployment

## Tech Stack
- Backend: FastAPI + Python
- Database: MongoDB
- Frontend: React
- Data: Binance API

---
*Last Updated: 2026-04-02*
*Phase 4.8.2 + 4.8.3 + 4.8.4 COMPLETE — Microstructure Validated*
*VERDICT: CASE_1_IDEAL — KEEP_WEIGHTING — Production Ready*
