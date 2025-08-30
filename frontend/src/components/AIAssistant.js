import React, { useState, useRef, useEffect } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { MessageCircle, Send, Sparkles, X, Loader2, Bot, User } from "lucide-react";
import { aiApi } from "../services/api";

const AIAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      type: "ai",
      content: "👋 Hi! I'm StableYield AI. I can help you with current stablecoin yields, comparisons, and market analysis. What would you like to know?",
      timestamp: new Date()
    }
  ]);
  const [currentMessage, setCurrentMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [sampleQueries, setSampleQueries] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load sample queries when component mounts
  useEffect(() => {
    const loadSamples = async () => {
      try {
        const response = await aiApi.getSamples();
        setSampleQueries(response.data.samples || []);
      } catch (error) {
        console.error("Failed to load sample queries:", error);
      }
    };
    
    if (isOpen) {
      loadSamples();
    }
  }, [isOpen]);

  const handleSendMessage = async (message = currentMessage) => {
    if (!message.trim() || isLoading) return;

    const userMessage = {
      type: "user",
      content: message,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage("");
    setIsLoading(true);

    try {
      const response = await aiApi.chat({
        session_id: sessionId,
        message: message
      });

      const aiMessage = {
        type: "ai",
        content: response.data.response,
        timestamp: new Date(),
        messageId: response.data.message_id
      };

      setMessages(prev => [...prev, aiMessage]);
      
    } catch (error) {
      console.error("AI chat error:", error);
      
      let errorContent = "I apologize, but I'm experiencing technical difficulties. Please try again later.";
      
      // Handle specific error cases
      if (error.response?.status === 500 && error.response?.data?.detail?.includes('OpenAI API key')) {
        errorContent = "🔑 The AI assistant is ready but needs an OpenAI API key to be configured by the administrator. Please contact support for assistance.";
      } else if (error.response?.data?.detail) {
        errorContent = error.response.data.detail;
      }
      
      const errorMessage = {
        type: "ai",
        content: errorContent,
        timestamp: new Date(),
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatMessage = (content) => {
    // Simple formatting for better readability
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br />');
  };

  return (
    <>
      {/* Floating Button */}
      <div className="fixed bottom-6 right-6 z-[9999]">
        <Button
          onClick={() => setIsOpen(true)}
          className="h-14 w-14 rounded-full bg-[#E47C3C] hover:bg-[#E47C3C]/90 text-white shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-110"
          aria-label="Open AI Assistant"
        >
          <MessageCircle className="h-6 w-6" />
        </Button>
      </div>

      {/* Chat Dialog */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="sm:max-w-[600px] h-[700px] flex flex-col p-0">
          {/* Header */}
          <DialogHeader className="p-6 pb-4 border-b bg-[#1F4FFF]/5">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-[#1F4FFF] rounded-full flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
                <DialogTitle className="text-xl font-bold text-[#1A1A1A]">
                  StableYield AI
                </DialogTitle>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsOpen(false)}
                className="hover:bg-gray-100"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
            <p className="text-sm text-[#6B7280] mt-2">
              Professional assistant for stablecoin yields, benchmarks, and risk analytics
            </p>
          </DialogHeader>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`flex items-start space-x-2 max-w-[80%] ${
                    message.type === "user" ? "flex-row-reverse space-x-reverse" : ""
                  }`}
                >
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.type === "user"
                        ? "bg-[#E47C3C]"
                        : message.isError
                        ? "bg-red-500"
                        : "bg-[#1F4FFF]"
                    }`}
                  >
                    {message.type === "user" ? (
                      <User className="w-4 h-4 text-white" />
                    ) : (
                      <Bot className="w-4 h-4 text-white" />
                    )}
                  </div>
                  <div
                    className={`rounded-lg p-3 ${
                      message.type === "user"
                        ? "bg-[#E47C3C] text-white"
                        : message.isError
                        ? "bg-red-50 text-red-700 border border-red-200"
                        : "bg-gray-100 text-[#1A1A1A]"
                    }`}
                  >
                    <div
                      className="text-sm leading-relaxed whitespace-pre-wrap"
                      dangerouslySetInnerHTML={{
                        __html: formatMessage(message.content)
                      }}
                    />
                    <div className="text-xs opacity-70 mt-2">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-gradient-to-r from-[#4CC1E9] to-[#007A99] rounded-full flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-gray-100 rounded-lg p-3">
                    <div className="flex items-center space-x-2">
                      <Loader2 className="w-4 h-4 animate-spin text-[#4CC1E9]" />
                      <span className="text-sm text-gray-600">Analyzing...</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Sample Queries */}
          {messages.length === 1 && sampleQueries.length > 0 && (
            <div className="p-4 border-t bg-gray-50">
              <p className="text-sm font-medium text-[#0E1A2B] mb-2">Try asking:</p>
              <div className="grid grid-cols-1 gap-2">
                {sampleQueries.slice(0, 4).map((query, index) => (
                  <button
                    key={index}
                    onClick={() => handleSendMessage(query)}
                    className="text-left text-sm p-2 bg-white rounded-lg border hover:border-[#4CC1E9] hover:bg-[#4CC1E9]/5 transition-colors"
                    disabled={isLoading}
                  >
                    {query}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="p-4 border-t">
            <div className="flex space-x-2">
              <Input
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about stablecoin yields..."
                disabled={isLoading}
                className="flex-1"
              />
              <Button
                onClick={() => handleSendMessage()}
                disabled={!currentMessage.trim() || isLoading}
                className="bg-gradient-to-r from-[#4CC1E9] to-[#007A99] hover:from-[#007A99] hover:to-[#4CC1E9] text-white"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Press Enter to send • AI responses include disclaimers
            </p>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default AIAssistant;