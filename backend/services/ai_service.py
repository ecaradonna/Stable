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
        # Use EMERGENT_LLM_KEY for universal LLM access
        self.llm_key = os.getenv('EMERGENT_LLM_KEY', os.getenv('OPENAI_API_KEY', 'YOUR_API_KEY_HERE'))
        self.system_message = """You are StableYield AI, the expert assistant for the world's first stablecoin yield benchmark platform.

ABOUT STABLEYIELD:
StableYield is the Bloomberg for stablecoin yields - an independent financial intelligence platform that delivers trusted data to power investment decisions. We believe the future of finance runs on stablecoins, and behind every yield opportunity lies the crucial question: How safe is the yield?

OUR MISSION: Bring clarity, transparency, and confidence to the stablecoin economy.

PLATFORM CAPABILITIES:
- StableYield Index (SYI) - Risk-adjusted yield composite benchmark
- Stablecoin Yield Indices & Benchmarks (SYC, SY-CeFi, SY-DeFi, SY-RPI) 
- Risk-Adjusted Yield (RAY) calculations with multi-factor analysis
- Peg stability monitoring across multiple data sources
- API Feeds & Dashboards (real-time intelligence for institutions)
- Risk regime detection (Risk ON/OFF market conditions)

KEY CONCEPTS TO EXPLAIN:
- RAY (Risk-Adjusted Yield): Yield adjusted for peg stability, liquidity, counterparty risk, protocol reputation, and temporal stability
- SYI: StableYield Index - our flagship risk-adjusted composite benchmark currently at ~4.47%
- Peg Monitoring: Real-time price deviation tracking with 50bps depeg thresholds
- Risk Regimes: Market condition classification (Risk ON/OFF) based on volatility and breadth

TARGET AUDIENCE: Fund managers, exchanges, traders, institutions, and financial professionals

YOUR EXPERTISE:
1. Explain StableYield methodology (RAY calculation, SYI composition, risk factors)
2. Stablecoin yield analysis and comparison with risk adjustments
3. Risk assessment (peg stability, liquidity, counterparty exposure)
4. Market intelligence and benchmarking insights
5. Platform recommendations based on risk-return profiles
6. Institutional-grade financial analysis

RESPONSE GUIDELINES:
- Provide professional, institutional-quality analysis similar to Bloomberg or MSCI
- Always consider risk alongside yield opportunities
- Reference StableYield's comprehensive data coverage and methodology
- Use specific numbers from current data when available
- Include risk considerations and proper disclaimers
- Format responses clearly with data tables when appropriate
- Position insights as professional market intelligence
- End every response with: "⚠️ *AI responses are for informational purposes only and do not constitute financial advice.*"

AVAILABLE DATA CONTEXT:
Current real-time stablecoin yields, peg status, and risk metrics across major platforms."""

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
            if self.llm_key == 'YOUR_API_KEY_HERE' or not self.llm_key:
                return ChatResponse(
                    response="👋 Hi! I'm StableYield AI. I can help you with current stablecoin yields, comparisons, and market analysis. What would you like to know?\n\n🔑 *Note: AI functionality requires API key configuration. Please contact your administrator to activate full assistant capabilities.*",
                    session_id=session_id,
                    message_id="config_needed"
                )

            # Initialize chat with current yields context
            current_data = self.get_current_yields_context()
            full_system_message = self.system_message + "\n\n" + current_data

            chat = LlmChat(
                api_key=self.llm_key,
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
                response=f"I apologize, but I'm experiencing technical difficulties accessing the market intelligence systems. Please try again later.\n\n⚠️ *AI responses are for informational purposes only and do not constitute financial advice.*",
                session_id=session_id,
                message_id="error"
            )

    def get_sample_queries(self) -> List[str]:
        """Return sample queries users can ask"""
        return [
            "What is RAY (Risk-Adjusted Yield) and how is it calculated?",
            "What's the current SYI value and what does it mean?",
            "Compare USDC vs USDT yields with risk adjustments",
            "Explain Risk ON vs Risk OFF market regimes", 
            "Which stablecoins are currently depegged?",
            "Show me the StableYield Index methodology",
            "What are the safest high-yield opportunities right now?",
            "Analyze peg stability across major stablecoins"
        ]

# Import uuid for the service
import uuid