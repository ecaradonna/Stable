import React, { useState, useEffect } from "react";
import Header from "../components/Header";
import HeroSection from "../components/HeroSection";
import LiveYields from "../components/LiveYields";
import StableYieldIndex from "../components/StableYieldIndex";
import QuotationSection from "../components/QuotationSection";
import WhyStableYield from "../components/WhyStableYield";
import Footer from "../components/Footer";
import ContactModal from "../components/ContactModal";
import ApiAccessModal from "../components/ApiAccessModal";
import WhitepaperDownloadModal from "../components/WhitepaperDownloadModal";
import AIAssistant from "../components/AIAssistant";
import SEOHead from "../components/SEOHead";

const HomePage = () => {
  const [isContactOpen, setIsContactOpen] = useState(false);
  const [isApiAccessOpen, setIsApiAccessOpen] = useState(false);
  const [isWhitepaperOpen, setIsWhitepaperOpen] = useState(false);

  // Listen for API modal events from AI Assistant
  useEffect(() => {
    const handleApiModalEvent = () => {
      setIsApiAccessOpen(true);
    };

    window.addEventListener('open-api-modal', handleApiModalEvent);
    return () => {
      window.removeEventListener('open-api-modal', handleApiModalEvent);
    };
  }, []);

  return (
    <div className="min-h-screen bg-white">
      <SEOHead 
        title="StableYield Index (SYI) – World's First Stablecoin Yield Benchmark"
        description="Real-time risk-adjusted stablecoin yield benchmark. Institutional-grade analytics for USDT, USDC, DAI and major stablecoins. Transparent methodology, compliance-ready data."
        url="https://stableyield.com/"
      />
      <Header 
        onJoinWaitlist={() => setIsApiAccessOpen(true)}
        onDownloadWhitepaper={() => setIsWhitepaperOpen(true)}
      />
      <HeroSection onJoinWaitlist={() => setIsApiAccessOpen(true)} />
      <LiveYields onJoinWaitlist={() => setIsApiAccessOpen(true)} />
      <StableYieldIndex onJoinWaitlist={() => setIsApiAccessOpen(true)} />
      <QuotationSection 
        onJoinWaitlist={() => setIsApiAccessOpen(true)}
        onDownloadWhitepaper={() => setIsWhitepaperOpen(true)}
      />
      <WhyStableYield />
      <Footer />
      <ContactModal 
        isOpen={isContactOpen} 
        onClose={() => setIsContactOpen(false)} 
      />
      <ApiAccessModal 
        isOpen={isApiAccessOpen} 
        onClose={() => setIsApiAccessOpen(false)} 
      />
      <WhitepaperDownloadModal 
        isOpen={isWhitepaperOpen} 
        onClose={() => setIsWhitepaperOpen(false)} 
      />
      <AIAssistant />
    </div>
  );
};

export default HomePage;