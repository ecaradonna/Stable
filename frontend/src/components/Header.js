import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { FileText } from "lucide-react";

const Header = ({ onJoinWaitlist, onDownloadWhitepaper }) => {
  const navigate = useNavigate();

  const handleLiveIndexClick = (e) => {
    e.preventDefault();
    console.log('Live Index clicked - navigating to /index-dashboard');
    
    try {
      // Try React Router navigation first
      navigate('/index-dashboard');
    } catch (error) {
      console.error('React Router navigation failed:', error);
      // Fallback to window.location
      window.location.href = '/index-dashboard';
    }
    
    // Additional fallback with timeout
    setTimeout(() => {
      if (window.location.pathname !== '/index-dashboard') {
        console.log('Navigation timeout - forcing window.location change');
        window.location.href = '/index-dashboard';
      }
    }, 1000);
  };

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
            <button 
              onClick={handleLiveIndexClick}
              className="text-[#0E1A2B] hover:text-[#2E6049] transition-colors font-medium cursor-pointer"
            >
              Live Index
            </button>
            {/* Backup Link for fallback */}
            <Link 
              to="/index-dashboard" 
              className="text-[#0E1A2B] hover:text-[#2E6049] transition-colors font-medium ml-4 text-sm"
              style={{display: 'none'}}
              id="backup-live-index-link"
            >
              [Dashboard]
            </Link>
            <Link to="/yield-indices" className="text-[#0E1A2B] hover:text-[#2E6049] transition-colors font-medium">
              Yield Indices & Benchmarks
            </Link>
            <Link to="/peg-monitor" className="text-[#0E1A2B] hover:text-[#2E6049] transition-colors font-medium">
              Peg Monitor
            </Link>
            <Link to="/blog" className="text-[#0E1A2B] hover:text-[#2E6049] transition-colors font-medium">
              Market Insights
            </Link>
            <Link to="/methodology" className="text-[#0E1A2B] hover:text-[#2E6049] transition-colors font-medium">
              Index Methodology
            </Link>
            <Link to="/api-documentation" className="text-[#0E1A2B] hover:text-[#2E6049] transition-colors font-medium">
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