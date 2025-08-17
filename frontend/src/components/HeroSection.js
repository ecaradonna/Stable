import React from "react";
import { Button } from "./ui/button";
import { TrendingUp, Shield, Clock } from "lucide-react";

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
          {/* Main headline */}
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight mb-8">
            <span className="text-[#0E1A2B]">The Benchmark for</span>
            <br />
            <span className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] bg-clip-text text-transparent">
              Stablecoin Yields
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-4xl mx-auto leading-relaxed">
            Transparent data on stablecoin returns. No custody. No hype. Just facts.
          </p>

          {/* Features grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12 max-w-4xl mx-auto">
            <div className="flex flex-col items-center p-6 bg-white/80 backdrop-blur-sm rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
              <div className="w-12 h-12 bg-gradient-to-br from-[#4CC1E9] to-[#007A99] rounded-lg flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-[#0E1A2B] mb-2">Transparency</h3>
              <p className="text-gray-600 text-center">Real-time data from verified sources</p>
            </div>

            <div className="flex flex-col items-center p-6 bg-white/80 backdrop-blur-sm rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
              <div className="w-12 h-12 bg-gradient-to-br from-[#4CC1E9] to-[#007A99] rounded-lg flex items-center justify-center mb-4">
                <Clock className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-[#0E1A2B] mb-2">Speed</h3>
              <p className="text-gray-600 text-center">Instant access to current yields</p>
            </div>

            <div className="flex flex-col items-center p-6 bg-white/80 backdrop-blur-sm rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
              <div className="w-12 h-12 bg-gradient-to-br from-[#4CC1E9] to-[#007A99] rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-[#0E1A2B] mb-2">Authority</h3>
              <p className="text-gray-600 text-center">Trusted by institutions worldwide</p>
            </div>
          </div>

          {/* CTA Button */}
          <Button 
            onClick={onJoinWaitlist}
            className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] text-white font-bold text-lg px-12 py-4 rounded-xl transition-all duration-300 shadow-xl hover:shadow-2xl transform hover:-translate-y-1"
          >
            Join Waitlist
          </Button>

          {/* Trust indicators */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <p className="text-gray-500 text-sm mb-4">Trusted by institutions and traders worldwide</p>
            <div className="flex justify-center items-center space-x-8 opacity-50">
              <div className="text-gray-400 font-semibold">CeFi • DeFi • TradFi</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;