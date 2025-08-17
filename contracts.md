# StableYield.com Backend Contracts

## 📋 API Contracts & Integration Plan

### Current Mock Data to Replace:
```javascript
// Frontend mock data in /app/frontend/src/mock/data.js
- mockYieldData: 5 stablecoins with yields, sources, risk scores
- mockHistoricalData: 7-day historical yield data
- newsletterSignups, waitlistSignups: User data storage
- mockBlogPosts: Blog content
```

### Database Schema (MongoDB)

#### 1. Yields Collection
```javascript
{
  _id: ObjectId,
  stablecoin: "USDT",
  name: "Tether USD", 
  currentYield: 8.45,
  source: "Binance Earn",
  sourceType: "CeFi", // CeFi | DeFi
  riskScore: "Medium", // Low | Medium | High
  change24h: 0.12,
  liquidity: "$89.2B",
  lastUpdated: Date,
  metadata: {
    platform: "binance",
    poolId: "USDT001",
    minimumAmount: 10
  }
}
```

#### 2. Historical Yields Collection
```javascript
{
  _id: ObjectId,
  stablecoin: "USDT",
  date: Date,
  yield: 8.45,
  source: "Binance Earn",
  timestamp: Date
}
```

#### 3. Users Collection (for waitlist/newsletter)
```javascript
{
  _id: ObjectId,
  email: "user@example.com",
  name: "John Doe",
  signupType: "waitlist", // waitlist | newsletter
  interest: "trader", // trader | investor | institution | media
  signupDate: Date,
  isActive: true
}
```

#### 4. AI Alerts Collection
```javascript
{
  _id: ObjectId,
  userEmail: "user@example.com",
  stablecoin: "USDT",
  condition: ">",
  threshold: 8.5,
  alertType: "yield_threshold",
  isActive: true,
  lastTriggered: Date,
  createdAt: Date
}
```

#### 5. Chat Messages Collection
```javascript
{
  _id: ObjectId,
  sessionId: "session_123",
  userId: "user_email", // optional
  message: "What's the current USDT yield?",
  response: "AI response...",
  timestamp: Date,
  metadata: {
    model: "gpt-4o-mini",
    tokensUsed: 150
  }
}
```

### External API Integrations Required

#### 1. DefiLlama API
```
BASE_URL: https://yields.llama.fi
ENDPOINTS:
- /pools → Get all yield pools
- /chart/{pool_id} → Historical data
- /config → Pool configurations

STABLECOINS TO TRACK:
- USDT, USDC, DAI, PYUSD, TUSD
- Filter by stablecoin pools only
- Focus on major protocols: Aave, Compound, Curve
```

#### 2. Binance Earn API  
```
BASE_URL: https://api.binance.com
ENDPOINTS:
- /sapi/v1/simple-earn/flexible/list → Flexible savings products
- /sapi/v1/simple-earn/locked/list → Locked savings products

AUTHENTICATION: API Key required
RATE LIMITS: 1200 requests/minute
```

#### 3. Aave API
```
BASE_URL: https://aave-api-v2.aave.com
ENDPOINTS:
- /data/liquidity/v2 → Current liquidity data
- /data/rates-history → Historical rates

NETWORKS: Ethereum, Polygon, Avalanche
```

### Backend API Endpoints to Implement

#### 1. Yields Endpoints
```
GET /api/yields → Get current yields for all stablecoins
GET /api/yields/{stablecoin} → Get specific stablecoin data
GET /api/yields/{stablecoin}/history → Get historical data
POST /api/yields/refresh → Manual refresh (admin only)
```

#### 2. User Management Endpoints  
```
POST /api/users/waitlist → Join waitlist
POST /api/users/newsletter → Subscribe to newsletter
GET /api/users/{email} → Get user data
PUT /api/users/{email} → Update user preferences
```

#### 3. AI Endpoints (Already Implemented)
```
POST /api/ai/chat → Chat with AI
GET /api/ai/chat/samples → Sample queries
POST /api/ai/alerts → Create alert
GET /api/ai/alerts/{email} → Get user alerts
DELETE /api/ai/alerts/{id} → Delete alert
```

### Data Update Schedule

#### Real-time Updates (Every 30 seconds)
- Current yield rates from all sources
- 24h change calculations
- Risk score updates

#### Hourly Updates
- Historical data points
- Liquidity metrics
- Platform availability

#### Daily Updates  
- Risk score recalculations
- Alert checking and notifications
- Data cleanup and optimization

### Frontend Integration Changes

#### Replace Mock Imports
```javascript
// REMOVE: import { mockYieldData } from "../mock/data";
// ADD: API calls to /api/yields

// REMOVE: localStorage for waitlist/newsletter
// ADD: API calls to /api/users/*

// KEEP: AI integration (already done)
```

#### Error Handling
```javascript
// Add proper error states for API failures
// Loading states for data fetching
// Offline/connection lost scenarios
// Rate limiting responses
```

### Data Aggregation Logic

#### Yield Calculation Priority
1. **CeFi Sources** (Higher reliability)
   - Binance Earn (Primary)
   - Kraken Staking 
   - Coinbase Earn

2. **DeFi Sources** (Higher yields, more risk)
   - Aave V3 (Primary)
   - Compound V3
   - Curve Finance

#### Risk Score Algorithm
```
Low Risk: CeFi platforms, regulated exchanges
Medium Risk: Major DeFi protocols (Aave, Compound) 
High Risk: Newer protocols, high yield (>15%)
```

### Caching Strategy
- **Redis** for frequently accessed data (current yields)
- **MongoDB** for persistent storage
- **CDN** for static blog content and images
- **API rate limiting** to prevent abuse

### Security Considerations
- API key management for external services
- Rate limiting on all endpoints
- Input validation and sanitization  
- CORS configuration for production
- User data encryption

### Monitoring & Logging
- API response times
- External API failures
- Data accuracy checks
- User engagement metrics
- Error tracking and alerts

---

## 🎯 Implementation Priority

### Phase 1: Core Data APIs (Week 1)
1. ✅ MongoDB connection and models
2. ✅ DefiLlama integration for DeFi yields
3. ✅ Binance API integration for CeFi yields
4. ✅ Basic yield aggregation logic

### Phase 2: Data Processing (Week 2)  
1. ✅ Historical data collection
2. ✅ Risk score calculation
3. ✅ 24h change tracking
4. ✅ Data validation and cleanup

### Phase 3: User Features (Week 3)
1. ✅ Waitlist/newsletter backend
2. ✅ AI alerts with email notifications
3. ✅ User preference management
4. ✅ Admin dashboard basics

### Phase 4: Production Ready (Week 4)
1. ✅ Caching implementation
2. ✅ Error handling and monitoring
3. ✅ Performance optimization
4. ✅ Security hardening

This contracts document will ensure seamless integration between frontend and backend while building a scalable, production-ready system.