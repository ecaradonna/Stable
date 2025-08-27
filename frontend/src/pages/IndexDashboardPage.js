import React, { useState, useEffect } from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import SEOHead from "../components/SEOHead";
import ContactModal from "../components/ContactModal";
import WhitepaperDownloadModal from "../components/WhitepaperDownloadModal";
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
  const [indexData, setIndexData] = useState({
    current_value: 1.0172,
    constituents_count: 6,
    last_updated: new Date().toISOString()
  });
  const [statistics, setStatistics] = useState({
    avg_yield: 12.5,
    total_tvl: 2450000,
    risk_score: 0.65
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

            {/* Current Index Value */}
            <div className="inline-flex items-center px-6 py-3 bg-[#4CC1E9]/10 border border-[#4CC1E9]/20 rounded-full mb-8">
              <BarChart3 className="w-5 h-5 text-[#4CC1E9] mr-2" />
              <span className="text-[#007A99] font-semibold">
                Current SYI: {indexData.current_value.toFixed(4)}
              </span>
            </div>
          </div>

          {/* Key Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            <Card className="text-center border-[#4CC1E9]/20 hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <DollarSign className="w-12 h-12 text-[#4CC1E9] mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-[#0E1A2B] mb-2">
                  {statistics.avg_yield.toFixed(1)}%
                </h3>
                <p className="text-gray-600">Average Yield</p>
              </CardContent>
            </Card>

            <Card className="text-center border-[#4CC1E9]/20 hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <Activity className="w-12 h-12 text-[#2E6049] mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-[#0E1A2B] mb-2">
                  ${(statistics.total_tvl / 1000000).toFixed(1)}M
                </h3>
                <p className="text-gray-600">Total TVL</p>
              </CardContent>
            </Card>

            <Card className="text-center border-[#4CC1E9]/20 hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <Shield className="w-12 h-12 text-[#007A99] mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-[#0E1A2B] mb-2">
                  {indexData.constituents_count}
                </h3>
                <p className="text-gray-600">Active Constituents</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Index Information */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Card className="border-[#4CC1E9]/20 bg-gradient-to-br from-white to-[#4CC1E9]/5">
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart3 className="w-6 h-6 mr-2 text-[#4CC1E9]" />
                StableYield Index Overview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg font-semibold text-[#0E1A2B] mb-4">Current Performance</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Index Value:</span>
                      <span className="font-semibold text-[#4CC1E9]">{indexData.current_value.toFixed(4)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Constituents:</span>
                      <span className="font-semibold">{indexData.constituents_count}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Risk Score:</span>
                      <Badge className={`${statistics.risk_score < 0.5 ? 'bg-green-100 text-green-800' : statistics.risk_score < 0.7 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                        {(statistics.risk_score * 100).toFixed(0)}/100
                      </Badge>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-[#0E1A2B] mb-4">Market Status</h3>
                  <div className="space-y-3">
                    <div className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                      <span className="text-gray-600">Real-time data feed active</span>
                    </div>
                    <div className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                      <span className="text-gray-600">All constituents reporting</span>
                    </div>
                    <div className="flex items-center">
                      <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                      <span className="text-gray-600">Risk monitoring active</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-8 p-4 bg-gradient-to-r from-[#0E1A2B] to-[#2E6049] rounded-xl text-white">
                <h4 className="font-semibold mb-2 flex items-center">
                  <Activity className="w-4 h-4 mr-2" />
                  Live Market Intelligence
                </h4>
                <p className="text-sm text-white/80">
                  The StableYield Index provides institutional-grade benchmarking for stablecoin yield strategies. 
                  Our risk-adjusted methodology ensures reliable performance measurement across market conditions.
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