import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Activity, TrendingUp, Target, Layers, BarChart2, 
  RefreshCw, Wifi, WifiOff, ChevronRight
} from 'lucide-react';
import TradingChart from '../../../components/charts/TradingChart';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// Unified API fetch
const fetchTerminalState = async (symbol) => {
  const res = await fetch(`${API_URL}/api/terminal/state/${symbol}`);
  if (!res.ok) throw new Error(`Failed to fetch: ${res.status}`);
  return res.json();
};

// Decision status colors
const DECISION_STYLES = {
  GO_FULL: 'bg-green-600 text-white',
  GO_REDUCED: 'bg-emerald-500 text-white',
  WAIT: 'bg-amber-500 text-white',
  WAIT_MICRO: 'bg-orange-500 text-white',
  SKIP: 'bg-gray-500 text-white'
};

// Strength badge colors
const STRENGTH_COLORS = {
  strong: 'bg-green-100 text-green-700 border-green-200',
  medium: 'bg-amber-100 text-amber-700 border-amber-200',
  weak: 'bg-gray-100 text-gray-600 border-gray-200'
};

const TradingTerminal = () => {
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Single unified fetch
  const loadState = useCallback(async () => {
    try {
      const response = await fetchTerminalState(symbol);
      if (response.ok && response.data) {
        setState(response.data);
        setLastUpdate(new Date());
        setConnected(true);
      }
    } catch (error) {
      console.error('Terminal state error:', error);
      setConnected(false);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    loadState();
    const interval = setInterval(loadState, 3000);
    return () => clearInterval(interval);
  }, [loadState]);

  const handleRefresh = () => loadState();

  if (loading && !state) {
    return (
      <div className="flex h-screen w-full bg-gray-50 items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
          <p className="text-sm text-gray-500">Loading terminal...</p>
        </div>
      </div>
    );
  }

  const decision = state?.decision || {};
  const execution = state?.execution || {};
  const micro = state?.micro || {};
  const position = state?.position || {};
  const portfolio = state?.portfolio || {};
  const risk = state?.risk || {};
  const validation = state?.validation || {};

  return (
    <div className="flex h-screen w-full bg-gray-50 overflow-hidden font-sans" data-testid="trading-terminal">
      {/* Sidebar - Dark */}
      <aside className="h-full w-16 lg:w-56 bg-gray-900 border-r border-gray-800 flex-shrink-0 flex flex-col">
        {/* Logo */}
        <div className="h-14 flex items-center justify-center lg:justify-start lg:px-4 border-b border-gray-800">
          <Target className="w-6 h-6 text-white" />
          <span className="hidden lg:block ml-2 text-white font-bold text-sm tracking-widest uppercase">Terminal</span>
        </div>

        {/* Symbol Selector */}
        <div className="p-2 lg:p-4 border-b border-gray-800">
          <select
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            className="w-full bg-gray-800 text-white text-sm font-medium px-3 py-2 rounded border border-gray-700 focus:border-gray-500 outline-none"
            data-testid="symbol-selector"
          >
            <option value="BTCUSDT">BTC/USDT</option>
            <option value="ETHUSDT">ETH/USDT</option>
            <option value="SOLUSDT">SOL/USDT</option>
          </select>
        </div>

        {/* Nav Items */}
        <nav className="flex-1 p-2 lg:p-3 space-y-1">
          <NavItem icon={Activity} label="Dashboard" active />
          <NavItem icon={BarChart2} label="Analysis" />
          <NavItem icon={Layers} label="Positions" />
          <NavItem icon={TrendingUp} label="History" />
        </nav>

        {/* Connection Status */}
        <div className="p-4 border-t border-gray-800">
          <div className={`flex items-center gap-2 text-xs ${connected ? 'text-green-400' : 'text-red-400'}`}>
            {connected ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
            <span className="hidden lg:block font-medium">
              {connected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          <div className="mt-1 text-xs text-gray-500 hidden lg:block">
            Source: {micro.source || 'mock'}
          </div>
        </div>
      </aside>

      {/* Main Area - Light */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Top Bar */}
        <header className="h-14 border-b border-gray-200 bg-white flex items-center justify-between px-6 flex-shrink-0">
          <div className="flex items-center gap-4">
            <h1 className="text-sm font-bold uppercase tracking-widest text-gray-900">
              {symbol}
            </h1>
            {lastUpdate && (
              <span className="text-xs text-gray-500">
                Last: {lastUpdate.toLocaleTimeString()}
              </span>
            )}
            {/* Mode Badge */}
            <span className={`text-xs px-2 py-0.5 rounded ${
              state?.system?.mode === 'LIVE' 
                ? 'bg-green-100 text-green-700' 
                : 'bg-amber-100 text-amber-700'
            }`}>
              {state?.system?.mode === 'LIVE' ? 'LIVE' : 'SIMULATION'}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button 
              onClick={handleRefresh}
              className="p-2 hover:bg-gray-100 rounded transition-colors"
              data-testid="refresh-button"
            >
              <RefreshCw className="w-4 h-4 text-gray-500" />
            </button>
          </div>
        </header>

        {/* Grid Content */}
        <main className="flex-1 overflow-auto p-4 md:p-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 md:gap-6">
            
            {/* Validation Block - Shows only when there are issues */}
            {(validation.critical_count > 0 || validation.warning_count > 0) && (
              <div className="lg:col-span-12">
                <ValidationBlock validation={validation} />
              </div>
            )}
            
            {/* Chart Block - FULL WIDTH */}
            <div className="lg:col-span-12 bg-white border border-gray-200 rounded-sm shadow-sm overflow-hidden">
              <TradingChart
                symbol={symbol}
                execution={execution}
                decision={decision}
                height={450}
                showVolume={true}
              />
            </div>

            {/* Decision Block */}
            <div className="lg:col-span-3 bg-white border border-gray-200 rounded-sm shadow-sm p-5" data-testid="decision-block">
              <h2 className="text-xs font-semibold tracking-widest text-gray-500 uppercase mb-4">Decision</h2>
              <div className="space-y-4">
                <div className={`inline-flex px-4 py-2 rounded text-2xl font-bold tracking-tight ${DECISION_STYLES[decision.action] || 'bg-gray-200'}`}>
                  {decision.action || 'WAIT'}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-500">Confidence:</span>
                  <span className="text-lg font-bold tabular-nums">{Math.round((decision.confidence || 0) * 100)}%</span>
                  <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-600 rounded-full transition-all"
                      style={{ width: `${(decision.confidence || 0) * 100}%` }}
                    />
                  </div>
                </div>
                <div className="text-sm text-gray-600">
                  Direction: <span className="font-medium">{decision.direction || 'NEUTRAL'}</span>
                </div>
              </div>
            </div>

            {/* Why Block */}
            <div className="lg:col-span-3 bg-white border border-gray-200 rounded-sm shadow-sm p-5" data-testid="why-block">
              <h2 className="text-xs font-semibold tracking-widest text-gray-500 uppercase mb-4">Why</h2>
              <div className="space-y-2">
                {decision.reasons?.length > 0 ? (
                  decision.reasons.map((reason, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <ChevronRight className="w-3 h-3 text-gray-400 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{reason}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-gray-400 text-sm">No reasons</div>
                )}
              </div>
            </div>

            {/* Execution Block */}
            <div className="lg:col-span-3 bg-white border border-gray-200 rounded-sm shadow-sm border-l-4 border-l-blue-600 p-5" data-testid="execution-block">
              <h2 className="text-xs font-semibold tracking-widest text-gray-500 uppercase mb-4">Execution</h2>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-gray-500 uppercase tracking-wider">Mode</label>
                    <div className="text-sm font-bold text-gray-900 mt-1">{execution.mode || 'PASSIVE_LIMIT'}</div>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 uppercase tracking-wider">Size</label>
                    <div className="text-sm font-bold text-gray-900 mt-1">{execution.size || 0}x</div>
                  </div>
                </div>

                <div className="border-t border-gray-100 pt-4 space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500 uppercase">Entry</span>
                    <span className="text-sm font-bold tabular-nums">${execution.entry?.toLocaleString() || '—'}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500 uppercase">Stop Loss</span>
                    <span className="text-sm font-bold tabular-nums text-red-600">${execution.stop?.toLocaleString() || '—'}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500 uppercase">Take Profit</span>
                    <span className="text-sm font-bold tabular-nums text-green-600">${execution.target?.toLocaleString() || '—'}</span>
                  </div>
                  <div className="flex justify-between items-center border-t border-gray-100 pt-3">
                    <span className="text-xs text-gray-500 uppercase">R:R</span>
                    <span className="text-lg font-bold tabular-nums">{execution.rr || '—'}</span>
                  </div>
                </div>

                <button 
                  className="w-full py-3 bg-blue-600 text-white font-bold uppercase tracking-widest text-sm hover:bg-blue-700 transition-colors rounded disabled:opacity-50"
                  disabled={decision.action === 'SKIP' || decision.action?.startsWith('WAIT')}
                  data-testid="execute-button"
                >
                  Execute Trade
                </button>
              </div>
            </div>

            {/* Microstructure Block */}
            <div className="lg:col-span-3 bg-white border border-gray-200 rounded-sm shadow-sm p-5" data-testid="micro-block">
              <h2 className="text-xs font-semibold tracking-widest text-gray-500 uppercase mb-4">Microstructure</h2>
              <div className="grid grid-cols-2 gap-3">
                <MicroStat 
                  label="Imbalance"
                  value={`${micro.imbalance > 0 ? '+' : ''}${((micro.imbalance || 0) * 100).toFixed(1)}%`}
                  color={micro.imbalance > 0.1 ? 'green' : micro.imbalance < -0.1 ? 'red' : 'gray'}
                />
                <MicroStat 
                  label="Spread"
                  value={`${micro.spread?.toFixed(1) || '—'} bps`}
                  color={micro.spread < 1.5 ? 'green' : micro.spread > 2.5 ? 'red' : 'amber'}
                />
                <MicroStat 
                  label="Liquidity"
                  value={micro.liquidity || 'unknown'}
                  color={micro.liquidity === 'strong_bid' ? 'green' : micro.liquidity === 'thin' ? 'red' : 'gray'}
                />
                <MicroStat 
                  label="State"
                  value={micro.state || 'unknown'}
                  color={micro.state === 'favorable' ? 'green' : micro.state === 'hostile' ? 'red' : 'amber'}
                />
              </div>
            </div>

            {/* Position Block */}
            <div className="lg:col-span-4 bg-white border border-gray-200 rounded-sm shadow-sm p-5" data-testid="position-block">
              <h2 className="text-xs font-semibold tracking-widest text-gray-500 uppercase mb-4">Position</h2>
              {position.has_position ? (
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className={`text-xs font-bold px-2 py-1 rounded ${position.side === 'LONG' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {position.side}
                    </span>
                    <span className="text-sm font-bold">{position.size} {symbol.replace('USDT', '')}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Entry</span>
                    <span className="font-medium">${position.entry?.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">PnL</span>
                    <span className={`font-bold ${position.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {position.pnl >= 0 ? '+' : ''}${position.pnl?.toFixed(2)} ({position.pnl_pct?.toFixed(2)}%)
                    </span>
                  </div>
                </div>
              ) : (
                <div className="text-gray-400 text-sm text-center py-4">No open position</div>
              )}
            </div>

            {/* Portfolio Block */}
            <div className="lg:col-span-4 bg-white border border-gray-200 rounded-sm shadow-sm p-5" data-testid="portfolio-block">
              <h2 className="text-xs font-semibold tracking-widest text-gray-500 uppercase mb-4">Portfolio</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-gray-500">Equity</label>
                  <div className="text-sm font-bold mt-1">${portfolio.equity?.toLocaleString() || '—'}</div>
                </div>
                <div>
                  <label className="text-xs text-gray-500">Exposure</label>
                  <div className="text-sm font-bold mt-1">{((portfolio.exposure || 0) * 100).toFixed(0)}%</div>
                </div>
                <div>
                  <label className="text-xs text-gray-500">Risk Used</label>
                  <div className="text-sm font-bold mt-1">{((portfolio.risk_used || 0) * 100).toFixed(0)}%</div>
                </div>
                <div>
                  <label className="text-xs text-gray-500">Free Capital</label>
                  <div className="text-sm font-bold mt-1">${portfolio.free_capital?.toLocaleString() || '—'}</div>
                </div>
              </div>
            </div>

            {/* Risk Block */}
            <div className="lg:col-span-4 bg-white border border-gray-200 rounded-sm shadow-sm p-5" data-testid="risk-block">
              <h2 className="text-xs font-semibold tracking-widest text-gray-500 uppercase mb-4">Risk</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-gray-500">Heat</label>
                  <div className={`text-sm font-bold mt-1 ${risk.heat > 0.6 ? 'text-red-600' : risk.heat > 0.4 ? 'text-amber-600' : 'text-green-600'}`}>
                    {((risk.heat || 0) * 100).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <label className="text-xs text-gray-500">Drawdown</label>
                  <div className={`text-sm font-bold mt-1 ${risk.drawdown > 0.1 ? 'text-red-600' : 'text-gray-900'}`}>
                    {((risk.drawdown || 0) * 100).toFixed(1)}%
                  </div>
                </div>
                <div>
                  <label className="text-xs text-gray-500">Status</label>
                  <div className={`text-sm font-bold mt-1 ${risk.status === 'normal' ? 'text-green-600' : risk.status === 'elevated' ? 'text-amber-600' : 'text-red-600'}`}>
                    {risk.status || 'unknown'}
                  </div>
                </div>
                <div>
                  <label className="text-xs text-gray-500">Kill Switch</label>
                  <div className={`text-sm font-bold mt-1 ${risk.kill_switch ? 'text-red-600' : 'text-green-600'}`}>
                    {risk.kill_switch ? 'ON' : 'OFF'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

// Helper Components
const NavItem = ({ icon: Icon, label, active = false }) => (
  <button className={`w-full flex items-center gap-3 px-3 py-2 rounded transition-colors ${
    active ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white'
  }`}>
    <Icon className="w-5 h-5 flex-shrink-0" />
    <span className="hidden lg:block text-sm font-medium">{label}</span>
  </button>
);

const MicroStat = ({ label, value, color = 'gray' }) => {
  const colorMap = {
    green: 'text-green-600',
    red: 'text-red-600',
    amber: 'text-amber-600',
    gray: 'text-gray-600'
  };
  
  return (
    <div className="flex flex-col">
      <span className="text-xs text-gray-500 uppercase tracking-wider">{label}</span>
      <span className={`text-lg font-bold tabular-nums mt-1 ${colorMap[color]}`}>{value}</span>
    </div>
  );
};

// Validation Block Component
const ValidationBlock = ({ validation }) => {
  if (!validation || !validation.issues?.length) return null;
  
  const hasCritical = validation.critical_count > 0;
  const hasWarning = validation.warning_count > 0;
  
  // Only show if there are actual issues worth displaying
  const relevantIssues = validation.issues?.filter(
    i => i.severity === 'critical' || i.severity === 'warning'
  ) || [];
  
  if (relevantIssues.length === 0) return null;
  
  return (
    <div 
      className={`rounded-sm border p-4 ${
        hasCritical 
          ? 'border-red-300 bg-red-50' 
          : hasWarning 
            ? 'border-amber-300 bg-amber-50'
            : 'border-gray-200 bg-gray-50'
      }`}
      data-testid="validation-block"
    >
      <div className={`text-xs font-bold uppercase tracking-widest mb-3 ${
        hasCritical ? 'text-red-700' : hasWarning ? 'text-amber-700' : 'text-gray-500'
      }`}>
        {hasCritical ? 'DATA ERROR' : 'Data Warning'}
      </div>
      <div className="space-y-2">
        {relevantIssues.map((issue, idx) => (
          <div 
            key={idx} 
            className={`flex items-start gap-2 text-sm ${
              issue.severity === 'critical' ? 'text-red-700' : 'text-amber-700'
            }`}
          >
            <span className="font-bold flex-shrink-0">
              {issue.valid ? '✓' : '✗'}
            </span>
            <span>{issue.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TradingTerminal;
