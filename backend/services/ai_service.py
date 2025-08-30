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
        """Get current yields and market data for AI context"""
        try:
            import requests
            import json
            from datetime import datetime
            
            context_data = []
            base_url = 'http://localhost:8001'
            
            # 1. API SYI: /api/syi/current (4.47%)
            try:
                syi_response = requests.get(f'{base_url}/api/syi/current', timeout=5)
                if syi_response.status_code == 200:
                    syi_data = syi_response.json()
                    if syi_data.get('success'):
                        syi_percent = syi_data.get('syi_percent', 'N/A')
                        components = syi_data.get('components_count', 'N/A')
                        version = syi_data.get('methodology_version', 'N/A')
                        context_data.append(f"📊 STABLEYIELD INDEX (SYI): {syi_percent}% (Current Benchmark)")
                        context_data.append(f"   • Components: {components} stablecoin yield sources")
                        context_data.append(f"   • Methodology: Version {version}")
                        context_data.append(f"   • Status: Live calculation active")
            except Exception as e:
                context_data.append("📊 SYI: Live calculation temporarily unavailable")
            
            # 2. Index Family: /api/v1/index-family/overview  
            try:
                family_response = requests.get(f'{base_url}/api/v1/index-family/overview', timeout=5)
                if family_response.status_code == 200:
                    family_data = family_response.json()
                    if family_data.get('success') and family_data.get('data'):
                        indices = family_data['data'].get('indices', {})
                        total_aum = family_data['data'].get('family_aum', 0)
                        
                        context_data.append(f"📈 INDEX FAMILY OVERVIEW:")
                        context_data.append(f"   • Total AUM: ${total_aum/1e9:.2f}B across index family")
                        
                        for code, index_data in indices.items():
                            if index_data and isinstance(index_data, dict):
                                value = index_data.get('value', 0)
                                tvl = index_data.get('total_tvl', 0)
                                context_data.append(f"   • {code}: {value*100:.2f}% (TVL: ${tvl/1e9:.1f}B)")
                                
            except Exception as e:
                context_data.append("📈 Index Family: Data temporarily unavailable")
            
            # 3. Peg Monitor: /api/peg/check (stato FRAX, USDC, etc.)
            try:
                peg_symbols = 'USDT,USDC,DAI,FRAX,TUSD,PYUSD'
                peg_response = requests.get(f'{base_url}/api/peg/check?symbols={peg_symbols}', timeout=5)
                if peg_response.status_code == 200:
                    peg_data = peg_response.json()
                    if peg_data.get('success') and peg_data.get('data', {}).get('results'):
                        stable_count = 0
                        monitoring_count = 0
                        depegged_count = 0
                        
                        context_data.append(f"🔍 PEG MONITORING STATUS:")
                        
                        for result in peg_data['data']['results']:
                            symbol = result.get('symbol', 'Unknown')
                            price = result.get('price_usd', 0)
                            deviation = result.get('deviation', {}).get('percentage', 0)
                            
                            if abs(deviation) < 0.5:
                                status = "🟢 Stable"
                                stable_count += 1
                            elif abs(deviation) > 5:
                                status = "🔴 Depegged"
                                depegged_count += 1
                            else:
                                status = "🟡 Monitoring"
                                monitoring_count += 1
                                
                            context_data.append(f"   • {symbol}: ${price:.4f} ({deviation:+.2f}%) {status}")
                        
                        context_data.append(f"   • Summary: {stable_count} Stable, {monitoring_count} Monitoring, {depegged_count} Depegged")
            except Exception as e:
                context_data.append("🔍 Peg Monitor: Live monitoring temporarily unavailable")
            
            # 4. Risk Regime: /api/regime/current (Risk ON/OFF)
            try:
                regime_response = requests.get(f'{base_url}/api/regime/current', timeout=5)
                if regime_response.status_code == 200:
                    regime_data = regime_response.json()
                    if regime_data.get('success') and regime_data.get('data'):
                        current_regime = regime_data['data'].get('current_regime', 'Unknown')
                        confidence = regime_data['data'].get('confidence', 0)
                        
                        regime_icon = "🟢" if "ON" in current_regime.upper() else "🔴" if "OFF" in current_regime.upper() else "🟡"
                        
                        context_data.append(f"⚡ RISK REGIME ANALYSIS:")
                        context_data.append(f"   • Current Status: {regime_icon} {current_regime}")
                        context_data.append(f"   • Confidence Level: {confidence:.1%}")
                        context_data.append(f"   • Market Conditions: {'Favorable for yield hunting' if 'ON' in current_regime.upper() else 'Exercise caution, focus on stability' if 'OFF' in current_regime.upper() else 'Mixed signals'}")
            except Exception as e:
                context_data.append("⚡ Risk Regime: Analysis temporarily unavailable")
            
            # 5. Additional Yields Context
            try:
                yields_response = requests.get(f'{base_url}/api/yields/', timeout=5)
                if yields_response.status_code == 200:
                    yields_data = yields_response.json()
                    if isinstance(yields_data, list) and len(yields_data) > 0:
                        context_data.append(f"💰 LIVE YIELD OPPORTUNITIES:")
                        context_data.append(f"   • Total Active Sources: {len(yields_data)} platforms monitored")
                        
                        # Sort by yield and show top 3
                        sorted_yields = sorted(yields_data, key=lambda x: x.get('currentYield', 0), reverse=True)
                        
                        for i, yield_item in enumerate(sorted_yields[:3]):
                            symbol = yield_item.get('stablecoin', 'Unknown')
                            apy = yield_item.get('currentYield', 0)
                            source = yield_item.get('source', 'Unknown')
                            source_type = yield_item.get('sourceType', 'Unknown')
                            
                            context_data.append(f"   • #{i+1}: {symbol} - {apy:.2f}% APY ({source}, {source_type})")
                            
            except Exception as e:
                context_data.append("💰 Live Yields: Data temporarily unavailable")
            
            # Add timestamp and summary
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            context_data.append(f"\n📅 Data Updated: {timestamp}")
            context_data.append(f"🔄 Status: {'Live data integration active' if len(context_data) > 2 else 'Fallback mode - some APIs unavailable'}")
            
            return "\n".join(context_data) if context_data else "❌ All live data sources temporarily unavailable - providing general StableYield guidance."
            
        except Exception as e:
            return f"❌ Live data integration error: {str(e)[:100]}... - providing general guidance based on StableYield methodology."

    async def process_query(self, message: str, session_id: str) -> ChatResponse:
        """Process user query and return AI response"""
        try:
            if self.llm_key == 'YOUR_API_KEY_HERE' or not self.llm_key:
                return ChatResponse(
                    response="👋 Hi! I'm StableYield AI. I can help you with current stablecoin yields, comparisons, and market analysis. What would you like to know?\n\n🔑 *Note: AI functionality requires API key configuration. Please contact your administrator to activate full assistant capabilities.*",
                    session_id=session_id,
                    message_id="config_needed"
                )

            # Get current data first
            current_data = self.get_current_yields_context()
            
            # Enhanced system prompt with key Q&A knowledge
            enhanced_prompt = self.system_message + """

CORE STABLEYIELD Q&A KNOWLEDGE BASE:

Q1: What is the StableYield Index (SYI)?
A1: The StableYield Index is the institutional benchmark for stablecoin yields. It measures returns adjusted for peg risk, liquidity, and counterparty exposure — making stablecoins comparable to T-Bills or Euribor. Currently at {current_syi}%.

Q2: Why do I need a benchmark for stablecoins?
A2: Because raw APYs across platforms are often inflated and inconsistent. SYI filters the noise, creating a single, transparent, auditable figure that serves as the foundation for evaluations, reporting, and strategy.

Q3: How does it help me manage risk?
A3: StableYield monitors in real time: peg deviations, liquidity depth, protocol resilience. You know when risk is rising, so you can protect capital or rotate into safer stablecoins.

Q4: What advantage does it give a trader?
A4: It delivers clear Risk ON / Risk OFF signals based on data, not sentiment. Traders can: anticipate market stress, exploit arbitrage on peg deviations, optimize collateral and yield strategies.

Q5: And for institutional investors?
A5: It provides a governance and compliance tool: you can benchmark your stablecoin performance against an institutional-grade index — just as you already do with bonds, equities, and money market rates.

Q6: How does it support treasury managers?
A6: It lets you assess whether allocating to stablecoins is more or less attractive than government securities. Always with risk-adjusted data and built-in regulatory monitoring.

Q7: Can I receive automatic alerts?
A7: Yes. With the Pro plan, you get real-time alerts via Telegram, TradingView, or email: when a stablecoin depegs, when the regime shifts (ON/OFF), when yields diverge from T-Bills.

Q8: What's the advantage over DeFiLlama or similar tools?
A8: StableYield doesn't just show raw APYs. It calculates RAY (Risk-Adjusted Yield) — the first system integrating stability, liquidity, and counterparty metrics. It's built for institutions, not retail.

Q9: How can I access the data?
A9: Live dashboard (Free tier with delayed data), API access for trading desks, risk managers, and reporting systems, Weekly or monthly reports for pro traders and institutions.

Q10: How does it improve my work in practice?
A10: You no longer need to monitor dozens of protocols: everything is in one index. You immediately know if your yields are above or below the market. You minimize hidden risks (depeg, illiquidity, counterparty). You make faster, informed, and defensible decisions for clients, boards, or investors.

Use this knowledge base to provide authoritative answers. Always reference current data when available."""

            full_system_message = enhanced_prompt + "\n\n" + current_data

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
        """Return sample queries users can ask - based on key StableYield Q&A"""
        return [
            "What is the StableYield Index (SYI)?",
            "How does SYI help me manage risk?", 
            "What advantage does it give traders?",
            "How does it support treasury managers?",
            "Can I receive automatic alerts?",
            "How can I access the data?",
            "What's the advantage over DeFiLlama?",
            "Why do I need a benchmark for stablecoins?"
        ]

# Import uuid for the service
import uuid