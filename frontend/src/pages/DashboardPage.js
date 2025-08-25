import React, { useState } from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import ContactModal from "../components/ContactModal";
import WhitepaperDownloadModal from "../components/WhitepaperDownloadModal";
import RiskAnalyticsDashboard from "../components/RiskAnalyticsDashboard";
import AIAssistant from "../components/AIAssistant";

const DashboardPage = () => {
  const [isContactOpen, setIsContactOpen] = useState(false);
  const [isWhitepaperOpen, setIsWhitepaperOpen] = useState(false);
  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        onJoinWaitlist={() => setIsContactOpen(true)}
        onDownloadWhitepaper={() => setIsWhitepaperOpen(true)}
      />
      
      <main className="pt-8 pb-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Page Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-[#0E1A2B]">Market Intelligence Dashboard</h1>
                <p className="text-gray-600 mt-2">
                  Real-time risk analytics and yield intelligence for stablecoin markets
                </p>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-500">StableYield Professional</div>
                <div className="text-lg font-semibold text-[#4CC1E9]">Stablecoin Yield Intelligence</div>
              </div>
            </div>
          </div>
          
          {/* Dashboard Content */}
          <RiskAnalyticsDashboard />
        </div>
      </main>

      <Footer />
      <AIAssistant />
      
      {/* Modals */}
      <ContactModal 
        isOpen={isContactOpen} 
        onClose={() => setIsContactOpen(false)} 
      />
      <WhitepaperDownloadModal 
        isOpen={isWhitepaperOpen} 
        onClose={() => setIsWhitepaperOpen(false)} 
      />
    </div>
  );
};

export default DashboardPage;