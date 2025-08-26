import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  Calendar,
  BarChart3,
  Activity,
  Zap
} from 'lucide-react';

const SYIHistoricalChart = () => {
  const [chartData, setChartData] = useState([]);
  const [timeframe, setTimeframe] = useState('30d');
  const [loading, setLoading] = useState(true);
  const [performance, setPerformance] = useState({});

  const timeframeOptions = [
    { label: '7D', value: '7d', days: 7 },
    { label: '30D', value: '30d', days: 30 },
    { label: '90D', value: '90d', days: 90 },
    { label: '1Y', value: '365d', days: 365 }
  ];

  const fetchHistoricalData = async (days) => {
    try {
      setLoading(true);
      
      // Dynamic backend URL detection
      const getBackendURL = () => {
        if (window.location.hostname === 'localhost') {
          return 'http://localhost:8001';
        }
        const envBackendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
        if (envBackendUrl) {
          return envBackendUrl;
        }
        const protocol = window.location.protocol === 'https:' ? 'https:' : window.location.protocol;
        const hostname = window.location.hostname;
        return `${protocol}//${hostname}`;
      };

      const backendUrl = getBackendURL();
      const response = await fetch(`${backendUrl}/api/index/history?days=${days}`);
      
      if (response.ok) {
        const data = await response.json();
        
        // Process data for chart
        const processedData = data.map((item, index) => {
          const date = new Date(item.timestamp);
          const yieldPercentage = ((item.value - 1) * 100); // Convert index value to yield percentage
          
          return {
            date: date.toISOString().split('T')[0],
            timestamp: item.timestamp,
            index_value: item.value,
            yield_percentage: yieldPercentage,
            formatted_date: date.toLocaleDateString('en-US', { 
              month: 'short', 
              day: 'numeric' 
            }),
            full_date: date.toLocaleDateString('en-US', {
              weekday: 'short',
              year: 'numeric',
              month: 'short', 
              day: 'numeric'
            })
          };
        });

        // Sort by date
        processedData.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        
        // Calculate performance metrics
        if (processedData.length > 0) {
          const latestValue = processedData[processedData.length - 1].yield_percentage;
          const earliestValue = processedData[0].yield_percentage;
          const change = latestValue - earliestValue;
          const changePercent = earliestValue !== 0 ? (change / Math.abs(earliestValue)) * 100 : 0;
          
          const maxValue = Math.max(...processedData.map(d => d.yield_percentage));
          const minValue = Math.min(...processedData.map(d => d.yield_percentage));
          const avgValue = processedData.reduce((sum, d) => sum + d.yield_percentage, 0) / processedData.length;
          
          setPerformance({
            current: latestValue,
            change: change,
            changePercent: changePercent,
            max: maxValue,
            min: minValue,
            average: avgValue,
            volatility: calculateVolatility(processedData.map(d => d.yield_percentage))
          });
        }
        
        setChartData(processedData);
      } else {
        // Fallback to mock data
        setChartData(generateMockData(days));
        setPerformance(generateMockPerformance());
      }
    } catch (error) {
      console.error('Error fetching historical data:', error);
      // Fallback to mock data
      setChartData(generateMockData(days));
      setPerformance(generateMockPerformance());
    } finally {
      setLoading(false);
    }
  };

  const calculateVolatility = (values) => {
    if (values.length < 2) return 0;
    const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
    const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / (values.length - 1);
    return Math.sqrt(variance);
  };

  const generateMockData = (days) => {
    const data = [];
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    
    let currentYield = 1.02; // Start with ~1.02% yield
    
    for (let i = 0; i < days; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      
      // Add some realistic volatility
      const randomChange = (Math.random() - 0.5) * 0.02; // ±1 basis point
      currentYield = Math.max(0.5, Math.min(2.5, currentYield + randomChange));
      
      data.push({
        date: date.toISOString().split('T')[0],
        timestamp: date.toISOString(),
        index_value: 1 + (currentYield / 100),
        yield_percentage: currentYield,
        formatted_date: date.toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric' 
        }),
        full_date: date.toLocaleDateString('en-US', {
          weekday: 'short',
          year: 'numeric',
          month: 'short', 
          day: 'numeric'
        })
      });
    }
    
    return data;
  };

  const generateMockPerformance = () => ({
    current: 1.017,
    change: 0.023,
    changePercent: 2.31,
    max: 1.156,
    min: 0.892,
    average: 1.024,
    volatility: 0.048
  });

  useEffect(() => {
    const selectedTimeframe = timeframeOptions.find(t => t.value === timeframe);
    fetchHistoricalData(selectedTimeframe?.days || 30);
  }, [timeframe]);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border">
          <p className="font-semibold text-[#0E1A2B] mb-1">{data.full_date}</p>
          <p className="text-[#4CC1E9]">
            SYI Yield: <span className="font-bold">{data.yield_percentage.toFixed(3)}%</span>
          </p>
          <p className="text-gray-600 text-sm">
            Index Value: {data.index_value.toFixed(4)}
          </p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <Card className="border-[#4CC1E9]/20">
        <CardContent className="p-6">
          <div className="animate-pulse">
            <div className="h-64 bg-gray-200 rounded mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-[#4CC1E9]/20 bg-gradient-to-br from-white to-[#4CC1E9]/5">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center">
            <BarChart3 className="w-6 h-6 mr-2 text-[#4CC1E9]" />
            StableYield Index (SYI) Historical Performance
          </CardTitle>
          
          <div className="flex items-center space-x-2">
            {timeframeOptions.map((option) => (
              <Button
                key={option.value}
                variant={timeframe === option.value ? "default" : "outline"}
                size="sm"
                onClick={() => setTimeframe(option.value)}
                className={timeframe === option.value ? "bg-[#4CC1E9] hover:bg-[#007A99]" : ""}
              >
                {option.label}
              </Button>
            ))}
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        {/* Performance Summary */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center p-3 bg-white rounded-lg border">
            <div className="flex items-center justify-center mb-1">
              <Activity className="w-4 h-4 text-[#4CC1E9] mr-1" />
              <span className="text-sm text-gray-600">Current Yield</span>
            </div>
            <div className="text-lg font-bold text-[#0E1A2B]">
              {performance.current?.toFixed(3)}%
            </div>
          </div>
          
          <div className="text-center p-3 bg-white rounded-lg border">
            <div className="flex items-center justify-center mb-1">
              {performance.change >= 0 ? (
                <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 text-red-500 mr-1" />
              )}
              <span className="text-sm text-gray-600">Change</span>
            </div>
            <div className={`text-lg font-bold ${performance.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {performance.change >= 0 ? '+' : ''}{performance.change?.toFixed(3)}%
            </div>
          </div>
          
          <div className="text-center p-3 bg-white rounded-lg border">
            <div className="flex items-center justify-center mb-1">
              <BarChart3 className="w-4 h-4 text-[#007A99] mr-1" />
              <span className="text-sm text-gray-600">Average</span>
            </div>
            <div className="text-lg font-bold text-[#0E1A2B]">
              {performance.average?.toFixed(3)}%
            </div>
          </div>
          
          <div className="text-center p-3 bg-white rounded-lg border">
            <div className="flex items-center justify-center mb-1">
              <Zap className="w-4 h-4 text-orange-500 mr-1" />
              <span className="text-sm text-gray-600">Volatility</span>
            </div>
            <div className="text-lg font-bold text-[#0E1A2B]">
              {(performance.volatility * 100)?.toFixed(2)}bp
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <defs>
                <linearGradient id="syiGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#4CC1E9" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#4CC1E9" stopOpacity={0.05}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="formatted_date" 
                stroke="#6B7280"
                fontSize={12}
              />
              <YAxis 
                stroke="#6B7280"
                fontSize={12}
                domain={['dataMin - 0.1', 'dataMax + 0.1']}
                tickFormatter={(value) => `${value.toFixed(2)}%`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="yield_percentage"
                stroke="#4CC1E9"
                strokeWidth={2}
                fill="url(#syiGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Analysis Summary */}
        <div className="mt-6 p-4 bg-gradient-to-r from-[#0E1A2B] to-[#2E6049] rounded-xl text-white">
          <h4 className="font-semibold mb-2 flex items-center">
            <Calendar className="w-4 h-4 mr-2" />
            {timeframe.toUpperCase()} Performance Analysis
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-white/70">Yield Range:</span>
              <span className="ml-2 font-medium">
                {performance.min?.toFixed(3)}% - {performance.max?.toFixed(3)}%
              </span>
            </div>
            <div>
              <span className="text-white/70">Trend:</span>
              <Badge 
                className={`ml-2 ${performance.change >= 0 ? 'bg-green-600' : 'bg-red-600'}`}
                variant="default"
              >
                {performance.change >= 0 ? 'Upward' : 'Downward'} {Math.abs(performance.changePercent)?.toFixed(1)}%
              </Badge>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default SYIHistoricalChart;