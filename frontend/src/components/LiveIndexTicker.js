import React, { useState, useEffect } from 'react';
import { TrendingUp, Activity, AlertCircle } from 'lucide-react';

const LiveIndexTicker = () => {
  const [indexData, setIndexData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchIndexData = async () => {
    try {
      const backendUrl = 'http://localhost:8001';  // Use localhost for local development
      const response = await fetch(`${backendUrl}/api/index/live`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch index data');
      }
      
      const data = await response.json();
      setIndexData(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching index data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchIndexData();
    
    // Set up polling every 30 seconds (for demo, in production use WebSocket)
    const interval = setInterval(fetchIndexData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'live': return 'text-green-500';
      case 'stale': return 'text-yellow-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'live': return <Activity className="w-4 h-4" />;
      case 'stale': return <AlertCircle className="w-4 h-4" />;
      default: return <TrendingUp className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="bg-gradient-to-r from-[#4CC1E9]/10 to-[#007A99]/10 rounded-lg p-4 border border-[#4CC1E9]/20">
        <div className="flex items-center space-x-3">
          <div className="animate-pulse">
            <TrendingUp className="w-5 h-5 text-[#4CC1E9]" />
          </div>
          <div>
            <div className="text-sm text-gray-500">StableYield Index</div>
            <div className="text-lg font-bold text-[#0E1A2B]">Loading...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 rounded-lg p-4 border border-red-200">
        <div className="flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-red-500" />
          <div>
            <div className="text-sm text-red-600">StableYield Index</div>
            <div className="text-lg font-bold text-red-700">Error loading data</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-[#4CC1E9]/10 to-[#007A99]/10 rounded-lg p-4 border border-[#4CC1E9]/20">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className={getStatusColor(indexData.status)}>
            {getStatusIcon(indexData.status)}
          </div>
          
          <div>
            <div className="text-sm text-gray-600">StableYield Index (SYI)</div>
            <div className="text-2xl font-bold text-[#0E1A2B]">
              {indexData.value.toFixed(4)}%
            </div>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-xs text-gray-500">
            {indexData.constituents_count} assets
          </div>
          <div className="text-xs text-gray-500">
            Updated {Math.floor(indexData.last_update_seconds / 60)}m ago
          </div>
          <div className={`text-xs font-medium ${getStatusColor(indexData.status)}`}>
            {indexData.status.toUpperCase()}
          </div>
        </div>
      </div>
      
      {/* TODO: PRODUCTION UPGRADE NEEDED */}
      <div className="mt-2 text-xs text-gray-400">
        📍 Demo data - Upgrade to production APIs for real-time accuracy
      </div>
    </div>
  );
};

export default LiveIndexTicker;