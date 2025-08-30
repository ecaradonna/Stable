import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { ArrowRight } from "lucide-react";
import { useToast } from "../hooks/use-toast";
import { usersApi } from "../services/api";

const Footer = () => {
  const [email, setEmail] = useState("");
  const [isSubscribing, setIsSubscribing] = useState(false);
  const { toast } = useToast();

  const handleNewsletterSubmit = async (e) => {
    e.preventDefault();
    if (!email) return;

    setIsSubscribing(true);
    
    try {
      await usersApi.subscribeNewsletter({
        email: email,
        name: null
      });

      toast({
        title: "Subscribed successfully!",
        description: "You'll receive our weekly StableYield Intelligence Report.",
      });

      setEmail("");

    } catch (error) {
      console.error("Newsletter subscription error:", error);
      toast({
        title: "Subscription failed",
        description: error.response?.data?.detail || "Something went wrong. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsSubscribing(false);
    }
  };

  return (
    <footer className="bg-white border-t border-[#E5E7EB]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Top Row - Branding + Mission */}
        <div className="pt-12 pb-8">
          <Link to="/" className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-[#1F4FFF] rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-xl">SY</span>
            </div>
            <div className="text-xl font-bold text-[#1A1A1A] font-inter">StableYield</div>
          </Link>
          <p className="text-[13px] text-[#6B7280] font-inter max-w-md">
            The Institutional Benchmark for Stablecoin Yields
          </p>
        </div>

        {/* Middle Row - Navigation Links + Newsletter */}
        <div className="py-8 grid grid-cols-1 md:grid-cols-4 gap-8">
          
          {/* Indices Column */}
          <div>
            <h4 className="font-medium text-[#1A1A1A] mb-4 text-[14px] font-inter">Indices</h4>
            <ul className="space-y-3">
              <li>
                <Link 
                  to="/index-dashboard" 
                  className="text-[#1A1A1A] hover:text-[#1F4FFF] hover:underline transition-colors text-[14px] font-inter"
                >
                  Live Index
                </Link>
              </li>
              <li>
                <Link 
                  to="/yield-indices" 
                  className="text-[#1A1A1A] hover:text-[#1F4FFF] hover:underline transition-colors text-[14px] font-inter"
                >
                  Indices & Benchmarks
                </Link>
              </li>
              <li>
                <Link 
                  to="/peg-monitor" 
                  className="text-[#1A1A1A] hover:text-[#1F4FFF] hover:underline transition-colors text-[14px] font-inter"
                >
                  Peg Monitor
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources Column */}
          <div>
            <h4 className="font-medium text-[#1A1A1A] mb-4 text-[14px] font-inter">Resources</h4>
            <ul className="space-y-3">
              <li>
                <Link 
                  to="/methodology" 
                  className="text-[#1A1A1A] hover:text-[#1F4FFF] hover:underline transition-colors text-[14px] font-inter"
                >
                  Methodology
                </Link>
              </li>
              <li>
                <Link 
                  to="/blog" 
                  className="text-[#1A1A1A] hover:text-[#1F4FFF] hover:underline transition-colors text-[14px] font-inter"
                >
                  Market Insights
                </Link>
              </li>
              <li>
                <button 
                  onClick={() => {/* Whitepaper modal handler */}}
                  className="text-[#1A1A1A] hover:text-[#1F4FFF] hover:underline transition-colors text-[14px] font-inter text-left"
                >
                  Whitepaper
                </button>
              </li>
            </ul>
          </div>

          {/* Company Column */}
          <div>
            <h4 className="font-medium text-[#1A1A1A] mb-4 text-[14px] font-inter">Company</h4>
            <ul className="space-y-3">
              <li>
                <Link 
                  to="/about" 
                  className="text-[#1A1A1A] hover:text-[#1F4FFF] hover:underline transition-colors text-[14px] font-inter"
                >
                  About StableYield
                </Link>
              </li>
              <li>
                <button 
                  onClick={() => {/* Contact modal handler */}}
                  className="text-[#1A1A1A] hover:text-[#1F4FFF] hover:underline transition-colors text-[14px] font-inter text-left"
                >
                  Contact Us
                </button>
              </li>
              <li>
                <Link 
                  to="/careers" 
                  className="text-[#1A1A1A] hover:text-[#1F4FFF] hover:underline transition-colors text-[14px] font-inter"
                >
                  Careers
                </Link>
              </li>
            </ul>
          </div>

          {/* Newsletter Signup Column */}
          <div>
            <h4 className="font-medium text-[#1A1A1A] mb-2 text-[14px] font-inter">Stay Ahead of Stablecoin Markets</h4>
            <p className="text-[12px] text-[#6B7280] font-inter mb-4">
              Get StableYield Insights in your inbox.
            </p>
            
            <form onSubmit={handleNewsletterSubmit} className="space-y-3">
              <Input
                type="email"
                placeholder="Your email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full text-[14px] border-[#E5E7EB] focus:border-[#1F4FFF] focus:ring-[#1F4FFF]"
                required
              />
              <Button
                type="submit"
                disabled={isSubscribing}
                className="w-full bg-[#E47C3C] hover:bg-[#E47C3C]/90 text-white font-medium py-2 px-4 rounded-md text-[14px] font-inter"
              >
                {isSubscribing ? "Subscribing..." : (
                  <>
                    Subscribe
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>
            </form>
            
            <p className="text-[11px] text-[#9FA6B2] font-inter mt-2">
              By subscribing, you agree to receive StableYield updates. Unsubscribe anytime.
            </p>
          </div>
        </div>

        {/* Bottom Row - Compliance & Legal */}
        <div className="border-t border-[#E5E7EB] py-6">
          <div className="text-center">
            <div className="text-[11px] text-[#9FA6B2] font-inter mb-2">
              © 2025 StableYield. All Rights Reserved.
            </div>
            <div className="text-[11px] text-[#9FA6B2] font-inter leading-relaxed max-w-4xl mx-auto">
              StableYield data and indices are benchmarks for informational and institutional purposes only. 
              They do not constitute financial advice. Compliance aligned with MiCA / BMR / IOSCO best practices.
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;