import React, { useState } from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import SEOHead from "../components/SEOHead";
import ContactModal from "../components/ContactModal";
import WhitepaperDownloadModal from "../components/WhitepaperDownloadModal";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { 
  Code, 
  Database, 
  Zap, 
  Shield, 
  TrendingUp,
  BarChart3,
  Brain,
  Activity,
  FileText,
  ExternalLink,
  Copy,
  CheckCircle
} from "lucide-react";

const ApiDocumentationPage = () => {
  const [isContactOpen, setIsContactOpen] = useState(false);
  const [isWhitepaperOpen, setIsWhitepaperOpen] = useState(false);
  const [copiedEndpoint, setCopiedEndpoint] = useState(null);

  const copyToClipboard = (text, endpoint) => {
    navigator.clipboard.writeText(text);
    setCopiedEndpoint(endpoint);
    setTimeout(() => setCopiedEndpoint(null), 2000);
  };

  const apiSections = [
    {
      title: "Yield Intelligence APIs",
      icon: TrendingUp,
      color: "text-[#4CC1E9]",
      description: "Access real-time stablecoin yields across DeFi and CeFi platforms",
      endpoints: [
        {
          method: "GET",
          path: "/api/yields/all",
          description: "Get all current stablecoin yields",
          example: `curl -X GET "${process.env.REACT_APP_BACKEND_URL || 'https://api.stableyield.com'}/api/yields/all"`
        },
        {
          method: "GET", 
          path: "/api/yields/stablecoin/{symbol}",
          description: "Get yields for specific stablecoin",
          example: `curl -X GET "${process.env.REACT_APP_BACKEND_URL || 'https://api.stableyield.com'}/api/yields/stablecoin/USDT"`
        }
      ]
    },
    {
      title: "StableYield Index (SYI) APIs",
      icon: BarChart3,
      color: "text-[#007A99]",
      description: "Access the institutional-grade StableYield Index data and analytics",
      endpoints: [
        {
          method: "GET",
          path: "/api/index/current",
          description: "Get current StableYield Index value",
          example: `curl -X GET "${process.env.REACT_APP_BACKEND_URL || 'https://api.stableyield.com'}/api/index/current"`
        },
        {
          method: "GET",
          path: "/api/index/history",
          description: "Get historical SYI data",
          example: `curl -X GET "${process.env.REACT_APP_BACKEND_URL || 'https://api.stableyield.com'}/api/index/history?days=30"`
        },
        {
          method: "GET",
          path: "/api/index/constituents",
          description: "Get index constituents and weights",
          example: `curl -X GET "${process.env.REACT_APP_BACKEND_URL || 'https://api.stableyield.com'}/api/index/constituents"`
        }
      ]
    },
    {
      title: "Risk-Adjusted Yield (RAY) APIs",
      icon: Shield,
      color: "text-[#2E6049]",
      description: "Advanced risk analytics and risk-adjusted yield calculations",
      endpoints: [
        {
          method: "POST",
          path: "/api/ray/calculate",
          description: "Calculate RAY for specific yield opportunity",
          example: `curl -X POST "${process.env.REACT_APP_BACKEND_URL || 'https://api.stableyield.com'}/api/ray/calculate" \\
  -H "Content-Type: application/json" \\
  -d '{"yield_data": {...}}'`
        },
        {
          method: "GET",
          path: "/api/ray/market-analysis",
          description: "Get market-wide RAY analysis",
          example: `curl -X GET "${process.env.REACT_APP_BACKEND_URL || 'https://api.stableyield.com'}/api/ray/market-analysis"`
        }
      ]
    },
    {
      title: "AI Portfolio Management APIs",
      icon: Brain,
      color: "text-[#4CC1E9]",
      description: "Advanced AI-powered portfolio optimization and management",
      endpoints: [
        {
          method: "GET",
          path: "/api/ai-portfolio/status",
          description: "Get AI portfolio service status and capabilities",
          example: `curl -X GET "${process.env.REACT_APP_BACKEND_URL || 'https://api.stableyield.com'}/api/ai-portfolio/status"`
        },
        {
          method: "POST",
          path: "/api/ai-portfolio/portfolios",
          description: "Create AI-managed portfolio",
          example: `curl -X POST "${process.env.REACT_APP_BACKEND_URL || 'https://api.stableyield.com'}/api/ai-portfolio/portfolios" \\
  -H "Content-Type: application/json" \\
  -d '{"strategy": "ai_enhanced", "risk_tolerance": 0.6}'`
        },
        {
          method: "GET",
          path: "/api/ai-portfolio/summary",
          description: "Get comprehensive AI portfolio management summary",
          example: `curl -X GET "${process.env.REACT_APP_BACKEND_URL || 'https://api.stableyield.com'}/api/ai-portfolio/summary"`
        }
      ]
    },
    {
      title: "Enhanced Risk Management APIs", 
      icon: Activity,
      color: "text-[#007A99]",
      description: "Institutional-grade risk monitoring and compliance management",
      endpoints: [
        {
          method: "GET",
          path: "/api/risk-management/status",
          description: "Get risk management service status",
          example: `curl -X GET "${process.env.REACT_APP_BACKEND_URL || 'https://api.stableyield.com'}/api/risk-management/status"`
        },
        {
          method: "GET",
          path: "/api/risk-management/metrics/{portfolio_id}",
          description: "Get comprehensive risk metrics for portfolio",
          example: `curl -X GET "${process.env.REACT_APP_BACKEND_URL || 'https://api.stableyield.com'}/api/risk-management/metrics/portfolio_123"`
        },
        {
          method: "POST",
          path: "/api/risk-management/stress-test/{portfolio_id}",
          description: "Run stress test on portfolio",
          example: `curl -X POST "${process.env.REACT_APP_BACKEND_URL || 'https://api.stableyield.com'}/api/risk-management/stress-test/portfolio_123" \\
  -H "Content-Type: application/json" \\
  -d '{"scenario_id": "peg_break"}'`
        }
      ]
    },
    {
      title: "Trading Engine APIs",
      icon: Zap,
      color: "text-[#2E6049]",
      description: "Advanced trading and execution management system",
      endpoints: [
        {
          method: "GET",
          path: "/api/trading/status",
          description: "Get trading engine status",
          example: `curl -X GET "${process.env.REACT_APP_BACKEND_URL || 'https://api.stableyield.com'}/api/trading/status"`
        },
        {
          method: "POST",
          path: "/api/trading/orders",
          description: "Create trading order",
          example: `curl -X POST "${process.env.REACT_APP_BACKEND_URL || 'https://api.stableyield.com'}/api/trading/orders" \\
  -H "Content-Type: application/json" \\
  -d '{"symbol": "USDT", "quantity": 1000, "type": "market"}'`
        }
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <SEOHead 
        title="API Documentation - StableYield Developer Resources"
        description="Comprehensive API documentation for StableYield's institutional-grade stablecoin yield intelligence, risk management, and portfolio optimization APIs."
      />
      
      <Header 
        onContactOpen={() => setIsContactOpen(true)}
        onDownloadWhitepaper={() => setIsWhitepaperOpen(true)}
      />
      
      {/* Hero Section */}
      <section className="pt-32 pb-20 bg-gradient-to-br from-[#0E1A2B] via-[#2E6049] to-[#007A99] text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-4xl mx-auto">
            <div className="flex items-center justify-center mb-6">
              <Code className="w-12 h-12 text-[#4CC1E9] mr-4" />
              <h1 className="text-4xl md:text-5xl font-bold">
                API Documentation
              </h1>
            </div>
            
            <p className="text-xl text-white/80 mb-8">
              Integrate StableYield's institutional-grade stablecoin intelligence into your applications. 
              Access real-time yields, risk analytics, AI portfolio management, and comprehensive market data.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                <Database className="w-8 h-8 text-[#4CC1E9] mb-2 mx-auto" />
                <h3 className="font-semibold mb-1">Real-time Data</h3>
                <p className="text-sm text-white/70">Live stablecoin yields and market intelligence</p>
              </div>
              
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                <Shield className="w-8 h-8 text-[#4CC1E9] mb-2 mx-auto" />
                <h3 className="font-semibold mb-1">Risk Analytics</h3>
                <p className="text-sm text-white/70">Advanced risk-adjusted yield calculations</p>
              </div>
              
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                <Brain className="w-8 h-8 text-[#4CC1E9] mb-2 mx-auto" />
                <h3 className="font-semibold mb-1">AI Portfolio Management</h3>
                <p className="text-sm text-white/70">Machine learning-driven portfolio optimization</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Getting Started */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">Getting Started</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              All API endpoints use standard REST architecture with JSON responses. 
              Base URL: <code className="bg-gray-100 px-2 py-1 rounded text-sm">{process.env.REACT_APP_BACKEND_URL || 'https://api.stableyield.com'}</code>
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-[#4CC1E9]" />
                  Authentication (Coming Soon)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  Enterprise API keys will be available for institutional clients requiring authenticated access 
                  to advanced features and higher rate limits.
                </p>
                <Button 
                  onClick={() => setIsContactOpen(true)}
                  className="bg-[#4CC1E9] hover:bg-[#007A99] text-white"
                >
                  Contact for Enterprise Access
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="w-5 h-5 mr-2 text-[#007A99]" />
                  Rate Limits
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Public APIs:</span>
                    <Badge variant="outline">100 req/hour</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Enterprise APIs:</span>
                    <Badge className="bg-[#4CC1E9]">1000+ req/hour</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* API Sections */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="space-y-16">
            {apiSections.map((section, index) => (
              <div key={index} className="bg-white rounded-2xl shadow-lg overflow-hidden">
                <div className="bg-gradient-to-r from-[#0E1A2B] to-[#2E6049] p-8">
                  <div className="flex items-center mb-4">
                    <section.icon className={`w-8 h-8 ${section.color} mr-4`} />
                    <h3 className="text-2xl font-bold text-white">{section.title}</h3>
                  </div>
                  <p className="text-white/80">{section.description}</p>
                </div>
                
                <div className="p-8">
                  <div className="space-y-6">
                    {section.endpoints.map((endpoint, endpointIndex) => (
                      <Card key={endpointIndex} className="border-l-4 border-l-[#4CC1E9]">
                        <CardHeader>
                          <CardTitle className="flex items-center justify-between">
                            <div className="flex items-center">
                              <Badge 
                                className={`mr-3 ${
                                  endpoint.method === 'GET' ? 'bg-green-500' : 
                                  endpoint.method === 'POST' ? 'bg-blue-500' : 
                                  'bg-orange-500'
                                }`}
                              >
                                {endpoint.method}
                              </Badge>
                              <code className="text-lg font-mono">{endpoint.path}</code>
                            </div>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => copyToClipboard(endpoint.example, `${index}-${endpointIndex}`)}
                            >
                              {copiedEndpoint === `${index}-${endpointIndex}` ? (
                                <CheckCircle className="w-4 h-4 text-green-500" />
                              ) : (
                                <Copy className="w-4 h-4" />
                              )}
                            </Button>
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-gray-600 mb-4">{endpoint.description}</p>
                          <div className="bg-gray-900 text-white p-4 rounded-lg overflow-x-auto">
                            <code className="text-sm">{endpoint.example}</code>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">Need Help?</h2>
          <p className="text-gray-600 mb-8">
            Our team is here to help you integrate StableYield APIs into your applications. 
            Contact us for technical support, enterprise features, or custom integration assistance.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <Button 
              onClick={() => setIsContactOpen(true)}
              className="bg-[#4CC1E9] hover:bg-[#007A99] text-white px-8 py-3"
            >
              Contact Support
              <ExternalLink className="w-4 h-4 ml-2" />
            </Button>
            <Button 
              onClick={() => setIsWhitepaperOpen(true)}
              variant="outline" 
              className="border-[#4CC1E9] text-[#4CC1E9] hover:bg-[#4CC1E9] hover:text-white px-8 py-3"
            >
              Download Technical Whitepaper
              <FileText className="w-4 h-4 ml-2" />
            </Button>
          </div>
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

export default ApiDocumentationPage;