import React from "react";
import { Shield, Zap, Award, Eye, Clock, TrendingUp } from "lucide-react";

const WhyStableYield = () => {
  const features = [
    {
      icon: Shield,
      title: "Transparency",
      description: "Complete visibility into data sources, methodology, and real-time updates from verified platforms.",
      color: "from-[#4CC1E9] to-[#007A99]"
    },
    {
      icon: Zap,
      title: "Speed",
      description: "Lightning-fast access to current yields across all major CeFi and DeFi platforms in one dashboard.",
      color: "from-[#2E6049] to-[#4CC1E9]"
    },
    {
      icon: Award,
      title: "Authority",
      description: "Trusted benchmark for institutional investors, traders, and DeFi protocols worldwide.",
      color: "from-[#007A99] to-[#2E6049]"
    }
  ];

  const stats = [
    { value: "50+", label: "Platforms Tracked" },
    { value: "$2.1T", label: "TVL Monitored" },
    { value: "24/7", label: "Real-time Updates" },
    { value: "99.9%", label: "Uptime Guarantee" }
  ];

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold text-[#0E1A2B] mb-6">
            Why StableYield?
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            The most comprehensive and trusted source for stablecoin yield data. 
            Built for professionals who need accurate, real-time information.
          </p>
        </div>

        {/* Main Features */}
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

        {/* Stats Section */}
        <div className="bg-white rounded-2xl p-8 md:p-12 shadow-lg">
          <div className="text-center mb-8">
            <h3 className="text-2xl md:text-3xl font-bold text-[#0E1A2B] mb-4">
              Trusted by the Industry
            </h3>
            <p className="text-gray-600">
              Real numbers from our platform performance
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

        {/* Additional Benefits */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-center space-x-4 p-6 bg-white/80 backdrop-blur-sm rounded-xl border border-gray-100">
            <Eye className="w-8 h-8 text-[#4CC1E9]" />
            <div>
              <h4 className="font-semibold text-[#0E1A2B]">No Hidden Fees</h4>
              <p className="text-gray-600 text-sm">Transparent pricing, no surprises</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4 p-6 bg-white/80 backdrop-blur-sm rounded-xl border border-gray-100">
            <Clock className="w-8 h-8 text-[#007A99]" />
            <div>
              <h4 className="font-semibold text-[#0E1A2B]">Real-time Data</h4>
              <p className="text-gray-600 text-sm">Updates every 30 seconds</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4 p-6 bg-white/80 backdrop-blur-sm rounded-xl border border-gray-100">
            <TrendingUp className="w-8 h-8 text-[#2E6049]" />
            <div>
              <h4 className="font-semibold text-[#0E1A2B]">Historical Analysis</h4>
              <p className="text-gray-600 text-sm">Track trends over time</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WhyStableYield;