import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { TrendingUp, TrendingDown, BarChart3, Calendar, Download } from 'lucide-react';

const SYIMacroAnalysisChart = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('6M');
  const [selectedMetrics, setSelectedMetrics] = useState(['syi', 'tbill', 'volatility']);
  
  // Sample data - replace with real API call
  const generateSampleData = () => {
    const days = timeRange === '1M' ? 30 : timeRange === '3M' ? 90 : 180;
    const data = [];
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    
    for (let i = 0; i < days; i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i);
      
      // Generate realistic SYI data with some volatility
      const baseSYI = 4.47;
      const syiVariation = (Math.sin(i / 10) + Math.random() * 0.5 - 0.25) * 0.3;
      
      // T-Bill rates (more stable)
      const baseTBill = 5.25;
      const tbillVariation = (Math.random() * 0.1 - 0.05);
      
      // Volatility indicator
      const volatility = Math.abs(syiVariation) * 10 + Math.random() * 5 + 15;
      
      // Risk regime (simplified)
      const riskOn = baseSYI + syiVariation > baseTBill + tbillVariation ? 1 : 0;
      
      data.push({
        date: date.toISOString().split('T')[0],
        dateLabel: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        syi: baseSYI + syiVariation,
        tbill: baseTBill + tbillVariation,
        spread: (baseSYI + syiVariation) - (baseTBill + tbillVariation),
        volatility: volatility,
        riskRegime: riskOn
      });
    }
    return data;
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Dynamic backend URL detection
        const getBackendURL = () => {
          // Always use environment variable if available
          const envBackendUrl = process.env.REACT_APP_BACKEND_URL || import.meta?.env?.REACT_APP_BACKEND_URL;
          if (envBackendUrl) {
            return envBackendUrl;
          }
          
          // Fallback for localhost development
          if (window.location.hostname === 'localhost') {
            return 'http://localhost:8001';
          }
          
          // Use same protocol and hostname as current page
          const protocol = window.location.protocol === 'https:' ? 'https:' : window.location.protocol;
          const hostname = window.location.hostname;
          return `${protocol}//${hostname}`;
        };

        const backendUrl = getBackendURL();
        
        // Try to fetch real data from SYI API
        const response = await fetch(`${backendUrl}/api/syi/history?from=${new Date(Date.now() - 180*24*60*60*1000).toISOString().split('T')[0]}&to=${new Date().toISOString().split('T')[0]}`);
        
        if (response.ok) {
          const result = await response.json();
          if (result.success && result.series) {
            // Transform API data to chart format
            const transformedData = result.series.map(entry => ({
              date: entry.date,
              dateLabel: new Date(entry.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
              syi: entry.syi_excess ? entry.syi_excess * 100 + 5.25 : 4.47, // Add back T-Bill approximation
              tbill: 5.25, // Default T-Bill rate
              spread: entry.syi_excess ? entry.syi_excess * 100 : -0.78,
              volatility: Math.abs(entry.z_score || 0) * 10 + 20,
              riskRegime: (entry.state === 'ON' || entry.state === 'NEU') ? 1 : 0
            }));
            setData(transformedData);
          } else {
            throw new Error('Invalid API response');
          }
        } else {
          throw new Error('API request failed');
        }
      } catch (error) {
        console.error('Error fetching SYI data:', error);
        // Fallback to sample data
        setData(generateSampleData());
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [timeRange]);

  const metrics = {
    syi: { 
      key: 'syi', 
      name: 'SYI', 
      color: '#4CC1E9', 
      unit: '%',
      format: (val) => `${val.toFixed(2)}%`
    },
    tbill: { 
      key: 'tbill', 
      name: '3M T-Bill', 
      color: '#007A99', 
      unit: '%',
      format: (val) => `${val.toFixed(2)}%`
    },
    spread: { 
      key: 'spread', 
      name: 'SYI Spread', 
      color: '#2E6049', 
      unit: 'bps',
      format: (val) => `${(val * 100).toFixed(0)}bps`
    },
    volatility: { 
      key: 'volatility', 
      name: 'Volatility', 
      color: '#F59E0B', 
      unit: '%',
      format: (val) => `${val.toFixed(1)}%`
    }
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900 mb-2">{label}</p>
          {payload.map((entry) => {
            const metric = Object.values(metrics).find(m => m.key === entry.dataKey);
            return (
              <div key={entry.dataKey} className="flex items-center space-x-2 mb-1">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: entry.color }}
                />
                <span className="text-sm text-gray-700">
                  {metric?.name}: {metric?.format ? metric.format(entry.value) : entry.value}
                </span>
              </div>
            );
          })}
          
          {/* Risk Regime Indicator */}
          {payload[0]?.payload?.riskRegime !== undefined && (
            <div className="mt-2 pt-2 border-t border-gray-100">
              <div className="flex items-center space-x-2">
                <div 
                  className={`w-3 h-3 rounded-full ${payload[0].payload.riskRegime ? 'bg-green-500' : 'bg-red-500'}`}
                />
                <span className="text-sm font-medium">
                  {payload[0].payload.riskRegime ? 'Risk-On' : 'Risk-Off'} Regime
                </span>
              </div>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="w-5 h-5" />
            <span>SYI Macro Analysis</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-96 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#4CC1E9]"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-4 sm:space-y-0">
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="w-5 h-5" />
            <span>SYI Macro Analysis</span>
          </CardTitle>
          
          <div className="flex flex-wrap items-center gap-2">
            {/* Time Range Selector */}
            <div className="flex items-center space-x-1">
              {['1M', '3M', '6M'].map((range) => (
                <Button
                  key={range}
                  variant={timeRange === range ? "default" : "outline"}
                  size="sm"
                  onClick={() => setTimeRange(range)}
                  className={`h-8 px-3 ${timeRange === range ? 'bg-[#4CC1E9]' : ''}`}
                >
                  {range}
                </Button>
              ))}
            </div>
            
            {/* Download Button */}
            <Button variant="outline" size="sm" className="h-8">
              <Download className="w-4 h-4 mr-1" />
              Export
            </Button>
          </div>
        </div>
        
        {/* Metric Toggles */}
        <div className="flex flex-wrap gap-2 mt-4">
          {Object.entries(metrics).map(([key, metric]) => (
            <Badge
              key={key}
              variant={selectedMetrics.includes(key) ? "default" : "outline"}
              className={`cursor-pointer ${selectedMetrics.includes(key) ? 'bg-[#4CC1E9]' : ''}`}
              onClick={() => {
                setSelectedMetrics(prev => 
                  prev.includes(key) 
                    ? prev.filter(m => m !== key)
                    : [...prev, key]
                );
              }}
            >
              <div 
                className="w-2 h-2 rounded-full mr-1" 
                style={{ backgroundColor: metric.color }}
              />
              {metric.name}
            </Badge>
          ))}
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis 
                dataKey="dateLabel" 
                className="text-xs"
                tick={{ fontSize: 12 }}
              />
              <YAxis 
                className="text-xs"
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => `${value.toFixed(1)}%`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              
              {/* Zero line for spread */}
              {selectedMetrics.includes('spread') && (
                <ReferenceLine y={0} stroke="#666" strokeDasharray="2 2" />
              )}
              
              {/* Render selected metrics */}
              {selectedMetrics.map((metricKey) => {
                const metric = metrics[metricKey];
                return (
                  <Line
                    key={metricKey}
                    type="monotone"
                    dataKey={metric.key}
                    stroke={metric.color}
                    strokeWidth={2}
                    dot={{ fill: metric.color, strokeWidth: 2, r: 3 }}
                    activeDot={{ r: 5, stroke: metric.color, strokeWidth: 2 }}
                    name={metric.name}
                  />
                );
              })}
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-100">
          {Object.entries(metrics).map(([key, metric]) => {
            if (!selectedMetrics.includes(key)) return null;
            
            const values = data.map(d => d[key]).filter(v => v !== undefined);
            const avg = values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0;
            const trend = values.length >= 2 ? values[values.length - 1] - values[0] : 0;
            
            return (
              <div key={key} className="text-center">
                <div className="text-sm text-gray-600">{metric.name}</div>
                <div className="text-lg font-semibold" style={{ color: metric.color }}>
                  {metric.format ? metric.format(avg) : avg.toFixed(2)}
                </div>
                <div className={`text-xs flex items-center justify-center ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {trend >= 0 ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                  {Math.abs(trend).toFixed(2)}{metric.unit}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default SYIMacroAnalysisChart;