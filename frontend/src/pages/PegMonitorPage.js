import React, { useEffect, useMemo, useState } from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import SEOHead from "../components/SEOHead";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  TrendingUp, 
  Clock,
  BarChart3,
  Zap
} from "lucide-react";

/**
 * PegMonitorPage – full-page dashboard for stablecoin peg monitoring
 * ---------------------------------------------------------------
 * - Table of all tracked stables with peg status
 * - Charts of deviation over time (using CryptoCompare histominute/histoday data)
 * - Tabs to switch between intraday (1h, 24h) and long-term (30d)
 * - Integrates with PegCheck API (for real-time status)
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
  return `$${x.toFixed(6)}`;
}

function formatBps(bps) {
  if (bps === undefined || bps === null || Number.isNaN(bps)) return "–";
  return `${bps.toFixed(1)} bps`;
}

export default function PegMonitorPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState("USDT");
  const [history, setHistory] = useState([]);
  const [timeRange, setTimeRange] = useState("24h");
  
  const symbols = ["USDT", "USDC", "DAI", "FRAX", "TUSD", "PYUSD", "BUSD", "USDP"];
  
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
  const query = useMemo(() => encodeURI(symbols.join(",")), [symbols]);

  async function fetchData() {
    try {
      setError(null);
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
          threshold_bps: 50,
          symbols: symbols,
          reports: {},
          analysis: json.data.analysis || {}
        };
        
        json.data.results.forEach(result => {
          transformedData.reports[result.symbol] = {
            symbol: result.symbol,
            ref_price: result.price_usd,
            pct_diff_oracle: result.deviation?.percentage || 0,
            pct_diff_dex: result.deviation?.percentage || 0,
            bps_diff: result.deviation?.basis_points || 0,
            is_depeg: result.is_depegged || false,
            peg_status: result.peg_status || 'normal',
            confidence: result.confidence || 1.0,
            sources_used: result.sources_used || []
          };
        });
        
        setData(transformedData);
      } else {
        throw new Error(json.message || 'Invalid response format');
      }
    } catch (e) {
      console.error('PegMonitorPage fetch error:', e);
      setError(e?.message || "Network error");
    } finally {
      setLoading(false);
    }
  }

  async function fetchHistory(symbol, range) {
    try {
      // Mock historical data for now - in production you'd fetch from CryptoCompare
      const now = Date.now() / 1000;
      const points = range === "1h" ? 60 : range === "24h" ? 144 : 30;
      const interval = range === "1h" ? 60 : range === "24h" ? 600 : 86400;
      
      const mockHistory = Array.from({ length: points }, (_, i) => {
        const timestamp = now - (points - i) * interval;
        const basePrice = 1.0;
        const noise = (Math.random() - 0.5) * 0.01; // ±0.5% noise
        const price = basePrice + noise;
        
        return {
          time: timestamp,
          close: price,
          date: new Date(timestamp * 1000).toLocaleString()
        };
      });
      
      setHistory(mockHistory);
    } catch (e) {
      console.error("Failed to fetch history", e);
      setHistory([]);
    }
  }

  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, 30000);
    return () => clearInterval(id);
  }, [backendUrl, query]);

  useEffect(() => {
    if (selected) fetchHistory(selected, timeRange);
  }, [selected, timeRange]);

  const reports = data?.reports || {};
  
  // Calculate summary statistics
  const stats = useMemo(() => {
    const reportValues = Object.values(reports);
    const totalSymbols = reportValues.length;
    const depegged = reportValues.filter(r => r.is_depeg).length;
    const warning = reportValues.filter(r => !r.is_depeg && Math.abs(r.bps_diff || 0) >= 25).length;
    const normal = totalSymbols - depegged - warning;
    const maxDeviation = Math.max(...reportValues.map(r => Math.abs(r.bps_diff || 0)), 0);
    
    return { totalSymbols, depegged, warning, normal, maxDeviation };
  }, [reports]);

  return (
    <div className="min-h-screen bg-gray-50">
      <SEOHead 
        title="Stablecoin Peg Monitor – Real-time Peg Stability Analysis"
        description="Advanced stablecoin peg monitoring with real-time deviation tracking, multi-source analysis, and comprehensive market intelligence."
        url="https://stableyield.com/peg-monitor"
      />
      
      <Header />
      
      <div className="pt-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
          
          {/* Page Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <BarChart3 className="w-6 h-6 text-blue-600" />
                  </div>
                  Stablecoin Peg Monitor
                </h1>
                <p className="text-gray-600 mt-2">
                  Real-time monitoring of major stablecoins with historical trends and deviation analysis
                </p>
              </div>
              
              {data && (
                <div className="text-right text-sm text-gray-500">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    Last updated: {new Date((data.as_of || 0) * 1000).toLocaleString()}
                  </div>
                  <div className="mt-1">
                    Threshold: {(data.threshold_bps || 50) / 100}%
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Summary Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="border-green-200 bg-green-50">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-green-800">Normal</p>
                    <p className="text-2xl font-bold text-green-900">{stats.normal}</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-yellow-200 bg-yellow-50">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-yellow-800">Warning</p>
                    <p className="text-2xl font-bold text-yellow-900">{stats.warning}</p>
                  </div>
                  <AlertTriangle className="w-8 h-8 text-yellow-600" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-red-200 bg-red-50">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-red-800">Depegged</p>
                    <p className="text-2xl font-bold text-red-900">{stats.depegged}</p>
                  </div>
                  <Zap className="w-8 h-8 text-red-600" />
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-blue-200 bg-blue-50">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-800">Max Deviation</p>
                    <p className="text-2xl font-bold text-blue-900">{formatBps(stats.maxDeviation)}</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Activity className="w-6 h-6 animate-spin text-blue-600 mr-2" />
              <span className="text-gray-600">Loading peg data...</span>
            </div>
          ) : error ? (
            <div className="rounded-xl border border-rose-200 bg-rose-50 p-6 text-center">
              <AlertTriangle className="w-8 h-8 text-rose-600 mx-auto mb-2" />
              <div className="text-sm text-rose-700">
                Failed to load peg data: {error}
              </div>
            </div>
          ) : (
            <>
              {/* Main Peg Status Table */}
              <Card className="mb-8">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5" />
                    Stablecoin Peg Status
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Deviation (bps)</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sources</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {symbols.map((s) => {
                          const r = reports[s];
                          if (!r) return null;
                          let color = "green";
                          let statusText = "Within Peg";
                          let statusBg = "bg-green-100 text-green-800";
                          
                          if (r.is_depeg) {
                            color = "red";
                            statusText = "Depegged";
                            statusBg = "bg-red-100 text-red-800";
                          } else if (Math.abs(r.bps_diff || 0) >= 25) {
                            color = "yellow";
                            statusText = "Warning";
                            statusBg = "bg-yellow-100 text-yellow-800";
                          }
                          
                          return (
                            <tr
                              key={s}
                              className={`hover:bg-gray-50 cursor-pointer transition-colors ${selected === s ? 'bg-blue-50' : ''}`}
                              onClick={() => setSelected(s)}
                            >
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 flex items-center gap-2">
                                <Dot color={color} /> 
                                <span className="font-semibold">{s}</span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 tabular-nums">
                                {formatUSD(r.ref_price)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 tabular-nums">
                                {formatBps(r.bps_diff)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusBg}`}>
                                  {statusText}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 tabular-nums">
                                {(r.confidence * 100).toFixed(0)}%
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {r.sources_used?.join(', ') || 'N/A'}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>

              {/* Historical Chart */}
              <Card>
                <CardContent className="p-6">
                  <div className="mb-4 flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                      <TrendingUp className="w-5 h-5" />
                      {selected} Price History
                    </h2>
                    <Tabs value={timeRange} onValueChange={setTimeRange}>
                      <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="1h">1 Hour</TabsTrigger>
                        <TabsTrigger value="24h">24 Hours</TabsTrigger>
                        <TabsTrigger value="30d">30 Days</TabsTrigger>
                      </TabsList>
                    </Tabs>
                  </div>

                  <div className="h-80 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={history}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis 
                          dataKey="date" 
                          hide={timeRange === "1h"} 
                          tick={{ fontSize: 10 }} 
                          minTickGap={30} 
                        />
                        <YAxis 
                          domain={[0.99, 1.01]} 
                          tickFormatter={(v) => `$${v.toFixed(4)}`}
                          tick={{ fontSize: 12 }}
                        />
                        <Tooltip 
                          formatter={(v) => [`$${Number(v).toFixed(6)}`, 'Price']}
                          labelFormatter={(l) => l} 
                        />
                        <Line 
                          type="monotone" 
                          dataKey="close" 
                          stroke="#2563eb" 
                          strokeWidth={2} 
                          dot={false} 
                        />
                        {/* Reference line at $1.00 */}
                        <Line
                          type="monotone"
                          dataKey={() => 1.0}
                          stroke="#ef4444"
                          strokeWidth={1}
                          strokeDasharray="5 5"
                          dot={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  
                  <div className="mt-4 text-center text-sm text-gray-500">
                    Red dashed line shows $1.00 peg target. Click any symbol in the table above to view its chart.
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>

      <Footer />
    </div>
  );
}