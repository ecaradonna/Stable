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
  const [isContactOpen, setIsContactOpen] = useState(false);

  return (
    <div className="min-h-screen bg-white">
      <Header onJoinWaitlist={() => setIsContactOpen(true)} />
      <HeroSection onJoinWaitlist={() => setIsContactOpen(true)} />
      <LiveYields />
      <StableYieldIndex />
      <QuotationSection onJoinWaitlist={() => setIsContactOpen(true)} />
      <WhyStableYield />
      <Footer />
      <ContactModal 
        isOpen={isContactOpen} 
        onClose={() => setIsContactOpen(false)} 
      />
      <AIAssistant />
    </div>
  );
};

export default HomePage;