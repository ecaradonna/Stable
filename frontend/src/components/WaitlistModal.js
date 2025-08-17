import React, { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { X, CheckCircle } from "lucide-react";
import { useToast } from "../hooks/use-toast";

const WaitlistModal = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    interest: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const { toast } = useToast();

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Store in localStorage (mock database)
    const existingSignups = JSON.parse(localStorage.getItem('waitlistSignups') || '[]');
    const newSignup = {
      ...formData,
      id: Date.now(),
      timestamp: new Date().toISOString()
    };
    existingSignups.push(newSignup);
    localStorage.setItem('waitlistSignups', JSON.stringify(existingSignups));

    setIsSubmitting(false);
    setIsSuccess(true);
    
    toast({
      title: "Successfully joined!",
      description: "Welcome to StableYield waitlist. We'll notify you when we launch.",
    });

    // Reset form after 2 seconds
    setTimeout(() => {
      setIsSuccess(false);
      setFormData({ name: "", email: "", interest: "" });
      onClose();
    }, 2000);
  };

  const isFormValid = formData.name && formData.email && formData.interest;

  if (isSuccess) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="sm:max-w-md">
          <div className="text-center py-8">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-[#0E1A2B] mb-2">Welcome aboard!</h3>
            <p className="text-gray-600 mb-4">
              You're now on the StableYield waitlist. We'll email you as soon as we launch.
            </p>
            <div className="bg-gradient-to-r from-[#4CC1E9]/10 to-[#007A99]/10 rounded-lg p-4">
              <p className="text-sm text-[#0E1A2B]">
                <strong>What's next?</strong><br />
                Get ready for transparent stablecoin yield data, real-time alerts, and institutional-grade analytics.
              </p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-[#0E1A2B] mb-2">
            Join StableYield Waitlist
          </DialogTitle>
          <p className="text-gray-600">
            Be the first to access transparent stablecoin yield data when we launch.
          </p>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 mt-6">
          <div className="space-y-2">
            <Label htmlFor="name" className="text-[#0E1A2B] font-medium">
              Full Name
            </Label>
            <Input
              id="name"
              type="text"
              placeholder="Enter your full name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              className="border-gray-300 focus:border-[#4CC1E9] focus:ring-[#4CC1E9]"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email" className="text-[#0E1A2B] font-medium">
              Email Address
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="Enter your email address"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              className="border-gray-300 focus:border-[#4CC1E9] focus:ring-[#4CC1E9]"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="interest" className="text-[#0E1A2B] font-medium">
              I'm a...
            </Label>
            <Select onValueChange={(value) => handleInputChange('interest', value)}>
              <SelectTrigger className="border-gray-300 focus:border-[#4CC1E9] focus:ring-[#4CC1E9]">
                <SelectValue placeholder="Select your role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="trader">Trader</SelectItem>
                <SelectItem value="investor">Investor</SelectItem>
                <SelectItem value="institution">Institution</SelectItem>
                <SelectItem value="media">Media</SelectItem>
                <SelectItem value="developer">Developer</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="bg-[#4CC1E9]/5 rounded-lg p-4 border border-[#4CC1E9]/20">
            <h4 className="font-semibold text-[#0E1A2B] mb-2">What you'll get:</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Early access to our yield dashboard</li>
              <li>• Weekly StableYield reports via email</li>
              <li>• Real-time yield alerts and notifications</li>
              <li>• Exclusive insights and market analysis</li>
            </ul>
          </div>

          <div className="flex space-x-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1"
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={!isFormValid || isSubmitting}
              className="flex-1 bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] text-white font-semibold"
            >
              {isSubmitting ? "Joining..." : "Join Waitlist"}
            </Button>
          </div>
        </form>

        <p className="text-xs text-gray-500 text-center mt-4">
          We respect your privacy. No spam, unsubscribe anytime.
        </p>
      </DialogContent>
    </Dialog>
  );
};

export default WaitlistModal;