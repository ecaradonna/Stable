import React from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import SEOHead from "../components/SEOHead";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { 
  BarChart3, 
  Shield, 
  TrendingUp, 
  Target, 
  CheckCircle, 
  ArrowRight,
  Building2,
  LineChart,
  DollarSign
} from "lucide-react";

const YieldIndicesPage = () => {
  const methodologyPoints = [
    {
      icon: BarChart3,
      title: "Comprehensive Yield Data",
      description: "Aggregated across DeFi protocols, CeFi platforms, and TradFi instruments.",
      color: "text-[#4CC1E9]"
    },
    {
      icon: Shield,
      title: "Peg Stability Analytics",
      description: "Monitoring deviations, volatility, and resilience of each stablecoin against the U.S. dollar.",
      color: "text-[#007A99]"
    },
    {
      icon: TrendingUp,
      title: "Liquidity & Market Depth Metrics",
      description: "Evaluating how efficiently capital can enter and exit strategies without slippage.",
      color: "text-[#2E6049]"
    }
  ];

  const institutionalBenefits = [
    {
      icon: Target,
      title: "Measure and Compare",
      description: "Yield strategies across platforms with standardized metrics"
    },
    {
      icon: LineChart,
      title: "Performance Reporting",
      description: "Incorporate standardized indices into institutional reporting frameworks"
    },
    {
      icon: Building2,
      title: "Licensing Opportunities",
      description: "Transparent reference rates for funds, structured products, and exchange offerings"
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <SEOHead 
        title="Yield Indices & Benchmarks – Institutional Stablecoin Analytics"
        description="Professional yield indices and benchmarks for USD stablecoins. Risk-adjusted returns, peg stability analytics, and institutional-grade data for USDT, USDC, DAI."
        url="https://stableyield.com/yield-indices"
      />
      <Header />
      
      {/* Hero Section */}
      <section className="pt-20 pb-16 bg-gradient-to-br from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 bg-[#4CC1E9]/10 border border-[#4CC1E9]/20 rounded-full mb-6">
              <BarChart3 className="w-4 h-4 text-[#4CC1E9] mr-2" />
              <span className="text-[#007A99] font-semibold text-sm">Institutional-Grade Benchmarks</span>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold text-[#0E1A2B] mb-6">
              Yield Indices & Benchmarks
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-4xl mx-auto leading-relaxed">
              Institutional-grade reference points for stablecoin market performance.
            </p>
            
            <div className="bg-gradient-to-r from-[#4CC1E9]/10 to-[#007A99]/10 rounded-2xl p-8 border border-[#4CC1E9]/20 max-w-5xl mx-auto">
              <p className="text-lg text-gray-700 leading-relaxed">
                StableYield develops the industry's first suite of <strong>risk-adjusted stablecoin yield indices</strong> — 
                designed to serve as transparent, authoritative benchmarks for investors, funds, and market participants.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Methodology Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-[#0E1A2B] mb-6">
              Beyond Simple APY Tracking
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Unlike simple APY trackers, our methodology integrates comprehensive risk factors 
              to provide true market performance insights.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            {methodologyPoints.map((point, index) => {
              const IconComponent = point.icon;
              return (
                <Card key={index} className="text-center hover:shadow-lg transition-all duration-300 border-2 hover:border-[#4CC1E9]/30">
                  <CardHeader>
                    <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-[#4CC1E9]/10 to-[#007A99]/10 flex items-center justify-center">
                      <IconComponent className={`w-8 h-8 ${point.color}`} />
                    </div>
                    <CardTitle className="text-xl text-[#0E1A2B]">{point.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600">{point.description}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <div className="text-center">
            <Badge className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] text-white px-6 py-3 text-base">
              = Risk-Adjusted Yield Indices
            </Badge>
          </div>
        </div>
      </section>

      {/* Institutional Benefits Section */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-[#0E1A2B] mb-6">
              Institutional Applications
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              These benchmarks enable institutions to build more sophisticated and trustworthy stablecoin strategies.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            {institutionalBenefits.map((benefit, index) => {
              const IconComponent = benefit.icon;
              return (
                <div key={index} className="bg-white rounded-xl p-8 shadow-md hover:shadow-lg transition-shadow border border-gray-100">
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-gradient-to-br from-[#4CC1E9] to-[#007A99] rounded-lg flex items-center justify-center">
                        <IconComponent className="w-6 h-6 text-white" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-[#0E1A2B] mb-3">{benefit.title}</h3>
                      <p className="text-gray-600 leading-relaxed">{benefit.description}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Value Proposition Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-r from-[#0E1A2B] to-[#2E6049] rounded-2xl p-8 md:p-12 text-white">
            <div className="max-w-4xl mx-auto text-center">
              <h2 className="text-3xl md:text-4xl font-bold mb-8">
                Transforming Stablecoin Yields into an Institution-Ready Asset Class
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                  <CheckCircle className="w-8 h-8 text-[#4CC1E9] mb-4 mx-auto" />
                  <h3 className="text-xl font-bold mb-3">Consistent Baseline</h3>
                  <p className="text-white/90">
                    Establishing verifiable benchmarks that provide a standardized foundation for comparison and analysis.
                  </p>
                </div>
                
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                  <DollarSign className="w-8 h-8 text-[#4CC1E9] mb-4 mx-auto" />
                  <h3 className="text-xl font-bold mb-3">Safer Capital Allocation</h3>
                  <p className="text-white/90">
                    Enabling more rigorous financial products through transparent, risk-adjusted performance metrics.
                  </p>
                </div>
              </div>
              
              <p className="text-xl leading-relaxed mb-8 text-white/95">
                By establishing a consistent and verifiable baseline, StableYield transforms stablecoin yields 
                into a trustworthy, institution-ready asset class, enabling safer capital allocation and more 
                rigorous financial products.
              </p>
              
              <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
                <Button className="bg-white text-[#0E1A2B] hover:bg-gray-100 font-semibold px-8 py-3">
                  View Live Indices
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
                <Button variant="outline" className="border-white text-white hover:bg-white hover:text-[#0E1A2B] px-8 py-3">
                  API Documentation
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default YieldIndicesPage;