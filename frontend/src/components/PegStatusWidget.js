import React, { useEffect, useMemo, useState } from "react";
import { Button } from "./ui/button";

/**
 * PegStatusWidget – drop-in widget for StableYield dashboard
 * ---------------------------------------------------------
 * - Fetches peg status from PegCheck API and renders compact badges
 * - Visual traffic-light indicator (🟢 within peg, 🟡 mild, 🔴 depeg)
 * - Auto-refreshes every 30s (configurable)
 * - Designed for quick embed in existing dashboard cards
 *
 * Props:
 *  - apiBase: string   -> e.g. "http://localhost:8001/api/peg" (no trailing slash)
 *  - symbols: string[] -> e.g. ["USDT","USDC","DAI","FRAX","TUSD","PYUSD"]
 *  - refreshMs?: number (default 30000)
 *  - linkHref?: string (default "/peg-monitor") – CTA to full page
 */

function classNames(...c) {
  return c.filter(Boolean).join(" ");
}

function Dot({ color }) {
  const c = color === "green" ? "bg-emerald-500" : color === "yellow" ? "bg-amber-500" : "bg-rose-500";
  return <span className={classNames("inline-block h-2.5 w-2.5 rounded-full", c)} />;
}

function formatPct(p) {
  if (p === undefined || p === null || Number.isNaN(p)) return "–";
  return `${p.toFixed(2)}%`;
}

function formatUSD(x) {
  if (x === undefined || x === null || Number.isNaN(x)) return "–";
  return `$${x.toFixed(4)}`;
}

export default function PegStatusWidget({
  apiBase,
  symbols = ["USDT", "USDC", "DAI", "FRAX", "TUSD", "PYUSD"],
  refreshMs = 30000,
  linkHref = "/peg-monitor",
  onCreateAlert,
}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const query = useMemo(() => encodeURI(symbols.join(",")), [symbols]);

  async function fetchData() {
    try {
      setError(null);
      
      // Dynamic backend URL detection
      const getBackendURL = () => {
        // Always use environment variable if available
        const envBackendUrl = process.env.REACT_APP_BACKEND_URL || import.meta?.env?.REACT_APP_BACKEND_URL;
        if (envBackendUrl) {
          return envBackendUrl;
        }
        
        // Fallback for localhost development
        if (window.location.hostname === 'localhost') {
          return 'http://localhost:8001';
        }
        
        // Use same protocol and hostname as current page
        const protocol = window.location.protocol; // Keeps https: if served over HTTPS
        const hostname = window.location.hostname;
        return `${protocol}//${hostname}`;
      };
      
      const backendUrl = getBackendURL();
      const res = await fetch(`${backendUrl}/api/peg/check?symbols=${query}`, { 
        cache: "no-store",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        }
      });
      
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      
      // Transform the response to match expected format
      if (json.success && json.data && json.data.results) {
        const transformedData = {
          as_of: json.data.analysis?.timestamp || Date.now() / 1000,
          threshold_bps: 50, // Default threshold
          symbols: symbols,
          reports: {}
        };
        
        // Transform results to reports format
        json.data.results.forEach(result => {
          transformedData.reports[result.symbol] = {
            symbol: result.symbol,
            ref_price: result.price_usd,
            pct_diff_oracle: result.deviation?.percentage || 0,
            pct_diff_dex: result.deviation?.percentage || 0,
            is_depeg: result.is_depegged || false,
            abs_diff_oracle: result.deviation?.absolute || 0,
            abs_diff_dex: result.deviation?.absolute || 0
          };
        });
        
        setData(transformedData);
      } else {
        throw new Error(json.message || 'Invalid response format');
      }
    } catch (e) {
      console.error('PegStatusWidget fetch error:', e);
      setError(e?.message || "Network error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, refreshMs);
    return () => clearInterval(id);
  }, [apiBase, query, refreshMs]);

  const rows = useMemo(() => {
    const reports = data?.reports || {};
    return symbols.map((s) => {
      const r = reports[s];
      // Priority: oracle deviation, fallback to dex deviation
      const pct = Number.isFinite(r?.pct_diff_oracle) && r?.pct_diff_oracle > 0 ? r?.pct_diff_oracle : r?.pct_diff_dex;
      let color = "green";
      if (r?.is_depeg) color = "red";
      else if (pct && pct >= 0.25) color = "yellow"; // mild drift
      return { s, r, pct: pct ?? NaN, color };
    });
  }, [data, symbols]);

  return (
    <div className="w-full rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900">Peg Status</h3>
          <p className="text-xs text-gray-500">Real-time stablecoin peg monitor</p>
        </div>
        <a
          href={linkHref}
          className="inline-flex items-center gap-2 rounded-xl border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 transition-colors"
        >
          View details
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-4 w-4">
            <path fillRule="evenodd" d="M3.75 12a.75.75 0 0 1 .75-.75h13.19l-3.72-3.72a.75.75 0 1 1 1.06-1.06l5 5a.75.75 0 0 1 0 1.06l-5 5a.75.75 0 1 1-1.06-1.06l3.72-3.72H4.5A.75.75 0 0 1 3.75 12Z" clipRule="evenodd" />
          </svg>
        </a>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 gap-2">
          {symbols.map((s) => (
            <div key={s} className="flex items-center justify-between rounded-xl bg-gray-50 px-3 py-2">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-gray-300" />
                <span className="h-3 w-10 animate-pulse rounded bg-gray-300" />
              </div>
              <span className="h-3 w-12 animate-pulse rounded bg-gray-300" />
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
          Failed to load peg data: {error}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-2 md:grid-cols-3 lg:grid-cols-4">
          {rows.map(({ s, r, pct, color }) => (
            <div key={s} className="flex items-center justify-between rounded-xl border border-gray-100 px-3 py-2 hover:bg-gray-50 transition-colors">
              <div className="flex items-center gap-2">
                <Dot color={color} />
                <span className="text-xs font-semibold text-gray-800">{s}</span>
              </div>
              <div className="text-right">
                <div className="text-xs tabular-nums text-gray-900">{formatUSD(r?.ref_price)}</div>
                <div className={classNames("text-[10px] tabular-nums", 
                  color === "red" ? "text-rose-600" : 
                  color === "yellow" ? "text-amber-600" : "text-emerald-600"
                )}>
                  Δ {formatPct(pct)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {onCreateAlert && (
        <div className="mt-3 text-center">
          <Button 
            variant="outline" 
            size="sm"
            onClick={onCreateAlert}
            className="text-xs px-3 py-1 h-7"
          >
            Create Alert
          </Button>
        </div>
      )}

      <div className="mt-3 flex items-center justify-between text-[10px] text-gray-500">
        <span>
          Updated: {data ? new Date((data.as_of || 0) * 1000).toLocaleString() : "–"}
        </span>
        <span>
          Threshold: {(data?.threshold_bps ?? 50) / 100}%
        </span>
      </div>
    </div>
  );
}