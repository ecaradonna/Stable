import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Activity, 
  BarChart3,
  Shield,
  Zap,
  RefreshCw
} from 'lucide-react';

const RiskRegimeWidget = ({ onCreateAlert }) => {
  const [regimeData, setRegimeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchRegimeData = async () => {
    setLoading(true);
    try {
      const getBackendURL = () => {
        const envBackendUrl = process.env.REACT_APP_BACKEND_URL || import.meta?.env?.REACT_APP_BACKEND_URL;
        if (envBackendUrl) {
          return envBackendUrl;
        }
        if (window.location.hostname === 'localhost') {
          if (window.location.hostname === 'localhost') {
          return 'http://localhost:8001';
        }
        // Always use environment variable if available for production
        const envBackendUrl = process.env.REACT_APP_BACKEND_URL || import.meta?.env?.REACT_APP_BACKEND_URL;
        if (envBackendUrl) {
          return envBackendUrl;
        }
        // Use same protocol and hostname as current page
        const protocol = window.location.protocol === 'https:' ? 'https:' : window.location.protocol;
        const hostname = window.location.hostname;
        return `${protocol}//${hostname}`;
        }
        const protocol = window.location.protocol === 'https:' ? 'https:' : window.location.protocol;
        const hostname = window.location.hostname;
        return `${protocol}//${hostname}`;
      };

      const backendUrl = getBackendURL();
      
      // Try to get current regime status
      const response = await fetch(`${backendUrl}/api/regime/current`);
      const data = await response.json();
      
      if (response.ok) {
        setRegimeData(data);
        setLastUpdate(new Date().toLocaleTimeString());
        setError(null);
      } else {
        throw new Error(data.detail || 'Failed to fetch regime data');
      }
    } catch (err) {
      console.error('Error fetching regime data:', err);
      setError(err.message);
      
      // Fallback to mock data for demonstration
      setRegimeData({
        state: "NEU",
        syi_excess: -0.0085,
        z_score: -0.42,
        spread: -0.0012,
        slope7: -0.0008,
        breadth_pct: 35,
        message: "Demo regime data - service initializing"
      });
      setLastUpdate(new Date().toLocaleTimeString());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchRegimeData();
    
    // Set up polling every 5 minutes for regime updates
    const interval = setInterval(fetchRegimeData, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  const getRegimeConfig = (state) => {
    const configs = {
      ON: {
        name: 'Risk-On',
        color: 'text-green-600',
        bgColor: 'bg-green-100',
        borderColor: 'border-green-300',
        icon: TrendingUp,
        description: 'Favorable risk conditions for stablecoin yields',
        badgeColor: 'bg-green-100 text-green-800'
      },
      OFF: {
        name: 'Risk-Off',
        color: 'text-red-600',
        bgColor: 'bg-red-100',
        borderColor: 'border-red-300',
        icon: TrendingDown,
        description: 'Defensive regime - elevated risk conditions',
        badgeColor: 'bg-red-100 text-red-800'
      },
      OFF_OVERRIDE: {
        name: 'Risk-Off Override',
        color: 'text-orange-600',
        bgColor: 'bg-orange-100',
        borderColor: 'border-orange-300',
        icon: AlertTriangle,
        description: 'Forced Risk-Off due to peg stress conditions',
        badgeColor: 'bg-orange-100 text-orange-800'
      },
      NEU: {
        name: 'Neutral',
        color: 'text-gray-600',
        bgColor: 'bg-gray-100',
        borderColor: 'border-gray-300',
        icon: Activity,
        description: 'Initializing or no clear regime signal',
        badgeColor: 'bg-gray-100 text-gray-800'
      }
    };
    
    return configs[state] || configs.NEU;
  };

  const formatValue = (value, type) => {
    if (value === null || value === undefined) return 'N/A';
    
    switch (type) {
      case 'percent':
        return `${(value * 100).toFixed(2)}%`;
      case 'bps':
        return `${(value * 10000).toFixed(0)}bps`;
      case 'z_score':
        return value.toFixed(2);
      case 'breadth':
        return `${value.toFixed(0)}%`;
      default:
        return value.toFixed(4);
    }
  };

  const config = regimeData ? getRegimeConfig(regimeData.state) : getRegimeConfig('NEU');
  const IconComponent = config.icon;

  if (loading) {
    return (
      <Card className="border-gray-200 hover:shadow-lg transition-shadow">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="p-2 rounded-lg bg-gray-100">
              <Activity className="w-5 h-5 text-gray-600 animate-pulse" />
            </div>
            <Badge className="bg-gray-100 text-gray-800">Loading...</Badge>
          </div>
          <CardTitle className="text-lg">Risk Regime Detection</CardTitle>
        </CardHeader>
        
        <CardContent>
          <div className="space-y-4">
            <div className="text-center text-gray-500">
              <div className="animate-pulse">Loading regime data...</div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`${config.borderColor} hover:shadow-lg transition-shadow`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className={`p-2 rounded-lg ${config.bgColor}`}>
            <IconComponent className={`w-5 h-5 ${config.color}`} />
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={config.badgeColor}>
              {config.name}
            </Badge>
            <Button
              variant="ghost"
              size="sm"
              onClick={fetchRegimeData}
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>
        <CardTitle className="text-lg">Risk Regime Detection</CardTitle>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-4">
          {/* Main Status */}
          <div className="text-center">
            <div className={`text-2xl font-bold ${config.color}`}>
              {config.name}
            </div>
            <p className="text-sm text-gray-600 mt-1">
              {config.description}
            </p>
          </div>
          
          {/* Key Indicators */}
          <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-100">
            <div className="text-center">
              <div className="text-xs text-gray-500">SYI Excess</div>
              <div className={`font-semibold ${regimeData.syi_excess >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatValue(regimeData.syi_excess, 'bps')}
              </div>
            </div>
            
            <div className="text-center">
              <div className="text-xs text-gray-500">Z-Score</div>
              <div className={`font-semibold ${regimeData.z_score >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                {formatValue(regimeData.z_score, 'z_score')}
              </div>
            </div>
            
            <div className="text-center">
              <div className="text-xs text-gray-500">Momentum</div>
              <div className={`font-semibold ${regimeData.slope7 >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatValue(regimeData.slope7, 'bps')}
              </div>
            </div>
            
            <div className="text-center">
              <div className="text-xs text-gray-500">Breadth</div>
              <div className={`font-semibold ${regimeData.breadth_pct >= 50 ? 'text-green-600' : 'text-red-600'}`}>
                {formatValue(regimeData.breadth_pct, 'breadth')}
              </div>
            </div>
          </div>
          
          {/* Alert Information */}
          {regimeData.alert_type && (
            <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-yellow-600" />
                <span className="text-sm font-medium text-yellow-800">
                  {regimeData.alert_type}
                </span>
              </div>
            </div>
          )}
          
          {/* Create Alert Button */}
          {onCreateAlert && (
            <div className="mt-3 text-center">
              <Button 
                variant="outline" 
                size="sm"
                onClick={onCreateAlert}
                className="text-xs px-4 py-2 h-8"
              >
                Create Alert
              </Button>
            </div>
          )}
          
          {/* Last Update */}
          <div className="text-xs text-gray-400 text-center">
            📊 Regime Analysis • Updated: {lastUpdate}
            {error && <div className="text-red-500 mt-1">⚠️ {error}</div>}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default RiskRegimeWidget;