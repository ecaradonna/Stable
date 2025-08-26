import React, { useState, useEffect } from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import SEOHead from "../components/SEOHead";
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

  const fetchAllData = async () => {
    try {
      // Dynamic backend URL detection
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
      
      const backendUrl = getBackendURL();
      
      // Fetch current index data
      const indexResponse = await fetch(`${backendUrl}/api/index/current`);
      const indexData = await indexResponse.json();
      setIndexData(indexData);
      
      // Fetch constituents
      const constituentsResponse = await fetch(`${backendUrl}/api/index/constituents`);
      const constituentsData = await constituentsResponse.json();
      setConstituents(constituentsData.constituents || []);
      
      // Fetch statistics
      const statsResponse = await fetch(`${backendUrl}/api/index/statistics?days=7`);
      const statsData = await statsResponse.json();
      setStatistics(statsData);
      
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
    
    // Refresh data every 60 seconds
    const interval = setInterval(fetchAllData, 60000);
    return () => clearInterval(interval);
  }, []);

  const formatMarketCap = (value) => {
    if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
    return `$${value.toLocaleString()}`;
  };

  const getScoreColor = (score) => {
    if (score >= 0.9) return 'text-green-600';
    if (score >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBadge = (score) => {
    if (score >= 0.9) return 'bg-green-100 text-green-800';
    if (score >= 0.7) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white">
        <Header />
        <div className="pt-20 pb-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <div className="animate-pulse">
                <div className="h-8 bg-gray-200 rounded mb-4"></div>
                <div className="h-4 bg-gray-200 rounded mb-8 max-w-2xl mx-auto"></div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="h-32 bg-gray-200 rounded"></div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <SEOHead 
        title="Live StableYield Index Dashboard – Real-Time Stablecoin Analytics"
        description="Live StableYield Index (SYI) dashboard with real-time risk-adjusted yields, constituent analysis, and historical performance data for major stablecoins."
        url="https://stableyield.com/index-dashboard"
      />
      <Header 
        onJoinWaitlist={() => setIsContactOpen(true)}
        onDownloadWhitepaper={() => setIsWhitepaperOpen(true)}
      />
      
      {/* Hero Section */}
      <section className="pt-20 pb-8 bg-gradient-to-br from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center px-4 py-2 bg-[#4CC1E9]/10 border border-[#4CC1E9]/20 rounded-full mb-6">
              <BarChart3 className="w-4 h-4 text-[#4CC1E9] mr-2" />
              <span className="text-[#007A99] font-semibold text-sm">Real-Time Index Dashboard</span>
            </div>
            
            <h1 className="text-4xl md:text-5xl font-bold text-[#0E1A2B] mb-4">
              StableYield Index Dashboard
            </h1>
            
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Live market-cap weighted benchmark of risk-adjusted stablecoin yields
            </p>
            
            <div className="max-w-2xl mx-auto">
              <LiveIndexTicker />
            </div>
          </div>
        </div>
      </section>

      {/* Statistics Cards */}
      {statistics && (
        <section className="py-8 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
                    <TrendingUp className="w-4 h-4 mr-2" />
                    Current Value
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-[#0E1A2B]">
                    {indexData?.value?.toFixed(4)}%
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
                    <BarChart3 className="w-4 h-4 mr-2" />
                    7-Day Average
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-[#0E1A2B]">
                    {statistics.average_value?.toFixed(4)}%
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
                    <Activity className="w-4 h-4 mr-2" />
                    Volatility
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-[#0E1A2B]">
                    {statistics.volatility ? (statistics.volatility * 100).toFixed(2) : '0.00'}%
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
                    <Users className="w-4 h-4 mr-2" />
                    Constituents
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-[#0E1A2B]">
                    {constituents.length}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>
      )}

      {/* Constituents Table */}
      <section className="py-8 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-[#0E1A2B] mb-6">Index Constituents</h2>
          
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Asset
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Weight
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Market Cap
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Raw APY
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Risk-Adjusted Yield
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Risk Scores
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {constituents.map((constituent, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="w-8 h-8 bg-gradient-to-br from-[#4CC1E9] to-[#007A99] rounded-full flex items-center justify-center text-white font-bold text-sm mr-3">
                              {constituent.symbol.charAt(0)}
                            </div>
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {constituent.symbol}
                              </div>
                              <div className="text-sm text-gray-500">{constituent.name}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {(constituent.weight * 100).toFixed(2)}%
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {formatMarketCap(constituent.market_cap)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {constituent.raw_apy.toFixed(2)}%
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-bold text-[#4CC1E9]">
                            {constituent.ray.toFixed(4)}%
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex space-x-2">
                            <Badge className={getScoreBadge(constituent.peg_score)}>
                              Peg: {(constituent.peg_score * 100).toFixed(0)}%
                            </Badge>
                            <Badge className={getScoreBadge(constituent.liquidity_score)}>
                              Liq: {(constituent.liquidity_score * 100).toFixed(0)}%
                            </Badge>
                            <Badge className={getScoreBadge(constituent.counterparty_score)}>
                              Risk: {(constituent.counterparty_score * 100).toFixed(0)}%
                            </Badge>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
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

      {/* Methodology Note */}
      <section className="py-8 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Card className="border-[#4CC1E9]/20 bg-gradient-to-r from-[#4CC1E9]/5 to-[#007A99]/5">
            <CardContent className="p-6">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-gradient-to-br from-[#4CC1E9] to-[#007A99] rounded-lg flex items-center justify-center">
                    <BarChart3 className="w-6 h-6 text-white" />
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-[#0E1A2B] mb-2">Index Methodology</h3>
                  <p className="text-gray-700 mb-4">
                    The StableYield Index is calculated as a market-cap weighted average of Risk-Adjusted Yields (RAY). 
                    Each constituent's RAY is computed using: <strong>RAY = APY × f(Peg Stability, Liquidity, Counterparty Risk)</strong>
                  </p>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <div className="flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                      Updates every 1 minute
                    </div>
                    <div className="flex items-center">
                      <AlertCircle className="w-4 h-4 text-yellow-500 mr-1" />
                      Demo data - production APIs needed for accuracy
                    </div>
                  </div>
                </div>
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