import React, { useState } from "react";
import Header from "../components/Header";
import HeroSection from "../components/HeroSection";
import WhyStableYield from "../components/WhyStableYield";
import LiveYields from "../components/LiveYields";
import Footer from "../components/Footer";
import WaitlistModal from "../components/WaitlistModal";

const HomePage = () => {
  const [isWaitlistOpen, setIsWaitlistOpen] = useState(false);

  return (
    <div className="min-h-screen bg-white">
      <Header onJoinWaitlist={() => setIsWaitlistOpen(true)} />
      <HeroSection onJoinWaitlist={() => setIsWaitlistOpen(true)} />
      <WhyStableYield />
      <LiveYields />
      <Footer />
      <WaitlistModal 
        isOpen={isWaitlistOpen} 
        onClose={() => setIsWaitlistOpen(false)} 
      />
    </div>
  );
};

export default HomePage;