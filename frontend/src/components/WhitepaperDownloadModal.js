import React, { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { useToast } from "../hooks/use-toast";
import { X, Download, FileText, Mail, Building2, User, CheckCircle } from "lucide-react";

const WhitepaperDownloadModal = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company: "",
    jobTitle: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [downloadStarted, setDownloadStarted] = useState(false);
  const { toast } = useToast();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Send lead information to ec@hexelon.ch
      const leadData = {
        type: "whitepaper_download",
        timestamp: new Date().toISOString(),
        name: formData.name,
        email: formData.email,
        company: formData.company,
        jobTitle: formData.jobTitle,
        document: "StableYield Index (SYI) Whitepaper"
      };
      
      // Simulate API call - replace with actual endpoint
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      console.log("Whitepaper download lead sent to ec@hexelon.ch:", leadData);
      
      // Start the download
      const link = document.createElement('a');
      link.href = '/stableyield-whitepaper.pdf';
      link.download = 'StableYield-Index-Whitepaper.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setDownloadStarted(true);
      
      toast({
        title: "Download Started!",
        description: "The StableYield Index whitepaper is downloading. Thank you for your interest!",
      });
      
      // Reset form after successful submission
      setTimeout(() => {
        setFormData({
          name: "",
          email: "",
          company: "",
          jobTitle: ""
        });
        setDownloadStarted(false);
        onClose();
      }, 3000);
      
    } catch (error) {
      console.error("Error submitting download form:", error);
      toast({
        title: "Error",
        description: "Failed to process download request. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-[#4CC1E9] to-[#007A99] rounded-lg flex items-center justify-center">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-[#0E1A2B]">Download Whitepaper</h2>
                <p className="text-gray-600 text-sm">StableYield Index (SYI) - Technical Overview</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {!downloadStarted ? (
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            <div className="bg-gradient-to-r from-[#4CC1E9]/10 to-[#007A99]/10 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-[#0E1A2B] mb-2">What's Inside:</h3>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>• Institutional-grade benchmark methodology</li>
                <li>• Risk-adjusted yield calculation framework</li>
                <li>• EU BMR and IOSCO compliance overview</li>
                <li>• Technical architecture and data sources</li>
                <li>• Use cases for trading desks and fund managers</li>
              </ul>
            </div>

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
                  Job Title
                </label>
                <Input
                  type="text"
                  name="jobTitle"
                  value={formData.jobTitle}
                  onChange={handleInputChange}
                  placeholder="Portfolio Manager"
                  className="w-full"
                />
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
              <p>By downloading this whitepaper, you agree to receive occasional updates about StableYield Index developments. We respect your privacy and won't spam you.</p>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 pt-4">
              <Button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] text-white font-semibold py-3 rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Processing...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    Download Whitepaper
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
          </form>
        ) : (
          <div className="p-6 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-xl font-bold text-[#0E1A2B] mb-2">Download Started!</h3>
            <p className="text-gray-600 mb-4">
              The StableYield Index whitepaper is downloading to your device. 
              Thank you for your interest in institutional-grade stablecoin benchmarks!
            </p>
            <div className="bg-gradient-to-r from-[#4CC1E9]/10 to-[#007A99]/10 rounded-lg p-4">
              <p className="text-sm text-gray-700">
                We'll occasionally send you updates about StableYield developments. 
                For questions, contact us at <strong>ec@hexelon.ch</strong>
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WhitepaperDownloadModal;