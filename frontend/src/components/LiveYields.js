import React, { useState, useEffect } from "react";
import { TrendingUp, TrendingDown, ExternalLink, Sparkles, RefreshCw } from "lucide-react";
import { Button } from "./ui/button";
import AIAlerts from "./AIAlerts";
import { yieldsApi } from "../services/api";
import { useToast } from "../hooks/use-toast";

const LiveYields = () => {
  const [yieldsData, setYieldsData] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const { toast } = useToast();

  // Fetch yields from backend
  const fetchYields = async (showRefreshToast = false) => {
    try {
      const response = await yieldsApi.getAllYields();
      const yieldsFromAPI = response.data;
      
      // Take top 3 for display
      setYieldsData(yieldsFromAPI.slice(0, 3));
      setLastUpdated(new Date());
      
      if (showRefreshToast) {
        toast({
          title: "Data Updated",
          description: "Latest yield data has been loaded.",
        });
      }
    } catch (error) {
      console.error("Failed to fetch yields:", error);
      
      // Fallback to mock data on error
      const mockData = [
        {
          stablecoin: "USDT",
          name: "Tether USD",
          currentYield: 8.45,
          source: "Binance Earn",
          sourceType: "CeFi",
          riskScore: "Medium",
          change24h: 0.12,
          liquidity: "$89.2B"
        },
        {
          stablecoin: "USDC", 
          name: "USD Coin",
          currentYield: 7.82,
          source: "Aave V3",
          sourceType: "DeFi",
          riskScore: "Low",
          change24h: -0.05,
          liquidity: "$32.1B"
        },
        {
          stablecoin: "DAI",
          name: "Dai Stablecoin", 
          currentYield: 6.95,
          source: "Compound",
          sourceType: "DeFi",
          riskScore: "Medium",
          change24h: 0.08,
          liquidity: "$4.8B"
        }
      ];
      setYieldsData(mockData);
      
      toast({
        title: "Using Cached Data",
        description: "Unable to fetch latest data. Showing cached results.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Manual refresh
  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await yieldsApi.refreshYields(); // Trigger backend refresh
      await fetchYields(true);
    } catch (error) {
      toast({
        title: "Refresh Failed",
        description: "Unable to refresh data. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsRefreshing(false);
    }
  };

  // Initial load and periodic updates
  useEffect(() => {
    fetchYields();
    
    // Update every 5 minutes
    const interval = setInterval(() => {
      fetchYields();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  const getRiskScoreColor = (score) => {
    switch(score?.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSourceTypeColor = (type) => {
    return type === 'CeFi' 
      ? 'text-blue-600 bg-blue-100' 
      : 'text-purple-600 bg-purple-100';
  };

  if (isLoading) {
    return (
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#4CC1E9] mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading latest yield data...</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Sparkles className="w-6 h-6 text-[#4CC1E9]" />
            <span className="text-sm font-semibold text-[#007A99] uppercase tracking-wider">Live Data</span>
          </div>
          <h2 className="text-3xl md:text-5xl font-bold text-[#0E1A2B] mb-6">
            Top Stablecoin Yields
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-4">
            Real-time yields from the most trusted stablecoins across CeFi and DeFi platforms
          </p>
          <div className="flex items-center justify-center space-x-4">
            <p className="text-sm text-gray-500">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="hover:bg-[#4CC1E9]/10 hover:border-[#4CC1E9]"
            >
              <RefreshCw className={`w-4 h-4 mr-1 ${isRefreshing ? 'animate-spin' : ''}`} />
              {isRefreshing ? 'Refreshing...' : 'Refresh'}
            </Button>
            <AIAlerts />
          </div>
        </div>

        {/* Yields Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {yieldsData.map((yieldItem, index) => (
            <div 
              key={yieldItem.stablecoin}
              className="group bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 hover:border-[#4CC1E9]/30 transform hover:-translate-y-1"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                    <span className="font-bold text-[#0E1A2B]">
                      {yieldItem.stablecoin}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-bold text-[#0E1A2B]">{yieldItem.stablecoin}</h3>
                    <p className="text-sm text-gray-500">{yieldItem.name}</p>
                  </div>
                </div>
                
                {index === 0 && (
                  <div className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] text-white text-xs font-bold px-2 py-1 rounded-full">
                    #1
                  </div>
                )}
              </div>

              {/* Yield Display */}
              <div className="text-center mb-6">
                <div className="text-4xl font-bold bg-gradient-to-r from-[#4CC1E9] to-[#007A99] bg-clip-text text-transparent mb-2">
                  {yieldItem.currentYield.toFixed(2)}%
                </div>
                <div className="flex items-center justify-center space-x-1">
                  {yieldItem.change24h >= 0 ? (
                    <TrendingUp className="w-4 h-4 text-green-500" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-red-500" />
                  )}
                  <span className={`text-sm font-medium ${
                    yieldItem.change24h >= 0 ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {yieldItem.change24h >= 0 ? '+' : ''}{yieldItem.change24h.toFixed(2)}%
                  </span>
                  <span className="text-gray-500 text-sm">24h</span>
                </div>
              </div>

              {/* Details */}
              <div className="space-y-3 mb-6">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 text-sm">Source</span>
                  <span className="font-medium text-[#0E1A2B]">{yieldItem.source}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 text-sm">Type</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSourceTypeColor(yieldItem.sourceType)}`}>
                    {yieldItem.sourceType}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 text-sm">Risk</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskScoreColor(yieldItem.riskScore)}`}>
                    {yieldItem.riskScore}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 text-sm">Liquidity</span>
                  <span className="font-medium text-[#0E1A2B]">{yieldItem.liquidity}</span>
                </div>
              </div>

              {/* Action Button */}
              <Button 
                variant="outline" 
                className="w-full group-hover:bg-[#4CC1E9] group-hover:text-white group-hover:border-[#4CC1E9] transition-all duration-300"
              >
                View Details
                <ExternalLink className="w-4 h-4 ml-2" />
              </Button>
            </div>
          ))}
        </div>

        {/* Call to Action */}
        <div className="text-center bg-gradient-to-br from-[#4CC1E9]/5 to-[#007A99]/5 rounded-2xl p-12 border border-[#4CC1E9]/20">
          <h3 className="text-2xl md:text-3xl font-bold text-[#0E1A2B] mb-4">
            Want to see all yields?
          </h3>
          <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
            Get access to our complete dashboard with 50+ stablecoins, historical data, risk analysis, and real-time alerts.
          </p>
          <Button className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] text-white font-semibold px-8 py-3 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl">
            Join Waitlist for Early Access
          </Button>
        </div>
      </div>
    </section>
  );
};

export default LiveYields;