import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { 
  TrendingUp, 
  TrendingDown,
  BarChart3,
  Building2,
  Layers,
  Target,
  DollarSign,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Minus
} from 'lucide-react';

const IndexFamilyOverview = () => {
  const [indices, setIndices] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState('1D');

  useEffect(() => {
    fetchIndexFamily();
  }, []);

  const fetchIndexFamily = async () => {
    try {
      // Dynamic backend URL detection
      const getBackendURL = () => {
        // Always use environment variable if available
        const envBackendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
        if (envBackendUrl) {
          return envBackendUrl;
        }
        
        // Fallback for localhost development
        if (window.location.hostname === 'localhost') {
          return 'http://localhost:8001';
        }
        
        // Always use HTTPS in production
        const protocol = window.location.protocol === 'https:' ? 'https:' : window.location.protocol;
        const hostname = window.location.hostname;
        return `${protocol}//${hostname}`;
      };
      
      const backendUrl = getBackendURL();
      let indexData = {};
      
      // First, try to get the new SYI calculation for SYC index
      try {
        const syiResponse = await fetch(`${backendUrl}/api/syi/current`);
        const syiData = await syiResponse.json();
        
        if (syiData.success) {
          // Use new SYI calculation as the SY100 index
          indexData.SY100 = {
            index_code: 'SY100',
            value: syiData.syi_decimal, // Use decimal format (e.g., 0.0447448)
            mode: 'Normal',
            constituent_count: syiData.components_count,
            total_tvl: 127500000000, // Placeholder TVL
            avg_yield: syiData.syi_decimal,
            confidence: 0.98, // High confidence for new calculation
            methodology_version: syiData.methodology_version,
            is_syi_calculated: true
          };
        }
      } catch (syiError) {
        console.warn('New SYI system unavailable, using fallback for SY100:', syiError);
      }
      
      // Then get the other indices from the Index Family system
      try {
        // Calculate indices to ensure they exist
        await fetch(`${backendUrl}/api/v1/index-family/calculate`, {
          method: 'POST'
        });
        
        // Fetch index family overview
        const response = await fetch(`${backendUrl}/api/v1/index-family/overview`);
        const data = await response.json();
        
        if (data.success && data.data.indices) {
          // Merge with existing SYI-based SY100 if available
          const familyIndices = data.data.indices;
          
          // Only use family SY100 if we don't have new SYI calculation
          if (!indexData.SY100 && familyIndices.SY100) {
            indexData.SY100 = familyIndices.SY100;
          }
          
          // Add other indices (SY-CeFi, SY-DeFi, SY-RPI)
          ['SYCEFI', 'SYDEFI', 'SYRPI'].forEach(code => {
            if (familyIndices[code]) {
              indexData[code] = familyIndices[code];
            }
          });
        }
      } catch (familyError) {
        console.warn('Index Family system unavailable:', familyError);
      }
      
      // If we have at least one index, use it; otherwise fallback
      if (Object.keys(indexData).length > 0) {
        setIndices(indexData);
      } else {
        throw new Error('Both SYI and Index Family systems unavailable');
      }
      
      setError(null);
    } catch (err) {
      console.error('Error fetching index family:', err);
      setError(err.message);
      
      // Fallback to mock data with new SYI value
      setIndices({
        SY100: {
          index_code: 'SY100',
          value: 0.0447448, // Use new SYI expected value
          mode: 'Normal',
          constituent_count: 6,
          total_tvl: 127500000000,
          avg_yield: 0.0447448,
          confidence: 0.98,
          methodology_version: '2.0.0',
          is_syi_calculated: true
        },
        SYCEFI: {
          index_code: 'SYCEFI', 
          value: 0.0423,
          mode: 'Normal',
          constituent_count: 8,
          total_tvl: 2800000000,
          avg_yield: 0.0445,
          confidence: 1.0
        },
        SYDEFI: {
          index_code: 'SYDEFI',
          value: 0.0789,
          mode: 'Normal', 
          constituent_count: 12,
          total_tvl: 15600000000,
          avg_yield: 0.0823,
          confidence: 0.92
        },
        SYRPI: {
          index_code: 'SYRPI',
          value: 0.0162,
          mode: 'Normal',
          constituent_count: 6,
          avg_yield: 0.0687,
          confidence: 0.98
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const getIndexConfig = (indexCode) => {
    const configs = {
      SY100: {
        name: 'StableYield 100',
        description: 'Top 100 risk-adjusted stablecoin yield strategies',
        color: 'text-[#4CC1E9]',
        bgColor: 'bg-[#4CC1E9]/10',
        borderColor: 'border-[#4CC1E9]/20',
        icon: Target,
        methodology: 'Equal-risk weighting (inverse volatility)'
      },
      SYCEFI: {
        name: 'SY-CeFi Index',
        description: 'Centralized finance stablecoin yields benchmark', 
        color: 'text-[#2E6049]',
        bgColor: 'bg-[#2E6049]/10',
        borderColor: 'border-[#2E6049]/20',
        icon: Building2,
        methodology: 'Capacity-weighted by platform AUM'
      },
      SYDEFI: {
        name: 'SY-DeFi Index',
        description: 'Decentralized protocol yields benchmark',
        color: 'text-[#007A99]',
        bgColor: 'bg-[#007A99]/10', 
        borderColor: 'border-[#007A99]/20',
        icon: Layers,
        methodology: 'TVL-weighted by protocol maturity'
      },
      SYRPI: {
        name: 'Risk Premium Index',
        description: 'Stablecoin yield premium vs U.S. Treasury Bills',
        color: 'text-[#F59E0B]',
        bgColor: 'bg-[#F59E0B]/10',
        borderColor: 'border-[#F59E0B]/20', 
        icon: BarChart3,
        methodology: 'Average RAY minus 3M T-Bill rate'
      }
    };
    
    return configs[indexCode] || {
      name: indexCode,
      description: 'Index description',
      color: 'text-gray-600',
      bgColor: 'bg-gray-100',
      borderColor: 'border-gray-200',
      icon: Activity,
      methodology: 'Custom methodology'
    };
  };

  const formatValue = (value, indexCode) => {
    if (value === null || value === undefined) return 'N/A';
    
    if (indexCode === 'SYRPI') {
      // Risk Premium can be negative
      const percentage = (value * 100).toFixed(2);
      return `${value >= 0 ? '+' : ''}${percentage}bp`;
    } else {
      // Regular indices show as percentage
      return `${(value * 100).toFixed(2)}%`;
    }
  };

  const getPerformanceIcon = (value, indexCode) => {
    if (value === null || value === undefined) return <Minus className="w-4 h-4" />;
    
    if (indexCode === 'SYRPI') {
      // For RPI, positive is good (risk premium above T-Bills)
      if (value > 0) return <ArrowUpRight className="w-4 h-4 text-green-600" />;
      if (value < 0) return <ArrowDownRight className="w-4 h-4 text-red-600" />;
      return <Minus className="w-4 h-4 text-gray-500" />;
    } else {
      // For other indices, higher yields are generally positive
      return <ArrowUpRight className="w-4 h-4 text-green-600" />;
    }
  };

  const getModeColor = (mode) => {
    switch (mode) {
      case 'Normal': return 'bg-green-100 text-green-800';
      case 'Bear': return 'bg-yellow-100 text-yellow-800';
      case 'High-Vol': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-48 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[#0E1A2B]">StableYield Index Family</h2>
          <p className="text-gray-600">
            Comprehensive benchmark suite for stablecoin yield strategies
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          {['1D', '7D', '30D', '90D'].map((timeframe) => (
            <Button
              key={timeframe}
              variant={selectedTimeframe === timeframe ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedTimeframe(timeframe)}
            >
              {timeframe}
            </Button>
          ))}
        </div>
      </div>

      {/* Index Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Object.entries(indices).map(([indexCode, data]) => {
          const config = getIndexConfig(indexCode);
          const IconComponent = config.icon;
          
          return (
            <Card key={indexCode} className={`${config.borderColor} hover:shadow-lg transition-shadow`}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className={`p-2 rounded-lg ${config.bgColor}`}>
                    <IconComponent className={`w-5 h-5 ${config.color}`} />
                  </div>
                  <div className="flex flex-col space-y-1">
                    <Badge className={getModeColor(data.mode || 'Normal')}>
                      {data.mode || 'Normal'}
                    </Badge>
                    {data.is_syi_calculated && indexCode === 'SY100' && (
                      <Badge className="bg-blue-100 text-blue-800 text-xs">
                        SYI v{data.methodology_version}
                      </Badge>
                    )}
                  </div>
                </div>
                <CardTitle className="text-lg">{config.name}</CardTitle>
              </CardHeader>
              
              <CardContent>
                <div className="space-y-4">
                  {/* Value */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getPerformanceIcon(data.value, indexCode)}
                      <span className="text-2xl font-bold text-[#0E1A2B]">
                        {formatValue(data.value, indexCode)}
                      </span>
                    </div>
                  </div>
                  
                  {/* Description */}
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {config.description}
                  </p>
                  
                  {/* Metrics */}
                  <div className="space-y-2 pt-2 border-t border-gray-100">
                    {data.constituent_count && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">Constituents:</span>
                        <span className="font-medium">{data.constituent_count}</span>
                      </div>
                    )}
                    
                    {data.total_tvl && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">Total TVL:</span>
                        <span className="font-medium">
                          ${(data.total_tvl / 1_000_000_000).toFixed(1)}B
                        </span>
                      </div>
                    )}
                    
                    {data.confidence && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">Confidence:</span>
                        <span className="font-medium">
                          {(data.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                  </div>
                  
                  {/* Methodology */}
                  <div className="pt-2 border-t border-gray-100">
                    <p className="text-xs text-gray-500">
                      {config.methodology}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Family Summary */}
      <Card className="border-[#4CC1E9]/20 bg-gradient-to-br from-white to-[#4CC1E9]/5">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Activity className="w-5 h-5 mr-2 text-[#4CC1E9]" />
            Index Family Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-[#0E1A2B] mb-1">
                {Object.keys(indices).length}
              </div>
              <p className="text-sm text-gray-600">Active Indices</p>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-[#0E1A2B] mb-1">
                {Object.values(indices).reduce((sum, idx) => sum + (idx.constituent_count || 0), 0)}
              </div>
              <p className="text-sm text-gray-600">Total Constituents</p>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-[#0E1A2B] mb-1">
                ${(Object.values(indices).reduce((sum, idx) => sum + (idx.total_tvl || 0), 0) / 1_000_000_000).toFixed(1)}B
              </div>
              <p className="text-sm text-gray-600">Combined TVL</p>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-[#0E1A2B] mb-1">
                {(Object.values(indices).reduce((sum, idx) => sum + ((idx.confidence || 0) * 100), 0) / Object.keys(indices).length).toFixed(0)}%
              </div>
              <p className="text-sm text-gray-600">Avg Confidence</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="py-4">
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-yellow-600" />
              <div>
                <p className="text-sm text-yellow-800 font-medium">
                  Using demonstration data
                </p>
                <p className="text-xs text-yellow-600">
                  Backend API not available: {error}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default IndexFamilyOverview;