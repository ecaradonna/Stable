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
  Lock,
  Activity,
  FileText,
  Mail,
  CheckCircle,
  Users,
  Building2,
  AlertCircle
} from "lucide-react";

const ApiDocumentationPage = () => {
  const [isContactOpen, setIsContactOpen] = useState(false);
  const [isWhitepaperOpen, setIsWhitepaperOpen] = useState(false);
  const [formData, setFormData] = useState({
    company: '',
    email: '',
    useCase: '',
    message: ''
  });
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    // In a real application, this would submit to your backend
    console.log('API Access Request:', formData);
    setIsSubmitted(true);
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const apiCapabilities = [
    {
      title: "Real-Time Yield Data",
      icon: TrendingUp,
      color: "text-[#4CC1E9]",
      description: "Access live stablecoin yields across 50+ protocols with risk-adjusted calculations"
    },
    {
      title: "StableYield Index (SYI)",
      icon: BarChart3,
      color: "text-[#2E6049]",
      description: "Institutional benchmark data with historical performance and constituent analytics"
    },
    {
      title: "Risk Analytics",
      icon: Shield,
      color: "text-[#007A99]",
      description: "Peg stability, liquidity depth, and counterparty risk metrics for informed decisions"
    },
    {
      title: "Market Intelligence",
      icon: Database,
      color: "text-[#F59E0B]",
      description: "Advanced analytics including stress testing, correlation analysis, and regime detection"
    }
  ];

  const useCases = [
    {
      title: "Institutional Trading",
      description: "Systematic yield farming strategies with risk-adjusted portfolio optimization"
    },
    {
      title: "Treasury Management",
      description: "Corporate treasury yield maximization with regulatory compliance monitoring"
    },
    {
      title: "Risk Management",
      description: "Real-time risk monitoring and stress testing for stablecoin exposures"
    },
    {
      title: "Research & Analytics",
      description: "Market research, academic studies, and quantitative analysis of stablecoin markets"
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <SEOHead 
        title="StableYield API Access – Institutional Data for Professionals"
        description="Request access to StableYield's institutional-grade API for real-time stablecoin yield data, risk analytics, and market intelligence."
        url="https://stableyield.com/api-documentation"
      />
      <Header 
        onJoinWaitlist={() => setIsContactOpen(true)}
        onDownloadWhitepaper={() => setIsWhitepaperOpen(true)}
      />
      
      {/* Hero Section */}
      <section className="pt-20 pb-16 bg-gradient-to-br from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <div className="inline-flex items-center px-4 py-2 bg-[#4CC1E9]/10 border border-[#4CC1E9]/20 rounded-full mb-6">
              <Lock className="w-4 h-4 text-[#4CC1E9] mr-2" />
              <span className="text-[#007A99] font-semibold text-sm">Professional API Access</span>
            </div>
            
            <h1 className="text-4xl md:text-5xl font-bold text-[#0E1A2B] mb-6">
              StableYield API
            </h1>
            
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Institutional-grade API for real-time stablecoin yield data, risk analytics, 
              and market intelligence. Built for trading desks, treasury teams, and research institutions.
            </p>

            <div className="flex items-center justify-center space-x-6 text-sm text-gray-600">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                99.9% Uptime SLA
              </div>
              <div className="flex items-center">
                <Shield className="w-5 h-5 text-green-500 mr-2" />
                Enterprise Security
              </div>
              <div className="flex items-center">
                <Zap className="w-5 h-5 text-green-500 mr-2" />
                Real-Time Data
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* API Capabilities */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">API Capabilities</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Comprehensive access to StableYield's institutional-grade data infrastructure
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
            {apiCapabilities.map((capability, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow border-gray-200">
                <CardHeader className="pb-4">
                  <capability.icon className={`w-12 h-12 ${capability.color} mb-4`} />
                  <CardTitle className="text-lg">{capability.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 text-sm">{capability.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">Enterprise Use Cases</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Trusted by leading institutions for mission-critical stablecoin operations
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
            {useCases.map((useCase, index) => (
              <Card key={index} className="border-gray-200">
                <CardContent className="p-6">
                  <h3 className="text-lg font-semibold text-[#0E1A2B] mb-3">{useCase.title}</h3>
                  <p className="text-gray-600">{useCase.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* API Access Request Form */}
      <section className="py-16 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">Request API Access</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Our API is available to qualified institutions and professional traders. 
              Submit your request and our team will review your application.
            </p>
          </div>

          {!isSubmitted ? (
            <Card className="border-[#4CC1E9]/20 bg-gradient-to-br from-white to-[#4CC1E9]/5">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Mail className="w-6 h-6 mr-2 text-[#4CC1E9]" />
                  API Access Application
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-2">
                        Company / Institution *
                      </label>
                      <input
                        type="text"
                        id="company"
                        name="company"
                        required
                        value={formData.company}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#4CC1E9] focus:border-[#4CC1E9]"
                        placeholder="Your company name"
                      />
                    </div>
                    
                    <div>
                      <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                        Professional Email *
                      </label>
                      <input
                        type="email"
                        id="email"
                        name="email"
                        required
                        value={formData.email}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#4CC1E9] focus:border-[#4CC1E9]"
                        placeholder="your.name@company.com"
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="useCase" className="block text-sm font-medium text-gray-700 mb-2">
                      Primary Use Case *
                    </label>
                    <select
                      id="useCase"
                      name="useCase"
                      required
                      value={formData.useCase}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#4CC1E9] focus:border-[#4CC1E9]"
                    >
                      <option value="">Select your primary use case</option>
                      <option value="trading">Institutional Trading</option>
                      <option value="treasury">Treasury Management</option>
                      <option value="risk">Risk Management</option>
                      <option value="research">Research & Analytics</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                      Additional Information
                    </label>
                    <textarea
                      id="message"
                      name="message"
                      rows={4}
                      value={formData.message}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#4CC1E9] focus:border-[#4CC1E9]"
                      placeholder="Tell us more about your specific requirements, expected usage volume, and timeline..."
                    />
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="flex items-start space-x-2">
                      <AlertCircle className="w-5 h-5 text-[#F59E0B] mt-0.5 flex-shrink-0" />
                      <div className="text-sm text-gray-600">
                        <strong>Note:</strong> API access is currently limited to institutional clients. 
                        We typically respond to qualified applications within 2-3 business days.
                      </div>
                    </div>
                  </div>

                  <Button 
                    type="submit"
                    className="w-full bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] text-white font-semibold py-3 px-6 rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl"
                  >
                    Submit API Access Request
                  </Button>
                </form>
              </CardContent>
            </Card>
          ) : (
            <Card className="border-green-200 bg-gradient-to-br from-white to-green-50">
              <CardContent className="text-center py-12">
                <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-6" />
                <h3 className="text-2xl font-bold text-[#0E1A2B] mb-4">
                  Application Submitted Successfully!
                </h3>
                <p className="text-gray-600 mb-6 max-w-md mx-auto">
                  Thank you for your interest in StableYield API. Our team will review your application 
                  and respond within 2-3 business days.
                </p>
                <Button 
                  onClick={() => setIsSubmitted(false)}
                  variant="outline"
                  className="border-green-500 text-green-600 hover:bg-green-50"
                >
                  Submit Another Request
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </section>

      {/* Enterprise Support */}
      <section className="py-16 bg-gradient-to-r from-[#0E1A2B] to-[#2E6049] text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <Building2 className="w-16 h-16 mx-auto mb-6 text-[#4CC1E9]" />
          <h2 className="text-3xl font-bold mb-4">Enterprise Support</h2>
          <p className="text-xl text-white/80 mb-8 max-w-2xl mx-auto">
            Dedicated support, custom integrations, and white-label solutions 
            for enterprise clients with high-volume requirements.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <Users className="w-8 h-8 mx-auto mb-3 text-[#4CC1E9]" />
              <h3 className="font-semibold mb-2">Dedicated Account Manager</h3>
              <p className="text-sm text-white/70">Personal support for integration and optimization</p>
            </div>
            <div className="text-center">
              <Code className="w-8 h-8 mx-auto mb-3 text-[#4CC1E9]" />
              <h3 className="font-semibold mb-2">Custom Integrations</h3>
              <p className="text-sm text-white/70">Tailored solutions for your specific infrastructure</p>
            </div>
            <div className="text-center">
              <Shield className="w-8 h-8 mx-auto mb-3 text-[#4CC1E9]" />
              <h3 className="font-semibold mb-2">Priority Support</h3>
              <p className="text-sm text-white/70">24/7 technical support with guaranteed SLA</p>
            </div>
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