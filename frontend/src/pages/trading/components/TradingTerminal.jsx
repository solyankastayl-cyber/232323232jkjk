import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Activity, TrendingUp, Target, Layers, BarChart2, 
  RefreshCw, Wifi, WifiOff, ChevronRight, AlertTriangle,
  Shield, Gauge, Zap, Clock, DollarSign
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// =====================================================
// UNIFIED API - Single source of truth
// =====================================================
const fetchTerminalState = async (symbol) => {
  const res = await fetch(`${API_URL}/api/terminal/state/${symbol}`);
  if (!res.ok) throw new Error(`Failed to fetch: ${res.status}`);
  return res.json();
};

// =====================================================
// DECISION STYLES
// =====================================================
const getDecisionStyle = (action) => {
  if (!action) return 'bg-gray-600/20 text-gray-300 border-gray-500/30';
  if (action.includes('GO_FULL')) return 'bg-green-600/20 text-green-300 border-green-500/30';
  if (action.includes('GO_REDUCED')) return 'bg-emerald-600/20 text-emerald-300 border-emerald-500/30';
  if (action.includes('WAIT')) return 'bg-amber-600/20 text-amber-300 border-amber-500/30';
  if (action.includes('SKIP')) return 'bg-red-600/20 text-red-300 border-red-500/30';
  return 'bg-gray-600/20 text-gray-300 border-gray-500/30';
};

const getRiskStyle = (status) => {
  if (status === 'normal') return 'text-green-400';
  if (status === 'elevated') return 'text-amber-400';
  if (status === 'critical') return 'text-red-400';
  return 'text-gray-400';
};

// =====================================================
// MAIN COMPONENT
// =====================================================
const TradingTerminal = () => {
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [inputSymbol, setInputSymbol] = useState('BTCUSDT');
  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Single unified fetch
  const loadState = useCallback(async () => {
    try {
      const response = await fetchTerminalState(symbol);
      if (response.ok && response.data) {
        setState(response.data);
        setLastUpdate(new Date());
        setError(null);
      }
    } catch (err) {
      console.error('Terminal state error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    loadState();
    const interval = setInterval(loadState, 3000);
    return () => clearInterval(interval);
  }, [loadState]);

  const handleSymbolChange = () => {
    const normalized = inputSymbol.trim().toUpperCase();
    if (normalized && normalized !== symbol) {
      setSymbol(normalized);
      setLoading(true);
    }
  };

  const decisionStyle = useMemo(() => 
    getDecisionStyle(state?.decision?.action), 
    [state?.decision?.action]
  );

  if (loading && !state) {
    return (
      <div className="min-h-screen bg-[#0a0e14] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-gray-700 border-t-white rounded-full animate-spin" />
          <p className="text-sm text-gray-500">Loading terminal...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0e14] text-white font-sans" data-testid="trading-terminal-v2">
      {/* Top Bar */}
      <header className="h-14 border-b border-white/10 bg-[#0f1419] flex items-center justify-between px-6">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-blue-400" />
            <span className="font-bold tracking-widest text-sm">TERMINAL</span>
          </div>
          <div className="h-4 w-px bg-white/20" />
          <span className="text-lg font-bold tracking-tight">{symbol}</span>
          
          {/* Mode Badge */}
          <span className={`text-xs px-2 py-1 rounded ${
            state?.system?.mode === 'LIVE' 
              ? 'bg-green-600/20 text-green-400' 
              : 'bg-amber-600/20 text-amber-400'
          }`}>
            {state?.system?.mode || 'SIMULATION'}
          </span>
          
          {/* Data Source */}
          <span className="text-xs px-2 py-1 rounded bg-gray-700/50 text-gray-400">
            {state?.micro?.source || 'offline'}
          </span>
          
          {lastUpdate && (
            <span className="text-xs text-gray-500">
              {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>

        <div className="flex items-center gap-3">
          <input
            value={inputSymbol}
            onChange={(e) => setInputSymbol(e.target.value.toUpperCase())}
            onKeyDown={(e) => e.key === 'Enter' && handleSymbolChange()}
            placeholder="BTCUSDT"
            className="w-32 bg-[#0a0e14] border border-white/10 rounded px-3 py-1.5 text-sm outline-none focus:border-blue-500/50"
            data-testid="symbol-input"
          />
          <button
            onClick={handleSymbolChange}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 rounded text-sm font-medium transition-colors"
          >
            Load
          </button>
          <button
            onClick={loadState}
            className="p-2 hover:bg-white/5 rounded transition-colors"
            data-testid="refresh-button"
          >
            <RefreshCw className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </header>

      {error && (
        <div className="mx-6 mt-4 p-4 bg-red-600/10 border border-red-500/30 rounded text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Main Grid */}
      <main className="p-4 md:p-6">
        <div className="grid grid-cols-12 gap-4 md:gap-6">
          
          {/* LEFT COLUMN: Chart + Execution */}
          <div className="col-span-12 xl:col-span-8 space-y-4">
            {/* Chart Placeholder */}
            <Panel title="Chart Workspace" icon={BarChart2}>
              <div className="h-[500px] flex items-center justify-center border border-dashed border-white/10 rounded bg-[#0a0e14]">
                <div className="text-center text-gray-500">
                  <BarChart2 className="w-12 h-12 mx-auto mb-2 opacity-30" />
                  <p className="text-sm">TradingView Chart</p>
                  <p className="text-xs text-gray-600">{symbol}</p>
                </div>
              </div>
            </Panel>

            {/* Execution Block */}
            <Panel title="Execution Panel" icon={Zap}>
              {state?.execution && (
                <>
                  <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-6 gap-3">
                    <Metric label="Mode" value={state.execution.mode} />
                    <Metric label="Size" value={`${state.execution.size || 0}x`} />
                    <Metric label="Entry" value={formatPrice(state.execution.entry)} />
                    <Metric label="Stop" value={formatPrice(state.execution.stop)} color="red" />
                    <Metric label="Target" value={formatPrice(state.execution.target)} color="green" />
                    <Metric label="R:R" value={state.execution.rr || '—'} />
                  </div>
                  <div className="mt-4 flex items-center justify-between p-3 bg-[#0a0e14] rounded">
                    <span className="text-sm text-gray-400">Final Action:</span>
                    <span className={`px-3 py-1 rounded font-bold ${decisionStyle}`}>
                      {state.decision?.action || 'WAIT'}
                    </span>
                  </div>
                </>
              )}
            </Panel>
          </div>

          {/* RIGHT COLUMN: Decision + Micro + Risk */}
          <div className="col-span-12 xl:col-span-4 space-y-4">
            {/* Decision Block */}
            <Panel title="Decision Center" icon={Target}>
              {state?.decision && (
                <div className={`p-4 rounded border ${decisionStyle}`} data-testid="decision-block">
                  <div className="text-3xl font-bold tracking-tight">
                    {state.decision.action}
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-3">
                    <Metric label="Direction" value={state.decision.direction} />
                    <Metric label="Confidence" value={`${Math.round((state.decision.confidence || 0) * 100)}%`} />
                  </div>
                </div>
              )}
            </Panel>

            {/* Why Block */}
            <Panel title="Why Chain" icon={ChevronRight}>
              <div className="space-y-2" data-testid="why-block">
                {state?.decision?.reasons?.length > 0 ? (
                  state.decision.reasons.map((reason, i) => (
                    <div key={i} className="flex items-center gap-2 p-2 bg-[#0a0e14] rounded text-sm">
                      <ChevronRight className="w-3 h-3 text-gray-500 flex-shrink-0" />
                      <span className="text-gray-300">{reason}</span>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-gray-500">No reasons available</p>
                )}
              </div>
            </Panel>

            {/* Microstructure Block */}
            <Panel title="Microstructure" icon={Activity}>
              {state?.micro && (
                <div className="space-y-3" data-testid="micro-block">
                  <div className="grid grid-cols-2 gap-3">
                    <Metric 
                      label="Imbalance" 
                      value={`${state.micro.imbalance > 0 ? '+' : ''}${((state.micro.imbalance || 0) * 100).toFixed(1)}%`}
                      color={state.micro.imbalance > 0.1 ? 'green' : state.micro.imbalance < -0.1 ? 'red' : 'gray'}
                    />
                    <Metric label="Spread" value={`${state.micro.spread?.toFixed(1) || '—'} bps`} />
                    <Metric label="Liquidity" value={state.micro.liquidity} />
                    <Metric 
                      label="State" 
                      value={state.micro.state}
                      color={state.micro.state === 'favorable' ? 'green' : state.micro.state === 'hostile' ? 'red' : 'amber'}
                    />
                  </div>
                  {state.micro.reasons?.length > 0 && (
                    <div className="pt-2 border-t border-white/5">
                      {state.micro.reasons.map((r, i) => (
                        <div key={i} className="text-xs text-gray-500 py-1">• {r}</div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </Panel>

            {/* System State */}
            <Panel title="System State" icon={Shield}>
              <div className="grid grid-cols-2 gap-3">
                <Metric label="Adaptive" value={state?.system?.adaptive_active ? 'ACTIVE' : 'OFF'} />
                <Metric label="Scheduler" value={state?.system?.scheduler || 'unknown'} />
                <Metric label="Profile" value={state?.strategy?.profile || 'UNKNOWN'} />
                <Metric 
                  label="Risk" 
                  value={state?.risk?.status || 'unknown'}
                  color={state?.risk?.status === 'normal' ? 'green' : state?.risk?.status === 'elevated' ? 'amber' : 'red'}
                />
              </div>
            </Panel>
          </div>

          {/* BOTTOM ROW */}
          <div className="col-span-12 lg:col-span-4">
            <Panel title="Position" icon={TrendingUp}>
              {state?.position?.has_position ? (
                <div className="grid grid-cols-2 gap-3" data-testid="position-block">
                  <Metric label="Side" value={state.position.side} color={state.position.side === 'LONG' ? 'green' : 'red'} />
                  <Metric label="Size" value={state.position.size} />
                  <Metric label="Entry" value={formatPrice(state.position.entry)} />
                  <Metric label="Mark" value={formatPrice(state.position.mark)} />
                  <Metric 
                    label="PnL" 
                    value={`$${state.position.pnl?.toFixed(2) || 0}`}
                    color={state.position.pnl >= 0 ? 'green' : 'red'}
                  />
                  <Metric 
                    label="PnL %" 
                    value={`${state.position.pnl_pct?.toFixed(2) || 0}%`}
                    color={state.position.pnl_pct >= 0 ? 'green' : 'red'}
                  />
                </div>
              ) : (
                <p className="text-sm text-gray-500">No open position</p>
              )}
            </Panel>
          </div>

          <div className="col-span-12 lg:col-span-4">
            <Panel title="Portfolio" icon={DollarSign}>
              {state?.portfolio && (
                <div className="grid grid-cols-2 gap-3" data-testid="portfolio-block">
                  <Metric label="Equity" value={formatPrice(state.portfolio.equity)} />
                  <Metric label="Exposure" value={`${((state.portfolio.exposure || 0) * 100).toFixed(0)}%`} />
                  <Metric label="Free" value={formatPrice(state.portfolio.free_capital)} />
                  <Metric label="Risk Used" value={`${((state.portfolio.risk_used || 0) * 100).toFixed(0)}%`} />
                </div>
              )}
            </Panel>
          </div>

          <div className="col-span-12 lg:col-span-4">
            <Panel title="Risk Metrics" icon={Gauge}>
              {state?.risk && (
                <div className="grid grid-cols-2 gap-3" data-testid="risk-block">
                  <Metric 
                    label="Heat" 
                    value={`${((state.risk.heat || 0) * 100).toFixed(0)}%`}
                    color={state.risk.heat > 0.6 ? 'red' : state.risk.heat > 0.4 ? 'amber' : 'green'}
                  />
                  <Metric 
                    label="Drawdown" 
                    value={`${((state.risk.drawdown || 0) * 100).toFixed(1)}%`}
                    color={state.risk.drawdown > 0.1 ? 'red' : 'green'}
                  />
                  <Metric label="Daily DD" value={`${((state.risk.daily_drawdown || 0) * 100).toFixed(1)}%`} />
                  <Metric 
                    label="Kill Switch" 
                    value={state.risk.kill_switch ? 'ON' : 'OFF'}
                    color={state.risk.kill_switch ? 'red' : 'green'}
                  />
                </div>
              )}
            </Panel>
          </div>
        </div>
      </main>
    </div>
  );
};

// =====================================================
// HELPER COMPONENTS
// =====================================================
const Panel = ({ title, icon: Icon, children }) => (
  <div className="bg-[#0f1419] border border-white/10 rounded-lg p-4">
    <div className="flex items-center gap-2 mb-3">
      {Icon && <Icon className="w-4 h-4 text-gray-500" />}
      <h3 className="text-xs font-semibold uppercase tracking-widest text-gray-500">{title}</h3>
    </div>
    {children}
  </div>
);

const Metric = ({ label, value, color = 'white' }) => {
  const colorClass = {
    white: 'text-white',
    green: 'text-green-400',
    red: 'text-red-400',
    amber: 'text-amber-400',
    gray: 'text-gray-400'
  }[color] || 'text-white';

  return (
    <div className="bg-[#0a0e14] rounded p-2.5">
      <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-1">{label}</div>
      <div className={`text-sm font-medium ${colorClass}`}>{value || '—'}</div>
    </div>
  );
};

const formatPrice = (value) => {
  if (value === null || value === undefined) return '—';
  return `$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

export default TradingTerminal;
