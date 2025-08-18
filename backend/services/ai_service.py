import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from models.ai_models import ChatMessage, ChatResponse
from mock.data import mockYieldData  # Import mock data

load_dotenv()

class StableYieldAI:
    def __init__(self):
        # This will be set when user provides OpenAI key
        self.openai_key = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_KEY_HERE')
        self.system_message = """You are StableYield AI, the expert assistant for the world's first stablecoin yield benchmark platform.

ABOUT STABLEYIELD:
StableYield is the Bloomberg for stablecoin yields - an independent financial intelligence platform that delivers trusted data to power investment decisions. We believe the future of finance runs on stablecoins, and behind every yield opportunity lies the crucial question: How safe is the yield?

OUR MISSION: Bring clarity, transparency, and confidence to the stablecoin economy.

PLATFORM CAPABILITIES:
- Stablecoin Yield Indices & Benchmarks (reference points for market performance)
- Risk-Adjusted Analytics (peg stability, liquidity depth, counterparty risk)
- API Feeds & Dashboards (real-time intelligence for funds, exchanges, institutions)
- Comprehensive tracking from DeFi protocols to CeFi platforms and TradFi integrations

TARGET AUDIENCE: Fund managers, exchanges, traders, institutions, and financial professionals

YOUR EXPERTISE:
1. Stablecoin yield analysis and comparison
2. Risk assessment (peg stability, liquidity, counterparty exposure)
3. Market intelligence and benchmarking
4. Platform recommendations based on risk-return profiles
5. Institutional-grade financial insights

RESPONSE GUIDELINES:
- Provide professional, institutional-quality analysis
- Always consider risk alongside yield opportunities
- Reference StableYield's comprehensive data coverage
- Include risk considerations and disclaimers
- Format responses clearly with data tables when appropriate
- Position insights as professional market intelligence
- End every response with: "⚠️ Disclaimer: Market intelligence for professional use. Not investment advice. Always conduct due diligence."

AVAILABLE DATA CONTEXT:
Current real-time stablecoin yields across major CeFi and DeFi platforms."""

    def get_current_yields_context(self) -> str:
        """Get current yield data to provide context to the AI"""
        try:
            # In production, this would query the actual database
            # For now, using mock data
            context = "STABLEYIELD CURRENT MARKET INTELLIGENCE (Last Updated: " + datetime.now().strftime("%Y-%m-%d %H:%M") + "):\n\n"
            
            for yield_item in mockYieldData:
                context += f"• {yield_item['stablecoin']} ({yield_item['name']}): {yield_item['currentYield']:.2f}%\n"
                context += f"  Platform: {yield_item['source']} ({yield_item['sourceType']})\n"
                context += f"  Risk Level: {yield_item['riskScore']}, Liquidity: {yield_item['liquidity']}\n"
                context += f"  24h Change: {yield_item['change24h']:+.2f}%\n\n"
            
            context += "\nRISK ASSESSMENT FRAMEWORK:\n"
            context += "- Low Risk: Regulated CeFi platforms, major DeFi protocols with proven track records\n"
            context += "- Medium Risk: Established protocols with moderate exposure, emerging platforms\n"
            context += "- High Risk: New protocols, complex strategies, high yield outliers\n\n"
            
            return context
        except Exception as e:
            return "Current yield data temporarily unavailable."

    async def process_query(self, message: str, session_id: str) -> ChatResponse:
        """Process user query and return AI response"""
        try:
            if self.openai_key == 'YOUR_OPENAI_KEY_HERE':
                return ChatResponse(
                    response="🔑 StableYield AI is ready but requires OpenAI API key configuration. Please contact your administrator to activate the full AI assistant functionality for professional market intelligence.",
                    session_id=session_id,
                    message_id="config_needed"
                )

            # Initialize chat with current yields context
            current_data = self.get_current_yields_context()
            full_system_message = self.system_message + "\n\n" + current_data

            chat = LlmChat(
                api_key=self.openai_key,
                session_id=session_id,
                system_message=full_system_message
            ).with_model("openai", "gpt-4o-mini")

            # Create user message
            user_message = UserMessage(text=message)
            
            # Get AI response
            ai_response = await chat.send_message(user_message)
            
            return ChatResponse(
                response=ai_response,
                session_id=session_id,
                message_id=str(uuid.uuid4())
            )

        except Exception as e:
            return ChatResponse(
                response=f"I apologize, but I'm experiencing technical difficulties accessing the market intelligence systems. Please try again later. Error: {str(e)}",
                session_id=session_id,
                message_id="error"
            )

    def get_sample_queries(self) -> List[str]:
        """Return sample queries users can ask"""
        return [
            "What's the current risk-adjusted yield ranking for major stablecoins?",
            "Compare USDC vs USDT yields across CeFi and DeFi platforms",
            "Which platforms offer the safest high-yield opportunities?",
            "Analyze the liquidity and counterparty risk for top yields",
            "What are the key risk factors I should consider for stablecoin yields?",
            "Show me institutional-grade yield opportunities with low risk scores"
        ]

# Import uuid for the service
import uuid