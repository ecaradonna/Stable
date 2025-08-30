import React, { useState } from "react";
import { Link } from "react-router-dom";
import Header from "../components/Header";
import Footer from "../components/Footer";
import ContactModal from "../components/ContactModal";
import WhitepaperDownloadModal from "../components/WhitepaperDownloadModal";
import { mockBlogPosts } from "../mock/data";
import { Clock, ArrowRight, TrendingUp } from "lucide-react";
import { Button } from "../components/ui/button";

const BlogPage = () => {
  const [isContactOpen, setIsContactOpen] = useState(false);
  const [isWhitepaperOpen, setIsWhitepaperOpen] = useState(false);
  const featuredPost = mockBlogPosts[0];
  const recentPosts = mockBlogPosts.slice(1);

  return (
    <div className="min-h-screen bg-white">
      <Header 
        onJoinWaitlist={() => setIsContactOpen(true)}
        onDownloadWhitepaper={() => setIsWhitepaperOpen(true)}
      />
      
      <main className="pt-8">
        {/* Hero Section */}
        <section className="py-16 bg-gradient-to-br from-gray-50 to-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <div className="inline-flex items-center px-4 py-2 bg-[#1F4FFF]/10 border border-[#1F4FFF]/20 rounded-full mb-6">
                <span className="text-[#1F4FFF] font-semibold text-sm">Market Intelligence</span>
              </div>
              <h1 className="text-4xl md:text-6xl font-bold text-[#0E1A2B] mb-6">
                Market Intelligence 
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#1F4FFF] to-[#E47C3C]">
                  {" "}& Insights
                </span>
              </h1>
              <p className="text-xl text-gray-600 max-w-4xl mx-auto">
                Professional insights on stablecoin markets, yield analytics, and institutional trends. 
                The essential intelligence for financial professionals navigating the digital asset economy.
              </p>
            </div>
          </div>
        </section>

        {/* Featured Post */}
        <section className="py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="mb-8">
              <span className="text-sm font-semibold text-[#1F4FFF] uppercase tracking-wider">Featured Intelligence Report</span>
            </div>
            
            <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 md:p-12 shadow-lg border border-gray-100">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
                <div>
                  <div className="flex items-center space-x-4 mb-4">
                    <span className="bg-[#1F4FFF]/10 text-[#1F4FFF] px-3 py-1 rounded-full text-sm font-medium">
                      {featuredPost.category}
                    </span>
                    <div className="flex items-center text-gray-500 text-sm">
                      <Clock className="w-4 h-4 mr-1" />
                      {featuredPost.readTime}
                    </div>
                  </div>
                  
                  <h2 className="text-3xl md:text-4xl font-bold text-[#0E1A2B] mb-4">
                    {featuredPost.title}
                  </h2>
                  
                  <p className="text-gray-600 text-lg mb-6 leading-relaxed">
                    {featuredPost.excerpt}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500 text-sm">
                      {new Date(featuredPost.date).toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                      })}
                    </span>
                    <Button className="bg-[#E47C3C] hover:bg-[#E47C3C]/90 text-white">
                      Read Article
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                </div>
                
                <div className="bg-gradient-to-br from-[#1F4FFF]/10 to-[#E47C3C]/10 rounded-xl p-8 h-64 flex items-center justify-center">
                  <TrendingUp className="w-24 h-24 text-[#1F4FFF]" />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Recent Posts */}
        <section className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="mb-12">
              <h3 className="text-3xl font-bold text-[#0E1A2B] mb-4">Recent Articles</h3>
              <p className="text-gray-600">Stay updated with the latest insights from our research team</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {recentPosts.map((post) => (
                <article 
                  key={post.id}
                  className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 transform hover:-translate-y-1"
                >
                  <div className="flex items-center space-x-4 mb-4">
                    <span className="bg-[#9FA6B2]/10 text-[#9FA6B2] px-3 py-1 rounded-full text-sm font-medium">
                      {post.category}
                    </span>
                    <div className="flex items-center text-gray-500 text-sm">
                      <Clock className="w-4 h-4 mr-1" />
                      {post.readTime}
                    </div>
                  </div>
                  
                  <h4 className="text-xl font-bold text-[#0E1A2B] mb-3 line-clamp-2">
                    {post.title}
                  </h4>
                  
                  <p className="text-gray-600 mb-4 line-clamp-3">
                    {post.excerpt}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500 text-sm">
                      {new Date(post.date).toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                      })}
                    </span>
                    <Button variant="outline" size="sm">
                      Read More
                    </Button>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        {/* Newsletter CTA */}
        <section className="py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="bg-gradient-to-br from-[#1F4FFF]/5 to-[#E47C3C]/5 rounded-2xl p-12 text-center border border-[#1F4FFF]/20">
              <h3 className="text-3xl font-bold text-[#0E1A2B] mb-4">
                Never Miss an Update
              </h3>
              <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
                Subscribe to our newsletter and get the latest stablecoin yield insights, 
                market analysis, and platform updates delivered to your inbox weekly.
              </p>
              <Button 
                className="bg-[#E47C3C] hover:bg-[#E47C3C]/90 text-white font-semibold px-8 py-3 rounded-xl"
                onClick={() => setIsContactOpen(true)}
              >
                Subscribe to Newsletter
              </Button>
            </div>
          </div>
        </section>
      </main>

      <Footer />
      
        {/* FAQ Section */}
        <section className="py-16">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-[#0E1A2B] mb-4">
                Frequently Asked Questions
              </h2>
              <p className="text-xl text-gray-600">
                Everything you need to know about StableYield and institutional stablecoin benchmarking
              </p>
            </div>
            
            <div className="space-y-4">
              {[
                {
                  question: "What is the StableYield Index (SYI)?",
                  answer: "The StableYield Index is the institutional benchmark for stablecoin yields. It measures returns adjusted for peg risk, liquidity, and counterparty exposure — making stablecoins comparable to T-Bills or Euribor."
                },
                {
                  question: "Why do I need a benchmark for stablecoins?",
                  answer: "Because raw APYs across platforms are often inflated and inconsistent. SYI filters the noise, creating a single, transparent, auditable figure that serves as the foundation for evaluations, reporting, and strategy."
                },
                {
                  question: "How does it help me manage risk?",
                  answer: "StableYield monitors in real time: peg deviations, liquidity depth, protocol resilience. You know when risk is rising, so you can protect capital or rotate into safer stablecoins."
                },
                {
                  question: "What advantage does it give a trader?",
                  answer: "It delivers clear Risk ON / Risk OFF signals based on data, not sentiment. Traders can: anticipate market stress, exploit arbitrage on peg deviations, optimize collateral and yield strategies."
                },
                {
                  question: "And for institutional investors?",
                  answer: "It provides a governance and compliance tool: you can benchmark your stablecoin performance against an institutional-grade index — just as you already do with bonds, equities, and money market rates."
                },
                {
                  question: "How does it support treasury managers?",
                  answer: "It lets you assess whether allocating to stablecoins is more or less attractive than government securities. Always with risk-adjusted data and built-in regulatory monitoring."
                },
                {
                  question: "Can I receive automatic alerts?",
                  answer: "Yes. With the Pro plan, you get real-time alerts via Telegram, TradingView, or email: when a stablecoin depegs, when the regime shifts (ON/OFF), when yields diverge from T-Bills."
                },
                {
                  question: "What's the advantage over DeFiLlama or similar tools?",
                  answer: "StableYield doesn't just show raw APYs. It calculates RAY (Risk-Adjusted Yield) — the first system integrating stability, liquidity, and counterparty metrics. It's built for institutions, not retail."
                },
                {
                  question: "How can I access the data?",
                  answer: "Live dashboard (Free tier with delayed data), API access for trading desks, risk managers, and reporting systems, Weekly or monthly reports for pro traders and institutions."
                },
                {
                  question: "How does it improve my work in practice?",
                  answer: "You no longer need to monitor dozens of protocols: everything is in one index. You immediately know if your yields are above or below the market. You minimize hidden risks (depeg, illiquidity, counterparty). You make faster, informed, and defensible decisions for clients, boards, or investors."
                }
              ].map((faq, index) => (
                <details key={index} className="bg-white border border-gray-200 rounded-lg">
                  <summary className="p-6 cursor-pointer hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold text-[#0E1A2B] pr-8">{faq.question}</h3>
                      <div className="text-[#1F4FFF] transform transition-transform">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </div>
                  </summary>
                  <div className="px-6 pb-6">
                    <p className="text-gray-600 leading-relaxed">{faq.answer}</p>
                  </div>
                </details>
              ))}
            </div>
            
            <div className="text-center mt-12">
              <p className="text-gray-600 mb-4">Have more questions?</p>
              <Button 
                className="bg-[#E47C3C] hover:bg-[#E47C3C]/90 text-white font-semibold px-8 py-3 rounded-xl"
                onClick={() => setIsContactOpen(true)}
              >
                Contact Our Team
              </Button>
            </div>
          </div>
        </section>

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

export default BlogPage;