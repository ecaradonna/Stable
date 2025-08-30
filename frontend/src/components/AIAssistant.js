import React, { useState, useEffect, useRef } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { 
  MessageCircle, 
  Send, 
  X, 
  Sparkles,
  Bot,
  User,
  Loader2,
  AlertCircle,
  TrendingUp,
  Shield,
  Bell
} from 'lucide-react';
import { aiApi } from '../services/api';

const AIAssistant = ({ className = "", onAnalyticsEvent }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [showProactiveToast, setShowProactiveToast] = useState(false);
  const [hasShownToast, setHasShownToast] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Proactive nudge logic
  useEffect(() => {
    // Show proactive toast once per session on specific pages
    const currentPath = window.location.pathname;
    const shouldShowToast = ['/index-dashboard', '/api-documentation', '/'].includes(currentPath);
    const hasToastShown = sessionStorage.getItem('sy-ai-toast-shown');
    
    if (shouldShowToast && !hasToastShown && !hasShownToast && window.innerWidth > 768) {
      const timer = setTimeout(() => {
        setShowProactiveToast(true);
        setHasShownToast(true);
        sessionStorage.setItem('sy-ai-toast-shown', 'true');
        
        // Auto-hide after 5s
        setTimeout(() => setShowProactiveToast(false), 5000);
        
        // Analytics
        onAnalyticsEvent?.('bot_proactive_nudge_shown', { page: currentPath });
      }, 6000);
      
      return () => clearTimeout(timer);
    }
  }, [hasShownToast, onAnalyticsEvent]);

  // Initialize welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([{
        id: 'welcome',
        type: 'ai',
        text: "👋 Hi, I'm StableYield AI. I can help with stablecoin yields, benchmarks (SYI), peg stability, and Risk ON/OFF signals.",
        timestamp: new Date().toISOString(),
        isError: false
      }]);
    }
  }, [messages.length]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const quickPrompts = [
    "What is the StableYield Index (SYI)?",
    "How does SYI help me manage risk?", 
    "What advantage does it give traders?",
    "Can I receive automatic alerts?",
    "What's the advantage over DeFiLlama?",
    "How can I access the data?"
  ];

  const handleSendMessage = async (messageText) => {
    const message = messageText || currentMessage.trim();
    if (!message) return;

    // Analytics
    onAnalyticsEvent?.('bot_message_send', { 
      session_id: sessionId,
      message_type: messageText ? 'quick_prompt' : 'manual',
      message_preview: message.substring(0, 50)
    });

    setIsLoading(true);
    setCurrentMessage("");

    // Add user message
    const userMessage = {
      id: `user_${Date.now()}`,
      type: 'user',
      text: message,
      timestamp: new Date().toISOString(),
      isError: false
    };
    
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await aiApi.chat({
        message,
        session_id: sessionId
      });

      // Add AI response
      const aiMessage = {
        id: response.message_id || `ai_${Date.now()}`,
        type: 'ai',
        text: response.response,
        timestamp: new Date().toISOString(),
        isError: false
      };
      
      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      console.error('AI chat error:', error);
      
      // Add error message
      const errorMessage = {
        id: `error_${Date.now()}`,
        type: 'ai',
        text: "I apologize, but I'm experiencing technical difficulties. Please try again later or contact support for assistance.\n\n⚠️ *AI responses are for informational purposes only and do not constitute financial advice.*",
        timestamp: new Date().toISOString(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickPromptClick = (prompt) => {
    onAnalyticsEvent?.('bot_quick_prompt_click', { prompt });
    handleSendMessage(prompt);
  };

  const handleOpen = () => {
    setIsOpen(true);
    onAnalyticsEvent?.('bot_open', { session_id: sessionId });
    
    // Hide toast if shown
    setShowProactiveToast(false);
  };

  const handleClose = () => {
    setIsOpen(false);
    onAnalyticsEvent?.('bot_close', { session_id: sessionId });
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <>
      {/* Proactive Toast */}
      {showProactiveToast && (
        <div className="sy-proactive-toast fixed right-24 bottom-28 bg-white border border-[#E5E7EB] rounded-lg shadow-lg p-3 max-w-xs z-[9998] animate-in slide-in-from-right-5 fade-in duration-300">
          <div className="flex items-start space-x-2">
            <div className="w-6 h-6 bg-[#1F4FFF] rounded-full flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-3 h-3 text-white" />
            </div>
            <div>
              <p className="text-sm font-medium text-[#1A1A1A] mb-1">New: Risk ON/OFF alerts</p>
              <p className="text-xs text-[#6B7280]">Ask me to activate.</p>
            </div>
            <button 
              onClick={() => setShowProactiveToast(false)}
              className="text-[#9FA6B2] hover:text-[#6B7280]"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Floating Launcher */}
      <div className="fixed right-6 bottom-6 z-[9999]">
        {/* Live Badge */}
        <div className="absolute -top-2 -right-2 bg-white bg-opacity-90 border border-[#E5E7EB] rounded-full px-2 py-1 shadow-sm">
          <span className="text-[10px] font-semibold text-[#1F4FFF]">AI</span>
        </div>
        
        {/* Launcher Button */}
        <button
          onClick={handleOpen}
          className="w-14 h-14 rounded-full bg-[#1F4FFF] hover:bg-[#1B44E6] text-white shadow-[0_10px_24px_rgba(0,0,0,0.15)] hover:shadow-[0_12px_28px_rgba(0,0,0,0.2)] transition-all duration-200 hover:-translate-y-0.5 flex items-center justify-center cursor-pointer"
          aria-label="Open StableYield AI Assistant"
          type="button"
        >
          <MessageCircle className="h-6 w-6" />
        </button>
      </div>

      {/* AI Panel Dialog */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="fixed right-6 bottom-24 w-full max-w-[420px] max-h-[70vh] p-0 border border-[#E5E7EB] rounded-xl shadow-[0_10px_30px_rgba(0,0,0,0.08)] bg-white overflow-hidden data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 md:right-6 md:bottom-24 md:w-[420px] sm:max-w-[420px]">
          
          {/* Header */}
          <DialogHeader className="flex-row items-center justify-between p-4 border-b border-[#E5E7EB] bg-[#F9FAFB]">
            <div className="flex-1">
              <DialogTitle className="text-sm font-semibold text-[#1A1A1A] flex items-center space-x-2">
                <div className="w-6 h-6 bg-[#1F4FFF] rounded-full flex items-center justify-center">
                  <Sparkles className="w-3 h-3 text-white" />
                </div>
                <span>StableYield AI</span>
              </DialogTitle>
              <p className="text-xs text-[#6B7280] mt-0.5">Institutional Market Assistant</p>
            </div>
            
            {/* Header CTAs */}
            <div className="flex items-center space-x-2 ml-4">
              <Button
                variant="outline"
                size="sm"
                className="text-xs border-[#1F4FFF] text-[#1F4FFF] hover:bg-[#1F4FFF] hover:text-white h-7 px-2"
                onClick={() => {
                  onAnalyticsEvent?.('bot_alert_subscribe_click');
                  window.location.href = '/risk-analytics';
                }}
              >
                <Bell className="w-3 h-3 mr-1" />
                Alerts
              </Button>
              
              <Button
                size="sm"
                className="text-xs bg-[#E47C3C] hover:bg-[#E47C3C]/90 text-white h-7 px-2"
                onClick={() => {
                  onAnalyticsEvent?.('bot_api_cta_click');
                  window.location.href = '/api-documentation';
                }}
              >
                API Access
              </Button>
              
              <button
                onClick={() => setIsOpen(false)}
                className="text-[#9FA6B2] hover:text-[#6B7280] p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </DialogHeader>

          {/* Messages Area */}
          <div className="flex flex-col h-[calc(70vh-140px)] max-h-96">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`flex items-start space-x-2 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    
                    {/* Avatar */}
                    <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.type === "user"
                        ? "bg-[#E47C3C]"
                        : message.isError
                        ? "bg-red-500"
                        : "bg-[#1F4FFF]"
                    }`}>
                      {message.type === "user" ? (
                        <User className="w-4 h-4 text-white" />
                      ) : (
                        <Bot className="w-4 h-4 text-white" />
                      )}
                    </div>

                    {/* Message Bubble */}
                    <div className={`rounded-lg p-3 ${
                      message.type === "user"
                        ? "bg-[#E47C3C] text-white"
                        : message.isError
                        ? "bg-red-50 text-red-700 border border-red-200"
                        : "bg-[#F9FAFB] text-[#1A1A1A] border border-[#E5E7EB]"
                    }`}>
                      <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                      <p className="text-xs mt-1 opacity-70">
                        {new Date(message.timestamp).toLocaleTimeString('en-US', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                  </div>
                </div>
              ))}

              {/* Loading State */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-2">
                    <div className="w-7 h-7 bg-[#1F4FFF] rounded-full flex items-center justify-center">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <div className="bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg p-3">
                      <div className="flex items-center space-x-2">
                        <Loader2 className="w-4 h-4 animate-spin text-[#1F4FFF]" />
                        <span className="text-sm text-[#6B7280]">Analyzing market data...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Quick Prompts */}
            <div className="p-3 border-t border-[#E5E7EB] bg-[#F9FAFB]">
              <div className="text-xs font-medium text-[#6B7280] mb-2">Try asking:</div>
              <div className="grid grid-cols-2 gap-2">
                {quickPrompts.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickPromptClick(prompt)}
                    className="text-left text-xs p-2 bg-white rounded-lg border border-[#E5E7EB] hover:border-[#1F4FFF] hover:text-[#1F4FFF] hover:bg-[#1F4FFF]/5 transition-all duration-150 font-medium"
                    disabled={isLoading}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-[#E5E7EB] bg-white">
              <div className="flex space-x-2">
                <Input
                  ref={inputRef}
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me about stablecoin yields..."
                  className="flex-1 text-sm border-[#E5E7EB] focus:border-[#1F4FFF] focus:ring-[#1F4FFF]"
                  disabled={isLoading}
                />
                <Button
                  onClick={() => handleSendMessage()}
                  disabled={!currentMessage.trim() || isLoading}
                  className="bg-[#E47C3C] hover:bg-[#E47C3C]/90 text-white px-3"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
              
              {/* Footer Disclaimer */}
              <div className="mt-2 flex items-center justify-between">
                <p className="text-xs text-[#9FA6B2]">
                  AI responses are informational only and not financial advice.
                </p>
                <a 
                  href="/privacy" 
                  className="text-xs text-[#9FA6B2] hover:text-[#1F4FFF] underline"
                >
                  Privacy & Terms
                </a>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default AIAssistant;