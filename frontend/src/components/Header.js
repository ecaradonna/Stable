import React from "react";
import { Link } from "react-router-dom";
import { Button } from "./ui/button";

const Header = ({ onJoinWaitlist }) => {
  return (
    <header className="sticky top-0 bg-white/95 backdrop-blur-sm border-b border-gray-100 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#4CC1E9] to-[#007A99] flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-lg">Y</span>
              </div>
            </div>
            <div className="hidden sm:block">
              <span className="text-xl font-bold tracking-wider">
                <span className="text-[#0E1A2B]">STABLE</span>
                <span className="text-[#2E6049]">YIELD</span>
              </span>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link to="/index-dashboard" className="text-[#0E1A2B] hover:text-[#2E6049] transition-colors font-medium">
              Live Index
            </Link>
            <Link to="/yield-indices" className="text-[#0E1A2B] hover:text-[#2E6049] transition-colors font-medium">
              Yield Indices & Benchmarks
            </Link>
            <Link to="/blog" className="text-[#0E1A2B] hover:text-[#2E6049] transition-colors font-medium">
              Market Insights
            </Link>
            <Link to="/methodology" className="text-[#0E1A2B] hover:text-[#2E6049] transition-colors font-medium">
              Index Methodology
            </Link>
          </nav>

          {/* CTA Button */}
          <Button 
            onClick={onJoinWaitlist}
            className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] text-white font-semibold px-6 py-2 rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          >
            Join Waitlist
          </Button>
        </div>
      </div>
    </header>
  );
};

export default Header;