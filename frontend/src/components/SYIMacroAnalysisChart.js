import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Area,
  AreaChart,
  ComposedChart,
  ReferenceLine
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  Calendar,
  BarChart3,
  Activity,
  Zap,
  AlertTriangle,
  Shield,
  Building2,
  Download,
  Info
} from 'lucide-react';

const SYIMacroAnalysisChart = () => {
  const [chartData, setChartData] = useState([]);
  const [timeframe, setTimeframe] = useState('90d');
  const [loading, setLoading] = useState(true);
  const [performance, setPerformance] = useState({});
  const [activeTab, setActiveTab] = useState('rpl');

  const timeframeOptions = [
    { label: '7D', value: '7d', days: 7 },
    { label: '30D', value: '30d', days: 30 },
    { label: '90D', value: '90d', days: 90 },
    { label: '1Y', value: '365d', days: 365 }
  ];

  const fetchMacroData = async (days) => {
    try {
      setLoading(true);
      
      // Fetch SYI data, U.S. Treasury data, and SSI data in parallel
      const [syiData, treasuryData, ssiData] = await Promise.all([
        fetchSYIData(days),
        fetchTreasuryData(days),
        fetchSSIData(days)
      ]);
      
      // Merge all data by date
      const mergedData = mergeMacroData(syiData, treasuryData, ssiData);
      
      // Calculate performance metrics and analytics
      const analytics = calculateMacroAnalytics(mergedData);
      
      setChartData(mergedData);
      setPerformance(analytics);
      
    } catch (error) {
      console.error('Error fetching macro data:', error);
      // Fallback to mock data
      const mockData = generateMockMacroData(days);
      setChartData(mockData);
      setPerformance(generateMockAnalytics());
    } finally {
      setLoading(false);
    }
  };

  const fetchSYIData = async (days) => {
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

    try {
      const backendUrl = getBackendURL();
      const response = await fetch(`${backendUrl}/api/index/history?days=${days}`);
      
      if (response.ok) {
        const data = await response.json();
        
        return data.map((item) => {
          const date = new Date(item.timestamp);
          const yieldPercentage = ((item.value - 1) * 100);
          
          return {
            date: date.toISOString().split('T')[0],
            timestamp: item.timestamp,
            syi_yield: yieldPercentage,
            formatted_date: date.toLocaleDateString('en-US', { 
              month: 'short', 
              day: 'numeric' 
            })
          };
        }).sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
      }
    } catch (error) {
      console.error('Error fetching SYI data:', error);
    }
    
    // Return mock data if fetch fails
    return generateMockSYIData(days);
  };

  const fetchTreasuryData = async (days) => {
    try {
      // FRED API for 3-Month Treasury Bills (DTB3)
      // Note: In production, you'd need FRED API key and proper CORS handling
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - days);
      
      // For now, using mock data that simulates realistic Treasury yields
      return generateMockTreasuryData(days);
      
    } catch (error) {
      console.error('Error fetching Treasury data:', error);
      return generateMockTreasuryData(days);
    }
  };

  const fetchSSIData = async (days) => {
    try {
      // SSI calculation: α × Kurtosis_peg + (1-α) × Entropy_liquidity
      // This would integrate with the backend SSI calculation
      return generateMockSSIData(days);
      
    } catch (error) {
      console.error('Error fetching SSI data:', error);
      return generateMockSSIData(days);
    }
  };

  const generateMockSYIData = (days) => {
    const data = [];
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    
    let currentYield = 1.72; // Current SYI yield
    
    for (let i = 0; i < days; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      
      // Add realistic SYI volatility (much lower than crypto)
      const randomChange = (Math.random() - 0.5) * 0.05; // ±2.5bp daily
      currentYield = Math.max(1.0, Math.min(2.5, currentYield + randomChange));
      
      data.push({
        date: date.toISOString().split('T')[0],
        timestamp: date.getTime(),
        syi_yield: currentYield,
        formatted_date: date.toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric' 
        })
      });
    }
    
    return data;
  };

  const generateMockTreasuryData = (days) => {
    const data = [];
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    
    let currentTBill = 5.25; // Current 3M T-Bill rate
    
    for (let i = 0; i < days; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      
      // T-Bills move slower and more predictably than SYI
      const randomChange = (Math.random() - 0.5) * 0.02; // ±1bp daily
      currentTBill = Math.max(4.5, Math.min(6.0, currentTBill + randomChange));
      
      data.push({
        date: date.toISOString().split('T')[0],
        tbill_3m: currentTBill
      });
    }
    
    return data;
  };

  const generateMockSSIData = (days) => {
    const data = [];
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    
    for (let i = 0; i < days; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      
      // SSI: normally low (0.1-0.3), spikes during stress (0.7-1.0)
      let baseSSI = 0.2;
      
      // Add periodic stress events
      if (Math.random() < 0.05) { // 5% chance of stress event
        baseSSI = 0.7 + Math.random() * 0.3; // Stress spike 0.7-1.0
      } else {
        baseSSI += (Math.random() - 0.5) * 0.1; // Normal fluctuation
      }
      
      baseSSI = Math.max(0.0, Math.min(1.0, baseSSI));
      
      data.push({
        date: date.toISOString().split('T')[0],
        ssi_index: baseSSI
      });
    }
    
    return data;
  };

  const mergeMacroData = (syiData, treasuryData, ssiData) => {
    return syiData.map(syiItem => {
      const treasuryItem = treasuryData.find(t => t.date === syiItem.date);
      const ssiItem = ssiData.find(s => s.date === syiItem.date);
      
      const syiYield = syiItem.syi_yield;
      const tbillYield = treasuryItem?.tbill_3m || 5.25;
      const rpl = syiYield - tbillYield; // Risk Premium Liquidity spread
      
      return {
        ...syiItem,
        tbill_3m: tbillYield,
        rpl_spread: rpl,
        ssi_index: ssiItem?.ssi_index || 0.2,
        // Risk regime classification
        risk_regime: rpl > 0 ? 'risk-on' : 'risk-off',
        stress_level: ssiItem?.ssi_index > 0.6 ? 'high' : 
                     ssiItem?.ssi_index > 0.4 ? 'medium' : 'low'
      };
    });
  };

  const calculateMacroAnalytics = (data) => {
    if (data.length === 0) return {};
    
    const latestData = data[data.length - 1];
    const firstData = data[0];
    
    // RPL Analytics
    const rplValues = data.map(d => d.rpl_spread);
    const avgRPL = rplValues.reduce((sum, val) => sum + val, 0) / rplValues.length;
    const rplVolatility = calculateVolatility(rplValues);
    const crossovers = countZeroCrossovers(rplValues);
    
    // SSI Analytics  
    const ssiValues = data.map(d => d.ssi_index);
    const avgSSI = ssiValues.reduce((sum, val) => sum + val, 0) / ssiValues.length;
    const maxSSI = Math.max(...ssiValues);
    const stressEvents = ssiValues.filter(val => val > 0.6).length;
    
    // Risk Regime Analysis
    const riskOnDays = data.filter(d => d.risk_regime === 'risk-on').length;
    const riskOnPercentage = (riskOnDays / data.length) * 100;
    
    return {
      current_syi: latestData.syi_yield,
      current_tbill: latestData.tbill_3m,
      current_rpl: latestData.rpl_spread,
      current_ssi: latestData.ssi_index,
      avg_rpl: avgRPL,
      rpl_volatility: rplVolatility,
      zero_crossovers: crossovers,
      avg_ssi: avgSSI,
      max_ssi: maxSSI,
      stress_events: stressEvents,
      risk_on_percentage: riskOnPercentage,
      current_regime: latestData.risk_regime,
      current_stress: latestData.stress_level
    };
  };

  const calculateVolatility = (values) => {
    if (values.length < 2) return 0;
    const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
    const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / (values.length - 1);
    return Math.sqrt(variance);
  };

  const countZeroCrossovers = (values) => {
    let crossovers = 0;
    for (let i = 1; i < values.length; i++) {
      if ((values[i-1] > 0 && values[i] <= 0) || (values[i-1] <= 0 && values[i] > 0)) {
        crossovers++;
      }
    }
    return crossovers;
  };

  const generateMockAnalytics = () => ({
    current_syi: 1.72,
    current_tbill: 5.25,
    current_rpl: -3.53,
    current_ssi: 0.23,
    avg_rpl: -3.45,
    rpl_volatility: 0.15,
    zero_crossovers: 2,
    avg_ssi: 0.25,
    max_ssi: 0.78,
    stress_events: 3,
    risk_on_percentage: 25.4,
    current_regime: 'risk-off',
    current_stress: 'low'
  });

  const exportData = (format) => {
    if (format === 'csv') {
      const csvData = chartData.map(row => ({
        Date: row.date,
        'SYI Yield': row.syi_yield.toFixed(4),
        '3M T-Bill': row.tbill_3m.toFixed(4),
        'RPL Spread': row.rpl_spread.toFixed(4),
        'SSI Index': row.ssi_index.toFixed(4),
        'Risk Regime': row.risk_regime,
        'Stress Level': row.stress_level
      }));
      
      const csv = [
        Object.keys(csvData[0]).join(','),
        ...csvData.map(row => Object.values(row).join(','))
      ].join('\n');
      
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `syi-macro-analysis-${timeframe}.csv`;
      a.click();
    }
  };

  useEffect(() => {
    const selectedTimeframe = timeframeOptions.find(t => t.value === timeframe);
    fetchMacroData(selectedTimeframe?.days || 90);
  }, [timeframe]);

  const RPLTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 rounded-lg shadow-xl border border-gray-200">
          <p className="font-semibold text-[#0E1A2B] mb-2">{data.formatted_date}</p>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[#4CC1E9] flex items-center">
                <div className="w-3 h-3 bg-[#4CC1E9] rounded-full mr-2"></div>
                SYI Yield:
              </span>
              <span className="font-bold ml-3">{data.syi_yield?.toFixed(3)}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-black flex items-center">
                <div className="w-3 h-3 bg-black rounded-full mr-2"></div>
                3M T-Bill:
              </span>
              <span className="font-bold ml-3">{data.tbill_3m?.toFixed(3)}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className={`flex items-center ${data.rpl_spread >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                <div className={`w-3 h-3 rounded-full mr-2 ${data.rpl_spread >= 0 ? 'bg-green-500' : 'bg-red-500'}`}></div>
                RPL Spread:
              </span>
              <span className={`font-bold ml-3 ${data.rpl_spread >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {data.rpl_spread >= 0 ? '+' : ''}{data.rpl_spread?.toFixed(2)}bp
              </span>
            </div>
            <div className="border-t pt-2 mt-2 text-xs text-gray-500">
              <div>Risk Regime: <span className="font-medium">{data.risk_regime}</span></div>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  const SSITooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 rounded-lg shadow-xl border border-gray-200">
          <p className="font-semibold text-[#0E1A2B] mb-2">{data.formatted_date}</p>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[#4CC1E9] flex items-center">
                <div className="w-3 h-3 bg-[#4CC1E9] rounded-full mr-2"></div>
                SYI Yield:
              </span>
              <span className="font-bold ml-3">{data.syi_yield?.toFixed(3)}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-red-500 flex items-center">
                <AlertTriangle className="w-3 h-3 mr-2" />
                SSI Index:
              </span>
              <span className="font-bold ml-3">{(data.ssi_index * 100)?.toFixed(1)}</span>
            </div>
            <div className="border-t pt-2 mt-2 text-xs text-gray-500">
              <div>Stress Level: <span className="font-medium capitalize">{data.stress_level}</span></div>
            </div>
          </div>
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
            SYI Macro Analysis - Risk-On/Risk-Off Indicators
          </CardTitle>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => exportData('csv')}
              className="text-gray-600 border-gray-300"
            >
              <Download className="w-4 h-4 mr-1" />
              CSV
            </Button>
            
            <div className="w-px h-6 bg-gray-300"></div>
            
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
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="rpl" className="flex items-center">
              <Building2 className="w-4 h-4 mr-2" />
              SYI vs T-Bills (RPL)
            </TabsTrigger>
            <TabsTrigger value="ssi" className="flex items-center">
              <AlertTriangle className="w-4 h-4 mr-2" />
              SYI vs SSI (Stress)
            </TabsTrigger>
          </TabsList>

          <TabsContent value="rpl" className="space-y-6">
            {/* RPL Performance Summary */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-white rounded-lg border">
                <div className="flex items-center justify-center mb-1">
                  <Activity className="w-4 h-4 text-[#4CC1E9] mr-1" />
                  <span className="text-sm text-gray-600">Current RPL</span>
                </div>
                <div className={`text-lg font-bold ${performance.current_rpl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {performance.current_rpl >= 0 ? '+' : ''}{performance.current_rpl?.toFixed(2)}bp
                </div>
              </div>
              
              <div className="text-center p-3 bg-white rounded-lg border">
                <div className="flex items-center justify-center mb-1">
                  <Shield className="w-4 h-4 text-gray-600 mr-1" />
                  <span className="text-sm text-gray-600">Risk Regime</span>
                </div>
                <Badge className={performance.current_regime === 'risk-on' ? 'bg-green-600' : 'bg-red-600'}>
                  {performance.current_regime}
                </Badge>
              </div>
              
              <div className="text-center p-3 bg-white rounded-lg border">
                <div className="flex items-center justify-center mb-1">
                  <TrendingUp className="w-4 h-4 text-orange-500 mr-1" />
                  <span className="text-sm text-gray-600">Crossovers</span>
                </div>
                <div className="text-lg font-bold text-[#0E1A2B]">
                  {performance.zero_crossovers || 0}
                </div>
              </div>
              
              <div className="text-center p-3 bg-white rounded-lg border">
                <div className="flex items-center justify-center mb-1">
                  <Zap className="w-4 h-4 text-purple-500 mr-1" />
                  <span className="text-sm text-gray-600">Risk-On %</span>
                </div>
                <div className="text-lg font-bold text-[#0E1A2B]">
                  {performance.risk_on_percentage?.toFixed(1)}%
                </div>
              </div>
            </div>

            {/* RPL Chart */}
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <defs>
                    <linearGradient id="positiveRPL" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10B981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10B981" stopOpacity={0.05}/>
                    </linearGradient>
                    <linearGradient id="negativeRPL" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#EF4444" stopOpacity={0.05}/>
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
                    tickFormatter={(value) => `${value.toFixed(1)}%`}
                  />
                  <Tooltip content={<RPLTooltip />} />
                  
                  {/* Zero reference line */}
                  <ReferenceLine y={0} stroke="#9CA3AF" strokeDasharray="2 2" />
                  
                  {/* SYI Line */}
                  <Line
                    type="monotone"
                    dataKey="syi_yield"
                    stroke="#4CC1E9"
                    strokeWidth={3}
                    dot={false}
                    name="SYI Yield"
                  />
                  
                  {/* T-Bill Line */}
                  <Line
                    type="monotone"
                    dataKey="tbill_3m"
                    stroke="#000000"
                    strokeWidth={2}
                    dot={false}
                    name="3M T-Bill"
                  />
                  
                  {/* RPL Area (positive/negative) */}
                  {chartData.map((entry, index) => (
                    <Area
                      key={index}
                      type="monotone"
                      dataKey="rpl_spread"
                      stroke={entry.rpl_spread >= 0 ? "#10B981" : "#EF4444"}
                      fill={entry.rpl_spread >= 0 ? "url(#positiveRPL)" : "url(#negativeRPL)"}
                    />
                  ))}
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            {/* RPL Analysis */}
            <div className="p-4 bg-gradient-to-r from-[#0E1A2B] to-[#2E6049] rounded-xl text-white">
              <h4 className="font-semibold mb-2 flex items-center">
                <Building2 className="w-4 h-4 mr-2" />
                Risk Premium Liquidity (RPL) Analysis
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-white/70">Current Spread:</span>
                  <span className={`ml-2 font-medium ${performance.current_rpl >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                    SYI ({performance.current_syi?.toFixed(2)}%) - T-Bill ({performance.current_tbill?.toFixed(2)}%) = {performance.current_rpl?.toFixed(2)}bp
                  </span>
                </div>
                <div>
                  <span className="text-white/70">Interpretation:</span>
                  <span className="ml-2 font-medium">
                    {performance.current_rpl >= 0 ? 'Risk-On: Stablecoins offer premium vs Treasuries' : 'Risk-Off: Flight to safety, Treasuries outperform'}
                  </span>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="ssi" className="space-y-6">
            {/* SSI Performance Summary */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-white rounded-lg border">
                <div className="flex items-center justify-center mb-1">
                  <AlertTriangle className="w-4 h-4 text-red-500 mr-1" />
                  <span className="text-sm text-gray-600">Current SSI</span>
                </div>
                <div className="text-lg font-bold text-red-600">
                  {(performance.current_ssi * 100)?.toFixed(1)}
                </div>
              </div>
              
              <div className="text-center p-3 bg-white rounded-lg border">
                <div className="flex items-center justify-center mb-1">
                  <Shield className="w-4 h-4 text-gray-600 mr-1" />
                  <span className="text-sm text-gray-600">Stress Level</span>
                </div>
                <Badge className={
                  performance.current_stress === 'high' ? 'bg-red-600' :
                  performance.current_stress === 'medium' ? 'bg-yellow-600' : 'bg-green-600'
                }>
                  {performance.current_stress}
                </Badge>
              </div>
              
              <div className="text-center p-3 bg-white rounded-lg border">
                <div className="flex items-center justify-center mb-1">
                  <TrendingUp className="w-4 h-4 text-orange-500 mr-1" />
                  <span className="text-sm text-gray-600">Max SSI</span>
                </div>
                <div className="text-lg font-bold text-[#0E1A2B]">
                  {(performance.max_ssi * 100)?.toFixed(1)}
                </div>
              </div>
              
              <div className="text-center p-3 bg-white rounded-lg border">
                <div className="flex items-center justify-center mb-1">
                  <Zap className="w-4 h-4 text-purple-500 mr-1" />
                  <span className="text-sm text-gray-600">Stress Events</span>
                </div>
                <div className="text-lg font-bold text-[#0E1A2B]">
                  {performance.stress_events || 0}
                </div>
              </div>
            </div>

            {/* SSI Chart */}
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis 
                    dataKey="formatted_date" 
                    stroke="#6B7280"
                    fontSize={12}
                  />
                  <YAxis 
                    yAxisId="yield"
                    stroke="#6B7280"
                    fontSize={12}
                    tickFormatter={(value) => `${value.toFixed(1)}%`}
                    orientation="left"
                  />
                  <YAxis 
                    yAxisId="ssi"
                    stroke="#EF4444"
                    fontSize={12}
                    domain={[0, 1]}
                    tickFormatter={(value) => `${(value * 100).toFixed(0)}`}
                    orientation="right"
                  />
                  <Tooltip content={<SSITooltip />} />
                  
                  {/* SYI Line */}
                  <Line
                    yAxisId="yield"
                    type="monotone"
                    dataKey="syi_yield"
                    stroke="#4CC1E9"
                    strokeWidth={3}
                    dot={false}
                    name="SYI Yield"
                  />
                  
                  {/* SSI Line with stress level highlighting */}
                  <Line
                    yAxisId="ssi"
                    type="monotone"
                    dataKey="ssi_index"
                    stroke="#EF4444"
                    strokeWidth={2}
                    dot={false}
                    name="SSI Index"
                  />
                  
                  {/* Stress threshold lines */}
                  <ReferenceLine yAxisId="ssi" y={0.6} stroke="#EF4444" strokeDasharray="2 2" />
                  <ReferenceLine yAxisId="ssi" y={0.4} stroke="#F59E0B" strokeDasharray="2 2" />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            {/* SSI Analysis */}
            <div className="p-4 bg-gradient-to-r from-[#0E1A2B] to-[#2E6049] rounded-xl text-white">
              <h4 className="font-semibold mb-2 flex items-center">
                <AlertTriangle className="w-4 h-4 mr-2" />
                Stablecoin Stress Index (SSI) Analysis
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-white/70">Formula:</span>
                  <span className="ml-2 font-medium font-mono">
                    SSI = α × Kurtosis_peg + (1-α) × Entropy_liquidity
                  </span>
                </div>
                <div>
                  <span className="text-white/70">Current Status:</span>
                  <span className="ml-2 font-medium">
                    {performance.current_ssi > 0.6 ? 'HIGH STRESS - Systemic risk detected' :
                     performance.current_ssi > 0.4 ? 'MODERATE STRESS - Monitor closely' :
                     'LOW STRESS - Normal market conditions'}
                  </span>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default SYIMacroAnalysisChart;