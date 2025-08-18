import React from "react";
import { Link } from "react-router-dom";
import { Button } from "./ui/button";
import { TrendingUp, Shield, Clock, BarChart3, Target, Zap } from "lucide-react";
import LiveIndexTicker from "./LiveIndexTicker";

const HeroSection = ({ onJoinWaitlist }) => {
  return (
    <section className="relative py-20 lg:py-32 overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-50 to-white"></div>
      
      {/* Decorative elements */}
      <div className="absolute top-20 right-10 w-64 h-64 bg-gradient-to-br from-[#4CC1E9]/10 to-[#007A99]/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-20 left-10 w-48 h-48 bg-gradient-to-br from-[#2E6049]/10 to-[#4CC1E9]/10 rounded-full blur-3xl"></div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center px-4 py-2 bg-[#4CC1E9]/10 border border-[#4CC1E9]/20 rounded-full mb-8">
            <BarChart3 className="w-4 h-4 text-[#4CC1E9] mr-2" />
            <span className="text-[#007A99] font-semibold text-sm">Stablecoin Yield Intelligence</span>
          </div>

          {/* Main headline */}
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight mb-8">
            <span className="text-[#0E1A2B]">The World's First</span>
            <br />
            <span className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] bg-clip-text text-transparent">
              Stablecoin Yield Benchmark
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-4xl mx-auto leading-relaxed">
            Combining cutting-edge data, risk analytics, and market intelligence into one trusted source. 
            Where yield meets safety in the digital dollar economy.
          </p>

          {/* StableYield Index Overview */}
          <div className="max-w-5xl mx-auto mb-8">
            <div className="bg-gradient-to-r from-[#4CC1E9]/10 to-[#007A99]/10 rounded-2xl p-8 border border-[#4CC1E9]/20">
              <h3 className="text-2xl font-bold text-[#0E1A2B] mb-4">
                What is the StableYield Index?
              </h3>
              <p className="text-lg text-gray-700 leading-relaxed mb-6">
                The StableYield Index is the <strong>world's first benchmark for stablecoin yields</strong>. 
                It measures and tracks how much return (APY) investors can earn on stablecoins — 
                adjusted for peg stability, liquidity, and risk.
              </p>
              <p className="text-base text-gray-600 leading-relaxed">
                Unlike simple yield trackers that only display headline APYs, the StableYield Index goes deeper. 
                It creates a <strong>risk-adjusted yield benchmark</strong> that reflects where safe, 
                sustainable returns actually exist in the stablecoin economy.
              </p>
            </div>
          </div>

          {/* Live Index Ticker */}
          <div className="max-w-2xl mx-auto mb-12">
            <LiveIndexTicker />
          </div>

          {/* Value propositions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12 max-w-5xl mx-auto">
            <Link to="/yield-indices" className="flex flex-col items-center p-6 bg-white/80 backdrop-blur-sm rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer">
              <div className="w-12 h-12 bg-gradient-to-br from-[#4CC1E9] to-[#007A99] rounded-lg flex items-center justify-center mb-4">
                <Target className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-[#0E1A2B] mb-2">Yield Indices & Benchmarks</h3>
              <p className="text-gray-600 text-center">Reference points for stablecoin market performance across all platforms</p>
            </Link>

            <Link to="/risk-analytics" className="flex flex-col items-center p-6 bg-white/80 backdrop-blur-sm rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer">
              <div className="w-12 h-12 bg-gradient-to-br from-[#4CC1E9] to-[#007A99] rounded-lg flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-[#0E1A2B] mb-2">Risk-Adjusted Analytics</h3>
              <p className="text-gray-600 text-center">Peg stability, liquidity depth, and counterparty risk analysis</p>
            </Link>

            <div className="flex flex-col items-center p-6 bg-white/80 backdrop-blur-sm rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
              <div className="w-12 h-12 bg-gradient-to-br from-[#4CC1E9] to-[#007A99] rounded-lg flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-[#0E1A2B] mb-2">API Feeds & Dashboards</h3>
              <p className="text-gray-600 text-center">Real-time intelligence for funds, exchanges, and institutions</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;