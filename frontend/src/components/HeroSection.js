import React from "react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { ArrowRight, TrendingUp, CheckCircle, Shield, Activity, Clock } from "lucide-react";

const HeroSection = ({ onJoinWaitlist, onDownloadWhitepaper }) => {
  return (
    <section className="relative py-20 lg:py-32 overflow-hidden bg-gradient-to-br from-gray-50 to-white">
      {/* Background Elements */}
      <div className="absolute top-20 right-10 w-64 h-64 bg-gradient-to-br from-[#1F4FFF]/10 to-[#9FA6B2]/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-20 left-10 w-48 h-48 bg-gradient-to-br from-[#1F4FFF]/5 to-[#E47C3C]/10 rounded-full blur-3xl"></div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center px-4 py-2 bg-[#1F4FFF]/10 border border-[#1F4FFF]/20 rounded-full mb-8">
            <Activity className="w-4 h-4 text-[#1F4FFF] mr-2" />
            <span className="text-sm font-medium text-[#1F4FFF]">Stablecoin Yield Intelligence</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-4xl md:text-6xl font-bold text-[#0E1A2B] mb-6 leading-tight">
            The Benchmark for 
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#1F4FFF] to-[#9FA6B2]">
              {" "}Stablecoin Yields
            </span>
          </h1>
          
          {/* Subtitle */}
          <p className="text-xl text-gray-600 max-w-4xl mx-auto mb-8 leading-relaxed">
            Where yield meets safety in the digital dollar economy. Real-time data, risk-adjusted analytics, 
            and institutional-grade benchmarks — all in one trusted source.
          </p>

          {/* SYI Live Value Box */}
          <div className="inline-flex items-center justify-center mb-8">
            <div className="bg-white rounded-2xl border-2 border-[#1F4FFF]/20 p-6 shadow-lg">
              <div className="text-center">
                <div className="text-sm font-medium text-gray-500 mb-2">StableYield Index (SYI)</div>
                <div className="text-4xl font-bold text-[#1F4FFF] mb-2">4.47%</div>
                <div className="flex items-center justify-center space-x-4">
                  <Badge className="bg-[#1F4FFF]/10 text-[#1F4FFF] border-[#1F4FFF]/20">
                    <TrendingUp className="w-3 h-3 mr-1" />
                    Live
                  </Badge>
                  <Badge className="bg-gray-100 text-gray-700">
                    6 Constituents
                  </Badge>
                </div>
                <p className="text-xs text-gray-500 mt-3 max-w-xs">
                  The first risk-adjusted benchmark for stablecoin yields — comparable to T-Bills & Euribor.
                </p>
              </div>
            </div>
          </div>

          {/* Trust Indicators */}
          <div className="flex flex-wrap items-center justify-center gap-6 mb-12">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <CheckCircle className="w-4 h-4 text-[#1F4FFF]" />
              <span>Real-time Data</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Shield className="w-4 h-4 text-[#1F4FFF]" />
              <span>Risk-Adjusted</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Activity className="w-4 h-4 text-[#1F4FFF]" />
              <span>Institutional Grade</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Clock className="w-4 h-4 text-[#1F4FFF]" />
              <span>30s Updates</span>
            </div>
          </div>

          {/* Primary CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <Button 
              className="bg-[#1F4FFF] hover:bg-[#1F4FFF]/90 text-white font-semibold px-8 py-4 text-lg rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              onClick={() => window.location.href = '/index-dashboard'}
            >
              Explore Live Index
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            
            {/* Mobile-optimized API Access Button */}
            <div 
              className="inline-flex items-center justify-center border-2 border-[#E47C3C] bg-white text-[#E47C3C] hover:bg-[#E47C3C] hover:text-white font-semibold px-8 py-4 text-lg rounded-xl transition-all duration-300 cursor-pointer min-w-[200px] touch-manipulation select-none"
              onClick={onJoinWaitlist}
              onTouchStart={() => {}}
              role="button"
              tabIndex={0}
            >
              <span className="text-[#E47C3C] hover:text-white font-semibold text-lg">Request API Access</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;