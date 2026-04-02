/**
 * TradingChart - Chart component for Trading Terminal
 * ====================================================
 * 
 * Uses lightweight-charts v5 API
 * Adds execution overlays: Entry, Stop Loss, Take Profit
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { createChart, CandlestickSeries, HistogramSeries, LineSeries } from 'lightweight-charts';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// Fetch candles - try Coinbase live first, fallback to mock
async function fetchCandles(asset, days = 7) {
  // Try Coinbase live candles first
  try {
    const coinbaseUrl = `${API_URL}/api/provider/coinbase/candles/${asset}?timeframe=1h&limit=168`;
    const coinbaseRes = await fetch(coinbaseUrl);
    if (coinbaseRes.ok) {
      const data = await coinbaseRes.json();
      if (data.ok && data.candles && data.candles.length > 0) {
        // Convert Coinbase format to chart format
        // Sort by timestamp ascending and deduplicate
        const seen = new Set();
        const candles = data.candles
          .sort((a, b) => (a.timestamp || 0) - (b.timestamp || 0))
          .filter(c => {
            const ts = c.timestamp;
            if (seen.has(ts)) return false;
            seen.add(ts);
            return true;
          })
          .map(c => {
            // Convert ms timestamp to date string YYYY-MM-DD
            const date = new Date(c.timestamp);
            const time = date.toISOString().split('T')[0];
            return {
              t: time,
              o: c.open || c.o,
              h: c.high || c.h,
              l: c.low || c.l,
              c: c.close || c.c,
              v: c.volume || c.v || 0
            };
          });
        
        // Aggregate hourly to daily candles
        const dailyMap = {};
        candles.forEach(c => {
          if (!dailyMap[c.t]) {
            dailyMap[c.t] = { t: c.t, o: c.o, h: c.h, l: c.l, c: c.c, v: c.v };
          } else {
            dailyMap[c.t].h = Math.max(dailyMap[c.t].h, c.h);
            dailyMap[c.t].l = Math.min(dailyMap[c.t].l, c.l);
            dailyMap[c.t].c = c.c; // Latest close
            dailyMap[c.t].v += c.v;
          }
        });
        
        const dailyCandles = Object.values(dailyMap).sort((a, b) => a.t.localeCompare(b.t));
        
        if (dailyCandles.length > 0) {
          return { ok: true, candles: dailyCandles, source: 'coinbase' };
        }
      }
    }
  } catch (e) {
    console.warn('Coinbase candles failed, using mock:', e);
  }
  
  // Fallback to mock data
  const url = `${API_URL}/api/ui/candles?asset=${asset}&days=${days}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed: ${res.status}`);
  const data = await res.json();
  return { ...data, source: 'mock' };
}

export default function TradingChart({
  symbol = 'BTCUSDT',
  execution = null,
  decision = null,
  height = 500,
  showVolume = true,
}) {
  const containerRef = useRef(null);
  const chartRef = useRef(null);
  const candleSeriesRef = useRef(null);
  const volumeSeriesRef = useRef(null);
  const [lastPrice, setLastPrice] = useState(null);
  const [error, setError] = useState(null);
  const [candleData, setCandleData] = useState([]);

  const asset = symbol.replace('USDT', '').replace('USD', '');

  // Create chart on mount
  useEffect(() => {
    if (!containerRef.current || chartRef.current) return;

    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height,
      layout: {
        background: { type: 'solid', color: '#ffffff' },
        textColor: '#111',
      },
      grid: {
        vertLines: { color: 'rgba(17, 24, 39, 0.06)' },
        horzLines: { color: 'rgba(17, 24, 39, 0.06)' },
      },
      rightPriceScale: { borderVisible: false },
      timeScale: {
        rightOffset: 12,
        barSpacing: 12,
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    candleSeriesRef.current = chart.addSeries(CandlestickSeries, {
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    });

    volumeSeriesRef.current = chart.addSeries(HistogramSeries, {
      priceFormat: { type: 'volume' },
      priceScaleId: '',
      scaleMargins: { top: 0.85, bottom: 0 },
    });

    // Resize handler
    const resizeObserver = new ResizeObserver(() => {
      if (containerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: containerRef.current.clientWidth });
      }
    });
    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
    };
  }, [height]);

  // Load candles
  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        const data = await fetchCandles(asset, 7);
        if (!mounted || !data.candles?.length) return;

        const candles = data.candles.map(c => ({
          time: c.time || c.t,
          open: c.open || c.o,
          high: c.high || c.h,
          low: c.low || c.l,
          close: c.close || c.c,
        }));

        setCandleData(candles);
        
        const lastCandle = candles[candles.length - 1];
        setLastPrice(lastCandle.close);

        if (candleSeriesRef.current) {
          candleSeriesRef.current.setData(candles);
        }

        if (volumeSeriesRef.current && showVolume) {
          const volumes = data.candles.map(c => {
            const close = c.close || c.c;
            const open = c.open || c.o;
            return {
              time: c.time || c.t,
              value: c.volume || c.v || 0,
              color: close >= open ? 'rgba(34, 197, 94, 0.25)' : 'rgba(239, 68, 68, 0.25)',
            };
          });
          volumeSeriesRef.current.setData(volumes);
        }

        chartRef.current?.timeScale().fitContent();
        setError(null);
      } catch (err) {
        console.error('[TradingChart] Error:', err);
        if (mounted) setError(err.message);
      }
    }

    load();
    const interval = setInterval(load, 30000);
    return () => { mounted = false; clearInterval(interval); };
  }, [asset, showVolume]);

  // Execution overlays (Entry/Stop/Target lines)
  useEffect(() => {
    if (!chartRef.current || !candleData.length) return;
    if (!decision?.action?.includes('GO')) return;
    if (!execution?.entry) return;

    const chart = chartRef.current;
    const firstTime = candleData[0].time;
    const lastTime = candleData[candleData.length - 1].time;

    // Add horizontal lines for entry/stop/target
    const { entry, stop, target } = execution;

    // Clean up old lines (would need refs to track them)
    // For now, just add new ones - they'll persist until chart remount

    if (entry) {
      try {
        const line = chart.addSeries(LineSeries, {
          color: 'rgba(59, 130, 246, 0.8)',
          lineWidth: 2,
          lineStyle: 0,
          lastValueVisible: true,
        });
        line.setData([
          { time: firstTime, value: entry },
          { time: lastTime, value: entry },
        ]);
      } catch (e) {}
    }

    if (stop) {
      try {
        const line = chart.addSeries(LineSeries, {
          color: 'rgba(239, 68, 68, 0.8)',
          lineWidth: 2,
          lineStyle: 2,
          lastValueVisible: true,
        });
        line.setData([
          { time: firstTime, value: stop },
          { time: lastTime, value: stop },
        ]);
      } catch (e) {}
    }

    if (target) {
      try {
        const line = chart.addSeries(LineSeries, {
          color: 'rgba(34, 197, 94, 0.8)',
          lineWidth: 2,
          lineStyle: 2,
          lastValueVisible: true,
        });
        line.setData([
          { time: firstTime, value: target },
          { time: lastTime, value: target },
        ]);
      } catch (e) {}
    }
  }, [execution, decision, candleData]);

  return (
    <div className="relative bg-white rounded">
      {/* Legend */}
      {execution && decision?.action?.includes('GO') && (
        <div className="absolute top-3 left-3 z-10 flex gap-3 text-xs">
          {execution.entry && (
            <div className="flex items-center gap-1.5 bg-white/90 px-2 py-1 rounded shadow-sm border border-gray-100">
              <div className="w-3 h-0.5 bg-blue-500" />
              <span className="text-gray-600">Entry ${execution.entry?.toLocaleString()}</span>
            </div>
          )}
          {execution.stop && (
            <div className="flex items-center gap-1.5 bg-white/90 px-2 py-1 rounded shadow-sm border border-gray-100">
              <div className="w-3 h-0.5 bg-red-500" />
              <span className="text-gray-600">Stop ${execution.stop?.toLocaleString()}</span>
            </div>
          )}
          {execution.target && (
            <div className="flex items-center gap-1.5 bg-white/90 px-2 py-1 rounded shadow-sm border border-gray-100">
              <div className="w-3 h-0.5 bg-green-500" />
              <span className="text-gray-600">Target ${execution.target?.toLocaleString()}</span>
            </div>
          )}
        </div>
      )}

      {/* Decision Badge */}
      {decision && (
        <div className="absolute top-3 right-3 z-10">
          <div className={`px-3 py-1.5 rounded text-sm font-bold shadow-sm ${
            decision.action?.includes('GO_FULL') ? 'bg-green-600 text-white' :
            decision.action?.includes('GO_REDUCED') ? 'bg-emerald-500 text-white' :
            decision.action?.includes('WAIT') ? 'bg-amber-500 text-white' :
            decision.action?.includes('SKIP') ? 'bg-gray-500 text-white' :
            'bg-gray-200 text-gray-700'
          }`}>
            {decision.action} ({Math.round((decision.confidence || 0) * 100)}%)
          </div>
        </div>
      )}

      {/* Chart */}
      <div ref={containerRef} style={{ height, minHeight: height }} />

      {/* Error */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-white/80">
          <p className="text-sm text-red-500">{error}</p>
        </div>
      )}

      {/* Current Price */}
      {lastPrice && (
        <div className="absolute bottom-3 right-3 z-10 bg-white/90 px-3 py-1.5 rounded shadow-sm border border-gray-100">
          <span className="text-xs text-gray-500">Last: </span>
          <span className="text-sm font-bold text-gray-900">${lastPrice?.toLocaleString()}</span>
        </div>
      )}
    </div>
  );
}
