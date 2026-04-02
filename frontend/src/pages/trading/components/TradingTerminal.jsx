import React, { useState, useEffect, useCallback } from 'react';
import { 
  Activity, TrendingUp, Target, Layers, BarChart2, 
  RefreshCw, Wifi, WifiOff, ChevronRight
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

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
  const [decision, setDecision] = useState(null);
  const [positions, setPositions] = useState([]);
  const [connected, setConnected] = useState(true);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [dataSource, setDataSource] = useState('mock'); // 'mock' | 'REST' | 'WebSocket'
  const [isLive, setIsLive] = useState(false);

  // Fetch decision data
  const fetchDecision = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/terminal/decision/${symbol}`);
      const data = await response.json();
      if (data.ok) {
        setDecision(data.data);
        setLastUpdate(new Date());
        setConnected(true);
        setIsLive(data.live || false);
        setDataSource(data.source || (data.live ? 'REST' : 'mock'));
      }
    } catch (error) {
      console.error('Decision fetch error:', error);
      setConnected(false);
    }
  }, [symbol]);

  // Fetch positions
  const fetchPositions = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/terminal/positions`);
      const data = await response.json();
      if (data.ok) {
        setPositions(data.data.positions);
      }
    } catch (error) {
      console.error('Positions fetch error:', error);
    }
  }, []);

  // Initial load and polling
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchDecision(), fetchPositions()]);
      setLoading(false);
    };
    loadData();

    // Poll every 3 seconds
    const interval = setInterval(() => {
      fetchDecision();
      fetchPositions();
    }, 3000);

    return () => clearInterval(interval);
  }, [fetchDecision, fetchPositions]);

  const handleRefresh = () => {
    fetchDecision();
    fetchPositions();
  };

  if (loading) {
    return (
      <div className="flex h-screen w-full bg-gray-50 items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
          <p className="text-sm text-gray-500">Loading terminal...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-full bg-gray-50 overflow-hidden font-sans" data-testid="trading-terminal">
      {/* Sidebar */}
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
          {connected && (
            <div className="mt-1 text-xs text-gray-500 hidden lg:block">
              Source: {dataSource}
            </div>
          )}
        </div>
      </aside>

      {/* Main Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Top Bar */}
        <header className="h-14 border-b border-gray-200 bg-white flex items-center justify-between px-6 flex-shrink-0">
          <div className="flex items-center gap-4">
            <h1 className="text-sm font-bold uppercase tracking-widest text-gray-900">
              {symbol}
            </h1>
            {decision && (
              <span className="text-xs text-gray-500">
                Last: {lastUpdate?.toLocaleTimeString()}
              </span>
            )}
            {/* Data Source Badge */}
            <span className={`text-xs px-2 py-0.5 rounded ${
              isLive 
                ? 'bg-green-100 text-green-700' 
                : 'bg-amber-100 text-amber-700'
            }`}>
              {isLive ? 'LIVE' : 'SIMULATION'}
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
            {/* Chart Block */}
            <div className="lg:col-span-8 lg:row-span-2 bg-white border border-gray-200 rounded-sm shadow-sm min-h-[400px] flex items-center justify-center">
              <div className="text-center text-gray-400">
                <BarChart2 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p className="text-sm">TradingView Chart</p>
                <p className="text-xs text-gray-300">{symbol}</p>
              </div>
            </div>

            {/* Decision Block */}
            <div className="lg:col-span-4 bg-white border border-gray-200 rounded-sm shadow-sm p-5" data-testid="decision-block">
              <h2 className="text-xs font-semibold tracking-widest text-gray-500 uppercase mb-4">Decision</h2>
              {decision ? (
                <div className="space-y-4">
                  <div className={`inline-flex px-4 py-2 rounded text-2xl font-bold tracking-tight ${DECISION_STYLES[decision.decision.action] || 'bg-gray-200'}`}>
                    {decision.decision.action}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-500">Confidence:</span>
                    <span className="text-lg font-bold tabular-nums">{(decision.decision.confidence * 100).toFixed(0)}%</span>
                    <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-blue-600 rounded-full transition-all"
                        style={{ width: `${decision.decision.confidence * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-gray-400 text-sm">No decision</div>
              )}
            </div>

            {/* Why Block */}
            <div className="lg:col-span-4 bg-white border border-gray-200 rounded-sm shadow-sm p-5" data-testid="why-block">
              <h2 className="text-xs font-semibold tracking-widest text-gray-500 uppercase mb-4">Why</h2>
              {decision?.why ? (
                <div className="space-y-2">
                  {decision.why.map((reason, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <ChevronRight className="w-3 h-3 text-gray-400 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{reason.text}</span>
                      <span className={`text-xs px-2 py-0.5 rounded border ${STRENGTH_COLORS[reason.strength] || STRENGTH_COLORS.weak}`}>
                        {reason.strength}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-gray-400 text-sm">No reasons</div>
              )}
            </div>

            {/* Execution Block */}
            <div className="lg:col-span-4 lg:row-span-2 bg-white border border-gray-200 rounded-sm shadow-sm border-l-4 border-l-blue-600 p-5" data-testid="execution-block">
              <h2 className="text-xs font-semibold tracking-widest text-gray-500 uppercase mb-4">Execution</h2>
              {decision?.execution ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs text-gray-500 uppercase tracking-wider">Mode</label>
                      <div className="text-sm font-bold text-gray-900 mt-1">{decision.execution.mode}</div>
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 uppercase tracking-wider">Size</label>
                      <div className="text-sm font-bold text-gray-900 mt-1">{decision.execution.size_multiplier}x</div>
                    </div>
                  </div>

                  <div className="border-t border-gray-100 pt-4 space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-500 uppercase">Entry</span>
                      <span className="text-sm font-bold tabular-nums">${decision.execution.entry.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-500 uppercase">Stop Loss</span>
                      <span className="text-sm font-bold tabular-nums text-red-600">${decision.execution.stop_loss.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-500 uppercase">Take Profit</span>
                      <span className="text-sm font-bold tabular-nums text-green-600">${decision.execution.take_profit.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center border-t border-gray-100 pt-3">
                      <span className="text-xs text-gray-500 uppercase">R:R</span>
                      <span className="text-lg font-bold tabular-nums">{decision.execution.risk_reward}</span>
                    </div>
                  </div>

                  <button 
                    className="w-full py-3 bg-blue-600 text-white font-bold uppercase tracking-widest text-sm hover:bg-blue-700 transition-colors rounded disabled:opacity-50"
                    disabled={decision.decision.action === 'SKIP' || decision.decision.action.startsWith('WAIT')}
                    data-testid="execute-button"
                  >
                    Execute Trade
                  </button>
                </div>
              ) : (
                <div className="text-gray-400 text-sm">No execution data</div>
              )}
            </div>

            {/* Microstructure Block */}
            <div className="lg:col-span-8 bg-white border border-gray-200 rounded-sm shadow-sm p-5" data-testid="micro-block">
              <h2 className="text-xs font-semibold tracking-widest text-gray-500 uppercase mb-4">Microstructure</h2>
              {decision?.micro ? (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  <MicroStat 
                    label="Imbalance"
                    value={`${decision.micro.imbalance > 0 ? '+' : ''}${(decision.micro.imbalance * 100).toFixed(1)}%`}
                    color={decision.micro.imbalance > 0.1 ? 'green' : decision.micro.imbalance < -0.1 ? 'red' : 'gray'}
                  />
                  <MicroStat 
                    label="Spread"
                    value={`${decision.micro.spread_bps.toFixed(1)} bps`}
                    color={decision.micro.spread_bps < 1.5 ? 'green' : decision.micro.spread_bps > 2.5 ? 'red' : 'amber'}
                  />
                  <MicroStat 
                    label="Liquidity"
                    value={decision.micro.liquidity_state}
                    color={decision.micro.liquidity_state === 'strong_bid' ? 'green' : decision.micro.liquidity_state === 'thin' ? 'red' : 'gray'}
                  />
                  <MicroStat 
                    label="State"
                    value={decision.micro.state}
                    color={decision.micro.state === 'favorable' ? 'green' : decision.micro.state === 'hostile' ? 'red' : 'amber'}
                  />
                </div>
              ) : (
                <div className="text-gray-400 text-sm">No microstructure data</div>
              )}
            </div>

            {/* Positions Block */}
            <div className="lg:col-span-12 bg-white border border-gray-200 rounded-sm shadow-sm p-5" data-testid="positions-block">
              <h2 className="text-xs font-semibold tracking-widest text-gray-500 uppercase mb-4">Positions</h2>
              {positions.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-100">
                        <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider py-2 px-3">Symbol</th>
                        <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider py-2 px-3">Side</th>
                        <th className="text-right text-xs font-semibold text-gray-500 uppercase tracking-wider py-2 px-3">Size</th>
                        <th className="text-right text-xs font-semibold text-gray-500 uppercase tracking-wider py-2 px-3">Entry</th>
                        <th className="text-right text-xs font-semibold text-gray-500 uppercase tracking-wider py-2 px-3">Current</th>
                        <th className="text-right text-xs font-semibold text-gray-500 uppercase tracking-wider py-2 px-3">PnL</th>
                        <th className="text-center text-xs font-semibold text-gray-500 uppercase tracking-wider py-2 px-3">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {positions.map((pos) => (
                        <tr key={pos.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors" data-testid={`position-row-${pos.id}`}>
                          <td className="py-3 px-3 text-sm font-bold text-gray-900">{pos.symbol}</td>
                          <td className="py-3 px-3">
                            <span className={`text-xs font-bold px-2 py-1 rounded ${pos.side === 'LONG' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                              {pos.side}
                            </span>
                          </td>
                          <td className="py-3 px-3 text-right text-sm tabular-nums text-gray-900">{pos.size}</td>
                          <td className="py-3 px-3 text-right text-sm tabular-nums text-gray-600">${pos.entry_price.toLocaleString()}</td>
                          <td className="py-3 px-3 text-right text-sm tabular-nums text-gray-900">${pos.current_price.toLocaleString()}</td>
                          <td className="py-3 px-3 text-right">
                            <span className={`text-sm font-bold tabular-nums ${pos.pnl_usd >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {pos.pnl_usd >= 0 ? '+' : ''}${pos.pnl_usd.toLocaleString()}
                              <span className="text-xs ml-1">({pos.pnl_percent.toFixed(2)}%)</span>
                            </span>
                          </td>
                          <td className="py-3 px-3 text-center">
                            <span className="text-xs font-medium px-2 py-1 bg-blue-100 text-blue-700 rounded">{pos.status}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-gray-400 text-sm text-center py-8">No open positions</div>
              )}
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

export default TradingTerminal;
