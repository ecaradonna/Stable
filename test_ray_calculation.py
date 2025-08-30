#!/usr/bin/env python3
"""
Test script per analizzare il calcolo RAY (Risk-Adjusted Yield)
"""

import requests
import json
import sys
from datetime import datetime

def test_ray_calculation():
    """Test del calcolo RAY con dati reali"""
    
    print("🔬 TEST CALCOLO RAY (Risk-Adjusted Yield)")
    print("=" * 60)
    
    # Step 1: Ottenere dati yield reali
    print("\n📊 STEP 1: Ottenere dati yields dal backend")
    
    try:
        response = requests.get("http://localhost:8001/api/yields/")
        yields_data = response.json()
        
        if not yields_data:
            print("❌ Nessun dato yield disponibile")
            return
            
        print(f"✅ Trovati {len(yields_data)} yields")
        
        # Prendi il primo yield per il test dettagliato
        test_yield = yields_data[0]
        
        print(f"\n🎯 YIELD DI TEST SELEZIONATO:")
        print(f"   Stablecoin: {test_yield.get('stablecoin', 'N/A')}")
        print(f"   APY grezzo: {test_yield.get('currentYield', 0):.3f}%")
        print(f"   Fonte: {test_yield.get('source', 'N/A')}")
        print(f"   TVL: {test_yield.get('tvl', test_yield.get('metadata', {}).get('tvl', 'N/A'))}")
        
    except Exception as e:
        print(f"❌ Errore nel recupero yields: {e}")
        return
    
    # Step 2: Analizzare il calcolo RAY manuale
    print(f"\n🧮 STEP 2: ANALISI CALCOLO RAY MANUALE")
    print("-" * 40)
    
    # Simulare il calcolo RAY seguendo la logica del RAYCalculator
    base_apy = test_yield.get('currentYield', 0)
    stablecoin = test_yield.get('stablecoin', 'UNKNOWN').upper()
    source = test_yield.get('source', '').lower()
    
    print(f"Base APY: {base_apy:.3f}%")
    
    # Calcolare i Risk Factors
    print(f"\n📈 FATTORI DI RISCHIO:")
    
    # 1. Peg Stability Score
    peg_scores = {
        'USDT': 0.92, 'USDC': 0.96, 'DAI': 0.88, 'TUSD': 0.90,
        'PYUSD': 0.85, 'FRAX': 0.82, 'USDP': 0.91
    }
    peg_stability = peg_scores.get(stablecoin, 0.75)
    
    # Aggiustamento per protocollo
    if 'curve' in source:
        peg_stability = min(1.0, peg_stability + 0.03)
    elif 'uniswap' in source:
        peg_stability = max(0.0, peg_stability - 0.02)
    
    print(f"   1. Peg Stability: {peg_stability:.3f} ({stablecoin})")
    
    # 2. Liquidity Score  
    tvl_usd = 0.0
    try:
        tvl_raw = test_yield.get('metadata', {}).get('tvl', 0)
        if tvl_raw:
            tvl_usd = float(tvl_raw)
    except:
        pass
    
    # Calcolo liquidity score
    if tvl_usd >= 100_000_000:  # $100M threshold
        liquidity_score = 1.0
    elif tvl_usd >= 10_000_000:  # $10M threshold
        ratio = (tvl_usd - 10_000_000) / (100_000_000 - 10_000_000)
        liquidity_score = 0.60 + (0.40 * ratio)
    else:
        if tvl_usd > 0:
            ratio = tvl_usd / 10_000_000
            liquidity_score = 0.30 + (0.30 * ratio)
        else:
            liquidity_score = 0.10
    
    print(f"   2. Liquidity Score: {liquidity_score:.3f} (TVL: ${tvl_usd:,.0f})")
    
    # 3. Counterparty Score
    source_type = test_yield.get('sourceType', 'DeFi')
    if source_type == 'DeFi':
        counterparty_score = 0.85
    elif source_type == 'CeFi':
        counterparty_score = 0.70
    else:
        counterparty_score = 0.75
    
    print(f"   3. Counterparty Score: {counterparty_score:.3f} ({source_type})")
    
    # 4. Protocol Reputation
    protocol_reputation = test_yield.get('metadata', {}).get('protocol_info', {}).get('reputation_score', 0.75)
    print(f"   4. Protocol Reputation: {protocol_reputation:.3f}")
    
    # 5. Temporal Stability (basato sull'APY)
    if base_apy > 50:
        temporal_stability = 0.30
    elif base_apy > 25:
        temporal_stability = 0.50
    elif base_apy > 15:
        temporal_stability = 0.70
    else:
        temporal_stability = 0.85
        
    print(f"   5. Temporal Stability: {temporal_stability:.3f} (basato su APY {base_apy:.1f}%)")
    
    # Step 3: Calcolare le penalità
    print(f"\n⚡ PENALITÀ DI RISCHIO:")
    
    # Calcolare penalità individuali
    peg_penalty = (1 - peg_stability) * 0.50  # Max 50% penalty
    liquidity_penalty = (1 - liquidity_score) * 0.40  # Max 40% penalty  
    counterparty_penalty = (1 - counterparty_score) * 0.60  # Max 60% penalty
    protocol_penalty = (1 - protocol_reputation) * 0.35  # Max 35% penalty
    temporal_penalty = (1 - temporal_stability) * 0.25  # Max 25% penalty
    
    print(f"   - Peg Penalty: {peg_penalty:.1%}")
    print(f"   - Liquidity Penalty: {liquidity_penalty:.1%}")  
    print(f"   - Counterparty Penalty: {counterparty_penalty:.1%}")
    print(f"   - Protocol Penalty: {protocol_penalty:.1%}")
    print(f"   - Temporal Penalty: {temporal_penalty:.1%}")
    
    # Penalità composta (compound)
    total_penalty_factor = 1.0
    penalties = [peg_penalty, liquidity_penalty, counterparty_penalty, protocol_penalty, temporal_penalty]
    
    for penalty in penalties:
        total_penalty_factor *= (1 - penalty)
    
    total_penalty = 1 - total_penalty_factor
    
    print(f"\n   TOTALE PENALTY: {total_penalty:.1%} (compound)")
    
    # Step 4: Calcolare RAY finale
    ray = base_apy * (1 - total_penalty)
    
    print(f"\n🎯 RISULTATO RAY:")
    print(f"   Base APY: {base_apy:.3f}%")
    print(f"   Total Risk Penalty: {total_penalty:.1%}")
    print(f"   RAY (Risk-Adjusted): {ray:.3f}%")
    print(f"   Riduzione: {((base_apy - ray) / base_apy * 100):.1f}%")
    
    # Step 5: Confrontare con il calcolo backend
    print(f"\n🔍 STEP 3: CONFRONTO CON BACKEND")
    print("-" * 40)
    
    try:
        # Chiamare endpoint SYI per vedere RAY calcolato
        syi_response = requests.get("http://localhost:8001/api/syi/current")
        syi_data = syi_response.json()
        
        print(f"SYI Backend Response:")
        print(f"   SYI Value: {syi_data.get('syi_percent', 0):.3f}%")
        print(f"   Components: {syi_data.get('components_count', 0)}")
        
    except Exception as e:
        print(f"❌ Errore nel recupero SYI: {e}")
    
    # Step 6: Test con dati sanitization
    sanitization = test_yield.get('metadata', {}).get('sanitization', {})
    if sanitization:
        print(f"\n🧹 DATI SANITIZATION:")
        print(f"   Original APY: {sanitization.get('original_apy', 'N/A')}")
        print(f"   Sanitized APY: {sanitization.get('sanitized_apy', 'N/A')}")
        print(f"   Confidence Score: {sanitization.get('confidence_score', 'N/A')}")
        print(f"   Warnings: {len(sanitization.get('warnings', []))}")
        
        if sanitization.get('warnings'):
            for warning in sanitization['warnings']:
                print(f"     - {warning}")
    
    print(f"\n✅ Test RAY completato!")
    return {
        'base_apy': base_apy,
        'calculated_ray': ray,
        'total_penalty': total_penalty,
        'risk_factors': {
            'peg_stability': peg_stability,
            'liquidity_score': liquidity_score, 
            'counterparty_score': counterparty_score,
            'protocol_reputation': protocol_reputation,
            'temporal_stability': temporal_stability
        }
    }

if __name__ == "__main__":
    test_ray_calculation()