import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { HelmetProvider } from 'react-helmet-async';
import HomePage from "./pages/HomePage";
import BlogPage from "./pages/BlogPage";
import DashboardPage from "./pages/DashboardPage";
import MethodologyPage from "./pages/MethodologyPage";
import YieldIndicesPage from "./pages/YieldIndicesPage";
import RiskAnalyticsPage from "./pages/RiskAnalyticsPage";
import IndexDashboardPage from "./pages/IndexDashboardPage";
import ApiDocumentationPage from "./pages/ApiDocumentationPage";
import { Toaster } from "./components/ui/toaster";

function App() {
  return (
    <HelmetProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/blog" element={<BlogPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/methodology" element={<MethodologyPage />} />
            <Route path="/yield-indices" element={<YieldIndicesPage />} />
            <Route path="/risk-analytics" element={<RiskAnalyticsPage />} />
            <Route path="/index-dashboard" element={<IndexDashboardPage />} />
            <Route path="/api-documentation" element={<ApiDocumentationPage />} />
          </Routes>
          <Toaster />
        </BrowserRouter>
      </div>
    </HelmetProvider>
  );
}

export default App;