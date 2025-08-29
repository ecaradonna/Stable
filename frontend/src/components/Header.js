import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "./ui/button";
import { FileText } from "lucide-react";

const Header = ({ onJoinWaitlist, onDownloadWhitepaper }) => {
  const location = useLocation();
  
  const isActivePage = (path) => {
    return location.pathname === path;
  };
  
  const getLinkClassName = (path) => {
    const baseClasses = "transition-colors font-medium px-3 py-2 rounded-md";
    if (isActivePage(path)) {
      return `${baseClasses} text-[#0E1A2B] bg-gray-100 font-semibold`;
    }
    return `${baseClasses} text-[#0E1A2B] hover:text-[#2E6049] hover:bg-gray-50`;
  };

  return (
    <header className="sticky top-0 bg-white/95 backdrop-blur-sm border-b border-gray-100 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo - Separate from Navigation */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-[#4CC1E9] to-[#007A99] rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-xl">SY</span>
            </div>
            <div>
              <div className="text-xl font-bold text-[#0E1A2B]">StableYield</div>
              <div className="text-xs text-gray-600">Market Intelligence</div>
            </div>
          </Link>

          {/* Navigation - Separate Section */}
          <nav className="hidden md:flex items-center space-x-1">
            <Link 
              to="/index-dashboard"
              className={getLinkClassName('/index-dashboard')}
            >
              Live Index
            </Link>
            <Link 
              to="/yield-indices" 
              className={getLinkClassName('/yield-indices')}
            >
              Yield Indices & Benchmarks
            </Link>
            <Link 
              to="/peg-monitor" 
              className={getLinkClassName('/peg-monitor')}
            >
              Peg Monitor
            </Link>
            <Link 
              to="/blog" 
              className={getLinkClassName('/blog')}
            >
              Market Insights
            </Link>
            <Link 
              to="/methodology" 
              className={getLinkClassName('/methodology')}
            >
              Index Methodology
            </Link>
            <Link 
              to="/api-documentation" 
              className={getLinkClassName('/api-documentation')}
            >
              API Access
            </Link>
          </nav>

          {/* Actions */}
          <div className="hidden md:flex items-center space-x-4">
            {/* Download Whitepaper Button */}
            <Button 
              onClick={onDownloadWhitepaper}
              variant="outline"
              className="border-[#4CC1E9] text-[#4CC1E9] hover:bg-[#4CC1E9] hover:text-white font-semibold px-4 py-2 rounded-lg transition-all duration-300"
            >
              <FileText className="w-4 h-4 mr-2" />
              Whitepaper
            </Button>
            
            {/* Contact Us Button */}
            <Button 
              onClick={onJoinWaitlist}
              className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] text-white font-semibold px-6 py-2 rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              Contact Us
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;