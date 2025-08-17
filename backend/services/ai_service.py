import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from ..models.ai_models import ChatMessage, ChatResponse
from ..mock.data import mockYieldData  # Import mock data

load_dotenv()

class StableYieldAI:
    def __init__(self):
        # This will be set when user provides OpenAI key
        self.openai_key = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_KEY_HERE')
        self.system_message = """You are StableYield AI, an expert assistant for stablecoin yield data and analysis.

CURRENT CONTEXT:
You have access to real-time stablecoin yield data from major platforms including Binance Earn, Aave, Compound, and other CeFi/DeFi protocols.

YOUR CAPABILITIES:
1. Answer questions about current stablecoin yields
2. Compare yields across different stablecoins (USDT, USDC, DAI, PYUSD, TUSD)
3. Explain risk factors and platform differences
4. Provide historical context and trends
5. Format responses in clear, structured formats

RESPONSE GUIDELINES:
- Always include current data when available
- Format numerical data clearly (tables when appropriate)
- Explain the source and methodology
- Be concise but informative
- Include risk considerations
- End every response with: "⚠️ Disclaimer: This is simulation data for informational purposes only. Not financial advice."

AVAILABLE DATA:
- Current yields for major stablecoins
- Platform sources (CeFi vs DeFi)
- Risk scores and liquidity information
- 24h changes and trends

Remember: You're providing data analysis, not investment advice."""

    def get_current_yields_context(self) -> str:
        """Get current yield data to provide context to the AI"""
        try:
            # In production, this would query the actual database
            # For now, using mock data
            context = "CURRENT STABLECOIN YIELDS (Last Updated: " + datetime.now().strftime("%Y-%m-%d %H:%M") + "):\n\n"
            
            for yield_item in mockYieldData:
                context += f"• {yield_item['stablecoin']} ({yield_item['name']}): {yield_item['currentYield']:.2f}%\n"
                context += f"  Source: {yield_item['source']} ({yield_item['sourceType']})\n"
                context += f"  Risk: {yield_item['riskScore']}, Liquidity: {yield_item['liquidity']}\n"
                context += f"  24h Change: {yield_item['change24h']:+.2f}%\n\n"
            
            return context
        except Exception as e:
            return "Current yield data temporarily unavailable."

    async def process_query(self, message: str, session_id: str) -> ChatResponse:
        """Process user query and return AI response"""
        try:
            if self.openai_key == 'YOUR_OPENAI_KEY_HERE':
                return ChatResponse(
                    response="🔑 OpenAI API key not configured yet. Please provide your OpenAI API key to enable the AI assistant.",
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
                response=f"I apologize, but I'm experiencing technical difficulties. Please try again later. Error: {str(e)}",
                session_id=session_id,
                message_id="error"
            )

    def get_sample_queries(self) -> List[str]:
        """Return sample queries users can ask"""
        return [
            "What's the current top yield for USDT?",
            "Compare USDC vs DAI yields today",
            "Which platform offers the best USDT yield?",
            "Show me all stablecoin yields above 6%",
            "What are the risks with high-yield stablecoins?",
            "Explain the difference between CeFi and DeFi yields"
        ]

# Import uuid for the service
import uuid