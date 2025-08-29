import React from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { ArrowRight, BarChart3, Shield, TrendingUp, Activity, CheckCircle, Target, Zap } from "lucide-react";

const StableYieldIndex = ({ onJoinWaitlist }) => {
  const capabilities = [
    {
      icon: TrendingUp,
      title: "Real-Time Yields",
      description: "Live yield data across 50+ DeFi and CeFi protocols with 30-second updates and historical performance tracking.",
      color: "text-[#1F4FFF]",
      bgColor: "bg-[#1F4FFF]/10"
    },
    {
      icon: BarChart3,
      title: "SYI Benchmark",
      description: "The world's first institutional-grade stablecoin yield benchmark, comparable to T-Bills and Euribor.",
      color: "text-[#1F4FFF]",
      bgColor: "bg-[#1F4FFF]/10"
    },
    {
      icon: Shield,
      title: "Risk Analytics",
      description: "Advanced peg monitoring, liquidity analysis, and automated risk regime detection with confidence scoring.",
      color: "text-[#D64545]",
      bgColor: "bg-[#D64545]/10"
    },
    {
      icon: Activity,
      title: "Market Intelligence",
      description: "Institutional insights, portfolio stress testing, and cross-asset correlations for informed decision making.",
      color: "text-[#9FA6B2]",
      bgColor: "bg-[#9FA6B2]/10"
    }
  ];

  const whyItMatters = [
    {
      icon: CheckCircle,
      title: "Clarity",
      description: "Cut through the noise with standardized, transparent yield calculations across all major stablecoins.",
      highlight: "clarity"
    },
    {
      icon: Shield,
      title: "Risk-Adjusted", 
      description: "Unlike raw APYs, our Risk-Adjusted Yield (RAY) accounts for peg stability, liquidity depth, and protocol risk.",
      highlight: "risk"
    },
    {
      icon: Target,
      title: "Benchmark",
      description: "The industry standard for measuring and comparing stablecoin performance — trusted by institutions globally.",
      highlight: "benchmark"
    },
    {
      icon: Zap,
      title: "Transparency",
      description: "Open methodology, auditable calculations, and real-time data — no black boxes or proprietary secrets.",
      highlight: "transparency"
    }
  ];

  return (
    <div className="bg-white">
      {/* What is SYI Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="bg-[#1F4FFF]/10 text-[#1F4FFF] mb-6 px-4 py-2">
              What is the StableYield Index?
            </Badge>
            <h2 className="text-3xl font-bold text-[#0E1A2B] mb-6">
              The world's first benchmark for stablecoin yields
            </h2>
            <p className="text-xl text-gray-600 max-w-4xl mx-auto mb-8">
              The StableYield Index measures and tracks how much return investors can earn on stablecoins — 
              adjusted for peg stability, liquidity, and risk. Unlike simple yield trackers that only display 
              headline APYs, the StableYield Index goes deeper.
            </p>
            <div className="bg-[#1F4FFF]/5 border-l-4 border-[#1F4FFF] p-6 max-w-4xl mx-auto rounded-r-lg">
              <p className="text-lg text-gray-700">
                It creates a <strong className="text-[#1F4FFF]">risk-adjusted yield benchmark</strong> that reflects 
                where <strong>safe, sustainable returns</strong> actually exist in the stablecoin economy.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Capabilities Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
              Comprehensive Stablecoin Intelligence
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Everything you need to understand, analyze, and optimize stablecoin yields in one platform
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            {capabilities.map((capability, index) => {
              const IconComponent = capability.icon;
              return (
                <Card key={index} className="hover:shadow-lg transition-shadow border-0 shadow-md">
                  <CardHeader>
                    <div className="flex items-center space-x-4">
                      <div className={`w-12 h-12 ${capability.bgColor} rounded-lg flex items-center justify-center`}>
                        <IconComponent className={`w-6 h-6 ${capability.color}`} />
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

      {/* Why It Matters Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-[#0E1A2B] mb-4">
              Why StableYield Matters
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              The stablecoin economy needs reliable, institutional-grade benchmarks
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {whyItMatters.map((item, index) => {
              const IconComponent = item.icon;
              return (
                <div key={index} className="text-center group">
                  <div className="w-16 h-16 bg-[#1F4FFF]/10 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:bg-[#1F4FFF]/20 transition-colors">
                    <IconComponent className="w-8 h-8 text-[#1F4FFF]" />
                  </div>
                  <h3 className="text-xl font-semibold text-[#0E1A2B] mb-3">{item.title}</h3>
                  <p className="text-gray-600 text-sm leading-relaxed">{item.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Closing CTA Section */}
      <section className="py-20 bg-gradient-to-r from-[#1F4FFF] to-[#9FA6B2]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              Ready to explore stablecoin yields?
            </h2>
            <p className="text-xl text-white/90 max-w-2xl mx-auto mb-8">
              Get instant access to real-time data, risk analytics, and institutional-grade benchmarks
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
              <Button 
                className="bg-white text-[#1F4FFF] hover:bg-gray-100 font-semibold px-8 py-3 rounded-xl transition-all duration-300"
                onClick={() => window.location.href = '/index-dashboard'}
              >
                Explore Live Index
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
              <Button 
                variant="outline" 
                className="border-2 border-white text-white hover:bg-white hover:text-[#1F4FFF] font-semibold px-8 py-3 rounded-xl transition-all duration-300"
                onClick={onJoinWaitlist}
              >
                Request API Access
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default StableYieldIndex;