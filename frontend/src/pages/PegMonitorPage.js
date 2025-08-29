import React, { useState, useEffect } from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import SEOHead from "../components/SEOHead";
import ContactModal from "../components/ContactModal";
import WhitepaperDownloadModal from "../components/WhitepaperDownloadModal";
import PegStatusWidget from "../components/PegStatusWidget";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { 
  Shield, 
  AlertTriangle, 
  Activity, 
  CheckCircle,
  TrendingDown,
  TrendingUp,
  Clock,
  Bell,
  FileText,
  BarChart3,
  Eye
} from "lucide-react";

const PegMonitorPage = () => {
  const [isContactOpen, setIsContactOpen] = useState(false);
  const [isWhitepaperOpen, setIsWhitepaperOpen] = useState(false);
  const [chartTimeframe, setChartTimeframe] = useState('7D');
  const [chartData, setChartData] = useState([]);

  // Generate sample peg chart data
  useEffect(() => {
    const generateChartData = () => {
      const timeframes = {
        '1H': { points: 60, interval: 'minute' },
        '24H': { points: 24, interval: 'hour' },
        '7D': { points: 7, interval: 'day' },
        '30D': { points: 30, interval: 'day' }
      };
      
      const config = timeframes[chartTimeframe];
      const data = [];
      
      for (let i = 0; i < config.points; i++) {
        const date = new Date();
        date.setHours(date.getHours() - (config.points - i));
        
        data.push({
          time: date.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit',
            ...(config.interval === 'day' && { month: 'short', day: 'numeric' })
          }),
          USDT: (Math.random() - 0.5) * 4, // -2 to +2 bps
          USDC: (Math.random() - 0.5) * 3, // -1.5 to +1.5 bps  
          DAI: (Math.random() - 0.5) * 6,  // -3 to +3 bps
          FRAX: (Math.random() - 0.5) * 200 + 50, // More volatile, 50 +/- 100 bps
        });
      }
      
      setChartData(data);
    };
    
    generateChartData();
  }, [chartTimeframe]);

  // Mock peg data - replace with real API calls
  const pegSummary = {
    stable: 5,
    neutral: 1, 
    depegged: 2
  };

  const stablecoinData = [
    {
      symbol: "USDT",
      name: "Tether",
      price: 0.9998,
      deviation: -0.02,
      status: "stable",
      volume24h: "$42.1B",
      marketCap: "$94.2B",
      lastUpdate: "2 mins ago"
    },
    {
      symbol: "USDC", 
      name: "USD Coin",
      price: 1.0001,
      deviation: 0.01,
      status: "stable",
      volume24h: "$18.7B", 
      marketCap: "$27.8B",
      lastUpdate: "1 min ago"
    },
    {
      symbol: "DAI",
      name: "Dai Stablecoin",
      price: 0.9995,
      deviation: -0.05,
      status: "neutral",
      volume24h: "$892M",
      marketCap: "$5.6B", 
      lastUpdate: "3 mins ago"
    },
    {
      symbol: "FRAX",
      name: "Frax",
      price: 1.0089,
      deviation: 0.89,
      status: "depegged",
      volume24h: "$156M",
      marketCap: "$890M",
      lastUpdate: "1 min ago"
    },
    {
      symbol: "TUSD",
      name: "TrueUSD", 
      price: 0.9876,
      deviation: -1.24,
      status: "depegged",
      volume24h: "$78M",
      marketCap: "$510M",
      lastUpdate: "4 mins ago"
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'stable': return 'text-[#1F4FFF] bg-[#1F4FFF]/10 border-[#1F4FFF]/20';
      case 'neutral': return 'text-[#9FA6B2] bg-[#9FA6B2]/10 border-[#9FA6B2]/20';
      case 'depegged': return 'text-[#D64545] bg-[#D64545]/10 border-[#D64545]/20';
      default: return 'text-[#9FA6B2] bg-[#9FA6B2]/10 border-[#9FA6B2]/20';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'stable': return <CheckCircle className="w-4 h-4" />;
      case 'neutral': return <Activity className="w-4 h-4" />;
      case 'depegged': return <AlertTriangle className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'stable': return 'Stable';
      case 'neutral': return 'Neutral';
      case 'depegged': return 'Depegged';
      default: return 'Unknown';
    }
  };

  const getDeviationColor = (deviation) => {
    const absDeviation = Math.abs(deviation);
    if (absDeviation <= 0.1) return 'text-[#1F4FFF]';
    if (absDeviation <= 0.5) return 'text-[#9FA6B2]';
    return 'text-[#D64545]';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <SEOHead 
        title="Peg Monitor - Real-Time Stablecoin Peg Stability Tracking"
        description="Monitor every major stablecoin. Spot deviations early, set alerts, protect capital. Real-time peg stability monitoring with institutional-grade precision."
        keywords="stablecoin peg, depeg monitoring, peg stability, stablecoin tracking, real-time alerts"
      />
      
      <Header 
        onJoinWaitlist={() => setIsContactOpen(true)}
        onDownloadWhitepaper={() => setIsWhitepaperOpen(true)}
      />

      <main>
        {/* Hero Section */}
        <section className="relative py-20 lg:py-32 overflow-hidden bg-gradient-to-br from-gray-50 to-white">
          <div className="absolute top-20 right-10 w-64 h-64 bg-gradient-to-br from-[#1F4FFF]/10 to-[#D64545]/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 left-10 w-48 h-48 bg-gradient-to-br from-[#1F4FFF]/5 to-[#E47C3C]/10 rounded-full blur-3xl"></div>

          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <Badge className="bg-[#1F4FFF]/10 text-[#1F4FFF] mb-6 px-4 py-2">
                <Eye className="w-4 h-4 mr-2" />
                Real-Time Monitoring
              </Badge>
              
              <h1 className="text-4xl md:text-6xl font-bold text-[#0E1A2B] mb-6 leading-tight">
                Peg Stability in 
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#1F4FFF] to-[#D64545]">
                  {" "}Real Time
                </span>
              </h1>
              
              <p className="text-xl text-gray-600 max-w-4xl mx-auto mb-12 leading-relaxed">
                Monitor every major stablecoin. Spot deviations early, set alerts, protect capital. 
                Professional-grade peg monitoring with institutional precision.
              </p>

              {/* Peg Status Summary */}
              <div className="bg-white rounded-2xl border border-gray-200 p-8 max-w-2xl mx-auto mb-8 shadow-lg">
                <h3 className="text-lg font-semibold text-[#0E1A2B] mb-6">Current Market Status</h3>
                <div className="grid grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="w-12 h-12 bg-[#1F4FFF]/10 rounded-full flex items-center justify-center mx-auto mb-3">
                      <CheckCircle className="w-6 h-6 text-[#1F4FFF]" />
                    </div>
                    <div className="text-2xl font-bold text-[#1F4FFF]">{pegSummary.stable}</div>
                    <div className="text-sm text-gray-600">Stable</div>
                  </div>
                  <div className="text-center">
                    <div className="w-12 h-12 bg-[#9FA6B2]/10 rounded-full flex items-center justify-center mx-auto mb-3">
                      <Activity className="w-6 h-6 text-[#9FA6B2]" />
                    </div>
                    <div className="text-2xl font-bold text-[#9FA6B2]">{pegSummary.neutral}</div>
                    <div className="text-sm text-gray-600">Neutral</div>
                  </div>
                  <div className="text-center">
                    <div className="w-12 h-12 bg-[#D64545]/10 rounded-full flex items-center justify-center mx-auto mb-3">
                      <AlertTriangle className="w-6 h-6 text-[#D64545]" />
                    </div>
                    <div className="text-2xl font-bold text-[#D64545]">{pegSummary.depegged}</div>
                    <div className="text-sm text-gray-600">Depegged</div>
                  </div>
                </div>
              </div>

              <Button 
                className="bg-[#E47C3C] hover:bg-[#E47C3C]/90 text-white font-semibold px-8 py-4 text-lg rounded-xl shadow-lg"
                onClick={() => setIsContactOpen(true)}
              >
                <Bell className="w-5 h-5 mr-2" />
                Set My Alerts
              </Button>
            </div>
          </div>
        </section>

        {/* Peg Dashboard */}
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
                Live Peg Monitor Dashboard
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Real-time tracking of stablecoin prices with deviation analysis and risk scoring
              </p>
            </div>
            
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xl text-[#0E1A2B]">Stablecoin Peg Status</CardTitle>
                  <Badge className="bg-[#1F4FFF]/10 text-[#1F4FFF]">
                    <Clock className="w-3 h-3 mr-1" />
                    Live Data
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-100">
                      <tr>
                        <th className="text-left py-4 px-6 text-sm font-semibold text-gray-700">Asset</th>
                        <th className="text-right py-4 px-6 text-sm font-semibold text-gray-700">Price</th>
                        <th className="text-center py-4 px-6 text-sm font-semibold text-gray-700">Deviation</th>
                        <th className="text-center py-4 px-6 text-sm font-semibold text-gray-700">Status</th>
                        <th className="text-right py-4 px-6 text-sm font-semibold text-gray-700">24h Volume</th>
                        <th className="text-right py-4 px-6 text-sm font-semibold text-gray-700">Market Cap</th>
                        <th className="text-center py-4 px-6 text-sm font-semibold text-gray-700">Last Update</th>
                      </tr>
                    </thead>
                    <tbody>
                      {stablecoinData.map((coin, index) => (
                        <tr key={index} className="border-b border-gray-50 hover:bg-gray-25">
                          <td className="py-4 px-6">
                            <div>
                              <div className="font-semibold text-[#0E1A2B]">{coin.symbol}</div>
                              <div className="text-sm text-gray-500">{coin.name}</div>
                            </div>
                          </td>
                          <td className="py-4 px-6 text-right">
                            <div className="font-mono font-semibold text-[#0E1A2B]">
                              ${coin.price.toFixed(4)}
                            </div>
                          </td>
                          <td className="py-4 px-6 text-center">
                            <div className={`font-semibold ${getDeviationColor(coin.deviation)}`}>
                              {coin.deviation > 0 ? '+' : ''}{coin.deviation.toFixed(2)}%
                            </div>
                          </td>
                          <td className="py-4 px-6 text-center">
                            <Badge className={`${getStatusColor(coin.status)} border font-medium`}>
                              <div className="flex items-center space-x-1">
                                {getStatusIcon(coin.status)}
                                <span>{getStatusText(coin.status)}</span>
                              </div>
                            </Badge>
                          </td>
                          <td className="py-4 px-6 text-right">
                            <div className="font-semibold text-[#0E1A2B]">{coin.volume24h}</div>
                          </td>
                          <td className="py-4 px-6 text-right">
                            <div className="font-semibold text-[#0E1A2B]">{coin.marketCap}</div>
                          </td>
                          <td className="py-4 px-6 text-center">
                            <div className="text-sm text-gray-500">{coin.lastUpdate}</div>
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

        {/* Graph Section */}
        <section className="py-20 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
                Historical Peg Analysis
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Track peg history across different time periods with advanced deviation analytics
              </p>
            </div>
            
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center space-x-2">
                    <BarChart3 className="w-5 h-5 text-[#1F4FFF]" />
                    <span>Peg Deviation History</span>
                  </CardTitle>
                  <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm">1H</Button>
                    <Button variant="outline" size="sm">24H</Button>
                    <Button variant="outline" size="sm" className="bg-[#1F4FFF] text-white">7D</Button>
                    <Button variant="outline" size="sm">30D</Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {/* Placeholder for chart */}
                <div className="h-64 bg-gradient-to-br from-[#1F4FFF]/5 to-[#9FA6B2]/5 rounded-lg flex items-center justify-center border border-gray-100">
                  <div className="text-center">
                    <BarChart3 className="w-12 h-12 text-[#9FA6B2] mx-auto mb-4" />
                    <div className="text-[#9FA6B2] font-medium">Interactive Peg Chart</div>
                    <div className="text-sm text-gray-500 mt-1">Real-time deviation tracking across time periods</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Enhanced Peg Widget */}
        <section className="py-20 bg-white">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
                Comprehensive Peg Monitoring
              </h2>
              <p className="text-gray-600">
                Advanced monitoring with multi-source price feeds and deviation analysis
              </p>
            </div>
            
            <PegStatusWidget 
              symbols={["USDT", "USDC", "DAI", "FRAX", "TUSD", "PYUSD"]}
              linkHref="/peg-monitor"
              onCreateAlert={() => setIsContactOpen(true)}
            />
          </div>
        </section>

        {/* Report Section */}
        <section className="py-20 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <Card className="border-2 border-[#1F4FFF]/20 bg-[#1F4FFF]/5">
              <CardContent className="p-12 text-center">
                <div className="w-20 h-20 bg-[#1F4FFF]/20 rounded-full flex items-center justify-center mx-auto mb-6">
                  <FileText className="w-10 h-10 text-[#1F4FFF]" />
                </div>
                <h3 className="text-2xl font-bold text-[#0E1A2B] mb-4">
                  Peg Intelligence Report
                </h3>
                <p className="text-gray-600 max-w-2xl mx-auto mb-8">
                  Get weekly comprehensive analysis of peg stability trends, risk factors, 
                  and market dynamics across all major stablecoins.
                </p>
                <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
                  <Button 
                    className="bg-[#1F4FFF] hover:bg-[#1F4FFF]/90 text-white font-semibold px-6 py-3 rounded-xl"
                    onClick={() => setIsContactOpen(true)}
                  >
                    Subscribe Now
                  </Button>
                  <Button 
                    variant="outline" 
                    className="border-[#1F4FFF] text-[#1F4FFF] hover:bg-[#1F4FFF] hover:text-white px-6 py-3 rounded-xl"
                  >
                    View Sample Report
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Call-to-Action */}
        <section className="py-20 bg-gradient-to-r from-[#1F4FFF] to-[#D64545]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-white mb-4">
                Never Miss a Peg Event Again
              </h2>
              <p className="text-xl text-white/90 max-w-3xl mx-auto mb-8">
                Set custom alerts, monitor in real-time, and protect your portfolio with 
                institutional-grade peg monitoring infrastructure.
              </p>
              
              <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
                <Button 
                  className="bg-white text-[#1F4FFF] hover:bg-gray-100 font-semibold px-8 py-4 text-lg rounded-xl"
                  onClick={() => setIsContactOpen(true)}
                >
                  <Bell className="w-5 h-5 mr-2" />
                  Set Up Alerts
                </Button>
                <Button 
                  variant="outline" 
                  className="border-2 border-white text-white hover:bg-white hover:text-[#1F4FFF] font-semibold px-8 py-4 text-lg rounded-xl"
                  onClick={() => window.location.href = '/api-documentation'}
                >
                  API Access
                </Button>
              </div>
            </div>
          </div>
        </section>
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

export default PegMonitorPage;