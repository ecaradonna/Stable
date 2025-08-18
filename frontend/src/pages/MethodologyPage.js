import React from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { BarChart3, Shield, Zap, Calculator, Database, Target } from "lucide-react";

const MethodologyPage = () => {
  const methodologySteps = [
    {
      step: 1,
      title: "Data Collection",
      icon: Database,
      description: "Aggregate real-time yield data from 50+ platforms across DeFi, CeFi, and TradFi",
      details: [
        "DeFi protocols: Aave, Compound, Curve, Convex",
        "CeFi platforms: Binance Earn, Coinbase, Kraken, Bybit",
        "TradFi integrations: Money market funds, treasury bills",
        "Update frequency: Every 30 seconds via WebSocket and REST APIs"
      ]
    },
    {
      step: 2, 
      title: "Peg Stability Analysis",
      icon: Shield,
      description: "Calculate peg deviation and volatility metrics using volume-weighted pricing",
      details: [
        "VWAP calculation across top 5-8 exchanges per stablecoin",
        "Peg deviation: 10,000 × (VWAP - 1.00) / 1.00 (basis points)",
        "Short-term volatility: Rolling 5-minute and 1-hour standard deviation",
        "Peg score: max(0, min(1, 1 - |peg_dev_bps|/50 - vol_5m_bps/100))"
      ]
    },
    {
      step: 3,
      title: "Liquidity Assessment", 
      icon: Zap,
      description: "Measure order book depth and spread across multiple venues",
      details: [
        "Depth calculation at 10, 20, and 50 basis points from mid-price",
        "Average spread monitoring across top exchanges",
        "Liquidity score: 40% depth_10bps + 40% depth_20bps + 20% spread_penalty",
        "Venue coverage requirement: Minimum 3 exchanges per stablecoin"
      ]
    },
    {
      step: 4,
      title: "Risk-Adjusted Calculation",
      icon: Calculator, 
      description: "Apply mathematical formula to weight yields by stability and liquidity",
      details: [
        "Formula: RY_APY = APY × (peg_score^α) × (liq_score^β)",
        "Default parameters: α = 1.0, β = 0.7",
        "Risk tier classification: Low (score &gt; 0.8), Medium (0.6-0.8), High (&lt;0.6)",
        "Capacity weighting for institutional allocation guidance"
      ]
    }
  ];

  const indexConstruction = [
    {
      name: "StableYield 100 Index",
      description: "Top 100 risk-adjusted stablecoin yield strategies",
      methodology: "Equal-risk weighted, monthly reconstitution, daily rebalancing"
    },
    {
      name: "StableYield CeFi Index", 
      description: "Centralized finance stablecoin yield benchmark",
      methodology: "Capacity-weighted, focuses on regulated platforms and traditional custody"
    },
    {
      name: "StableYield DeFi Index",
      description: "Decentralized finance protocol yield benchmark", 
      methodology: "TVL-weighted, emphasizes protocol maturity and audit history"
    },
    {
      name: "StableYield Risk Premium Index",
      description: "Excess return over risk-free rate (USD 3M Treasury)",
      methodology: "Average risk-adjusted yield minus 3-month Treasury bill yield"
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Header />
      
      <main className="pt-8">
        {/* Hero Section */}
        <section className="py-16 bg-gradient-to-br from-gray-50 to-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <div className="inline-flex items-center px-4 py-2 bg-[#4CC1E9]/10 border border-[#4CC1E9]/20 rounded-full mb-6">
                <BarChart3 className="w-4 h-4 text-[#4CC1E9] mr-2" />
                <span className="text-[#007A99] font-semibold text-sm">Transparent Methodology</span>
              </div>
              
              <h1 className="text-4xl md:text-6xl font-bold text-[#0E1A2B] mb-6">
                StableYield Index Methodology
              </h1>
              
              <p className="text-xl text-gray-600 max-w-4xl mx-auto">
                Learn how we calculate the world's first risk-adjusted stablecoin yield benchmark. 
                Our methodology combines cutting-edge data science with institutional-grade risk management.
              </p>
            </div>
          </div>
        </section>

        {/* Methodology Steps */}
        <section className="py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-[#0E1A2B] text-center mb-12">
              Four-Step Calculation Process
            </h2>
            
            <div className="space-y-8">
              {methodologySteps.map((step) => {
                const IconComponent = step.icon;
                return (
                  <Card key={step.step} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-gradient-to-r from-[#4CC1E9] to-[#007A99] text-white rounded-full flex items-center justify-center font-bold">
                            {step.step}
                          </div>
                          <div className="w-12 h-12 bg-[#4CC1E9]/10 rounded-lg flex items-center justify-center">
                            <IconComponent className="w-6 h-6 text-[#4CC1E9]" />
                          </div>
                        </div>
                        <div>
                          <CardTitle className="text-2xl text-[#0E1A2B]">{step.title}</CardTitle>
                          <p className="text-gray-600 mt-2">{step.description}</p>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="pl-16">
                        <ul className="space-y-2">
                          {step.details.map((detail, index) => (
                            <li key={index} className="flex items-start">
                              <div className="w-2 h-2 bg-[#4CC1E9] rounded-full mt-2 mr-3 flex-shrink-0"></div>
                              <span className="text-gray-700">{detail}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        </section>

        {/* Index Construction */}
        <section className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-[#0E1A2B] text-center mb-12">
              Index Family Construction
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {indexConstruction.map((index, i) => (
                <Card key={i} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-xl text-[#0E1A2B]">{index.name}</CardTitle>
                      <Badge className="bg-[#4CC1E9]/10 text-[#4CC1E9]">Live</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600 mb-4">{index.description}</p>
                    <div className="bg-[#4CC1E9]/5 rounded-lg p-3">
                      <h4 className="font-semibold text-[#0E1A2B] mb-1">Methodology:</h4>
                      <p className="text-sm text-gray-700">{index.methodology}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Quality Assurance */}
        <section className="py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="bg-gradient-to-r from-[#0E1A2B] to-[#2E6049] rounded-2xl p-8 md:p-12 text-white">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold mb-4">Quality Assurance & Monitoring</h2>
                <p className="text-xl opacity-90">Institutional-grade data validation and reliability</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
                  <Target className="w-8 h-8 text-[#4CC1E9] mb-4" />
                  <h3 className="font-bold mb-2">Data Quality</h3>
                  <ul className="text-sm opacity-90 space-y-1">
                    <li>• Outlier detection and filtering</li>
                    <li>• Minimum venue coverage requirements</li>
                    <li>• Real-time data validation</li>
                  </ul>
                </div>
                
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
                  <Shield className="w-8 h-8 text-[#4CC1E9] mb-4" />
                  <h3 className="font-bold mb-2">Risk Management</h3>
                  <ul className="text-sm opacity-90 space-y-1">
                    <li>• Peg deviation alerts (&gt;50 bps)</li>
                    <li>• Liquidity monitoring (score &lt;0.3)</li>
                    <li>• Platform health checks</li>
                  </ul>
                </div>
                
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
                  <BarChart3 className="w-8 h-8 text-[#4CC1E9] mb-4" />
                  <h3 className="font-bold mb-2">Performance SLOs</h3>
                  <ul className="text-sm opacity-90 space-y-1">
                    <li>• P95 latency &lt;5 seconds</li>
                    <li>• 99.9% data availability</li>
                    <li>• 15-min batch processing</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Footer CTA */}
        <section className="py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center bg-gradient-to-br from-[#4CC1E9]/5 to-[#007A99]/5 rounded-2xl p-12 border border-[#4CC1E9]/20">
              <h3 className="text-3xl font-bold text-[#0E1A2B] mb-4">
                Ready to Use Professional-Grade Data?
              </h3>
              <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
                Access the StableYield Index and comprehensive risk analytics through our API, 
                dashboards, or custom integrations for your institution.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
                <Badge className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] text-white px-6 py-3 text-lg font-semibold">
                  Contact for Enterprise Access
                </Badge>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default MethodologyPage;