import React, { useState } from "react";
import Header from "../components/Header";
import HeroSection from "../components/HeroSection";
import WhyStableYield from "../components/WhyStableYield";
import StableYieldIndex from "../components/StableYieldIndex";
import LiveYields from "../components/LiveYields";
import Footer from "../components/Footer";
import WaitlistModal from "../components/WaitlistModal";
import AIAssistant from "../components/AIAssistant";

const HomePage = () => {
  const [isWaitlistOpen, setIsWaitlistOpen] = useState(false);

  return (
    <div className="min-h-screen bg-white">
      <Header onJoinWaitlist={() => setIsWaitlistOpen(true)} />
      <HeroSection onJoinWaitlist={() => setIsWaitlistOpen(true)} />
      <LiveYields />
      <StableYieldIndex />
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