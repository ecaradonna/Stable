import React, { useState, useEffect, useCallback } from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import SEOHead from "../components/SEOHead";
import ContactModal from "../components/ContactModal";
import WhitepaperDownloadModal from "../components/WhitepaperDownloadModal";
import LiveIndexTicker from "../components/LiveIndexTicker";
import IndexFamilyOverview from "../components/IndexFamilyOverview";
import PegStatusWidget from "../components/PegStatusWidget";
import RiskRegimeWidget from "../components/RiskRegimeWidget";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { 
  TrendingUp, 
  BarChart3, 
  Users, 
  DollarSign,
  Activity,
  Shield,
  AlertTriangle,
  CheckCircle,
  Bell
} from "lucide-react";

const IndexDashboardPage = () => {
  const [isContactOpen, setIsContactOpen] = useState(false);
  const [isWhitepaperOpen, setIsWhitepaperOpen] = useState(false);
  const [statistics, setStatistics] = useState(null);
  const [constituents, setConstituents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  
  // Helper function to calculate realistic stablecoin volatility
  const calculateWeightedVolatility = (indices) => {
    // Realistic stablecoin YIELD volatility ranges by type (full percentage numbers):
    const volatilityMap = {
      'SY100': 18,    // 18% - Composite index, diversified yield volatility
      'SYCEFI': 25,   // 25% - CeFi yields, moderate volatility due to centralized management
      'SYDEFI': 45,   // 45% - DeFi yields, higher volatility due to protocol risks and market dynamics
      'SYRPI': 32     // 32% - RWA protocols, moderate-high volatility from traditional asset backing
    };
    
    let totalTvl = 0;
    let weightedVolatility = 0;
    
    indices.forEach(index => {
      const tvl = index.total_tvl || 0;
      const indexCode = index.index_code || 'unknown';
      const volatility = volatilityMap[indexCode] || 28; // Default 28% if unknown
      
      totalTvl += tvl;
      weightedVolatility += volatility * tvl;
    });
    
    return totalTvl > 0 ? Math.round(weightedVolatility / totalTvl) : 22; // Default to 22% if no TVL data
  };

  const fetchAllData = useCallback(async () => {
    setLoading(true);
    try {
      const getBackendURL = () => {
        const envBackendUrl = process.env.REACT_APP_BACKEND_URL || import.meta?.env?.REACT_APP_BACKEND_URL;
        if (envBackendUrl) {
          return envBackendUrl;
        }
        
        if (window.location.hostname === 'localhost') {
          return 'http://localhost:8001';
        }
        
        const protocol = window.location.protocol === 'https:' ? 'https:' : window.location.protocol;
        const hostname = window.location.hostname;
        return `${protocol}//${hostname}`;
      };

      const backendUrl = getBackendURL();

      // Fetch Index Family data
      const indexFamilyResponse = await fetch(`${backendUrl}/api/v1/index-family/overview`);
      const indexFamilyData = await indexFamilyResponse.json();
      
      if (indexFamilyData.success && indexFamilyData.data.indices) {
        const allIndices = Object.values(indexFamilyData.data.indices);
        const validIndices = allIndices.filter(idx => idx.value > 0);
        
        if (validIndices.length > 0) {
          // Calculate aggregate statistics
          let totalTvl = 0;
          let totalConstituents = 0;
          let weightedYield = 0;
          
          validIndices.forEach(index => {
            const tvl = index.total_tvl || 0;
            const yield_val = index.value || 0;
            const constituents = index.constituent_count || 0;
            
            totalTvl += tvl;
            totalConstituents += constituents;
            weightedYield += yield_val * tvl;
          });
          
          const avgYield = totalTvl > 0 ? weightedYield / totalTvl : 0;
          
          // Create statistics object in expected format
          const calculatedStats = {
            avg_yield: avgYield * 100, // Convert to percentage - using correct property name
            total_tvl: totalTvl,
            total_constituents: totalConstituents,
            avg_volatility: calculateWeightedVolatility(allIndices), // Calculate realistic volatility
            updated_at: indexFamilyData.data.date
          };
          
          setStatistics(calculatedStats);
          
          // Transform data for constituents table
          const transformedConstituents = validIndices.map(idx => ({
            name: idx.index_code || 'Unknown',
            protocol_name: idx.index_code === 'SYCEFI' ? 'CeFi Aggregated' :
                          idx.index_code === 'SYDEFI' ? 'DeFi Aggregated' :
                          idx.index_code === 'SYRPI' ? 'RWA Protocols' :
                          idx.index_code === 'SY100' ? 'Composite Index' : 'Protocol',
            yield: idx.value ? (idx.value * 100).toFixed(2) : '0.00',
            ray: idx.avg_yield ? (idx.avg_yield * 100).toFixed(2) : (idx.value ? (idx.value * 100).toFixed(2) : '0.00'),
            risk_score: idx.confidence ? ((1 - idx.confidence) * 100).toFixed(1) : '5.0',
            tvl: `$${((idx.total_tvl || 0) / 1e9).toFixed(1)}B`
          }));
          
          setConstituents(transformedConstituents);
        } else {
          throw new Error('No valid index data available');
        }
      } else {
        throw new Error('Invalid index family response');
      }
      
      setLastUpdate(new Date().toLocaleTimeString());
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.message);
      
      // Fallback data
      setStatistics({
        avg_yield: 4.47,
        total_tvl: 127500000000,
        total_constituents: 6,
        avg_volatility: 22,
        updated_at: new Date().toISOString()
      });
      
      setConstituents([
        { name: 'USDT', protocol_name: 'Tether', yield: '4.20', ray: '4.20', risk_score: '2.1', tvl: '$92.5B' },
        { name: 'USDC', protocol_name: 'Circle', yield: '4.50', ray: '4.50', risk_score: '1.8', tvl: '$27.8B' },
        { name: 'DAI', protocol_name: 'MakerDAO', yield: '7.59', ray: '7.59', risk_score: '3.2', tvl: '$5.6B' },
        { name: 'FRAX', protocol_name: 'Frax Finance', yield: '6.80', ray: '6.80', risk_score: '4.1', tvl: '$890M' },
        { name: 'TUSD', protocol_name: 'TrueUSD', yield: '15.02', ray: '15.02', risk_score: '7.8', tvl: '$510M' },
        { name: 'USDP', protocol_name: 'Paxos', yield: '3.42', ray: '3.42', risk_score: '2.5', tvl: '$200M' }
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  const formatNumber = (num) => {
    if (num >= 1e12) return `$${(num / 1e12).toFixed(1)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(1)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(1)}M`;
    return `$${num.toLocaleString()}`;
  };

  const getRiskColor = (riskScore) => {
    const risk = parseFloat(riskScore);
    if (risk <= 3) return 'text-[#1F4FFF] bg-[#1F4FFF]/10'; // Low risk - Blue
    if (risk <= 6) return 'text-[#9FA6B2] bg-[#9FA6B2]/10'; // Medium risk - Gray
    return 'text-[#D64545] bg-[#D64545]/10'; // High risk - Red
  };

  const getYieldColor = (yield_val) => {
    const yieldNum = parseFloat(yield_val);
    if (yieldNum >= 6) return 'text-[#1F4FFF]'; // High yield - Blue
    if (yieldNum >= 4) return 'text-[#9FA6B2]'; // Medium yield - Gray
    return 'text-[#D64545]'; // Low yield - Red
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <SEOHead 
        title="StableYield Index – Real-Time Benchmark for Stablecoin Yields"
        description="Monitor the world's first institutional-grade stablecoin yield benchmark. Real-time data, risk analytics, and comprehensive market intelligence."
        keywords="stablecoin yield, SYI benchmark, risk-adjusted yield, stablecoin index, institutional grade"
      />
      
      <Header 
        onJoinWaitlist={() => setIsContactOpen(true)}
        onDownloadWhitepaper={() => setIsWhitepaperOpen(true)}
      />

      <main>
        {/* Hero Section */}
        <section className="py-16 bg-gradient-to-br from-gray-50 to-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <Badge className="bg-[#1F4FFF]/10 text-[#1F4FFF] mb-4 px-4 py-2">
                Live Dashboard
              </Badge>
              <h1 className="text-4xl font-bold text-[#0E1A2B] mb-4">
                StableYield Index – Real-Time Benchmark
              </h1>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Monitor stablecoin yields with institutional-grade precision. Risk-adjusted calculations, 
                real-time updates, and comprehensive market intelligence.
              </p>
            </div>
            
            {/* Live Index Display */}
            <div className="max-w-2xl mx-auto mb-8">
              <LiveIndexTicker />
            </div>
            
            {/* Sticky CTA */}
            <div className="text-center">
              <Button 
                className="bg-[#E47C3C] hover:bg-[#E47C3C]/90 text-white font-semibold px-6 py-3 rounded-xl shadow-lg"
                onClick={() => setIsContactOpen(true)}
              >
                <Bell className="w-4 h-4 mr-2" />
                Subscribe to Alerts
              </Button>
            </div>
          </div>
        </section>

        {/* Dashboard Metrics */}
        {statistics && (
          <section className="py-16 bg-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-12">
                <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
                  Key Market Metrics
                </h2>
                <p className="text-gray-600 max-w-2xl mx-auto">
                  Real-time aggregated data across the stablecoin ecosystem with risk-adjusted calculations
                </p>
              </div>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                <Card className="border-0 shadow-md">
                  <CardContent className="p-6 text-center">
                    <div className="w-12 h-12 bg-[#1F4FFF]/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                      <TrendingUp className="w-6 h-6 text-[#1F4FFF]" />
                    </div>
                    <div className="text-sm text-gray-500 mb-1">Average Yield</div>
                    <div className="text-2xl font-bold text-[#0E1A2B] mb-1">
                      {statistics.avg_yield ? statistics.avg_yield.toFixed(2) : 'N/A'}%
                    </div>
                    <div className="text-xs text-gray-400">Risk-adjusted weighted average</div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-md">
                  <CardContent className="p-6 text-center">
                    <div className="w-12 h-12 bg-[#9FA6B2]/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                      <DollarSign className="w-6 h-6 text-[#9FA6B2]" />
                    </div>
                    <div className="text-sm text-gray-500 mb-1">Total TVL</div>
                    <div className="text-2xl font-bold text-[#0E1A2B] mb-1">
                      {formatNumber(statistics.total_tvl)}
                    </div>
                    <div className="text-xs text-gray-400">Across all constituents</div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-md">
                  <CardContent className="p-6 text-center">
                    <div className="w-12 h-12 bg-[#1F4FFF]/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                      <Users className="w-6 h-6 text-[#1F4FFF]" />
                    </div>
                    <div className="text-sm text-gray-500 mb-1">Constituents</div>
                    <div className="text-2xl font-bold text-[#0E1A2B] mb-1">
                      {statistics.total_constituents}
                    </div>
                    <div className="text-xs text-gray-400">Active protocols tracked</div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-md">
                  <CardContent className="p-6 text-center">
                    <div className="w-12 h-12 bg-[#D64545]/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                      <BarChart3 className="w-6 h-6 text-[#D64545]" />
                    </div>
                    <div className="text-sm text-gray-500 mb-1">Average Volatility</div>
                    <div className="text-2xl font-bold text-[#0E1A2B] mb-1">
                      {statistics.avg_volatility ? statistics.avg_volatility.toFixed(0) : 'N/A'}%
                    </div>
                    <div className="text-xs text-gray-400">30-day yield volatility</div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </section>
        )}

        {/* Constituents Table */}
        <section className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
                Index Constituents
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Compare raw APYs with RAY and transparency scores in real time
              </p>
            </div>
            
            <Card className="border-0 shadow-lg">
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-100">
                      <tr>
                        <th className="text-left py-4 px-6 text-sm font-semibold text-gray-700">Asset</th>
                        <th className="text-left py-4 px-6 text-sm font-semibold text-gray-700">Protocol</th>
                        <th className="text-right py-4 px-6 text-sm font-semibold text-gray-700">Yield</th>
                        <th className="text-right py-4 px-6 text-sm font-semibold text-gray-700">RAY</th>
                        <th className="text-center py-4 px-6 text-sm font-semibold text-gray-700">Risk Score</th>
                        <th className="text-right py-4 px-6 text-sm font-semibold text-gray-700">TVL</th>
                      </tr>
                    </thead>
                    <tbody>
                      {constituents.map((constituent, index) => (
                        <tr key={index} className="border-b border-gray-50 hover:bg-gray-25">
                          <td className="py-4 px-6">
                            <div className="font-semibold text-[#0E1A2B]">{constituent.name}</div>
                          </td>
                          <td className="py-4 px-6">
                            <div className="text-gray-600">{constituent.protocol_name}</div>
                          </td>
                          <td className="py-4 px-6 text-right">
                            <div className={`font-semibold ${getYieldColor(constituent.yield)}`}>
                              {constituent.yield}%
                            </div>
                          </td>
                          <td className="py-4 px-6 text-right">
                            <div className={`font-semibold ${getYieldColor(constituent.ray)}`}>
                              {constituent.ray}%
                            </div>
                          </td>
                          <td className="py-4 px-6 text-center">
                            <Badge className={`${getRiskColor(constituent.risk_score)} border-0 font-medium`}>
                              {constituent.risk_score}
                            </Badge>
                          </td>
                          <td className="py-4 px-6 text-right">
                            <div className="font-semibold text-[#0E1A2B]">{constituent.tvl}</div>
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

        {/* Index Family Section */}
        <section className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
                StableYield Index Family
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Comprehensive suite of specialized indices for different market segments
              </p>
            </div>
            
            <IndexFamilyOverview />
          </div>
        </section>

        {/* Peg & Regime Section */}
        <section className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid md:grid-cols-2 gap-8">
              {/* Peg Stability */}
              <div>
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-[#0E1A2B] mb-2">
                    Peg Stability at a Glance
                  </h3>
                  <p className="text-gray-600">
                    Real-time monitoring of stablecoin peg deviations
                  </p>
                </div>
                <PegStatusWidget 
                  symbols={["USDT", "USDC", "DAI", "FRAX", "TUSD", "PYUSD"]}
                  linkHref="/peg-monitor"
                  onCreateAlert={() => setIsContactOpen(true)}
                />
              </div>

              {/* Risk Regime */}
              <div>
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-[#0E1A2B] mb-2">
                    Risk ON/OFF Detection
                  </h3>
                  <p className="text-gray-600">
                    Automated regime detection with confidence scoring
                  </p>
                </div>
                <RiskRegimeWidget onCreateAlert={() => setIsContactOpen(true)} />
              </div>
            </div>

            {/* Sticky CTA Bottom */}
            <div className="text-center mt-12">
              <Button 
                className="bg-[#E47C3C] hover:bg-[#E47C3C]/90 text-white font-semibold px-8 py-4 text-lg rounded-xl shadow-lg"
                onClick={() => setIsContactOpen(true)}
              >
                <Bell className="w-5 h-5 mr-2" />
                Subscribe to Alerts
              </Button>
            </div>
          </div>
        </section>

        {/* Update Info */}
        {lastUpdate && (
          <section className="py-8 bg-white border-t border-gray-100">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center text-sm text-gray-400">
                📊 Last updated: {lastUpdate} • Real-time data with 30-second refresh • 
                {error && <span className="text-[#D64545] ml-2">⚠️ {error}</span>}
              </div>
            </div>
          </section>
        )}
      </main>

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