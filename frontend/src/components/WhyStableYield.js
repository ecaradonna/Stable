import React, { useState } from "react";
import { Shield, Zap, Award, BarChart3, Target, TrendingUp, Database, Globe, ChevronDown, CheckCircle } from "lucide-react";

const WhyStableYield = () => {
  const [openFaq, setOpenFaq] = useState(0);

  const features = [
    {
      icon: BarChart3,
      title: "Institutional Benchmark",
      description: "The world's first risk-adjusted stablecoin yield index - making stablecoins comparable to T-Bills or Euribor.",
      color: "from-[#1F4FFF] to-[#E47C3C]"
    },
    {
      icon: Shield,
      title: "Risk Management",
      description: "Real-time monitoring of peg deviations, liquidity depth, and protocol resilience to protect your capital.",
      color: "from-[#1F4FFF] to-[#9FA6B2]"
    },
    {
      icon: TrendingUp,
      title: "Trading Signals",
      description: "Clear Risk ON/OFF signals based on data, not sentiment - for arbitrage and yield optimization strategies.",
      color: "from-[#E47C3C] to-[#D64545]"
    }
  ];

  const keyFaqs = [
    {
      question: "What is the StableYield Index (SYI)?",
      answer: "The institutional benchmark for stablecoin yields. It measures returns adjusted for peg risk, liquidity, and counterparty exposure — making stablecoins comparable to T-Bills or Euribor."
    },
    {
      question: "Why do I need a benchmark for stablecoins?", 
      answer: "Because raw APYs across platforms are often inflated and inconsistent. SYI filters the noise, creating a single, transparent, auditable figure for evaluations and strategy."
    },
    {
      question: "How does it help me manage risk?",
      answer: "StableYield monitors in real time: peg deviations, liquidity depth, protocol resilience. You know when risk is rising to protect capital or rotate into safer stablecoins."
    },
    {
      question: "What advantage does it give traders?",
      answer: "Clear Risk ON/OFF signals based on data, not sentiment. Anticipate market stress, exploit arbitrage on peg deviations, optimize collateral and yield strategies."
    }
  ];

  const useCases = [
    {
      icon: Target,
      title: "Treasury Managers",
      description: "Assess stablecoin allocations vs government securities with risk-adjusted data"
    },
    {
      icon: TrendingUp,
      title: "Institutional Investors", 
      description: "Benchmark stablecoin performance against institutional-grade indices"
    },
    {
      icon: Database,
      title: "Trading Desks",
      description: "API access for real-time alerts and systematic yield strategies"
    }
  ];

  const stats = [
    { value: "4.47%", label: "Current SYI Benchmark" },
    { value: "6", label: "Live Components" },
    { value: "24/7", label: "Real-time Monitoring" },
    { value: "99.9%", label: "Uptime SLA" }
  ];

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center px-4 py-2 bg-[#1F4FFF]/10 border border-[#1F4FFF]/20 rounded-full mb-6">
            <span className="text-[#1F4FFF] font-semibold text-sm">Institutional Benchmark</span>
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-[#0E1A2B] mb-6">
            Why StableYield?
          </h2>
          <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
            The Bloomberg for stablecoin yields. We filter the noise to create the single, transparent, 
            auditable benchmark that serves as the foundation for institutional decision-making.
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

        {/* Key FAQ Section */}
        <div className="mb-20">
          <h3 className="text-2xl md:text-3xl font-bold text-[#0E1A2B] text-center mb-12">
            Key Questions Answered
          </h3>
          <div className="max-w-4xl mx-auto space-y-4">
            {keyFaqs.map((faq, index) => (
              <div key={index} className="bg-white border border-gray-200 rounded-xl overflow-hidden">
                <button
                  className="w-full p-6 text-left hover:bg-gray-50 transition-colors flex items-center justify-between"
                  onClick={() => setOpenFaq(openFaq === index ? -1 : index)}
                >
                  <h4 className="text-lg font-semibold text-[#0E1A2B] pr-4">{faq.question}</h4>
                  <ChevronDown 
                    className={`w-5 h-5 text-[#1F4FFF] transition-transform ${
                      openFaq === index ? 'transform rotate-180' : ''
                    }`}
                  />
                </button>
                {openFaq === index && (
                  <div className="px-6 pb-6">
                    <div className="flex items-start space-x-3">
                      <CheckCircle className="w-5 h-5 text-[#1F4FFF] mt-0.5 flex-shrink-0" />
                      <p className="text-gray-600 leading-relaxed">{faq.answer}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
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
                  <IconComponent className="w-8 h-8 text-[#1F4FFF] mb-4" />
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
              Live Benchmark Data
            </h3>
            <p className="text-gray-600">
              Real-time intelligence powering institutional stablecoin strategies
            </p>
          </div>
          
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-[#1F4FFF] to-[#E47C3C] bg-clip-text text-transparent mb-2">
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
          <div className="bg-gradient-to-r from-[#1F4FFF] to-[#0E1A2B] rounded-2xl p-8 md:p-12 text-white">
            <h3 className="text-2xl md:text-3xl font-bold mb-6">Our Mission</h3>
            <p className="text-xl leading-relaxed max-w-4xl mx-auto mb-6">
              Bring clarity, transparency, and confidence to the stablecoin economy. 
              We deliver the institutional benchmark that powers better financial decisions.
            </p>
            <div className="inline-flex items-center px-6 py-3 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20">
              <span className="text-[#E47C3C] font-semibold">The Bloomberg for Stablecoin Yields</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WhyStableYield;