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
              <span className="text-sm font-semibold text-[#4CC1E9] uppercase tracking-wider">Featured Intelligence Report</span>
            </div>
            
            <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 md:p-12 shadow-lg border border-gray-100">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
                <div>
                  <div className="flex items-center space-x-4 mb-4">
                    <span className="bg-[#4CC1E9]/10 text-[#4CC1E9] px-3 py-1 rounded-full text-sm font-medium">
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
                    <Button className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] text-white">
                      Read Article
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                </div>
                
                <div className="bg-gradient-to-br from-[#4CC1E9]/10 to-[#007A99]/10 rounded-xl p-8 h-64 flex items-center justify-center">
                  <TrendingUp className="w-24 h-24 text-[#4CC1E9]" />
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
                    <span className="bg-[#2E6049]/10 text-[#2E6049] px-3 py-1 rounded-full text-sm font-medium">
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
            <div className="bg-gradient-to-br from-[#4CC1E9]/5 to-[#007A99]/5 rounded-2xl p-12 text-center border border-[#4CC1E9]/20">
              <h3 className="text-3xl font-bold text-[#0E1A2B] mb-4">
                Never Miss an Update
              </h3>
              <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
                Subscribe to our newsletter and get the latest stablecoin yield insights, 
                market analysis, and platform updates delivered to your inbox weekly.
              </p>
              <Button 
                className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] text-white font-semibold px-8 py-3"
                onClick={() => setIsContactOpen(true)}
              >
                Subscribe to Newsletter
              </Button>
            </div>
          </div>
        </section>
      </main>

      <Footer />
      
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