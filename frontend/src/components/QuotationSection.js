import React from "react";
import { Button } from "./ui/button";
import { FileText } from "lucide-react";

const QuotationSection = ({ onJoinWaitlist, onDownloadWhitepaper }) => {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Mission statement */}
        <div className="bg-gradient-to-r from-[#4CC1E9]/5 to-[#007A99]/5 rounded-2xl p-8 mb-12 border border-[#4CC1E9]/20">
          <blockquote className="text-lg md:text-xl text-[#0E1A2B] leading-relaxed italic">
            "In a market built on stability, knowing where yield is truly safe makes all the difference."
          </blockquote>
        </div>

        {/* CTA Button */}
        <Button 
          onClick={onJoinWaitlist}
          className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] text-white font-bold text-lg px-12 py-4 rounded-xl transition-all duration-300 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 mb-8"
        >
          Contact Us
        </Button>

        {/* Trust indicators */}
        <div className="pt-8 border-t border-gray-200">
          <p className="text-gray-500 text-sm mb-4">Trusted by institutional investors, funds, and market makers</p>
          <div className="flex justify-center items-center space-x-8 opacity-60">
            <div className="text-gray-400 font-semibold">DeFi • CeFi • TradFi</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default QuotationSection;