import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { TrendingUp, Shield, Zap, Target, BarChart3, CheckCircle, ArrowRight } from "lucide-react";
import { Button } from "./ui/button";

const StableYieldIndex = () => {
  const indexComponents = [
    {
      icon: BarChart3,
      title: "Raw Yield Data",
      description: "Aggregated from DeFi, CeFi, and TradFi sources",
      color: "text-[#4CC1E9]"
    },
    {
      icon: Shield, 
      title: "Peg Stability Metrics",
      description: "Is the stablecoin truly holding $1.00?",
      color: "text-[#007A99]"
    },
    {
      icon: Zap,
      title: "Liquidity Metrics", 
      description: "How easily can capital move without slippage?",
      color: "text-[#2E6049]"
    }
  ];

  const benefits = [
    {
      icon: Target,
      title: "Brings Clarity to a Fragmented Market",
      description: "Stablecoin yields are scattered across platforms, protocols, and exchanges. The StableYield Index aggregates this into a single reference point, just like the S&P 500 does for equities."
    },
    {
      icon: Shield,
      title: "Separates Signal from Noise", 
      description: "Not all yields are created equal — some come with hidden risks (illiquidity, depegging, counterparty failure). The Index cuts through hype by weighting yields based on safety and liquidity, not just APY size."
    },
    {
      icon: BarChart3,
      title: "Creates a Benchmark for Investors",
      description: "Funds, institutions, and allocators need benchmarks to measure performance. The StableYield Index becomes the standard yardstick for stablecoin strategies."
    },
    {
      icon: CheckCircle,
      title: "Supports Transparency & Trust",
      description: "By publishing a transparent methodology, StableYield positions itself as the data authority for stablecoin yields, helping investors make more informed decisions."
    },
    {
      icon: TrendingUp,
      title: "Enables Products & Reporting",
      description: "Just like equity or bond indices underpin ETFs, structured products, and media coverage, the StableYield Index can be licensed to funds, exchanges, custodians, and financial media."
    }
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center px-4 py-2 bg-[#4CC1E9]/10 border border-[#4CC1E9]/20 rounded-full mb-6">
            <BarChart3 className="w-4 h-4 text-[#4CC1E9] mr-2" />
            <span className="text-[#007A99] font-semibold text-sm">World's First Stablecoin Yield Benchmark</span>
          </div>
          
          <h2 className="text-3xl md:text-5xl font-bold text-[#0E1A2B] mb-6">
            What is the StableYield Index?
          </h2>
          
          <div className="max-w-4xl mx-auto">
            <p className="text-xl text-gray-600 leading-relaxed mb-8">
              The StableYield Index is the <strong>world's first benchmark for stablecoin yields</strong>. 
              It measures and tracks how much return (APY) investors can earn on stablecoins — 
              adjusted for peg stability, liquidity, and risk.
            </p>
            
            <div className="bg-gradient-to-r from-[#4CC1E9]/10 to-[#007A99]/10 rounded-2xl p-6 border border-[#4CC1E9]/20">
              <p className="text-lg text-[#0E1A2B] leading-relaxed">
                Unlike simple yield trackers that only display headline APYs, the StableYield Index goes deeper. 
                It creates a <strong>risk-adjusted yield benchmark</strong> that reflects where safe, 
                sustainable returns actually exist in the stablecoin economy.
              </p>
            </div>
          </div>
        </div>

        {/* Index Components */}
        <div className="mb-16">
          <h3 className="text-2xl font-bold text-[#0E1A2B] text-center mb-8">
            How the Index Works
          </h3>
          <p className="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
            The StableYield Index blends three critical components to create the most comprehensive 
            stablecoin yield benchmark:
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {indexComponents.map((component, index) => {
              const IconComponent = component.icon;
              return (
                <Card key={index} className="text-center hover:shadow-lg transition-all duration-300 border-2 hover:border-[#4CC1E9]/30">
                  <CardHeader>
                    <div className={`w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-[#4CC1E9]/10 to-[#007A99]/10 flex items-center justify-center`}>
                      <IconComponent className={`w-8 h-8 ${component.color}`} />
                    </div>
                    <CardTitle className="text-xl text-[#0E1A2B]">{component.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600">{component.description}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
          
          <div className="text-center mt-8">
            <Badge className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] text-white px-4 py-2">
              = Risk-Adjusted Yield Benchmark
            </Badge>
          </div>
        </div>

        {/* Why It's Important */}
        <div className="mb-16">
          <h3 className="text-2xl md:text-3xl font-bold text-[#0E1A2B] text-center mb-12">
            Why is it Important?
          </h3>
          
          <div className="space-y-8">
            {benefits.map((benefit, index) => {
              const IconComponent = benefit.icon;
              return (
                <div key={index} className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow border border-gray-100">
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-gradient-to-br from-[#4CC1E9] to-[#007A99] rounded-lg flex items-center justify-center">
                        <IconComponent className="w-6 h-6 text-white" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <h4 className="text-xl font-bold text-[#0E1A2B] mb-3">{benefit.title}</h4>
                      <p className="text-gray-600 leading-relaxed">{benefit.description}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Bottom Summary */}
        <div className="bg-gradient-to-r from-[#0E1A2B] to-[#2E6049] rounded-2xl p-8 md:p-12 text-white text-center">
          <div className="max-w-4xl mx-auto">
            <h3 className="text-2xl md:text-3xl font-bold mb-6">The Foundation for Smarter Stablecoin Investing</h3>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 mb-8">
              <p className="text-xl leading-relaxed">
                <strong>In short:</strong> The StableYield Index transforms stablecoin yields from a chaotic marketplace 
                into a transparent, trusted benchmark — the foundation for safer allocation, better reporting, and smarter products.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
              <Button className="bg-white text-[#0E1A2B] hover:bg-gray-100 font-semibold px-8 py-3">
                View Live Index
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
              <Button variant="outline" className="border-white text-white hover:bg-white hover:text-[#0E1A2B] px-8 py-3">
                Read Methodology
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default StableYieldIndex;