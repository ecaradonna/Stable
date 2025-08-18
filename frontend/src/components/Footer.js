import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Twitter, Linkedin, Github, Mail, ArrowRight } from "lucide-react";
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
    <footer className="bg-[#0E1A2B] text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Newsletter Section */}
        <div className="py-12 border-b border-gray-700">
          <div className="text-center">
            <h3 className="text-2xl md:text-3xl font-bold mb-4">
              StableYield Intelligence Report
            </h3>
            <p className="text-gray-300 mb-8 max-w-2xl mx-auto">
              Weekly insights on stablecoin yields, risk analysis, and market intelligence. 
              The essential read for financial professionals in the digital asset space.
            </p>
            
            <form onSubmit={handleNewsletterSubmit} className="max-w-md mx-auto flex space-x-2">
              <Input
                type="email"
                placeholder="Enter your professional email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-white/10 border-gray-600 text-white placeholder-gray-400 focus:border-[#4CC1E9] focus:ring-[#4CC1E9]"
                required
              />
              <Button
                type="submit"
                disabled={isSubscribing}
                className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] px-6"
              >
                {isSubscribing ? "..." : <ArrowRight className="w-4 h-4" />}
              </Button>
            </form>
          </div>
        </div>

        {/* Main Footer Content */}
        <div className="py-12 grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Column */}
          <div className="col-span-1 md:col-span-2">
            <Link to="/" className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#4CC1E9] to-[#007A99] flex items-center justify-center">
                <span className="text-white font-bold text-lg">Y</span>
              </div>
              <span className="text-xl font-bold tracking-wider">
                <span className="text-white">STABLE</span>
                <span className="text-[#4CC1E9]">YIELD</span>
              </span>
            </Link>
            <p className="text-gray-300 mb-6 max-w-md leading-relaxed">
              The world's first benchmark platform for stablecoin yields. We are the Bloomberg for stablecoin yields — 
              delivering independent, trusted intelligence to power better financial decisions.
            </p>
            <div className="bg-[#4CC1E9]/10 border border-[#4CC1E9]/20 rounded-lg p-4 mb-6">
              <p className="text-[#4CC1E9] text-sm font-medium">
                "In a market built on stability, knowing where yield is truly safe makes all the difference."
              </p>
            </div>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-[#4CC1E9] transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-[#4CC1E9] transition-colors">
                <Linkedin className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-[#4CC1E9] transition-colors">
                <Github className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-[#4CC1E9] transition-colors">
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Products Column */}
          <div>
            <h4 className="font-semibold text-white mb-4">Platform</h4>
            <ul className="space-y-2 text-gray-300">
              <li><a href="#" className="hover:text-[#4CC1E9] transition-colors">Yield Benchmarks</a></li>
              <li><a href="#" className="hover:text-[#4CC1E9] transition-colors">Risk Analytics</a></li>
              <li><a href="#" className="hover:text-[#4CC1E9] transition-colors">API Access</a></li>
              <li><a href="#" className="hover:text-[#4CC1E9] transition-colors">Market Intelligence</a></li>
              <li><a href="#" className="hover:text-[#4CC1E9] transition-colors">Institution Tools</a></li>
            </ul>
          </div>

          {/* Company Column */}
          <div>
            <h4 className="font-semibold text-white mb-4">Company</h4>
            <ul className="space-y-2 text-gray-300">
              <li><Link to="/blog" className="hover:text-[#4CC1E9] transition-colors">Market Insights</Link></li>
              <li><a href="#" className="hover:text-[#4CC1E9] transition-colors">About Us</a></li>
              <li><a href="#" className="hover:text-[#4CC1E9] transition-colors">Methodology</a></li>
              <li><a href="#" className="hover:text-[#4CC1E9] transition-colors">Contact</a></li>
              <li><a href="#" className="hover:text-[#4CC1E9] transition-colors">Partnerships</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="py-6 border-t border-gray-700 flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="text-gray-400 text-sm">
            © 2025 StableYield. All rights reserved. Independent financial intelligence platform.
          </div>
          <div className="flex space-x-6 text-gray-400 text-sm">
            <a href="#" className="hover:text-[#4CC1E9] transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-[#4CC1E9] transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-[#4CC1E9] transition-colors">Data Sources</a>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="pb-6">
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
            <p className="text-yellow-300 text-sm">
              <strong>Financial Disclaimer:</strong> StableYield provides market intelligence and analytical tools for informational purposes only. 
              This platform does not provide investment advice. All yield data is for research purposes. Stablecoin investments carry risks including 
              smart contract risk, counterparty risk, and regulatory risk. Always conduct your own due diligence and consult with qualified 
              financial advisors before making investment decisions.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;