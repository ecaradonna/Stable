import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { TrendingUp, TrendingDown, Shield, Zap, AlertTriangle, CheckCircle } from "lucide-react";
import axios from "axios";

const getBackendURL = () => {
  if (window.location.hostname === 'localhost') {
    return 'http://localhost:8001';
  }
  // Always use HTTPS in production/preview environments
  const envBackendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
  if (envBackendUrl) {
    return envBackendUrl;
  }
  const protocol = window.location.protocol === 'https:' ? 'https:' : window.location.protocol;
  const hostname = window.location.hostname;
  return `${protocol}//${hostname}`;
};

const BACKEND_URL = getBackendURL();
const API = `${BACKEND_URL}/api`;

const RiskAnalyticsDashboard = () => {
  const [metrics, setMetrics] = useState([]);
  const [riskAdjustedYields, setRiskAdjustedYields] = useState([]);
  const [pegRanking, setPegRanking] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      setIsLoading(true);
      
      // Fetch all metrics in parallel
      const [metricsRes, yieldsRes, rankingRes] = await Promise.all([
        axios.get(`${API}/v1/stablecoins/all-metrics`),
        axios.get(`${API}/v1/strategies/risk-adjusted-yield`),
        axios.get(`${API}/v1/peg-stability/ranking`)
      ]);

      setMetrics(metricsRes.data.stablecoins || []);
      setRiskAdjustedYields(yieldsRes.data.strategies || []);
      setPegRanking(rankingRes.data.ranking || []);

    } catch (error) {
      console.error("Failed to fetch risk analytics data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getPegScoreColor = (score) => {
    if (score >= 0.9) return "text-green-600 bg-green-100";
    if (score >= 0.7) return "text-yellow-600 bg-yellow-100";
    return "text-red-600 bg-red-100";
  };

  const getRiskTierColor = (tier) => {
    switch (tier?.toLowerCase()) {
      case 'low': return "text-green-600 bg-green-100";
      case 'medium': return "text-yellow-600 bg-yellow-100"; 
      case 'high': return "text-red-600 bg-red-100";
      default: return "text-gray-600 bg-gray-100";
    }
  };

  const formatBps = (bps) => {
    return `${Math.abs(bps).toFixed(1)} bps`;
  };

  const formatUSD = (amount) => {
    if (amount >= 1e9) return `$${(amount / 1e9).toFixed(1)}B`;
    if (amount >= 1e6) return `$${(amount / 1e6).toFixed(1)}M`;
    if (amount >= 1e3) return `$${(amount / 1e3).toFixed(1)}K`;
    return `$${amount.toFixed(0)}`;
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#4CC1E9] mx-auto mb-4"></div>
          <p className="text-gray-600">Loading market intelligence data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[#0E1A2B]">Risk Analytics Dashboard</h2>
          <p className="text-gray-600">Real-time peg stability and liquidity intelligence</p>
        </div>
        <Badge className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] text-white">
          Live Data
        </Badge>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="peg-stability">Peg Stability</TabsTrigger>
          <TabsTrigger value="risk-adjusted">Risk-Adjusted Yields</TabsTrigger>
          <TabsTrigger value="liquidity">Liquidity Analysis</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {metrics.slice(0, 4).map((metric) => (
              <Card key={metric.symbol} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{metric.symbol}</CardTitle>
                    <Badge className={getPegScoreColor(metric.peg_score)}>
                      {(metric.peg_score * 100).toFixed(1)}%
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Peg Score</span>
                        <span className="font-medium">{(metric.peg_score * 100).toFixed(1)}%</span>
                      </div>
                      <Progress value={metric.peg_score * 100} className="h-2" />
                    </div>
                    
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Liquidity Score</span>
                        <span className="font-medium">{(metric.liq_score * 100).toFixed(1)}%</span>
                      </div>
                      <Progress value={metric.liq_score * 100} className="h-2" />
                    </div>
                    
                    <div className="pt-2 border-t">
                      <div className="flex items-center justify-between text-sm">
                        <span>Price</span>
                        <div className="flex items-center">
                          <span className="font-mono">${metric.vw_price?.toFixed(4)}</span>
                          {metric.peg_dev_bps >= 0 ? (
                            <TrendingUp className="w-3 h-3 text-green-500 ml-1" />
                          ) : (
                            <TrendingDown className="w-3 h-3 text-red-500 ml-1" />
                          )}
                        </div>
                      </div>
                      <div className="text-xs text-gray-500">
                        {formatBps(metric.peg_dev_bps)} from peg
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Peg Stability Tab */}
        <TabsContent value="peg-stability" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Shield className="w-5 h-5 mr-2 text-[#4CC1E9]" />
                Peg Stability Ranking
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {pegRanking.map((item, index) => (
                  <div key={item.symbol} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gradient-to-r from-[#4CC1E9] to-[#007A99] text-white rounded-full flex items-center justify-center text-sm font-bold">
                        {index + 1}
                      </div>
                      <div>
                        <h4 className="font-semibold text-[#0E1A2B]">{item.symbol}</h4>
                        <p className="text-sm text-gray-600">
                          Price: ${item.vw_price?.toFixed(4)} ({formatBps(item.peg_dev_bps)})
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className="text-sm font-medium">Peg Score</div>
                        <Badge className={getPegScoreColor(item.peg_score)}>
                          {(item.peg_score * 100).toFixed(1)}%
                        </Badge>
                      </div>
                      
                      <div className="text-right">
                        <div className="text-sm font-medium">Volatility</div>
                        <span className="text-sm text-gray-600">
                          {formatBps(item.peg_vol_5m_bps)}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Risk-Adjusted Yields Tab */}
        <TabsContent value="risk-adjusted" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-[#4CC1E9]" />
                Risk-Adjusted Yields
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {riskAdjustedYields.slice(0, 8).map((strategy) => (
                  <div key={strategy.strategy_id} className="p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                          <span className="font-bold text-sm text-[#0E1A2B]">{strategy.symbol}</span>
                        </div>
                        <div>
                          <h4 className="font-semibold text-[#0E1A2B]">{strategy.platform}</h4>
                          <p className="text-sm text-gray-600">{strategy.symbol}</p>
                        </div>
                      </div>
                      
                      <Badge className={getRiskTierColor(strategy.risk_tier)}>
                        {strategy.risk_tier} Risk
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Raw APY</span>
                        <div className="font-bold text-lg text-[#0E1A2B]">
                          {(strategy.apy / 100).toFixed(3)}%
                        </div>
                      </div>
                      
                      <div>
                        <span className="text-gray-600">Risk-Adjusted</span>
                        <div className="font-bold text-lg bg-gradient-to-r from-[#4CC1E9] to-[#007A99] bg-clip-text text-transparent">
                          {(strategy.ry_apy / 100).toFixed(3)}%
                        </div>
                      </div>
                      
                      <div>
                        <span className="text-gray-600">Peg Score</span>
                        <div className="font-medium">
                          {(strategy.peg_score * 100).toFixed(1)}%
                        </div>
                      </div>
                      
                      <div>
                        <span className="text-gray-600">Liquidity Score</span>
                        <div className="font-medium">
                          {(strategy.liq_score * 100).toFixed(1)}%
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Liquidity Analysis Tab */}
        <TabsContent value="liquidity" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {metrics.map((metric) => (
              <Card key={`liq-${metric.symbol}`}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>{metric.symbol} Liquidity</span>
                    <Badge className={metric.liq_score > 0.7 ? "bg-green-100 text-green-700" : 
                                   metric.liq_score > 0.4 ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"}>
                      {metric.liq_score > 0.7 ? "Excellent" : metric.liq_score > 0.4 ? "Good" : "Fair"}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span>Overall Liquidity Score</span>
                        <span className="font-bold">{(metric.liq_score * 100).toFixed(1)}%</span>
                      </div>
                      <Progress value={metric.liq_score * 100} className="h-3" />
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Price</span>
                        <div className="font-mono font-bold">
                          ${metric.vw_price?.toFixed(4)}
                        </div>
                      </div>
                      
                      <div>
                        <span className="text-gray-600">Peg Deviation</span>
                        <div className={`font-medium ${Math.abs(metric.peg_dev_bps) < 10 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatBps(metric.peg_dev_bps)}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default RiskAnalyticsDashboard;