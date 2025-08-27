import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  PieChart, 
  Pie, 
  Cell,
  BarChart,
  Bar,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  Area,
  AreaChart,
  Legend
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  BarChart3,
  Activity,
  Zap,
  AlertTriangle,
  Shield,
  Building2,
  Download,
  Users,
  Layers
} from 'lucide-react';

const StablecoinMarketCharts = () => {
  const [activeTab, setActiveTab] = useState('distribution');
  const [timeframe, setTimeframe] = useState('30d');
  const [loading, setLoading] = useState(false);

  // Mock data for market distribution
  const marketDistributionData = [
    { name: 'Fiat-Backed', value: 138.5, count: 8, color: '#4CC1E9' },
    { name: 'Crypto-Backed', value: 6.8, count: 6, color: '#2E6049' },
    { name: 'Algorithmic', value: 1.6, count: 4, color: '#F59E0B' },
    { name: 'Hybrid', value: 0.9, count: 2, color: '#8B5CF6' }
  ];

  // Mock data for top stablecoins by market cap
  const topStablecoinsData = [
    { name: 'USDT', marketCap: 83.2, yield: 8.45, volume24h: 45.2, type: 'Fiat-Backed' },
    { name: 'USDC', marketCap: 33.4, yield: 7.12, volume24h: 28.7, type: 'Fiat-Backed' },
    { name: 'BUSD', marketCap: 17.8, yield: 6.85, volume24h: 12.3, type: 'Fiat-Backed' },
    { name: 'DAI', marketCap: 5.3, yield: 9.31, volume24h: 4.8, type: 'Crypto-Backed' },
    { name: 'TUSD', marketCap: 2.1, yield: 4.23, volume24h: 1.2, type: 'Fiat-Backed' },
    { name: 'USDP', marketCap: 1.2, yield: 5.67, volume24h: 0.8, type: 'Fiat-Backed' },
    { name: 'FRAX', marketCap: 0.845, yield: 11.2, volume24h: 2.1, type: 'Algorithmic' },
    { name: 'LUSD', marketCap: 0.324, yield: 7.8, volume24h: 0.5, type: 'Crypto-Backed' }
  ];

  // Mock data for yield trends over time
  const generateYieldTrends = (days) => {
    const data = [];
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    
    const coins = ['USDT', 'USDC', 'DAI', 'FRAX'];
    const baseYields = { USDT: 8.45, USDC: 7.12, DAI: 9.31, FRAX: 11.2 };
    
    for (let i = 0; i < days; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      
      const dataPoint = {
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        timestamp: date.getTime()
      };
      
      // Add yield data for each coin with realistic volatility
      coins.forEach(coin => {
        const baseYield = baseYields[coin];
        const volatility = coin === 'FRAX' ? 0.2 : coin === 'DAI' ? 0.15 : 0.1;
        const randomChange = (Math.random() - 0.5) * volatility;
        dataPoint[coin] = Math.max(0, baseYield + randomChange);
      });
      
      data.push(dataPoint);
    }
    
    return data;
  };

  // Mock data for stablecoin adoption metrics
  const adoptionMetricsData = [
    { category: 'DeFi TVL', percentage: 45.2, amount: 68.3, color: '#4CC1E9' },
    { category: 'Exchange Reserves', percentage: 28.7, amount: 43.4, color: '#2E6049' },
    { category: 'Corporate Treasury', percentage: 15.1, amount: 22.8, color: '#F59E0B' },
    { category: 'Retail Holdings', percentage: 8.3, amount: 12.5, color: '#8B5CF6' },
    { category: 'Cross-border Payments', percentage: 2.7, amount: 4.1, color: '#EF4444' }
  ];

  const [yieldTrendsData] = useState(() => generateYieldTrends(30));

  const COLORS = ['#4CC1E9', '#2E6049', '#F59E0B', '#8B5CF6', '#EF4444', '#10B981', '#F97316', '#6366F1'];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 rounded-lg shadow-xl border border-gray-200">
          <p className="font-semibold text-[#0E1A2B] mb-2">{label}</p>
          <div className="space-y-2">
            {payload.map((entry, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="flex items-center" style={{ color: entry.color }}>
                  <div 
                    className="w-3 h-3 rounded-full mr-2" 
                    style={{ backgroundColor: entry.color }}
                  ></div>
                  {entry.dataKey}:
                </span>
                <span className="font-bold ml-3">
                  {entry.dataKey.includes('yield') || entry.name.includes('Yield') 
                    ? `${entry.value?.toFixed(2)}%` 
                    : entry.dataKey.includes('Cap') || entry.name.includes('Cap')
                    ? `$${entry.value}B`
                    : entry.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      );
    }
    return null;
  };

  const PieTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 rounded-lg shadow-xl border border-gray-200">
          <p className="font-semibold text-[#0E1A2B] mb-2">{data.name}</p>
          <div className="space-y-1">
            <div>Market Cap: <span className="font-bold">${data.value}B</span></div>
            <div>Projects: <span className="font-bold">{data.count}</span></div>
            <div>Share: <span className="font-bold">{((data.value / 147.8) * 100).toFixed(1)}%</span></div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      {/* Chart Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <div className="flex items-center justify-between mb-6">
          <TabsList className="grid w-full max-w-2xl grid-cols-4">
            <TabsTrigger value="distribution" className="flex items-center">
              <Layers className="w-4 h-4 mr-1" />
              Distribution
            </TabsTrigger>
            <TabsTrigger value="rankings" className="flex items-center">
              <BarChart3 className="w-4 h-4 mr-1" />
              Rankings
            </TabsTrigger>
            <TabsTrigger value="yields" className="flex items-center">
              <TrendingUp className="w-4 h-4 mr-1" />
              Yield Trends
            </TabsTrigger>
            <TabsTrigger value="adoption" className="flex items-center">
              <Users className="w-4 h-4 mr-1" />
              Adoption
            </TabsTrigger>
          </TabsList>

          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-1" />
              Export
            </Button>
          </div>
        </div>

        <TabsContent value="distribution">
          <Card className="border-[#4CC1E9]/20">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Layers className="w-5 h-5 mr-2 text-[#4CC1E9]" />
                Stablecoin Market Distribution by Type
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Pie Chart */}
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={marketDistributionData}
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      >
                        {marketDistributionData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip content={<PieTooltip />} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {/* Summary Stats */}
                <div className="space-y-4">
                  {marketDistributionData.map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div 
                          className="w-4 h-4 rounded-full" 
                          style={{ backgroundColor: item.color }}
                        ></div>
                        <div>
                          <h4 className="font-semibold text-[#0E1A2B]">{item.name}</h4>
                          <p className="text-sm text-gray-600">{item.count} projects</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-[#0E1A2B]">${item.value}B</div>
                        <div className="text-sm text-gray-600">
                          {((item.value / 147.8) * 100).toFixed(1)}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rankings">
          <Card className="border-[#4CC1E9]/20">
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart3 className="w-5 h-5 mr-2 text-[#4CC1E9]" />
                Top Stablecoins by Market Cap & Yield
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-80 mb-6">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={topStablecoinsData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                    <XAxis dataKey="name" stroke="#6B7280" />
                    <YAxis stroke="#6B7280" />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="marketCap" fill="#4CC1E9" name="Market Cap ($B)" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Rankings Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left">Rank</th>
                      <th className="px-4 py-2 text-left">Token</th>
                      <th className="px-4 py-2 text-left">Type</th>
                      <th className="px-4 py-2 text-right">Market Cap</th>
                      <th className="px-4 py-2 text-right">Yield</th>
                      <th className="px-4 py-2 text-right">24h Volume</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {topStablecoinsData.map((coin, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-4 py-2 font-bold">#{index + 1}</td>
                        <td className="px-4 py-2">
                          <div className="flex items-center space-x-2">
                            <div className="w-6 h-6 bg-gradient-to-r from-[#4CC1E9] to-[#007A99] rounded-full flex items-center justify-center text-white text-xs font-bold">
                              {coin.name.slice(0, 2)}
                            </div>
                            <span className="font-medium">{coin.name}</span>
                          </div>
                        </td>
                        <td className="px-4 py-2">
                          <Badge variant="outline" className="text-xs">
                            {coin.type}
                          </Badge>
                        </td>
                        <td className="px-4 py-2 text-right font-medium">${coin.marketCap}B</td>
                        <td className="px-4 py-2 text-right font-medium text-[#4CC1E9]">{coin.yield.toFixed(2)}%</td>
                        <td className="px-4 py-2 text-right">${coin.volume24h}B</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="yields">
          <Card className="border-[#4CC1E9]/20">
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-[#4CC1E9]" />
                Stablecoin Yield Trends (30 Days)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={yieldTrendsData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                    <XAxis dataKey="date" stroke="#6B7280" />
                    <YAxis stroke="#6B7280" tickFormatter={(value) => `${value.toFixed(1)}%`} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Line type="monotone" dataKey="USDT" stroke="#4CC1E9" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="USDC" stroke="#2E6049" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="DAI" stroke="#F59E0B" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="FRAX" stroke="#8B5CF6" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Yield Statistics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                {['USDT', 'USDC', 'DAI', 'FRAX'].map((coin, index) => {
                  const latestData = yieldTrendsData[yieldTrendsData.length - 1];
                  const firstData = yieldTrendsData[0];
                  const change = latestData[coin] - firstData[coin];
                  
                  return (
                    <div key={coin} className="p-3 bg-gray-50 rounded-lg text-center">
                      <div className="font-semibold text-[#0E1A2B]">{coin}</div>
                      <div className="text-lg font-bold text-[#4CC1E9]">
                        {latestData[coin].toFixed(2)}%
                      </div>
                      <div className={`text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {change >= 0 ? '+' : ''}{change.toFixed(2)}%
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="adoption">
          <Card className="border-[#4CC1E9]/20">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="w-5 h-5 mr-2 text-[#4CC1E9]" />
                Stablecoin Adoption Metrics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Bar Chart */}
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={adoptionMetricsData} layout="horizontal" margin={{ top: 5, right: 30, left: 80, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                      <XAxis type="number" domain={[0, 50]} tickFormatter={(value) => `${value}%`} />
                      <YAxis dataKey="category" type="category" width={80} />
                      <Tooltip 
                        formatter={(value, name) => [
                          name === 'percentage' ? `${value}%` : `$${value}B`,
                          name === 'percentage' ? 'Share' : 'Amount'
                        ]}
                      />
                      <Bar dataKey="percentage" fill="#4CC1E9" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Adoption Stats */}
                <div className="space-y-4">
                  {adoptionMetricsData.map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div 
                          className="w-4 h-4 rounded-full" 
                          style={{ backgroundColor: item.color }}
                        ></div>
                        <div>
                          <h4 className="font-semibold text-[#0E1A2B]">{item.category}</h4>
                          <p className="text-sm text-gray-600">{item.percentage}% of market</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-[#0E1A2B]">${item.amount}B</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default StablecoinMarketCharts;