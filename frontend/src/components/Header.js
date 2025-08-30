import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { FileText, Menu, X } from "lucide-react";

const Header = ({ onJoinWaitlist, onDownloadWhitepaper }) => {
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  
  const isActivePage = (path) => {
    return location.pathname === path;
  };
  
  const getLinkClassName = (path) => {
    const baseClasses = "font-medium px-3 py-2 rounded-none transition-all duration-200 text-[15px] font-inter relative border-b-2 border-transparent";
    if (isActivePage(path)) {
      return `${baseClasses} text-[#1F4FFF] border-b-[#1F4FFF]`;
    }
    return `${baseClasses} text-[#1A1A1A] hover:text-[#1F4FFF] hover:border-b-[#1F4FFF]`;
  };

  const navigationItems = [
    { path: "/index-dashboard", label: "Live Index", showBadge: true },
    { path: "/yield-indices", label: "Indices & Benchmarks" },
    { path: "/peg-monitor", label: "Peg Monitor" },
    { path: "/blog", label: "Market Insights" },
    { path: "/methodology", label: "Methodology" },
    { path: "/api-documentation", label: "API Access" }
  ];

  return (
    <header className="sticky top-0 bg-white backdrop-blur-sm border-b border-[#E5E7EB] z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          
          {/* Left Section - Branding */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-[#1F4FFF] rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-xl">SY</span>
            </div>
            <div>
              <div className="text-[18px] font-semibold text-[#1A1A1A] font-inter">StableYield</div>
              <div className="text-[12px] text-[#6B7280] font-inter">Institutional Stablecoin Benchmark</div>
            </div>
          </Link>

          {/* Center Section - Navigation Menu (Desktop) */}
          <nav className="hidden lg:flex items-center space-x-8">
            {navigationItems.map((item) => (
              <div key={item.path} className="relative">
                <Link 
                  to={item.path}
                  className={getLinkClassName(item.path)}
                >
                  <span className="flex items-center space-x-2">
                    <span>{item.label}</span>
                    {item.showBadge && (
                      <Badge className="bg-[#1F4FFF] text-white text-[10px] px-2 py-0.5 rounded-full font-medium">
                        Live
                      </Badge>
                    )}
                  </span>
                </Link>
              </div>
            ))}
          </nav>

          {/* Right Section - CTA Buttons (Desktop) */}
          <div className="hidden lg:flex items-center space-x-4">
            {/* Secondary CTA - Whitepaper */}
            <Button 
              onClick={onDownloadWhitepaper}
              variant="outline"
              className="border border-[#1F4FFF] text-[#1F4FFF] bg-white hover:bg-[#1F4FFF] hover:text-white font-medium px-[18px] py-[10px] rounded-md transition-all duration-200 text-[14px]"
            >
              <FileText className="w-4 h-4 mr-2" />
              Whitepaper
            </Button>
            
            {/* Primary CTA - Request API Access */}
            <Link to="/api-documentation">
              <Button 
                className="bg-[#E47C3C] hover:bg-[#E47C3C]/90 text-white font-medium px-[18px] py-[10px] rounded-md transition-all duration-200 shadow-sm hover:shadow-md text-[14px]"
              >
                Request API Access
              </Button>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <div className="lg:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-[#1A1A1A]"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {isMenuOpen && (
          <div className="lg:hidden border-t border-[#E5E7EB] bg-white">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navigationItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`${getLinkClassName(item.path)} block w-full text-left`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span className="flex items-center space-x-2">
                    <span>{item.label}</span>
                    {item.showBadge && (
                      <Badge className="bg-[#1F4FFF] text-white text-[10px] px-2 py-0.5 rounded-full font-medium">
                        Live
                      </Badge>
                    )}
                  </span>
                </Link>
              ))}
              
              {/* Mobile CTA Buttons */}
              <div className="pt-4 space-y-2">
                <Button 
                  onClick={onDownloadWhitepaper}
                  variant="outline"
                  className="w-full border border-[#1F4FFF] text-[#1F4FFF] bg-white hover:bg-[#1F4FFF] hover:text-white font-medium py-2 rounded-md text-[14px]"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Whitepaper
                </Button>
                
                <Link to="/api-documentation">
                  <Button 
                    onClick={() => setIsMenuOpen(false)}
                    className="w-full bg-[#E47C3C] hover:bg-[#E47C3C]/90 text-white font-medium py-2 rounded-md text-[14px]"
                  >
                    Request API Access
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;