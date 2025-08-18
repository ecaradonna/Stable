import React from "react";
import { Shield, Zap, Award, BarChart3, Target, TrendingUp, Database, Globe } from "lucide-react";

const WhyStableYield = () => {
  const features = [
    {
      icon: BarChart3,
      title: "Market Intelligence",
      description: "Independent authority delivering trusted data to power investment decisions, media insights, and market benchmarks.",
      color: "from-[#4CC1E9] to-[#007A99]"
    },
    {
      icon: Shield,
      title: "Risk Analytics",
      description: "Advanced risk assessment measuring peg stability, liquidity depth, and counterparty exposure across all platforms.",
      color: "from-[#2E6049] to-[#4CC1E9]"
    },
    {
      icon: Globe,
      title: "Global Coverage",
      description: "Comprehensive tracking from DeFi protocols to CeFi platforms and TradFi integrations worldwide.",
      color: "from-[#007A99] to-[#2E6049]"
    }
  ];

  const useCases = [
    {
      icon: Target,
      title: "Fund Managers",
      description: "Portfolio optimization with risk-adjusted stablecoin allocation strategies"
    },
    {
      icon: TrendingUp,
      title: "Exchanges & Traders",
      description: "Real-time yield arbitrage opportunities and market inefficiency detection"
    },
    {
      icon: Database,
      title: "Institutions",
      description: "Regulatory compliance and treasury management with verified yield data"
    }
  ];

  const stats = [
    { value: "50+", label: "Platforms Monitored" },
    { value: "$500B+", label: "Stablecoin TVL Tracked" },
    { value: "24/7", label: "Real-time Intelligence" },
    { value: "99.9%", label: "Data Accuracy" }
  ];

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center px-4 py-2 bg-[#4CC1E9]/10 border border-[#4CC1E9]/20 rounded-full mb-6">
            <span className="text-[#007A99] font-semibold text-sm">Financial Intelligence Platform</span>
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-[#0E1A2B] mb-6">
            Why StableYield?
          </h2>
          <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
            We believe the future of finance runs on stablecoins — the digital dollars that move at the speed of the internet. 
            Behind every yield opportunity lies the crucial question: How safe is the yield?
          </p>
        </div>

        {/* Core Features */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-20">
          {features.map((feature, index) => {
            const IconComponent = feature.icon;
            return (
              <div 
                key={index}
                className="group bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100"
              >
                <div className={`w-16 h-16 bg-gradient-to-br ${feature.color} rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <IconComponent className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-[#0E1A2B] mb-4">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>

        {/* Use Cases */}
        <div className="mb-20">
          <h3 className="text-2xl md:text-3xl font-bold text-[#0E1A2B] text-center mb-12">
            Trusted by Financial Professionals
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {useCases.map((useCase, index) => {
              const IconComponent = useCase.icon;
              return (
                <div key={index} className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-all duration-300 border border-gray-100">
                  <IconComponent className="w-8 h-8 text-[#4CC1E9] mb-4" />
                  <h4 className="font-bold text-[#0E1A2B] mb-2">{useCase.title}</h4>
                  <p className="text-gray-600 text-sm">{useCase.description}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Stats Section */}
        <div className="bg-white rounded-2xl p-8 md:p-12 shadow-lg border border-gray-100">
          <div className="text-center mb-8">
            <h3 className="text-2xl md:text-3xl font-bold text-[#0E1A2B] mb-4">
              Market-Leading Coverage
            </h3>
            <p className="text-gray-600">
              Comprehensive data infrastructure powering the stablecoin economy
            </p>
          </div>
          
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-[#4CC1E9] to-[#007A99] bg-clip-text text-transparent mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-600 font-medium">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Mission Statement */}
        <div className="mt-16 text-center">
          <div className="bg-gradient-to-r from-[#0E1A2B] to-[#2E6049] rounded-2xl p-8 md:p-12 text-white">
            <h3 className="text-2xl md:text-3xl font-bold mb-6">Our Mission</h3>
            <p className="text-xl leading-relaxed max-w-4xl mx-auto mb-6">
              Bring clarity, transparency, and confidence to the stablecoin economy. 
              We deliver independent, trusted intelligence that powers better financial decisions.
            </p>
            <div className="inline-flex items-center px-6 py-3 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20">
              <span className="text-[#4CC1E9] font-semibold">Clarity • Transparency • Confidence</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WhyStableYield;