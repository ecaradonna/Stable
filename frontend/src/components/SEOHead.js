import React from 'react';
import { Helmet } from 'react-helmet-async';

const SEOHead = ({ 
  title = "StableYield Index (SYI) – Institutional Risk-Adjusted Benchmark for Stablecoins",
  description = "StableYield Index (SYI) is an institutional benchmark of risk-adjusted yields across major USD stablecoins. Transparent methodology, compliance-ready.",
  image = "https://stableyield.com/og/stableyield-og.png",
  url = "https://stableyield.com/",
  type = "website"
}) => {
  return (
    <Helmet>
      {/* Primary SEO */}
      <title>{title}</title>
      <meta name="description" content={description} />
      <link rel="canonical" href={url} />
      
      {/* Open Graph / WhatsApp / LinkedIn */}
      <meta property="og:type" content={type} />
      <meta property="og:site_name" content="StableYield" />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={url} />
      <meta property="og:image" content={image} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:locale" content="en_US" />

      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={image} />
    </Helmet>
  );
};

export default SEOHead;