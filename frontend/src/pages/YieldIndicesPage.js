import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import Footer from "../components/Footer";
import SEOHead from "../components/SEOHead";
import ContactModal from "../components/ContactModal";
import WhitepaperDownloadModal from "../components/WhitepaperDownloadModal";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { 
  BarChart3, 
  TrendingUp, 
  Shield, 
  Activity,
  Target,
  CheckCircle,
  Building2,
  FileText,
  ArrowRight,
  Users,
  PieChart,
  Zap
} from "lucide-react";

const YieldIndicesPage = () => {
  const navigate = useNavigate();
  const [isContactOpen, setIsContactOpen] = useState(false);
  const [isWhitepaperOpen, setIsWhitepaperOpen] = useState(false);

  const capabilities = [
    {
      icon: TrendingUp,
      title: "Yield Data",
      description: "Comprehensive yield tracking across DeFi, CeFi, and traditional finance protocols with real-time updates.",
      color: "text-[#1F4FFF]",
      bgColor: "bg-[#1F4FFF]/10"
    },
    {
      icon: Shield,
      title: "Peg Analytics",
      description: "Advanced peg stability monitoring with deviation tracking, volatility analysis, and risk scoring.",
      color: "text-[#D64545]",
      bgColor: "bg-[#D64545]/10"
    },
    {
      icon: Activity,
      title: "Liquidity Metrics",
      description: "Depth analysis, slippage calculations, and market coverage assessment for institutional requirements.",
      color: "text-[#9FA6B2]",
      bgColor: "bg-[#9FA6B2]/10"
    }
  ];

  const institutionalApplications = [
    {
      icon: Target,
      title: "Measure & Compare",
      description: "Standardized benchmarks for measuring stablecoin performance across different yield strategies and protocols.",
      highlight: "Performance benchmarking"
    },
    {
      icon: FileText,
      title: "Performance Reporting",
      description: "Institutional-grade reporting tools with transparent methodology for compliance and investor communications.",
      highlight: "Regulatory compliance"
    },
    {
      icon: Building2,
      title: "Licensing Opportunities",
      description: "White-label indices for financial institutions, funds, and data providers seeking stablecoin benchmarks.",
      highlight: "Custom solutions"
    }
  ];

  const indexSuite = [
    {
      code: "SY100",
      name: "StableYield Index",
      description: "Composite benchmark tracking risk-adjusted yields across the entire stablecoin ecosystem.",
      value: "4.47%",
      constituents: "47 assets",
      color: "border-[#1F4FFF] bg-[#1F4FFF]/5",
      textColor: "text-[#1F4FFF]"
    },
    {
      code: "SYCEFI", 
      name: "CeFi Index",
      description: "Centralized finance yields from established institutions and regulated platforms.",
      value: "4.23%",
      constituents: "8 platforms",
      color: "border-[#1F4FFF] bg-[#1F4FFF]/5", 
      textColor: "text-[#1F4FFF]"
    },
    {
      code: "SYDEFI",
      name: "DeFi Index", 
      description: "Decentralized protocol yields with smart contract risk adjustments.",
      value: "7.89%",
      constituents: "12 protocols",
      color: "border-[#9FA6B2] bg-[#9FA6B2]/5",
      textColor: "text-[#9FA6B2]"
    },
    {
      code: "SYRPI",
      name: "Risk Premium Index",
      description: "Higher-yield opportunities with appropriate risk-adjusted calculations.",
      value: "12.34%", 
      constituents: "6 protocols",
      color: "border-[#D64545] bg-[#D64545]/5",
      textColor: "text-[#D64545]"
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <SEOHead 
        title="Yield Indices & Benchmarks - The Standard for Stablecoin Performance"
        description="The industry's first suite of risk-adjusted yield indices — transparent, auditable, and trusted by institutions."
        keywords="stablecoin indices, yield benchmarks, risk-adjusted performance, institutional benchmarks"
      />
      
      <Header 
        onJoinWaitlist={() => setIsContactOpen(true)}
        onDownloadWhitepaper={() => setIsWhitepaperOpen(true)}
      />

      <main>
        {/* Hero Section */}
        <section className="relative py-20 lg:py-32 overflow-hidden bg-gradient-to-br from-gray-50 to-white">
          <div className="absolute top-20 right-10 w-64 h-64 bg-gradient-to-br from-[#1F4FFF]/10 to-[#9FA6B2]/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 left-10 w-48 h-48 bg-gradient-to-br from-[#1F4FFF]/5 to-[#E47C3C]/10 rounded-full blur-3xl"></div>

          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <Badge className="bg-[#1F4FFF]/10 text-[#1F4FFF] mb-6 px-4 py-2">
                Index Suite
              </Badge>
              
              <h1 className="text-4xl md:text-6xl font-bold text-[#0E1A2B] mb-6 leading-tight">
                The Standard for 
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#1F4FFF] to-[#9FA6B2]">
                  {" "}Stablecoin Performance
                </span>
              </h1>
              
              <p className="text-xl text-gray-600 max-w-4xl mx-auto mb-12 leading-relaxed">
                The industry's first suite of risk-adjusted yield indices — transparent, auditable, 
                and trusted by institutions. From DeFi yields to institutional benchmarks.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
                <Button 
                  className="bg-[#1F4FFF] hover:bg-[#1F4FFF]/90 text-white font-semibold px-8 py-4 text-lg rounded-xl"
                  onClick={() => navigate('/index-dashboard')}
                >
                  View Live Indices
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
                <Button 
                  variant="outline" 
                  className="border-2 border-[#E47C3C] text-[#E47C3C] hover:bg-[#E47C3C] hover:text-white font-semibold px-8 py-4 text-lg rounded-xl"
                  onClick={() => setIsContactOpen(true)}
                >
                  Request API Access
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Index Suite Display */}
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
                StableYield Index Family
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Specialized indices for different market segments and risk profiles
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-6">
              {indexSuite.map((index, i) => (
                <Card key={i} className={`${index.color} border-2 hover:shadow-lg transition-all cursor-pointer`}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <Badge className={`${index.textColor} bg-transparent border mb-2`}>
                          {index.code}
                        </Badge>
                        <CardTitle className="text-xl text-[#0E1A2B]">{index.name}</CardTitle>
                      </div>
                      <div className="text-right">
                        <div className={`text-2xl font-bold ${index.textColor}`}>
                          {index.value}
                        </div>
                        <div className="text-sm text-gray-500">{index.constituents}</div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600">{index.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Capabilities Section */}
        <section className="py-20 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
                Comprehensive Market Intelligence
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Advanced analytics and data infrastructure powering institutional decision-making
              </p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8">
              {capabilities.map((capability, index) => {
                const IconComponent = capability.icon;
                return (
                  <Card key={index} className="hover:shadow-lg transition-shadow border-0 shadow-md text-center">
                    <CardContent className="p-8">
                      <div className={`w-16 h-16 ${capability.bgColor} rounded-2xl flex items-center justify-center mx-auto mb-6`}>
                        <IconComponent className={`w-8 h-8 ${capability.color}`} />
                      </div>
                      <h3 className="text-xl font-semibold text-[#0E1A2B] mb-4">{capability.title}</h3>
                      <p className="text-gray-600">{capability.description}</p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        </section>

        {/* Institutional Applications */}
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
                Institutional Applications
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Trusted by funds, treasury teams, and financial institutions worldwide
              </p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8">
              {institutionalApplications.map((app, index) => {
                const IconComponent = app.icon;
                return (
                  <div key={index} className="text-center">
                    <div className="w-16 h-16 bg-[#1F4FFF]/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
                      <IconComponent className="w-8 h-8 text-[#1F4FFF]" />
                    </div>
                    <h3 className="text-xl font-semibold text-[#0E1A2B] mb-3">{app.title}</h3>
                    <p className="text-gray-600 mb-4">{app.description}</p>
                    <Badge className="bg-[#1F4FFF]/10 text-[#1F4FFF]">
                      {app.highlight}
                    </Badge>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Risk-Adjusted Yield Indices CTA */}
        <section className="py-20 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <Card className="border-2 border-[#1F4FFF]/20 bg-[#1F4FFF]/5">
              <CardContent className="p-12 text-center">
                <div className="w-20 h-20 bg-[#1F4FFF]/20 rounded-full flex items-center justify-center mx-auto mb-6">
                  <BarChart3 className="w-10 h-10 text-[#1F4FFF]" />
                </div>
                <h3 className="text-2xl font-bold text-[#0E1A2B] mb-4">
                  Risk-Adjusted Yield Indices
                </h3>
                <p className="text-gray-600 max-w-2xl mx-auto mb-8">
                  Go beyond simple APY comparisons. Our Risk-Adjusted Yield (RAY) methodology 
                  accounts for peg stability, liquidity depth, and protocol risk.
                </p>
                <Button 
                  className="bg-[#1F4FFF] hover:bg-[#1F4FFF]/90 text-white font-semibold px-8 py-3 rounded-xl"
                  onClick={() => navigate('/risk-analytics')}
                >
                  View Risk-Adjusted Yield Indices
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Closing Section */}
        <section className="py-20 bg-gradient-to-r from-[#1F4FFF] to-[#9FA6B2]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-white mb-4">
                From DeFi Yields to Institutional Benchmarks
              </h2>
              <p className="text-xl text-white/90 max-w-3xl mx-auto mb-8">
                Whether you're managing a treasury, running a fund, or trading professionally — 
                StableYield provides the institutional-grade data and benchmarks you need.
              </p>
              
              <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
                <Button 
                  className="bg-white text-[#1F4FFF] hover:bg-gray-100 font-semibold px-8 py-4 text-lg rounded-xl"
                  onClick={() => navigate('/index-dashboard')}
                >
                  Explore Live Data
                  <BarChart3 className="w-5 h-5 ml-2" />
                </Button>
                <Button 
                  variant="outline" 
                  className="border-2 border-white text-white hover:bg-white hover:text-[#1F4FFF] font-semibold px-8 py-4 text-lg rounded-xl"
                  onClick={() => setIsContactOpen(true)}
                >
                  Request API Access
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

export default YieldIndicesPage;