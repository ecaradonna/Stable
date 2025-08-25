import React from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import SEOHead from "../components/SEOHead";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { 
  Shield, 
  TrendingUp, 
  BarChart3, 
  Target, 
  CheckCircle, 
  ArrowRight,
  Activity,
  DollarSign,
  AlertTriangle,
  Calculator,
  Zap
} from "lucide-react";

const RiskAnalyticsPage = () => {
  const riskDimensions = [
    {
      icon: DollarSign,
      title: "Peg Stability",
      description: "Continuous monitoring of stablecoin price deviations relative to $1.00 across major trading venues.",
      details: [
        "Calculation of short-horizon volatility, deviation persistence, and re-anchoring velocity",
        "Generation of a peg stability score that penalizes yields associated with unstable or weakly collateralized assets"
      ],
      color: "text-[#4CC1E9]"
    },
    {
      icon: Activity,
      title: "Liquidity Depth",
      description: "Aggregation of order book data and trading volumes across top exchanges and on-chain liquidity pools.",
      details: [
        "Measurement of executable depth within defined basis-point thresholds (e.g., 10 bps, 20 bps, 50 bps)",
        "Calculation of effective slippage costs for institutional-scale allocations",
        "Resulting liquidity score reflects capital efficiency and exit feasibility"
      ],
      color: "text-[#007A99]"
    },
    {
      icon: Shield,
      title: "Counterparty & Platform Risk",
      description: "Continuous evaluation of CeFi balance-sheet health, on-chain protocol solvency, and collateral sufficiency.",
      details: [
        "Integration of security assessments (smart contract audits, governance risks, historical exploits)",
        "Incorporation of credit-like factors such as rehypothecation exposure and custody concentration"
      ],
      color: "text-[#2E6049]"
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <SEOHead 
        title="Risk-Adjusted Analytics – Stablecoin Risk Assessment Platform"
        description="Advanced risk analytics for stablecoins. Peg stability metrics, liquidity analysis, counterparty risk assessment. Professional tools for institutional risk management."
        url="https://stableyield.com/risk-analytics"
      />
      <Header />
      
      {/* Hero Section */}
      <section className="pt-20 pb-16 bg-gradient-to-br from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 bg-[#4CC1E9]/10 border border-[#4CC1E9]/20 rounded-full mb-6">
              <BarChart3 className="w-4 h-4 text-[#4CC1E9] mr-2" />
              <span className="text-[#007A99] font-semibold text-sm">Quantitative Risk Frameworks</span>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold text-[#0E1A2B] mb-6">
              Risk-Adjusted Analytics
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-4xl mx-auto leading-relaxed">
              Quantitative frameworks for evaluating the true quality of stablecoin yields.
            </p>
            
            <div className="bg-gradient-to-r from-[#4CC1E9]/10 to-[#007A99]/10 rounded-2xl p-8 border border-[#4CC1E9]/20 max-w-5xl mx-auto">
              <p className="text-lg text-gray-700 leading-relaxed">
                StableYield's analytics engine applies a <strong>multi-factor risk model</strong> to every yield source, 
                ensuring that returns are evaluated not only on nominal APY but on their underlying stability, 
                liquidity, and counterparty soundness.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Key Dimensions Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-[#0E1A2B] mb-6">
              Key Dimensions of Analysis
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Our comprehensive risk framework evaluates yield opportunities across three critical dimensions.
            </p>
          </div>

          <div className="space-y-12">
            {riskDimensions.map((dimension, index) => {
              const IconComponent = dimension.icon;
              return (
                <div key={index} className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
                  <div className="flex items-start space-x-6">
                    <div className="flex-shrink-0">
                      <div className="w-16 h-16 bg-gradient-to-br from-[#4CC1E9] to-[#007A99] rounded-xl flex items-center justify-center">
                        <IconComponent className="w-8 h-8 text-white" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-2xl font-bold text-[#0E1A2B] mb-4">{dimension.title}</h3>
                      <p className="text-lg text-gray-700 mb-6 leading-relaxed">
                        {dimension.description}
                      </p>
                      <div className="space-y-3">
                        {dimension.details.map((detail, detailIndex) => (
                          <div key={detailIndex} className="flex items-start space-x-3">
                            <div className="flex-shrink-0 mt-1">
                              <div className="w-2 h-2 bg-[#4CC1E9] rounded-full"></div>
                            </div>
                            <p className="text-gray-600 leading-relaxed">{detail}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* RAY Formula Section */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-[#0E1A2B] mb-6">
              Risk-Adjusted Yield (RAY) Metric
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Each yield opportunity receives a comprehensive risk assessment, resulting in our proprietary RAY metric.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 md:p-12 shadow-xl border border-gray-100 max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <div className="inline-flex items-center px-4 py-2 bg-[#4CC1E9]/10 border border-[#4CC1E9]/20 rounded-full mb-6">
                <Calculator className="w-4 h-4 text-[#4CC1E9] mr-2" />
                <span className="text-[#007A99] font-semibold text-sm">Mathematical Formula</span>
              </div>
            </div>

            <div className="bg-gradient-to-r from-[#0E1A2B] to-[#2E6049] rounded-xl p-8 text-white mb-8">
              <div className="text-center">
                <h3 className="text-2xl font-bold mb-6">Risk-Adjusted Yield Formula</h3>
                <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 font-mono text-xl">
                  <div className="mb-2">RAY = APY × f(Peg Stability, Liquidity, Counterparty Risk)</div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-6 bg-[#4CC1E9]/5 rounded-xl border border-[#4CC1E9]/20">
                <DollarSign className="w-8 h-8 text-[#4CC1E9] mx-auto mb-3" />
                <h4 className="font-bold text-[#0E1A2B] mb-2">Peg Stability</h4>
                <p className="text-sm text-gray-600">Price deviation monitoring and volatility assessment</p>
              </div>
              
              <div className="text-center p-6 bg-[#007A99]/5 rounded-xl border border-[#007A99]/20">
                <Activity className="w-8 h-8 text-[#007A99] mx-auto mb-3" />
                <h4 className="font-bold text-[#0E1A2B] mb-2">Liquidity</h4>
                <p className="text-sm text-gray-600">Market depth and execution efficiency analysis</p>
              </div>
              
              <div className="text-center p-6 bg-[#2E6049]/5 rounded-xl border border-[#2E6049]/20">
                <Shield className="w-8 h-8 text-[#2E6049] mx-auto mb-3" />
                <h4 className="font-bold text-[#0E1A2B] mb-2">Counterparty Risk</h4>
                <p className="text-sm text-gray-600">Platform security and solvency evaluation</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Value Proposition Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-r from-[#0E1A2B] to-[#2E6049] rounded-2xl p-8 md:p-12 text-white">
            <div className="max-w-4xl mx-auto text-center">
              <h2 className="text-3xl md:text-4xl font-bold mb-8">
                Institution-Grade Risk Assessment
              </h2>
              
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-8 mb-8 border border-white/20">
                <p className="text-xl leading-relaxed mb-6">
                  This metric provides a <strong>normalized, institution-grade measure</strong> of stablecoin returns — 
                  enabling allocators, funds, and exchanges to distinguish between headline APYs and genuinely sustainable yields.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="w-6 h-6 text-[#4CC1E9] flex-shrink-0" />
                    <span className="text-white/90">Quantitative Risk Models</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="w-6 h-6 text-[#4CC1E9] flex-shrink-0" />
                    <span className="text-white/90">Real-Time Monitoring</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="w-6 h-6 text-[#4CC1E9] flex-shrink-0" />
                    <span className="text-white/90">Institutional Standards</span>
                  </div>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
                <Button className="bg-white text-[#0E1A2B] hover:bg-gray-100 font-semibold px-8 py-3">
                  View Risk Dashboard
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
                <Button variant="outline" className="border-white text-white hover:bg-white hover:text-[#0E1A2B] px-8 py-3">
                  Risk Methodology
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

export default RiskAnalyticsPage;