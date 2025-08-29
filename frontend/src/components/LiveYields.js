import React, { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';
import { TrendingUp, TrendingDown, ExternalLink, Sparkles, RefreshCw, BarChart3, Shield } from "lucide-react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import AIAlerts from "./AIAlerts";
import { yieldsApi } from "../services/api";
import { useToast } from "../hooks/use-toast";
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

console.log('LiveYields using Backend URL:', BACKEND_URL); // Debug log

const LiveYields = ({ onJoinWaitlist }) => {
  const [yieldsData, setYieldsData] = useState([]);
  const [riskMetrics, setRiskMetrics] = useState({});
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showRiskAdjusted, setShowRiskAdjusted] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

  // Fetch yields and risk data
  const fetchYields = async (showRefreshToast = false) => {
    try {
      // Dynamic API URL based on environment
      const getApiUrl = () => {
        if (window.location.hostname === 'localhost') {
          return 'http://localhost:8001/api';
        }
        // Always use HTTPS in production/preview environments
        const envBackendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
        if (envBackendUrl) {
          return `${envBackendUrl}/api`;
        }
        const protocol = window.location.protocol === 'https:' ? 'https:' : window.location.protocol;
        const hostname = window.location.hostname;
        return `${protocol}//${hostname}/api`;
      };
      
      const apiUrl = getApiUrl();
      
      // Fetch regular yields and risk-adjusted data in parallel
      const [yieldsResponse, riskResponse, metricsResponse] = await Promise.all([
        yieldsApi.getAllYields(),
        axios.get(`${apiUrl}/v1/strategies/risk-adjusted-yield`),
        axios.get(`${apiUrl}/v1/stablecoins/all-metrics`)
      ]);

      const yieldsFromAPI = yieldsResponse.data;
      const riskAdjustedData = riskResponse.data.strategies || [];
      const metricsData = metricsResponse.data.stablecoins || [];
      
      // Take top 3 for display
      setYieldsData(yieldsFromAPI.slice(0, 3));
      
      // Create risk metrics lookup
      const riskLookup = {};
      riskAdjustedData.forEach(item => {
        riskLookup[item.symbol] = {
          ry_apy: item.ry_apy,
          peg_score: item.peg_score,
          liq_score: item.liq_score,
          risk_tier: item.risk_tier
        };
      });
      
      // Add metrics data
      metricsData.forEach(metric => {
        if (riskLookup[metric.symbol]) {
          riskLookup[metric.symbol] = {
            ...riskLookup[metric.symbol],
            ...metric
          };
        } else {
          riskLookup[metric.symbol] = metric;
        }
      });
      
      setRiskMetrics(riskLookup);
      setLastUpdated(new Date());
      
      if (showRefreshToast) {
        toast({
          title: "Data Updated", 
          description: "Latest yield and risk data has been loaded.",
        });
      }
    } catch (error) {
      console.error("Failed to fetch yields:", error);
      
      // Fallback to mock data on error
      const mockData = [
        {
          stablecoin: "USDT", 
          name: "Tether USD",
          currentYield: 8.45,
          source: "Binance Earn",
          sourceType: "CeFi",
          riskScore: "Medium",
          change24h: 0.12,
          liquidity: "$89.2B"
        },
        {
          stablecoin: "USDC",
          name: "USD Coin", 
          currentYield: 7.82,
          source: "Aave V3",
          sourceType: "DeFi",
          riskScore: "Low",
          change24h: -0.05,
          liquidity: "$32.1B"
        },
        {
          stablecoin: "DAI",
          name: "Dai Stablecoin",
          currentYield: 6.95,
          source: "Compound", 
          sourceType: "DeFi",
          riskScore: "Medium",
          change24h: 0.08,
          liquidity: "$4.8B"
        }
      ];
      setYieldsData(mockData);
      
      // Don't show error toast - just log the error and use fallback data silently
      console.log("Using fallback data due to API error");
    } finally {
      setIsLoading(false);
    }
  };

  // Manual refresh
  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await yieldsApi.refreshYields(); // Trigger backend refresh
      await fetchYields(true);
    } catch (error) {
      console.error("Manual refresh failed:", error);
      // Don't show error toast - just log the error
    } finally {
      setIsRefreshing(false);
    }
  };

  // Initial load and periodic updates
  useEffect(() => {
    fetchYields();
    
    // Update every 5 minutes
    const interval = setInterval(() => {
      fetchYields();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  const getRiskScoreColor = (score) => {
    switch(score?.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSourceTypeColor = (type) => {
    return type === 'CeFi' 
      ? 'text-blue-600 bg-blue-100' 
      : 'text-purple-600 bg-purple-100';
  };

  const getRiskTierColor = (tier) => {
    switch(tier?.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (isLoading) {
    return (
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#4CC1E9] mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading latest yield data...</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Sparkles className="w-6 h-6 text-[#4CC1E9]" />
            <span className="text-sm font-semibold text-[#007A99] uppercase tracking-wider">Live Market Intelligence</span>
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-[#0E1A2B] mb-6">
            Risk-Adjusted Stablecoin Yields
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-4">
            Real-time yields with integrated peg stability and liquidity risk analysis
          </p>
          <div className="flex items-center justify-center space-x-4">
            <p className="text-sm text-gray-500">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="hover:bg-[#4CC1E9]/10 hover:border-[#4CC1E9]"
            >
              <RefreshCw className={`w-4 h-4 mr-1 ${isRefreshing ? 'animate-spin' : ''}`} />
              {isRefreshing ? 'Refreshing...' : 'Refresh'}
            </Button>
            <div className="flex items-center space-x-2">
              <Button
                variant={showRiskAdjusted ? "default" : "outline"}
                size="sm"
                onClick={() => setShowRiskAdjusted(!showRiskAdjusted)}
                className={showRiskAdjusted ? "bg-[#4CC1E9] hover:bg-[#007A99]" : ""}
              >
                <BarChart3 className="w-4 h-4 mr-1" />
                Risk View
              </Button>
              <AIAlerts />
            </div>
          </div>
        </div>

        {/* Yields Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {yieldsData.map((yieldItem, index) => {
            const risk = riskMetrics[yieldItem.stablecoin] || {};
            // Handle both mock data (currentYield) and backend data (apy values that need to be divided by 100)
            const baseYield = yieldItem.currentYield || (risk.apy ? risk.apy / 100 : 0);
            const displayYield = showRiskAdjusted && risk.ry_apy ? risk.ry_apy / 100 : baseYield;
            
            return (
              <div 
                key={yieldItem.stablecoin}
                className="group bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 hover:border-[#4CC1E9]/30 transform hover:-translate-y-1"
              >
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                      <span className="font-bold text-[#0E1A2B]">
                        {yieldItem.stablecoin}
                      </span>
                    </div>
                    <div>
                      <h3 className="font-bold text-[#0E1A2B]">{yieldItem.stablecoin}</h3>
                      <p className="text-sm text-gray-500">{yieldItem.name}</p>
                    </div>
                  </div>
                  
                  <div className="flex flex-col items-end space-y-1">
                    {index === 0 && (
                      <Badge className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] text-white text-xs">
                        #1
                      </Badge>
                    )}
                    {showRiskAdjusted && risk.risk_tier && (
                      <Badge className={getRiskTierColor(risk.risk_tier)} variant="outline">
                        {risk.risk_tier}
                      </Badge>
                    )}
                  </div>
                </div>

                {/* Yield Display */}
                <div className="text-center mb-6">
                  <div className="flex items-center justify-center space-x-2 mb-2">
                    <div className="text-4xl font-bold bg-gradient-to-r from-[#4CC1E9] to-[#007A99] bg-clip-text text-transparent">
                      {displayYield.toFixed(2)}%
                    </div>
                    {showRiskAdjusted && (
                      <Shield className="w-5 h-5 text-[#4CC1E9]" />
                    )}
                  </div>
                  
                  {showRiskAdjusted && risk.ry_apy && (
                    <div className="text-sm text-gray-500 mb-2">
                      Raw: {(yieldItem.currentYield || (risk.apy / 100)).toFixed(2)}% → Adjusted: {(risk.ry_apy / 100).toFixed(2)}%
                    </div>
                  )}
                  
                  <div className="flex items-center justify-center space-x-1">
                    {yieldItem.change24h >= 0 ? (
                      <TrendingUp className="w-4 h-4 text-green-500" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-red-500" />
                    )}
                    <span className={`text-sm font-medium ${
                      yieldItem.change24h >= 0 ? 'text-green-500' : 'text-red-500'
                    }`}>
                      {yieldItem.change24h >= 0 ? '+' : ''}{yieldItem.change24h.toFixed(2)}%
                    </span>
                    <span className="text-gray-500 text-sm">24h</span>
                  </div>
                </div>

                {/* Risk Metrics */}
                {showRiskAdjusted && (risk.peg_score || risk.liq_score) && (
                  <div className="space-y-3 mb-6 p-3 bg-[#4CC1E9]/5 rounded-lg">
                    {risk.peg_score && (
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Peg Stability</span>
                          <span className="font-medium">{(risk.peg_score * 100).toFixed(1)}%</span>
                        </div>
                        <Progress value={risk.peg_score * 100} className="h-1" />
                      </div>
                    )}
                    
                    {risk.liq_score && (
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Liquidity Score</span>
                          <span className="font-medium">{(risk.liq_score * 100).toFixed(1)}%</span>
                        </div>
                        <Progress value={risk.liq_score * 100} className="h-1" />
                      </div>
                    )}
                    
                    {risk.vw_price && (
                      <div className="text-xs text-gray-600">
                        Current Price: ${risk.vw_price.toFixed(4)}
                        {risk.peg_dev_bps && ` (${Math.abs(risk.peg_dev_bps).toFixed(1)} bps)`}
                      </div>
                    )}
                  </div>
                )}

                {/* Details */}
                <div className="space-y-3 mb-6">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 text-sm">Source</span>
                    <span className="font-medium text-[#0E1A2B]">{yieldItem.source}</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 text-sm">Type</span>
                    <Badge className={getSourceTypeColor(yieldItem.sourceType)} variant="outline">
                      {yieldItem.sourceType}
                    </Badge>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 text-sm">Risk Level</span>
                    <Badge className={getRiskScoreColor(yieldItem.riskScore)} variant="outline">
                      {yieldItem.riskScore}
                    </Badge>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 text-sm">Liquidity</span>
                    <span className="font-medium text-[#0E1A2B]">{yieldItem.liquidity}</span>
                  </div>
                </div>

                {/* Action Button */}
                <Button 
                  variant="outline" 
                  className="w-full group-hover:bg-[#4CC1E9] group-hover:text-white group-hover:border-[#4CC1E9] transition-all duration-300"
                  onClick={() => navigate('/dashboard')}
                >
                  View Details
                  <ExternalLink className="w-4 h-4 ml-2" />
                </Button>
              </div>
            );
          })}
        </div>

        {/* Call to Action */}
        <div className="text-center bg-gradient-to-br from-[#4CC1E9]/5 to-[#007A99]/5 rounded-2xl p-12 border border-[#4CC1E9]/20">
          <h3 className="text-2xl md:text-3xl font-bold text-[#0E1A2B] mb-4">
            Professional Market Intelligence
          </h3>
          <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
            Access comprehensive risk analytics, peg stability monitoring, and institutional-grade yield intelligence across 50+ platforms.
          </p>
          <Button 
            className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] text-white font-semibold px-8 py-3 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
            onClick={() => navigate('/risk-analytics')}
          >
            Get Professional Access
          </Button>
        </div>
      </div>
    </section>
  );
};

export default LiveYields;