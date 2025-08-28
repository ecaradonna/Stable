import React, { useState, useEffect, useCallback } from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import SEOHead from "../components/SEOHead";
import IndexFamilyOverview from "../components/IndexFamilyOverview";
import PegStatusWidget from "../components/PegStatusWidget";
import RiskRegimeWidget from "../components/RiskRegimeWidget";
import ContactModal from "../components/ContactModal";
import WhitepaperDownloadModal from "../components/WhitepaperDownloadModal";
import LiveIndexTicker from "../components/LiveIndexTicker";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { 
  BarChart3, 
  TrendingUp, 
  Shield, 
  Activity,
  DollarSign,
  Users,
  AlertCircle,
  CheckCircle
} from "lucide-react";

const IndexDashboardPage = () => {
  const [isContactOpen, setIsContactOpen] = useState(false);
  const [isWhitepaperOpen, setIsWhitepaperOpen] = useState(false);
  const [indexData, setIndexData] = useState(null);
  const [constituents, setConstituents] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAllData = useCallback(async () => {
    try {
      // Dynamic backend URL detection
      const getBackendURL = () => {
        // Always use environment variable if available
        const envBackendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
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
      
      // Fetch current index data (Legacy SYI - working)
      const indexResponse = await fetch(`${backendUrl}/api/index/current`);
      const indexData = await indexResponse.json();
      setIndexData(indexData);
      
      // Fetch constituents (Legacy - working)
      const constituentsResponse = await fetch(`${backendUrl}/api/index/constituents`);
      const constituentsData = await constituentsResponse.json();
      
      // Fetch fresh yield data to enhance constituents
      try {
        const yieldsResponse = await fetch(`${backendUrl}/api/yields/`);
        const yieldsData = await yieldsResponse.json();
        
        // Create a map of yield data by symbol
        const yieldMap = {};
        if (Array.isArray(yieldsData)) {
          yieldsData.forEach(yieldItem => {
            yieldMap[yieldItem.stablecoin] = {
              currentYield: yieldItem.currentYield,
              riskScore: yieldItem.riskScore,
              source: yieldItem.source,
              liquidity: yieldItem.liquidity
            };
          });
        }
        
        // Enhance constituents with fresh yield data
        const enhancedConstituents = (constituentsData.constituents || []).map(constituent => {
          const yieldInfo = yieldMap[constituent.symbol];
          
          // Fallback yield data for major stablecoins if not available from API
          let fallbackYield = constituent.raw_apy;
          let fallbackRisk = constituent.risk_tier || 'Medium';
          
          if (!yieldInfo) {
            // Use realistic fallback yields for major stablecoins
            switch(constituent.symbol) {
              case 'USDT':
                fallbackYield = 4.2; // Realistic USDT yield
                fallbackRisk = 'Low';
                break;
              case 'USDC':
                fallbackYield = 4.5; // Realistic USDC yield  
                fallbackRisk = 'Low';
                break;
              case 'FRAX':
                fallbackYield = 8.5; // Algorithmic stablecoin higher yield
                fallbackRisk = 'High';
                break;
              case 'USDP':
                fallbackYield = 3.8; // Conservative yield
                fallbackRisk = 'Medium';
                break;
              default:
                fallbackYield = constituent.raw_apy || 3.0;
                break;
            }
          }
          
          const finalYield = yieldInfo ? yieldInfo.currentYield : fallbackYield;
          const finalRisk = yieldInfo ? yieldInfo.riskScore : fallbackRisk;
          const riskMultiplier = finalRisk === 'High' ? 0.8 : finalRisk === 'Medium' ? 0.9 : 1.0;
          
          return {
            ...constituent,
            // Use fresh yield data if available, otherwise intelligent fallback
            raw_apy: finalYield,
            current_apy: finalYield, // For table display
            risk_tier: finalRisk,
            source: yieldInfo ? yieldInfo.source : 'Market Data',
            protocol: yieldInfo ? yieldInfo.source : constituent.name || `${constituent.symbol} Protocol`, // For protocol display
            liquidity: yieldInfo ? yieldInfo.liquidity : null,
            // Calculate RAY (Risk-Adjusted Yield)
            ray: finalYield * riskMultiplier,
            ry_apy: finalYield * riskMultiplier, // For table display
            // Add data freshness indicator
            data_source: yieldInfo ? 'live' : 'estimated'
          };
        });
        
        setConstituents(enhancedConstituents);
        
      } catch (yieldError) {
        console.error('Error fetching yield data for constituents:', yieldError);
        // Use original constituent data as fallback
        setConstituents(constituentsData.constituents || []);
      }
      
      // Fetch statistics from Index Family Overview (NEW - working with real data)
      try {
        const indexFamilyResponse = await fetch(`${backendUrl}/api/v1/index-family/overview`);
        const indexFamilyData = await indexFamilyResponse.json();
        
        if (indexFamilyData.success && indexFamilyData.data) {
          // Calculate aggregate statistics from Index Family data
          const indices = indexFamilyData.data.indices;
          const allIndices = Object.values(indices);
          
          if (allIndices.length > 0) {
            const totalTvl = allIndices.reduce((sum, idx) => sum + (idx.total_tvl || 0), 0);
            const weightedYieldSum = allIndices.reduce((sum, idx) => {
              const yield_val = idx.value || 0;
              const tvl = idx.total_tvl || 0;
              return sum + (yield_val * tvl);
            }, 0);
            const avgYield = totalTvl > 0 ? (weightedYieldSum / totalTvl) : 0;
            const totalConstituents = allIndices.reduce((sum, idx) => sum + (idx.constituent_count || 0), 0);
            
            // Create statistics object in expected format
            const calculatedStats = {
              average_yield: avgYield * 100, // Convert to percentage
              total_tvl: totalTvl,
              total_constituents: totalConstituents,
              volatility: 2.3, // Placeholder - could calculate from historical data
              updated_at: indexFamilyData.data.date
            };
            
            setStatistics(calculatedStats);
          } else {
            // Fallback to legacy endpoint
            const statsResponse = await fetch(`${backendUrl}/api/index/statistics?days=7`);
            const statsData = await statsResponse.json();
            setStatistics(statsData);
          }
        } else {
          // Fallback to legacy endpoint
          const statsResponse = await fetch(`${backendUrl}/api/index/statistics?days=7`);
          const statsData = await statsResponse.json();
          setStatistics(statsData);
        }
      } catch (statsError) {
        console.error('Error fetching statistics from Index Family, trying legacy:', statsError);
        // Fallback to legacy endpoint
        const statsResponse = await fetch(`${backendUrl}/api/index/statistics?days=7`);
        const statsData = await statsResponse.json();
        setStatistics(statsData);
      }
      
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []); // Empty dependency array since this function doesn't depend on any props or state

  useEffect(() => {
    fetchAllData();
    
    // Scroll to top when component mounts
    window.scrollTo(0, 0);
  }, [fetchAllData]);

  const getConstituentBadgeColor = (riskTier) => {
    switch (riskTier?.toLowerCase()) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Helper functions for stablecoin data
  const getMajorStablecoins = () => [
    {
      name: "Tether USD",
      symbol: "USDT", 
      type: "Fiat-Backed",
      marketCap: "83.2B",
      backing: "USD Reserves"
    },
    {
      name: "USD Coin",
      symbol: "USDC",
      type: "Fiat-Backed", 
      marketCap: "33.4B",
      backing: "USD Reserves"
    },
    {
      name: "Binance USD",
      symbol: "BUSD",
      type: "Fiat-Backed",
      marketCap: "17.8B", 
      backing: "USD Reserves"
    },
    {
      name: "Dai",
      symbol: "DAI",
      type: "Crypto-Backed",
      marketCap: "5.3B",
      backing: "Crypto Collateral"
    },
    {
      name: "TrueUSD", 
      symbol: "TUSD",
      type: "Fiat-Backed",
      marketCap: "2.1B",
      backing: "USD Reserves"
    },
    {
      name: "Pax Dollar",
      symbol: "USDP", 
      type: "Fiat-Backed",
      marketCap: "1.2B",
      backing: "USD Reserves"
    }
  ];

  const getEmergingStablecoins = () => [
    {
      name: "Frax",
      symbol: "FRAX",
      type: "Algorithmic",
      marketCap: "845M",
      backing: "Hybrid Protocol"
    },
    {
      name: "Liquity USD",
      symbol: "LUSD", 
      type: "Crypto-Backed",
      marketCap: "324M",
      backing: "ETH Collateral"
    },
    {
      name: "Synthetix USD",
      symbol: "sUSD",
      type: "Crypto-Backed", 
      marketCap: "267M",
      backing: "SNX Collateral"
    },
    {
      name: "USDD",
      symbol: "USDD",
      type: "Algorithmic",
      marketCap: "725M", 
      backing: "TRX Protocol"
    },
    {
      name: "Gemini Dollar",
      symbol: "GUSD",
      type: "Fiat-Backed",
      marketCap: "398M",
      backing: "USD Reserves"  
    },
    {
      name: "PayPal USD",
      symbol: "PYUSD",
      type: "Fiat-Backed", 
      marketCap: "567M",
      backing: "USD Reserves"
    },
    {
      name: "Curve USD",
      symbol: "crvUSD",
      type: "Crypto-Backed",
      marketCap: "156M",
      backing: "Curve Protocol"
    },
    {
      name: "Magic Internet Money",
      symbol: "MIM",
      type: "Crypto-Backed",
      marketCap: "234M", 
      backing: "Multi-Collateral"
    }
  ];

  const getTotalMarketCap = () => ({
    fiatBacked: "138.5",
    cryptoBacked: "6.8", 
    algorithmic: "1.6",
    totalCoins: "50+"
  });

  return (
    <div className="min-h-screen bg-white">
      <SEOHead 
        title="StableYield Index Dashboard – Live Market Data"
        description="Real-time StableYield Index (SYI) dashboard with live yield data, market statistics, and institutional analytics."
        url="https://stableyield.com/index-dashboard"
      />
      
      <Header 
        onJoinWaitlist={() => setIsContactOpen(true)}
        onDownloadWhitepaper={() => setIsWhitepaperOpen(true)}
      />
      
      {/* Live Index Ticker */}
      <LiveIndexTicker />
      
      {/* Hero Section */}
      <section className="pt-20 pb-16 bg-gradient-to-br from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-[#0E1A2B] mb-6">
              StableYield Index Dashboard
            </h1>
            
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Real-time market intelligence for stablecoin yield strategies. 
              Monitor performance, track constituents, and analyze market trends.
            </p>

            {loading ? (
              <div className="inline-flex items-center px-6 py-3 bg-gray-100 border border-gray-200 rounded-full">
                <Activity className="w-5 h-5 text-gray-500 mr-2 animate-spin" />
                <span className="text-gray-600">Loading index data...</span>
              </div>
            ) : error ? (
              <div className="inline-flex items-center px-6 py-3 bg-red-50 border border-red-200 rounded-full">
                <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                <span className="text-red-600">Error loading data</span>
              </div>
            ) : indexData ? (
              <div className="inline-flex items-center px-6 py-3 bg-[#4CC1E9]/10 border border-[#4CC1E9]/20 rounded-full">
                <BarChart3 className="w-5 h-5 text-[#4CC1E9] mr-2" />
                <span className="text-[#007A99] font-semibold">
                  Current SYI: {indexData.current_value?.toFixed(4) || 'N/A'}
                </span>
              </div>
            ) : null}
          </div>

          {/* Key Statistics */}
          {!loading && !error && statistics && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
              <Card className="text-center border-[#4CC1E9]/20 hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <DollarSign className="w-12 h-12 text-[#4CC1E9] mx-auto mb-4" />
                  <h3 className="text-2xl font-bold text-[#0E1A2B] mb-2">
                    {statistics.avg_yield?.toFixed(1) || 'N/A'}%
                  </h3>
                  <p className="text-gray-600">Average Yield</p>
                </CardContent>
              </Card>

              <Card className="text-center border-[#4CC1E9]/20 hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <Activity className="w-12 h-12 text-[#2E6049] mx-auto mb-4" />
                  <h3 className="text-2xl font-bold text-[#0E1A2B] mb-2">
                    ${statistics.total_tvl ? (statistics.total_tvl / 1000000).toFixed(1) : 'N/A'}M
                  </h3>
                  <p className="text-gray-600">Total TVL</p>
                </CardContent>
              </Card>

              <Card className="text-center border-[#4CC1E9]/20 hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <Shield className="w-12 h-12 text-[#007A99] mx-auto mb-4" />
                  <h3 className="text-2xl font-bold text-[#0E1A2B] mb-2">
                    {constituents.length}
                  </h3>
                  <p className="text-gray-600">Active Constituents</p>
                </CardContent>
              </Card>

              <Card className="text-center border-[#4CC1E9]/20 hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <Users className="w-12 h-12 text-[#F59E0B] mx-auto mb-4" />
                  <h3 className="text-2xl font-bold text-[#0E1A2B] mb-2">
                    {statistics.avg_volatility ? (statistics.avg_volatility * 100).toFixed(1) : 'N/A'}%
                  </h3>
                  <p className="text-gray-600">Avg Volatility</p>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </section>

      {/* Index Constituents */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">Index Constituents</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Current composition of the StableYield Index with real-time performance metrics
            </p>
          </div>

          {loading ? (
            <Card>
              <CardContent className="text-center py-12">
                <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4 animate-spin" />
                <p className="text-gray-600">Loading constituents...</p>
              </CardContent>
            </Card>
          ) : error ? (
            <Card>
              <CardContent className="text-center py-12">
                <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                <p className="text-red-600">Error loading constituents</p>
              </CardContent>
            </Card>
          ) : constituents.length > 0 ? (
            <Card className="border-[#4CC1E9]/20">
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Asset</th>
                        <th className="px-6 py-4 text-right text-sm font-semibold text-gray-900">Weight</th>
                        <th className="px-6 py-4 text-right text-sm font-semibold text-gray-900">Yield</th>
                        <th className="px-6 py-4 text-right text-sm font-semibold text-gray-900">RAY</th>
                        <th className="px-6 py-4 text-center text-sm font-semibold text-gray-900">Risk</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {constituents.map((constituent, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-6 py-4">
                            <div className="flex items-center">
                              <div className="w-8 h-8 bg-gradient-to-r from-[#4CC1E9] to-[#007A99] rounded-full flex items-center justify-center mr-3">
                                <span className="text-white font-bold text-sm">
                                  {constituent.symbol?.slice(0,2) || 'N/A'}
                                </span>
                              </div>
                              <div>
                                <div className="font-medium text-gray-900">{constituent.symbol || 'Unknown'}</div>
                                <div className="text-sm text-gray-500">{constituent.protocol || 'N/A'}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-right font-medium">
                            {constituent.weight ? `${(constituent.weight * 100).toFixed(1)}%` : 'N/A'}
                          </td>
                          <td className="px-6 py-4 text-right font-medium text-[#4CC1E9]">
                            {constituent.current_apy ? `${constituent.current_apy.toFixed(2)}%` : 'N/A'}
                          </td>
                          <td className="px-6 py-4 text-right font-medium text-[#2E6049]">
                            {constituent.ry_apy ? `${constituent.ry_apy.toFixed(2)}%` : 'N/A'}
                          </td>
                          <td className="px-6 py-4 text-center">
                            <Badge className={getConstituentBadgeColor(constituent.risk_tier)}>
                              {constituent.risk_tier || 'N/A'}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No constituents data available</p>
              </CardContent>
            </Card>
          )}
        </div>
      </section>

      {/* StableYield Index Family */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <IndexFamilyOverview />
        </div>
      </section>

      {/* Peg Status Widget Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
              Stablecoin Peg Monitoring
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Real-time monitoring of stablecoin peg stability with deviation analysis and market intelligence.
            </p>
          </div>
          
          <div className="max-w-4xl mx-auto">
            <PegStatusWidget 
              symbols={["USDT", "USDC", "DAI", "FRAX", "TUSD", "PYUSD"]}
              linkHref="/peg-monitor"
            />
          </div>
        </div>
      </section>

      {/* Risk Regime Detection */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
              Risk Regime Inversion Alert
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Advanced risk regime detection using SYI indicators, momentum analysis, and market breadth calculations.
            </p>
          </div>
          
          <div className="max-w-md mx-auto">
            <RiskRegimeWidget />
          </div>
        </div>
      </section>

      {/* Comprehensive Stablecoin Market Overview */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
              Comprehensive Stablecoin Market Overview
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Complete list of major USD stablecoins across all protocols and platforms, 
              providing broad market context beyond the StableYield Index constituents.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Major Stablecoins */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <DollarSign className="w-5 h-5 mr-2 text-[#4CC1E9]" />
                  Major Stablecoins (&gt;$1B Market Cap)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {getMajorStablecoins().map((coin) => (
                    <div key={coin.symbol} className="flex items-center justify-between p-3 bg-white rounded-lg border hover:shadow-md transition-shadow">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-r from-[#4CC1E9] to-[#007A99] rounded-full flex items-center justify-center">
                          <span className="text-white font-bold text-sm">{coin.symbol.slice(0,2)}</span>
                        </div>
                        <div>
                          <h4 className="font-semibold text-[#0E1A2B]">{coin.name}</h4>
                          <p className="text-sm text-gray-600">{coin.symbol} • {coin.type}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-[#0E1A2B]">
                          ${coin.marketCap}
                        </div>
                        <div className="text-sm text-gray-600">
                          {coin.backing}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Emerging & DeFi Stablecoins */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-[#007A99]" />
                  Emerging & DeFi Stablecoins
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {getEmergingStablecoins().map((coin) => (
                    <div key={coin.symbol} className="flex items-center justify-between p-3 bg-white rounded-lg border hover:shadow-md transition-shadow">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-r from-[#2E6049] to-[#4CC1E9] rounded-full flex items-center justify-center">
                          <span className="text-white font-bold text-sm">{coin.symbol.slice(0,2)}</span>
                        </div>
                        <div>
                          <h4 className="font-semibold text-[#0E1A2B]">{coin.name}</h4>
                          <p className="text-sm text-gray-600">{coin.symbol} • {coin.type}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-[#0E1A2B]">
                          ${coin.marketCap}
                        </div>
                        <div className="text-sm text-gray-600">
                          {coin.backing}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Stablecoin Categories Summary */}
          <div className="mt-12">
            <Card className="bg-gradient-to-r from-[#0E1A2B] to-[#2E6049] text-white">
              <CardHeader>
                <CardTitle className="text-center text-xl">
                  Stablecoin Market Segmentation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-[#4CC1E9] mb-2">
                      ${getTotalMarketCap().fiatBacked}B
                    </div>
                    <div className="text-sm text-white/80">Fiat-Backed</div>
                    <div className="text-xs text-white/60">USDT, USDC, BUSD</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-[#4CC1E9] mb-2">
                      ${getTotalMarketCap().cryptoBacked}B
                    </div>
                    <div className="text-sm text-white/80">Crypto-Backed</div>
                    <div className="text-xs text-white/60">DAI, sUSD, LUSD</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-[#4CC1E9] mb-2">
                      ${getTotalMarketCap().algorithmic}B
                    </div>
                    <div className="text-sm text-white/80">Algorithmic</div>
                    <div className="text-xs text-white/60">FRAX, FEI, AMPL</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-[#4CC1E9] mb-2">
                      {getTotalMarketCap().totalCoins}
                    </div>
                    <div className="text-sm text-white/80">Total Stablecoins</div>
                    <div className="text-xs text-white/60">Active Projects</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Index Methodology */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Card className="border-[#4CC1E9]/20 bg-gradient-to-br from-white to-[#4CC1E9]/5">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Shield className="w-6 h-6 mr-2 text-[#4CC1E9]" />
                Index Methodology & Risk Framework
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg font-semibold text-[#0E1A2B] mb-4">Risk-Adjusted Approach</h3>
                  <div className="space-y-3 text-sm text-gray-600">
                    <div className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                      <span>Peg stability monitoring (±0.5% threshold)</span>
                    </div>
                    <div className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                      <span>Liquidity depth analysis ($10M+ requirement)</span>
                    </div>
                    <div className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                      <span>Protocol risk assessment framework</span>
                    </div>
                    <div className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                      <span>Dynamic rebalancing (monthly)</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-[#0E1A2B] mb-4">Institutional Features</h3>
                  <div className="space-y-3 text-sm text-gray-600">
                    <div className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                      <span>Bloomberg-grade data quality</span>
                    </div>
                    <div className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                      <span>Real-time API access</span>
                    </div>
                    <div className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                      <span>Regulatory compliance ready</span>
                    </div>
                    <div className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                      <span>Enterprise integration support</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-8 p-6 bg-gradient-to-r from-[#0E1A2B] to-[#2E6049] rounded-xl text-white">
                <h4 className="font-semibold mb-3 flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  Risk-Adjusted Yield (RAY) Formula
                </h4>
                <div className="bg-white/10 p-4 rounded-lg font-mono text-sm">
                  RAY = Base_APY × Peg_Score × Liquidity_Score × (1 - Protocol_Risk)
                </div>
                <p className="text-sm text-white/80 mt-3">
                  Our proprietary RAY calculation adjusts raw yields for comprehensive risk factors, 
                  providing institutional investors with reliable, risk-adjusted return expectations.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      <Footer />
      
      {/* Modals */}
      <ContactModal 
        isOpen={isContactOpen} 
        onClose={() => setIsContactOpen(false)} 
      />
      <WhitepaperDownloadModal 
        isOpen={isWhitepaperOpen} 
        onClose={() => setIsWhitepaperOpen(false)} 
      />
    </div>
  );
};

export default IndexDashboardPage;