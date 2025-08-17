// Mock data for StableYield.com
// This will be replaced with real API calls in Phase 2

export const mockYieldData = [
  {
    id: 1,
    stablecoin: "USDT",
    name: "Tether USD",
    currentYield: 8.45,
    source: "Binance Earn",
    sourceType: "CeFi",
    riskScore: "Medium",
    change24h: 0.12,
    liquidity: "$89.2B",
    logo: "https://cryptologos.cc/logos/tether-usdt-logo.png"
  },
  {
    id: 2,
    stablecoin: "USDC",
    name: "USD Coin",
    currentYield: 7.82,
    source: "Aave V3",
    sourceType: "DeFi",
    riskScore: "Low",
    change24h: -0.05,
    liquidity: "$32.1B",
    logo: "https://cryptologos.cc/logos/usd-coin-usdc-logo.png"
  },
  {
    id: 3,
    stablecoin: "DAI",
    name: "Dai Stablecoin",
    currentYield: 6.95,
    source: "Compound",
    sourceType: "DeFi",
    riskScore: "Medium",
    change24h: 0.08,
    liquidity: "$4.8B",
    logo: "https://cryptologos.cc/logos/multi-collateral-dai-dai-logo.png"
  },
  {
    id: 4,
    stablecoin: "PYUSD",
    name: "PayPal USD",
    currentYield: 5.67,
    source: "Curve Finance",
    sourceType: "DeFi",
    riskScore: "Medium",
    change24h: 0.15,
    liquidity: "$890M",
    logo: "https://cryptologos.cc/logos/paypal-usd-pyusd-logo.png"
  },
  {
    id: 5,
    stablecoin: "TUSD",
    name: "TrueUSD",
    currentYield: 4.23,
    source: "Kraken Staking",
    sourceType: "CeFi",
    riskScore: "Low",
    change24h: -0.03,
    liquidity: "$2.1B",
    logo: "https://cryptologos.cc/logos/trueusd-tusd-logo.png"
  }
];

// Historical data for charts (mock 7-day data)
export const mockHistoricalData = {
  USDT: [
    { date: "2025-01-20", yield: 8.33 },
    { date: "2025-01-21", yield: 8.41 },
    { date: "2025-01-22", yield: 8.38 },
    { date: "2025-01-23", yield: 8.45 },
    { date: "2025-01-24", yield: 8.42 },
    { date: "2025-01-25", yield: 8.39 },
    { date: "2025-01-26", yield: 8.45 }
  ],
  USDC: [
    { date: "2025-01-20", yield: 7.75 },
    { date: "2025-01-21", yield: 7.80 },
    { date: "2025-01-22", yield: 7.85 },
    { date: "2025-01-23", yield: 7.87 },
    { date: "2025-01-24", yield: 7.84 },
    { date: "2025-01-25", yield: 7.79 },
    { date: "2025-01-26", yield: 7.82 }
  ],
  DAI: [
    { date: "2025-01-20", yield: 6.87 },
    { date: "2025-01-21", yield: 6.92 },
    { date: "2025-01-22", yield: 6.89 },
    { date: "2025-01-23", yield: 6.95 },
    { date: "2025-01-24", yield: 6.98 },
    { date: "2025-01-25", yield: 6.93 },
    { date: "2025-01-26", yield: 6.95 }
  ]
};

// Newsletter signup data structure
export const newsletterSignups = [];

// Waitlist signup data structure
export const waitlistSignups = [];

// Blog posts mock data
export const mockBlogPosts = [
  {
    id: 1,
    title: "USDT vs USDC: Complete Yield Comparison Guide 2025",
    excerpt: "Comprehensive analysis of the two largest stablecoins and their yield opportunities across CeFi and DeFi platforms.",
    date: "2025-01-25",
    readTime: "8 min read",
    category: "Analysis",
    slug: "usdt-vs-usdc-yield-comparison-2025"
  },
  {
    id: 2,
    title: "Understanding Stablecoin Risk Scores: A Deep Dive",
    excerpt: "How we calculate and assess risk for different stablecoin yield opportunities to help you make informed decisions.",
    date: "2025-01-22",
    readTime: "6 min read",
    category: "Education",
    slug: "understanding-stablecoin-risk-scores"
  }
];