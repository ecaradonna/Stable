import React, { useState } from "react";
import Header from "../components/Header";
import HeroSection from "../components/HeroSection";
import LiveYields from "../components/LiveYields";
import StableYieldIndex from "../components/StableYieldIndex";
import QuotationSection from "../components/QuotationSection";
import WhyStableYield from "../components/WhyStableYield";
import Footer from "../components/Footer";
import ContactModal from "../components/ContactModal";
import AIAssistant from "../components/AIAssistant";

const HomePage = () => {
  const [isWaitlistOpen, setIsWaitlistOpen] = useState(false);

  return (
    <div className="min-h-screen bg-white">
      <Header onJoinWaitlist={() => setIsWaitlistOpen(true)} />
      <HeroSection onJoinWaitlist={() => setIsWaitlistOpen(true)} />
      <LiveYields />
      <StableYieldIndex />
      <QuotationSection onJoinWaitlist={() => setIsWaitlistOpen(true)} />
      <WhyStableYield />
      <Footer />
      <WaitlistModal 
        isOpen={isWaitlistOpen} 
        onClose={() => setIsWaitlistOpen(false)} 
      />
      <AIAssistant />
    </div>
  );
};

export default HomePage;