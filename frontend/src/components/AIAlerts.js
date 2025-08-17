import React, { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Alert, AlertDescription } from "./ui/alert";
import { Bell, Plus, Trash2, AlertTriangle, CheckCircle, X } from "lucide-react";
import { useToast } from "../hooks/use-toast";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AIAlerts = ({ userEmail = "demo@stableyield.com" }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    stablecoin: "",
    condition: "",
    threshold: "",
    alert_type: "yield_threshold"
  });
  const [availableOptions, setAvailableOptions] = useState({
    conditions: [],
    stablecoins: []
  });
  const { toast } = useToast();

  useEffect(() => {
    if (isOpen) {
      fetchAlerts();
      fetchAvailableOptions();
    }
  }, [isOpen]);

  const fetchAlerts = async () => {
    try {
      const response = await axios.get(`${API}/ai/alerts/${userEmail}`);
      setAlerts(response.data.alerts || []);
    } catch (error) {
      console.error("Failed to fetch alerts:", error);
      toast({
        title: "Error",
        description: "Failed to load your alerts. Please try again.",
        variant: "destructive"
      });
    }
  };

  const fetchAvailableOptions = async () => {
    try {
      const response = await axios.get(`${API}/ai/alerts/conditions`);
      setAvailableOptions(response.data);
    } catch (error) {
      console.error("Failed to fetch options:", error);
    }
  };

  const handleCreateAlert = async (e) => {
    e.preventDefault();
    if (!formData.stablecoin || !formData.condition || !formData.threshold) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields.",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);
    try {
      const alertData = {
        user_email: userEmail,
        stablecoin: formData.stablecoin,
        condition: formData.condition,
        threshold: parseFloat(formData.threshold),
        alert_type: formData.alert_type
      };

      await axios.post(`${API}/ai/alerts`, alertData);
      
      toast({
        title: "Alert Created!",
        description: `You'll be notified when ${formData.stablecoin} yield ${formData.condition} ${formData.threshold}%`,
      });

      // Reset form and refresh alerts
      setFormData({
        stablecoin: "",
        condition: "",
        threshold: "",
        alert_type: "yield_threshold"
      });
      fetchAlerts();
      
    } catch (error) {
      console.error("Failed to create alert:", error);
      toast({
        title: "Error",
        description: "Failed to create alert. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAlert = async (alertId) => {
    try {
      await axios.delete(`${API}/ai/alerts/${alertId}?user_email=${userEmail}`);
      
      toast({
        title: "Alert Deleted",
        description: "Your alert has been removed.",
      });
      
      fetchAlerts();
      
    } catch (error) {
      console.error("Failed to delete alert:", error);
      toast({
        title: "Error",
        description: "Failed to delete alert. Please try again.",
        variant: "destructive"
      });
    }
  };

  const formatCondition = (condition) => {
    const conditionMap = {
      ">": "greater than",
      ">=": "greater than or equal to",
      "<": "less than",
      "<=": "less than or equal to",
      "=": "equal to"
    };
    return conditionMap[condition] || condition;
  };

  return (
    <>
      {/* Trigger Button */}
      <Button
        onClick={() => setIsOpen(true)}
        variant="outline"
        className="flex items-center space-x-2 hover:bg-[#4CC1E9]/10 hover:border-[#4CC1E9]"
      >
        <Bell className="w-4 h-4" />
        <span>Set AI Alert</span>
      </Button>

      {/* Alert Management Dialog */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Bell className="w-5 h-5 text-[#4CC1E9]" />
                <DialogTitle className="text-xl font-bold text-[#0E1A2B]">
                  AI Yield Alerts
                </DialogTitle>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsOpen(false)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
            <p className="text-sm text-gray-600">
              Get notified when stablecoin yields meet your conditions
            </p>
          </DialogHeader>

          <div className="space-y-6">
            {/* Create New Alert */}
            <div className="border rounded-lg p-4 bg-gray-50">
              <h3 className="font-semibold text-[#0E1A2B] mb-4 flex items-center">
                <Plus className="w-4 h-4 mr-2" />
                Create New Alert
              </h3>
              
              <form onSubmit={handleCreateAlert} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="stablecoin">Stablecoin</Label>
                    <Select
                      value={formData.stablecoin}
                      onValueChange={(value) => setFormData(prev => ({ ...prev, stablecoin: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select coin" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableOptions.stablecoins.map((coin) => (
                          <SelectItem key={coin} value={coin}>
                            {coin}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="condition">Condition</Label>
                    <Select
                      value={formData.condition}
                      onValueChange={(value) => setFormData(prev => ({ ...prev, condition: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select condition" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableOptions.conditions.map((cond) => (
                          <SelectItem key={cond.value} value={cond.value}>
                            {cond.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="threshold">Yield %</Label>
                    <Input
                      id="threshold"
                      type="number"
                      step="0.01"
                      min="0"
                      max="50"
                      placeholder="e.g., 8.5"
                      value={formData.threshold}
                      onChange={(e) => setFormData(prev => ({ ...prev, threshold: e.target.value }))}
                    />
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={isLoading}
                  className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] text-white w-full"
                >
                  {isLoading ? "Creating..." : "Create Alert"}
                </Button>
              </form>
            </div>

            {/* Existing Alerts */}
            <div>
              <h3 className="font-semibold text-[#0E1A2B] mb-4">Your Active Alerts</h3>
              
              {alerts.length === 0 ? (
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    No alerts configured yet. Create your first alert above to get notified about yield changes.
                  </AlertDescription>
                </Alert>
              ) : (
                <div className="space-y-3">
                  {alerts.map((alert) => (
                    <div
                      key={alert.id}
                      className="flex items-center justify-between p-4 border rounded-lg bg-white hover:bg-gray-50"
                    >
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-semibold text-[#0E1A2B]">
                            {alert.stablecoin}
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            alert.is_active 
                              ? "bg-green-100 text-green-700" 
                              : "bg-gray-100 text-gray-700"
                          }`}>
                            {alert.is_active ? "Active" : "Inactive"}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600">
                          Notify when yield is <strong>{formatCondition(alert.condition)} {alert.threshold}%</strong>
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          Created {new Date(alert.created_at).toLocaleDateString()}
                          {alert.last_triggered && (
                            <span> • Last triggered {new Date(alert.last_triggered).toLocaleDateString()}</span>
                          )}
                        </p>
                      </div>
                      
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteAlert(alert.id)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Info Section */}
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                <strong>How it works:</strong> Our AI monitors yield data every hour and sends email notifications when your conditions are met. 
                All alerts include disclaimers that this is simulation data for informational purposes only.
              </AlertDescription>
            </Alert>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default AIAlerts;