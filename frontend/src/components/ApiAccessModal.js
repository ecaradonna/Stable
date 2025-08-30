import React, { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { useToast } from "../hooks/use-toast";
import { X, Mail, User, Building2, Phone, Code, DollarSign, TrendingUp } from "lucide-react";

const ApiAccessModal = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company: "",
    phone: "",
    useCase: "",
    tradingVolume: "",
    message: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Send API access request email
      const emailData = {
        to: "ec@hexelon.ch",
        subject: `StableYield API Access Request - ${formData.company}`,
        name: formData.name,
        email: formData.email,
        company: formData.company,
        phone: formData.phone,
        useCase: formData.useCase,
        tradingVolume: formData.tradingVolume,
        message: formData.message,
        timestamp: new Date().toISOString(),
        type: "API_ACCESS_REQUEST"
      };
      
      // Simulate API call - replace with actual endpoint
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log("API Access request submitted to ec@hexelon.ch:", emailData);
      
      toast({
        title: "API Access Request Submitted!",
        description: "We'll review your request and send you API credentials within 24-48 hours.",
      });

      // Reset form
      setFormData({
        name: "",
        email: "",
        company: "",
        phone: "",
        useCase: "",
        tradingVolume: "",
        message: ""
      });
      
      onClose();
    } catch (error) {
      console.error("Error submitting API access request:", error);
      toast({
        title: "Error",
        description: "Failed to submit request. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999] p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-[#1F4FFF] to-[#4CC1E9] text-white p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">Request API Access</h2>
              <p className="text-blue-100 mt-1">Get institutional-grade stablecoin market data</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* API Plans */}
        <div className="p-6 bg-gray-50 border-b">
          <h3 className="font-semibold text-gray-900 mb-3">Available API Plans</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="flex items-center mb-2">
                <TrendingUp className="w-5 h-5 text-[#1F4FFF] mr-2" />
                <span className="font-semibold text-[#1F4FFF]">Pro Trader Plan</span>
              </div>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Real-time yield data</li>
                <li>• Risk-adjusted metrics</li>
                <li>• 10,000 calls/month</li>
                <li>• Email support</li>
              </ul>
            </div>
            <div className="bg-white p-4 rounded-lg border border-[#E47C3C]">
              <div className="flex items-center mb-2">
                <DollarSign className="w-5 h-5 text-[#E47C3C] mr-2" />
                <span className="font-semibold text-[#E47C3C]">Enterprise</span>
              </div>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Unlimited API calls</li>
                <li>• Custom integrations</li>
                <li>• Historical data access</li>
                <li>• Priority support</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <User className="w-4 h-4 inline mr-1" />
                Full Name *
              </label>
              <Input
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="John Smith"
                required
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Mail className="w-4 h-4 inline mr-1" />
                Email Address *
              </label>
              <Input
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="john@company.com"
                required
                className="w-full"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Building2 className="w-4 h-4 inline mr-1" />
                Company *
              </label>
              <Input
                name="company"
                value={formData.company}
                onChange={handleInputChange}
                placeholder="Hedge Fund XYZ"
                required
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Phone className="w-4 h-4 inline mr-1" />
                Phone Number
              </label>
              <Input
                name="phone"
                type="tel"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="+1 (555) 123-4567"
                className="w-full"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Code className="w-4 h-4 inline mr-1" />
              Primary Use Case *
            </label>
            <select
              name="useCase"
              value={formData.useCase}
              onChange={handleInputChange}
              required
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#1F4FFF] focus:border-transparent"
            >
              <option value="">Select your use case</option>
              <option value="trading">Algorithmic Trading</option>
              <option value="research">Investment Research</option>
              <option value="risk_management">Risk Management</option>
              <option value="portfolio_analytics">Portfolio Analytics</option>
              <option value="market_making">Market Making</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <TrendingUp className="w-4 h-4 inline mr-1" />
              Monthly Trading Volume (USD)
            </label>
            <select
              name="tradingVolume"
              value={formData.tradingVolume}
              onChange={handleInputChange}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#1F4FFF] focus:border-transparent"
            >
              <option value="">Select volume range</option>
              <option value="under_1m">Under $1M</option>
              <option value="1m_10m">$1M - $10M</option>
              <option value="10m_100m">$10M - $100M</option>
              <option value="100m_1b">$100M - $1B</option>
              <option value="over_1b">Over $1B</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Additional Requirements
            </label>
            <Textarea
              name="message"
              value={formData.message}
              onChange={handleInputChange}
              placeholder="Tell us about your specific data requirements, integration needs, or any questions you have about our API..."
              rows={4}
              className="w-full"
            />
          </div>

          <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 pt-4">
            <Button
              type="submit"
              disabled={isSubmitting}
              className="bg-[#E47C3C] hover:bg-[#E47C3C]/90 text-white flex-1"
            >
              {isSubmitting ? "Submitting..." : "Submit API Request"}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="border-gray-300 text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </Button>
          </div>

          <div className="text-xs text-gray-500 mt-4 p-4 bg-gray-50 rounded-lg">
            <strong>Next Steps:</strong> We'll review your request within 24-48 hours and send you API credentials, documentation, and pricing details. For immediate assistance, contact us at{" "}
            <a href="mailto:ec@hexelon.ch" className="text-[#1F4FFF] hover:underline">
              ec@hexelon.ch
            </a>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ApiAccessModal;