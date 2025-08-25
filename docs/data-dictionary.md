# StableYield Data Dictionary

**Version:** 1.0.0  
**Last Updated:** 2025-01-25  
**Schema Location:** `/schema/canonical_entities.json`

## Overview

This document defines the canonical data model for StableYield.com, establishing unified entity definitions for stablecoins, protocols, pools, and chains. All data ingestion, processing, and API responses must conform to these canonical formats.

## Core Entities

### 1. Stablecoin Entity

**Purpose:** Standardized representation of USD-pegged stablecoins  
**Canonical ID Pattern:** `^[A-Z0-9]+$` (e.g., USDT, USDC, DAI)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `canonical_id` | string | ✅ | Primary identifier (USDT, USDC, DAI) |
| `name` | string | ✅ | Full name (Tether USD, USD Coin) |
| `symbol` | string | ✅ | Trading symbol |
| `synonyms` | array | ❌ | Alternative names/symbols |
| `peg_currency` | enum | ✅ | USD, EUR, GBP, CHF |
| `mechanism` | enum | ✅ | collateralized, algorithmic, hybrid |
| `issuer` | string | ❌ | Issuing organization |
| `market_cap_tier` | enum | ❌ | tier_1, tier_2, tier_3 |

**Examples:**
- `USDT`: Tier 1, collateralized, issued by Tether Limited
- `USDC`: Tier 1, collateralized, issued by Centre Consortium  
- `DAI`: Tier 1, collateralized, issued by MakerDAO

### 2. Protocol Entity

**Purpose:** DeFi protocol standardization with reputation scoring  
**Canonical ID Pattern:** `^[a-z0-9_]+$` (e.g., aave_v3, compound_v3)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `canonical_id` | string | ✅ | Protocol identifier (aave_v3, curve) |
| `name` | string | ✅ | Display name (Aave V3, Curve Finance) |
| `protocol_type` | enum | ✅ | lending, amm, stable_pool, yield_farming |
| `reputation_score` | number | ✅ | Score [0,1] based on audits/TVL/longevity |
| `audit_status` | object | ❌ | Audit firms, dates, status |
| `exploit_history` | array | ❌ | Historical security incidents |
| `launch_date` | date | ❌ | Protocol launch date |

**Reputation Score Calculation:**
- **0.90-1.00**: Major protocols (Aave V3, Compound V3)
- **0.70-0.89**: Established protocols (Curve, Balancer)
- **0.50-0.69**: Emerging protocols with audits
- **0.00-0.49**: Experimental or unaudited protocols

### 3. Chain Entity

**Purpose:** Blockchain network standardization  
**Canonical ID Pattern:** `^[a-z0-9_]+$` (e.g., ethereum, polygon, arbitrum)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `canonical_id` | string | ✅ | Chain identifier (ethereum, polygon) |
| `name` | string | ✅ | Display name (Ethereum, Polygon) |
| `chain_type` | enum | ✅ | L1, L2, sidechain |
| `parent_chain` | string | ❌ | Parent chain for L2s |
| `native_token` | string | ✅ | Native token (ETH, MATIC) |
| `avg_block_time` | number | ❌ | Block time in seconds |
| `finality_time` | number | ❌ | Finality time in seconds |

### 4. Pool Entity

**Purpose:** Standardized yield-generating pool representation

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pool_id` | string | ✅ | Source-specific pool identifier |
| `canonical_pool_id` | string | ❌ | StableYield canonical identifier |
| `protocol_id` | string | ✅ | Reference to canonical protocol |
| `chain_id` | string | ✅ | Reference to canonical chain |
| `pool_type` | enum | ✅ | single_asset, multi_asset, lp_token, vault |
| `assets` | array | ✅ | Array of stablecoin assets with weights |
| `pool_address` | string | ❌ | Smart contract address |

### 5. Yield Data Entity

**Purpose:** Standardized yield information with risk metrics

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pool_id` | string | ✅ | Reference to pool entity |
| `timestamp` | datetime | ✅ | Data timestamp (ISO 8601) |
| `apy_base` | number | ✅ | Base APY excluding incentives |
| `apy_reward` | number | ❌ | Additional APY from token rewards |
| `apy_total` | number | ❌ | Total APY (base + rewards) |
| `tvl_usd` | number | ✅ | Total Value Locked in USD |
| `volume_24h_usd` | number | ❌ | 24-hour volume in USD |
| `risk_factors` | object | ❌ | Peg/liquidity/counterparty scores |
| `data_quality` | object | ❌ | Staleness and confidence metrics |

## Canonical Mappings

### Supported Stablecoins
- **USDT** (Tether USD): Tier 1, $89B+ market cap
- **USDC** (USD Coin): Tier 1, $32B+ market cap  
- **DAI** (Dai Stablecoin): Tier 1, $4.8B+ market cap
- **TUSD** (TrueUSD): Tier 2, <$500M market cap
- **PYUSD** (PayPal USD): Tier 2, emerging

### Supported Protocols
- **aave_v3**: Lending protocol, reputation 0.95
- **compound_v3**: Lending protocol, reputation 0.90
- **curve**: AMM/stable pools, reputation 0.85

### Supported Chains
- **ethereum**: L1, 12s blocks, 6.4min finality
- **polygon**: Sidechain, 2s blocks, 4.3min finality  
- **arbitrum**: L2, 0.25s blocks, 7-day finality

## Validation Rules

### APY Bounds
- **Minimum APY**: 0%
- **Reasonable Maximum**: 50% (triggers review)
- **Outlier Threshold**: 100% (flagged for manual review)

### TVL Requirements  
- **Minimum TVL**: $1,000 (inclusion threshold)
- **Institutional Minimum**: $10M (institutional-grade pools)

### Data Freshness
- **Maximum Age**: 30 minutes (data expiry)
- **Stale Warning**: 10 minutes (UI warning threshold)

## Implementation Notes

### Data Ingestion
1. All incoming data must be normalized to canonical format
2. Unknown entities are logged and require manual mapping
3. Validation rules are enforced at ingestion time
4. Failed validations are logged with detailed error messages

### API Responses
1. All APIs return data in canonical format
2. Original source identifiers preserved in metadata
3. Confidence scores included for data quality assessment
4. Synonyms provided for client-side matching

### Schema Evolution
1. Backwards-compatible changes preferred
2. Breaking changes require version increment
3. Migration scripts provided for schema updates
4. All changes documented in this data dictionary

## Related Documentation
- `/schema/canonical_entities.json` - JSON Schema definition
- `/config/protocol_policy.yml` - Protocol allowlist/denylist (STEP 2)
- `/config/liquidity_thresholds.yml` - TVL filtering rules (STEP 3)
- `/lib/yield_sanitizer.ts` - Outlier detection logic (STEP 4)