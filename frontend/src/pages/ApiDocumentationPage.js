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
  TrendingUp, 
  BarChart3, 
  Shield, 
  Activity,
  Building2,
  Users,
  PieChart,
  Search,
  Zap,
  CheckCircle,
  ArrowRight,
  Clock,
  FileText,
  Mail,
  X
} from "lucide-react";

const ApiDocumentationPage = () => {
  const [isContactOpen, setIsContactOpen] = useState(false);
  const [isWhitepaperOpen, setIsWhitepaperOpen] = useState(false);
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    intendedUse: ''
  });
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('API Access Request:', formData);
    setIsSubmitted(true);
    setTimeout(() => {
      setShowRequestForm(false);
      setIsSubmitted(false);
      setFormData({ name: '', email: '', company: '', intendedUse: '' });
    }, 3000);
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const capabilities = [
    {
      icon: TrendingUp,
      title: "Real-Time Yield Data",
      description: "Live and historical yields across 50+ DeFi protocols. Includes RAY (Risk-Adjusted Yield), TVL metrics, and liquidity depth."
    },
    {
      icon: BarChart3,
      title: "StableYield Index (SYI)",
      description: "The institutional benchmark for stablecoins. Real-time value, historical performance, updated composition, and transparent methodology. Directly comparable to T-Bills and Euribor."
    },
    {
      icon: Shield,
      title: "Risk Analytics",
      description: "Continuous monitoring of peg stability, liquidity depth, and counterparty risk. Real-time depeg alerts with resilience scoring."
    },
    {
      icon: Activity,
      title: "Market Intelligence",
      description: "Portfolio stress testing, cross-asset correlations, and automated Risk ON/OFF regime detection with confidence scores and evidence."
    }
  ];

  const useCases = [
    {
      icon: Building2,
      title: "Institutional Trading",
      description: "Systematic yield strategies on stablecoins with risk-adjusted optimization and cross-chain coverage.",
      color: "text-[#1F4FFF]"
    },
    {
      icon: PieChart,
      title: "Treasury Management",
      description: "Corporate treasury yield maximization with compliance monitoring and liquidity risk tracking.",
      color: "text-[#1F4FFF]"
    },
    {
      icon: Shield,
      title: "Risk Management",
      description: "Real-time exposure monitoring, scenario analysis, and stress testing for institutional portfolios.",
      color: "text-[#D64545]"
    },
    {
      icon: Search,
      title: "Research & Analytics",
      description: "Quantitative datasets and historical benchmarks for academic research and advanced market studies.",
      color: "text-[#9FA6B2]"
    },
    {
      icon: Zap,
      title: "Pro Traders",
      description: "Real-time Risk ON/OFF alerts via Telegram and TradingView, with SYI vs BTC/ETH/T-Bills comparisons and weekly reports.",
      color: "text-[#E47C3C]"
    }
  ];

  const accessSteps = [
    {
      step: 1,
      title: "Sign up & request API access",
      description: "Complete our access request form with your use case details"
    },
    {
      step: 2,
      title: "Receive approval and your personal API key",
      description: "Get approved within 24 hours and receive your secure API credentials"
    },
    {
      step: 3,
      title: "Get full technical documentation",
      description: "Access comprehensive API docs, code examples, and integration guides"
    },
    {
      step: 4,
      title: "Integrate in 60 seconds",
      description: "Connect to TradingView, Telegram Bot, Webhooks, or custom applications"
    }
  ];

  const pricingPlans = [
    {
      name: "Free",
      price: "Free",
      features: [
        "1k calls/day",
        "15-min delayed data",
        "Basic dashboard",
        "Community support"
      ],
      buttonText: "Get Started",
      popular: false
    },
    {
      name: "Pro Trader",
      price: "Contact Sales",
      features: [
        "Real-time data",
        "Risk ON/OFF alerts via Telegram/TradingView",
        "Weekly market insights report",
        "100k calls/day",
        "Priority support"
      ],
      buttonText: "Request Access",
      popular: true,
      badge: "Most Popular"
    },
    {
      name: "Enterprise",
      price: "Contact Sales",
      features: [
        "Unlimited access",
        "99.9% SLA guarantees",
        "Monthly report & advisory",
        "Custom API endpoints",
        "Dedicated support manager"
      ],
      buttonText: "Contact Sales",
      popular: false
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <SEOHead 
        title="StableYield API - Institutional-Grade Stablecoin Intelligence"
        description="Real-time stablecoin yields, benchmark indices (SYI), risk analytics, and market insights - all in one API. Designed for trading desks, corporate treasury teams, researchers, and professional traders."
        keywords="stablecoin API, yield data API, SYI benchmark, risk analytics API, trading desk API"
      />
      
      <Header 
        onJoinWaitlist={() => setIsContactOpen(true)}
        onDownloadWhitepaper={() => setIsWhitepaperOpen(true)}
      />

      <main>
        {/* Hero Section */}
        <section className="relative py-20 lg:py-32 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-gray-50 to-white"></div>
          <div className="absolute top-20 right-10 w-64 h-64 bg-gradient-to-br from-[#1F4FFF]/10 to-[#E47C3C]/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 left-10 w-48 h-48 bg-gradient-to-br from-[#1F4FFF]/5 to-[#E47C3C]/5 rounded-full blur-3xl"></div>

          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h1 className="text-4xl md:text-6xl font-bold text-[#0E1A2B] mb-6">
                StableYield API – Institutional-Grade 
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#1F4FFF] to-[#E47C3C]">
                  {" "}Stablecoin Intelligence
                </span>
              </h1>
              
              <p className="text-xl text-gray-600 max-w-4xl mx-auto mb-8">
                Real-time stablecoin yields, benchmark indices (SYI), risk analytics, and market insights – all in one API. 
                Designed for trading desks, corporate treasury teams, researchers, and professional traders.
              </p>

              {/* Badges */}
              <div className="flex flex-wrap items-center justify-center gap-4 mb-12">
                <Badge className="bg-[#1F4FFF]/10 text-[#1F4FFF] border-[#1F4FFF]/20 px-4 py-2 font-medium">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  99.9% Uptime SLA
                </Badge>
                <Badge className="bg-[#1F4FFF]/10 text-[#1F4FFF] border-[#1F4FFF]/20 px-4 py-2 font-medium">
                  <Shield className="w-4 h-4 mr-2" />
                  Enterprise Security
                </Badge>
                <Badge className="bg-[#1F4FFF]/10 text-[#1F4FFF] border-[#1F4FFF]/20 px-4 py-2 font-medium">
                  <Clock className="w-4 h-4 mr-2" />
                  Real-Time & Historical Data
                </Badge>
                <Badge className="bg-[#E47C3C]/10 text-[#E47C3C] border-[#E47C3C]/20 px-4 py-2 font-medium">
                  <FileText className="w-4 h-4 mr-2" />
                  MiCA / BMR Compliant
                </Badge>
              </div>

              {/* Primary CTA */}
              <Button 
                className="bg-[#E47C3C] hover:bg-[#E47C3C]/90 text-white font-semibold px-12 py-4 text-lg rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300"
                onClick={() => setShowRequestForm(true)}
              >
                Request API Access
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </div>
          </div>
        </section>

        {/* What You Get Section - Capabilities */}
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
                What You Get
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Comprehensive stablecoin intelligence through institutional-grade APIs
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-8">
              {capabilities.map((capability, index) => {
                const IconComponent = capability.icon;
                return (
                  <Card key={index} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-[#1F4FFF] rounded-lg flex items-center justify-center">
                          <IconComponent className="w-6 h-6 text-white" />
                        </div>
                        <CardTitle className="text-xl text-[#0E1A2B]">{capability.title}</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-600">{capability.description}</p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        </section>

        {/* Use Cases Section */}
        <section className="py-20 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
                Use Cases
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                From institutional trading to professional research - StableYield API serves diverse use cases
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {useCases.map((useCase, index) => {
                const IconComponent = useCase.icon;
                return (
                  <Card key={index} className="hover:shadow-lg transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-center space-x-3 mb-4">
                        <IconComponent className={`w-6 h-6 ${useCase.color}`} />
                        <h3 className="font-semibold text-[#0E1A2B]">{useCase.title}</h3>
                      </div>
                      <p className="text-gray-600 text-sm">{useCase.description}</p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        </section>

        {/* How Access Works Section */}
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
                How Access Works
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Get started with StableYield API in four simple steps
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              {accessSteps.map((step, index) => (
                <div key={index} className="text-center">
                  <div className="w-16 h-16 bg-[#1F4FFF] text-white rounded-full flex items-center justify-center font-bold text-xl mb-4 mx-auto">
                    {step.step}
                  </div>
                  <h3 className="font-semibold text-[#0E1A2B] mb-3">{step.title}</h3>
                  <p className="text-gray-600 text-sm">{step.description}</p>
                </div>
              ))}
            </div>

            <div className="text-center mt-12">
              <Button 
                className="bg-[#E47C3C] hover:bg-[#E47C3C]/90 text-white font-semibold px-8 py-3 rounded-xl"
                onClick={() => setShowRequestForm(true)}
              >
                Request API Access
              </Button>
            </div>
          </div>
        </section>

        {/* Pricing Plans Section */}
        <section className="py-20 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
                Plans
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Choose the plan that fits your needs - from individual traders to enterprise clients
              </p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8">
              {pricingPlans.map((plan, index) => (
                <Card key={index} className={`relative ${plan.popular ? 'ring-2 ring-[#E47C3C] scale-105' : ''} hover:shadow-lg transition-all`}>
                  {plan.popular && (
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                      <Badge className="bg-[#E47C3C] text-white px-4 py-1 font-semibold">
                        {plan.badge || "Most Popular"}
                      </Badge>
                    </div>
                  )}
                  <CardHeader className="text-center">
                    <CardTitle className="text-2xl text-[#0E1A2B] mb-2">{plan.name}</CardTitle>
                    <div className="text-3xl font-bold text-[#0E1A2B] mb-4">{plan.price}</div>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3 mb-6">
                      {plan.features.map((feature, featureIndex) => (
                        <li key={featureIndex} className="flex items-center">
                          <CheckCircle className="w-4 h-4 text-[#1F4FFF] mr-2" />
                          <span className="text-gray-600">{feature}</span>
                        </li>
                      ))}
                    </ul>
                    <Button 
                      className={`w-full ${plan.popular ? 'bg-[#E47C3C] hover:bg-[#E47C3C]/90 text-white' : 'border border-[#1F4FFF] text-[#1F4FFF] hover:bg-[#1F4FFF] hover:text-white'}`}
                      variant={plan.popular ? "default" : "outline"}
                      onClick={() => setShowRequestForm(true)}
                    >
                      {plan.buttonText}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="text-center mt-12">
              <Button 
                className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] text-white font-semibold px-12 py-4 text-lg rounded-xl"
                onClick={() => setShowRequestForm(true)}
              >
                Request API Access
              </Button>
            </div>
          </div>
        </section>

        {/* Footer Note */}
        <section className="py-8 bg-white border-t border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <p className="text-sm text-gray-500">
                StableYield APIs provide benchmark and analytics data. They do not constitute financial advice. 
                Compliance aligned with MiCA / BMR / IOSCO best practices.
              </p>
            </div>
          </div>
        </section>
      </main>

      <Footer />

      {/* API Access Request Form Modal */}
      {showRequestForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-xl text-[#0E1A2B]">Request API Access</CardTitle>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setShowRequestForm(false)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {!isSubmitted ? (
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Name
                    </label>
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#4CC1E9]"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#4CC1E9]"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Company
                    </label>
                    <input
                      type="text"
                      name="company"
                      value={formData.company}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#4CC1E9]"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Intended Use
                    </label>
                    <textarea
                      name="intendedUse"
                      value={formData.intendedUse}
                      onChange={handleInputChange}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#4CC1E9]"
                      placeholder="Describe how you plan to use the API..."
                      required
                    />
                  </div>
                  <Button 
                    type="submit"
                    className="w-full bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] text-white font-semibold py-2 rounded-md"
                  >
                    Submit Request
                  </Button>
                </form>
              ) : (
                <div className="text-center py-8">
                  <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-[#0E1A2B] mb-2">
                    Request Submitted Successfully!
                  </h3>
                  <p className="text-gray-600">
                    We'll review your request and get back to you within 24 hours.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Contact Modal */}
      <ContactModal 
        isOpen={isContactOpen} 
        onClose={() => setIsContactOpen(false)} 
      />
      
      {/* Whitepaper Download Modal */}
      <WhitepaperDownloadModal 
        isOpen={isWhitepaperOpen} 
        onClose={() => setIsWhitepaperOpen(false)} 
      />
    </div>
  );
};

export default ApiDocumentationPage;