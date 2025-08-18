import React, { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { useToast } from "../hooks/use-toast";
import { X, Mail, User, MessageSquare, Building2, Phone } from "lucide-react";

const ContactModal = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company: "",
    phone: "",
    subject: "",
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
      // Simulate API call - replace with actual endpoint
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log("Contact form submitted:", formData);
      
      toast({
        title: "Message Sent!",
        description: "Thank you for your interest. We'll get back to you within 24 hours.",
      });
      
      // Reset form
      setFormData({
        name: "",
        email: "",
        company: "",
        phone: "",
        subject: "",
        message: ""
      });
      
      onClose();
      
    } catch (error) {
      console.error("Error submitting contact form:", error);
      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-[#0E1A2B]">Contact StableYield</h2>
              <p className="text-gray-600 mt-1">Get in touch with our team for institutional access</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Name and Email Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <User className="w-4 h-4 inline mr-2" />
                Full Name *
              </label>
              <Input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                placeholder="John Doe"
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Mail className="w-4 h-4 inline mr-2" />
                Email Address *
              </label>
              <Input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                placeholder="john@company.com"
                className="w-full"
              />
            </div>
          </div>

          {/* Company and Phone Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Building2 className="w-4 h-4 inline mr-2" />
                Company
              </label>
              <Input
                type="text"
                name="company"
                value={formData.company}
                onChange={handleInputChange}
                placeholder="Your Company"
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Phone className="w-4 h-4 inline mr-2" />
                Phone Number
              </label>
              <Input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="+1 (555) 123-4567"
                className="w-full"
              />
            </div>
          </div>

          {/* Subject */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <MessageSquare className="w-4 h-4 inline mr-2" />
              Subject *
            </label>
            <select
              name="subject"
              value={formData.subject}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#4CC1E9] focus:border-transparent"
            >
              <option value="">Select a subject</option>
              <option value="institutional_access">Institutional Access</option>
              <option value="api_integration">API Integration</option>
              <option value="data_licensing">Data Licensing</option>
              <option value="partnership">Partnership Opportunity</option>
              <option value="media_inquiry">Media Inquiry</option>
              <option value="technical_support">Technical Support</option>
              <option value="general_inquiry">General Inquiry</option>
            </select>
          </div>

          {/* Message */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Message *
            </label>
            <Textarea
              name="message"
              value={formData.message}
              onChange={handleInputChange}
              required
              rows={4}
              placeholder="Tell us about your use case, requirements, or questions..."
              className="w-full resize-none"
            />
          </div>

          {/* Contact Preferences */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">What best describes you?</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <label className="flex items-center">
                <input type="radio" name="user_type" value="institutional_investor" className="mr-2" />
                Institutional Investor
              </label>
              <label className="flex items-center">
                <input type="radio" name="user_type" value="fund_manager" className="mr-2" />
                Fund Manager
              </label>
              <label className="flex items-center">
                <input type="radio" name="user_type" value="trader" className="mr-2" />
                Professional Trader
              </label>
              <label className="flex items-center">
                <input type="radio" name="user_type" value="developer" className="mr-2" />
                Developer/Integrator
              </label>
              <label className="flex items-center">
                <input type="radio" name="user_type" value="researcher" className="mr-2" />
                Researcher/Analyst
              </label>
              <label className="flex items-center">
                <input type="radio" name="user_type" value="media" className="mr-2" />
                Media/Press
              </label>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4">
            <Button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] text-white font-semibold py-3 rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Sending...
                </>
              ) : (
                <>
                  <Mail className="w-4 h-4 mr-2" />
                  Send Message
                </>
              )}
            </Button>
            <Button
              type="button"
              onClick={onClose}
              variant="outline"
              className="flex-1 sm:flex-none border-gray-300 text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </Button>
          </div>

          {/* Contact Information */}
          <div className="bg-gradient-to-r from-[#4CC1E9]/10 to-[#007A99]/10 rounded-lg p-4 mt-6">
            <h4 className="font-medium text-[#0E1A2B] mb-2">Need immediate assistance?</h4>
            <div className="text-sm text-gray-600 space-y-1">
              <p>📧 Email: contact@stableyield.com</p>
              <p>📞 Phone: +1 (555) STABLE-1</p>
              <p>🕒 Business Hours: Monday - Friday, 9 AM - 6 PM EST</p>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ContactModal;