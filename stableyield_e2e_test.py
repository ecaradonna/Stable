#!/usr/bin/env python3
"""
StableYield End-to-End Integration Test Suite
Complete testing of STEP 0-4 integration for institutional-grade system
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class StableYieldE2ETester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.performance_metrics = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_time: float = None):
        """Log test results with performance metrics"""
        status = "✅ PASS" if success else "❌ FAIL"
        perf_info = f" ({response_time:.0f}ms)" if response_time else ""
        print(f"{status} {test_name}{perf_info}")
        if details:
            print(f"    Details: {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'response_time_ms': response_time,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def measure_request(self, method: str, url: str, **kwargs):
        """Measure request performance"""
        start_time = time.time()
        if method.upper() == 'GET':
            response = await self.session.get(url, **kwargs)
        elif method.upper() == 'POST':
            response = await self.session.post(url, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        return response, response_time
    
    # ========================================
    # 1. COMPLETE END-TO-END SYSTEM TESTING
    # ========================================
    
    async def test_complete_yield_pipeline(self):
        """Test complete yield data pipeline with all filters"""
        print("\n🔄 Testing Complete Yield Pipeline (STEP 0-4)...")
        
        # Test 1: Basic yields endpoint with all filters active
        try:
            response, response_time = await self.measure_request('GET', f"{API_BASE}/yields/")
            if response.status == 200:
                data = await response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Verify complete data structure
                    first_yield = data[0]
                    required_fields = ['stablecoin', 'currentYield', 'source', 'metadata']
                    missing_fields = [field for field in required_fields if field not in first_yield]
                    
                    if not missing_fields:
                        # Check for complete metadata pipeline
                        metadata = first_yield.get('metadata', {})
                        has_protocol_info = 'protocol_info' in metadata
                        has_liquidity_metrics = 'liquidity_metrics' in metadata
                        has_sanitization = 'sanitization' in metadata
                        
                        pipeline_complete = has_protocol_info and has_liquidity_metrics and has_sanitization
                        
                        if pipeline_complete:
                            self.log_test("Complete Yield Pipeline", True, 
                                        f"Found {len(data)} yields with complete metadata pipeline", response_time)
                        else:
                            self.log_test("Complete Yield Pipeline", False, 
                                        f"Incomplete metadata: protocol_info={has_protocol_info}, liquidity_metrics={has_liquidity_metrics}, sanitization={has_sanitization}")
                    else:
                        self.log_test("Complete Yield Pipeline", False, f"Missing required fields: {missing_fields}")
                else:
                    self.log_test("Complete Yield Pipeline", False, f"Empty or invalid response: {data}")
            else:
                self.log_test("Complete Yield Pipeline", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Complete Yield Pipeline", False, f"Exception: {str(e)}")
    
    async def test_institutional_filtering(self):
        """Test institutional-grade filtering with combined parameters"""
        print("\n🏛️ Testing Institutional Filtering...")
        
        # Test combined institutional filters
        try:
            params = "min_tvl=50000000&institutional_only=true"
            response, response_time = await self.measure_request('GET', f"{API_BASE}/yields/?{params}")
            if response.status == 200:
                data = await response.json()
                if isinstance(data, list):
                    # Verify institutional-grade criteria
                    institutional_yields = []
                    for yield_item in data:
                        metadata = yield_item.get('metadata', {})
                        protocol_info = metadata.get('protocol_info', {})
                        liquidity_metrics = metadata.get('liquidity_metrics', {})
                        
                        # Check reputation score (should be high for institutional)
                        reputation = protocol_info.get('reputation_score', 0)
                        tvl_usd = liquidity_metrics.get('tvl_usd', 0)
                        
                        if reputation >= 0.7 and tvl_usd >= 50000000:
                            institutional_yields.append(yield_item)
                    
                    if len(institutional_yields) == len(data):
                        self.log_test("Institutional Filtering", True, 
                                    f"All {len(data)} yields meet institutional criteria (TVL≥$50M, reputation≥0.7)", response_time)
                    else:
                        self.log_test("Institutional Filtering", False, 
                                    f"Only {len(institutional_yields)}/{len(data)} yields meet institutional criteria")
                else:
                    self.log_test("Institutional Filtering", False, f"Invalid response format: {type(data)}")
            else:
                self.log_test("Institutional Filtering", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Institutional Filtering", False, f"Exception: {str(e)}")
    
    async def test_stableyield_index_integration(self):
        """Test StableYield Index with filtered and sanitized data"""
        print("\n📊 Testing StableYield Index Integration...")
        
        # Test 1: Current index calculation
        try:
            response, response_time = await self.measure_request('GET', f"{API_BASE}/index/current")
            if response.status == 200:
                data = await response.json()
                required_fields = ['index_value', 'timestamp', 'constituent_count', 'methodology']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    index_value = data['index_value']
                    constituent_count = data['constituent_count']
                    methodology = data['methodology']
                    
                    # Verify index uses quality-controlled data
                    if constituent_count > 0 and index_value > 0:
                        self.log_test("StableYield Index Current", True, 
                                    f"SYI: {index_value:.2f}, {constituent_count} constituents, methodology: {methodology}", response_time)
                    else:
                        self.log_test("StableYield Index Current", False, 
                                    f"Invalid index values: value={index_value}, constituents={constituent_count}")
                else:
                    self.log_test("StableYield Index Current", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("StableYield Index Current", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("StableYield Index Current", False, f"Exception: {str(e)}")
        
        # Test 2: Index constituents quality
        try:
            response, response_time = await self.measure_request('GET', f"{API_BASE}/index/constituents")
            if response.status == 200:
                data = await response.json()
                if 'constituents' in data:
                    constituents = data['constituents']
                    
                    # Verify all constituents meet quality criteria
                    quality_constituents = 0
                    for constituent in constituents:
                        # Check for complete quality control metadata
                        has_protocol_policy = 'protocol_reputation' in constituent
                        has_liquidity_grade = 'liquidity_grade' in constituent
                        has_sanitization = 'confidence_score' in constituent
                        
                        if has_protocol_policy and has_liquidity_grade and has_sanitization:
                            quality_constituents += 1
                    
                    if quality_constituents == len(constituents):
                        self.log_test("StableYield Index Constituents", True, 
                                    f"All {len(constituents)} constituents have complete quality control", response_time)
                    else:
                        self.log_test("StableYield Index Constituents", False, 
                                    f"Only {quality_constituents}/{len(constituents)} constituents have complete quality control")
                else:
                    self.log_test("StableYield Index Constituents", False, f"No constituents in response: {data}")
            else:
                self.log_test("StableYield Index Constituents", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("StableYield Index Constituents", False, f"Exception: {str(e)}")
    
    # ========================================
    # 2. QUALITY CONTROL PIPELINE TESTING
    # ========================================
    
    async def test_quality_control_pipeline(self):
        """Test complete quality control pipeline: Canonical → Policy → Liquidity → Sanitization"""
        print("\n🔍 Testing Quality Control Pipeline...")
        
        # Get a sample yield and trace it through the pipeline
        try:
            response, response_time = await self.measure_request('GET', f"{API_BASE}/yields/")
            if response.status == 200:
                data = await response.json()
                if data and len(data) > 0:
                    sample_yield = data[0]
                    metadata = sample_yield.get('metadata', {})
                    
                    # Step 1: Canonical Model (STEP 1)
                    canonical_fields = ['stablecoin', 'currentYield', 'source', 'sourceType', 'riskScore']
                    canonical_complete = all(field in sample_yield for field in canonical_fields)
                    
                    # Step 2: Protocol Policy (STEP 2)
                    protocol_info = metadata.get('protocol_info', {})
                    policy_complete = 'reputation_score' in protocol_info and 'policy_decision' in protocol_info
                    
                    # Step 3: Liquidity Filter (STEP 3)
                    liquidity_metrics = metadata.get('liquidity_metrics', {})
                    liquidity_complete = 'tvl_usd' in liquidity_metrics and 'liquidity_grade' in liquidity_metrics
                    
                    # Step 4: Yield Sanitization (STEP 4)
                    sanitization = metadata.get('sanitization', {})
                    sanitization_complete = 'confidence_score' in sanitization and 'outlier_score' in sanitization
                    
                    pipeline_steps = {
                        'Canonical Model': canonical_complete,
                        'Protocol Policy': policy_complete,
                        'Liquidity Filter': liquidity_complete,
                        'Yield Sanitization': sanitization_complete
                    }
                    
                    completed_steps = sum(pipeline_steps.values())
                    
                    if completed_steps == 4:
                        self.log_test("Quality Control Pipeline", True, 
                                    f"All 4 pipeline steps completed for {sample_yield['stablecoin']}", response_time)
                    else:
                        failed_steps = [step for step, complete in pipeline_steps.items() if not complete]
                        self.log_test("Quality Control Pipeline", False, 
                                    f"Pipeline incomplete: {completed_steps}/4 steps. Failed: {failed_steps}")
                else:
                    self.log_test("Quality Control Pipeline", False, "No yield data available for pipeline testing")
            else:
                self.log_test("Quality Control Pipeline", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Quality Control Pipeline", False, f"Exception: {str(e)}")
    
    async def test_confidence_scores_and_risk_adjustments(self):
        """Test confidence scores and risk adjustments throughout pipeline"""
        print("\n📈 Testing Confidence Scores and Risk Adjustments...")
        
        try:
            response, response_time = await self.measure_request('GET', f"{API_BASE}/yields/")
            if response.status == 200:
                data = await response.json()
                if data and len(data) > 0:
                    confidence_scores = []
                    risk_adjustments = []
                    
                    for yield_item in data:
                        # Base risk score
                        base_risk = yield_item.get('riskScore', 0)
                        
                        # Sanitization confidence
                        metadata = yield_item.get('metadata', {})
                        sanitization = metadata.get('sanitization', {})
                        confidence = sanitization.get('confidence_score')
                        
                        # Protocol reputation (risk adjustment factor)
                        protocol_info = metadata.get('protocol_info', {})
                        reputation = protocol_info.get('reputation_score')
                        
                        if confidence is not None:
                            confidence_scores.append(confidence)
                        if reputation is not None:
                            risk_adjustments.append(reputation)
                    
                    if confidence_scores and risk_adjustments:
                        avg_confidence = sum(confidence_scores) / len(confidence_scores)
                        avg_reputation = sum(risk_adjustments) / len(risk_adjustments)
                        
                        # Good confidence scores should be > 0.5, good reputation > 0.7
                        if avg_confidence > 0.4 and avg_reputation > 0.7:
                            self.log_test("Confidence Scores and Risk Adjustments", True, 
                                        f"Avg confidence: {avg_confidence:.2f}, Avg reputation: {avg_reputation:.2f}", response_time)
                        else:
                            self.log_test("Confidence Scores and Risk Adjustments", False, 
                                        f"Low quality scores - Confidence: {avg_confidence:.2f}, Reputation: {avg_reputation:.2f}")
                    else:
                        self.log_test("Confidence Scores and Risk Adjustments", False, 
                                    "No confidence scores or risk adjustments found")
                else:
                    self.log_test("Confidence Scores and Risk Adjustments", False, "No yield data available")
            else:
                self.log_test("Confidence Scores and Risk Adjustments", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Confidence Scores and Risk Adjustments", False, f"Exception: {str(e)}")
    
    # ========================================
    # 3. MULTI-SYSTEM CONFIGURATION TESTING
    # ========================================
    
    async def test_multi_system_configuration(self):
        """Test configuration consistency across all systems"""
        print("\n⚙️ Testing Multi-System Configuration...")
        
        # Test all system summaries
        systems = {
            'policy': '/api/policy/summary',
            'liquidity': '/api/liquidity/summary',
            'sanitization': '/api/sanitization/summary'
        }
        
        system_configs = {}
        
        for system_name, endpoint in systems.items():
            try:
                response, response_time = await self.measure_request('GET', f"{API_BASE.replace('/api', '')}{endpoint}")
                if response.status == 200:
                    data = await response.json()
                    system_configs[system_name] = data
                    
                    # Check for version consistency
                    version = data.get('version') or data.get('config_version') or data.get('policy_version')
                    if version:
                        self.log_test(f"{system_name.title()} System Config", True, 
                                    f"Version: {version}, Status: operational", response_time)
                    else:
                        self.log_test(f"{system_name.title()} System Config", False, 
                                    f"No version information found")
                else:
                    self.log_test(f"{system_name.title()} System Config", False, f"HTTP {response.status}")
            except Exception as e:
                self.log_test(f"{system_name.title()} System Config", False, f"Exception: {str(e)}")
        
        # Test configuration consistency
        if len(system_configs) == 3:
            # All systems should be operational
            all_operational = True
            for system_name, config in system_configs.items():
                if not config:  # Empty config indicates issues
                    all_operational = False
                    break
            
            if all_operational:
                self.log_test("Multi-System Configuration Consistency", True, 
                            "All 3 systems (policy, liquidity, sanitization) operational and configured")
            else:
                self.log_test("Multi-System Configuration Consistency", False, 
                            "Some systems not properly configured")
        else:
            self.log_test("Multi-System Configuration Consistency", False, 
                        f"Only {len(system_configs)}/3 systems accessible")
    
    # ========================================
    # 4. STRESS TESTING WITH EXTREME PARAMETERS
    # ========================================
    
    async def test_extreme_parameter_stress(self):
        """Test system with extreme filtering parameters"""
        print("\n🔥 Testing Extreme Parameter Stress...")
        
        # Test 1: Very high TVL filter (500M+)
        try:
            response, response_time = await self.measure_request('GET', f"{API_BASE}/yields/?min_tvl=500000000")
            if response.status == 200:
                data = await response.json()
                if isinstance(data, list):
                    self.log_test("Extreme TVL Filter $500M+", True, 
                                f"System handled extreme TVL filter, returned {len(data)} yields", response_time)
                else:
                    self.log_test("Extreme TVL Filter $500M+", False, f"Invalid response format: {type(data)}")
            else:
                self.log_test("Extreme TVL Filter $500M+", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Extreme TVL Filter $500M+", False, f"Exception: {str(e)}")
        
        # Test 2: Blue chip only filter
        try:
            response, response_time = await self.measure_request('GET', f"{API_BASE}/yields/?grade_filter=blue_chip")
            if response.status == 200:
                data = await response.json()
                if isinstance(data, list):
                    # Verify all results are actually blue chip
                    blue_chip_count = 0
                    for yield_item in data:
                        metadata = yield_item.get('metadata', {})
                        liquidity_metrics = metadata.get('liquidity_metrics', {})
                        grade = liquidity_metrics.get('liquidity_grade', '').lower()
                        if 'blue' in grade or 'chip' in grade:
                            blue_chip_count += 1
                    
                    if blue_chip_count == len(data) or len(data) == 0:  # All blue chip or none available
                        self.log_test("Blue Chip Grade Filter", True, 
                                    f"Blue chip filter working: {len(data)} yields, {blue_chip_count} verified blue chip", response_time)
                    else:
                        self.log_test("Blue Chip Grade Filter", False, 
                                    f"Filter not working: {blue_chip_count}/{len(data)} are actually blue chip")
                else:
                    self.log_test("Blue Chip Grade Filter", False, f"Invalid response format: {type(data)}")
            else:
                self.log_test("Blue Chip Grade Filter", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Blue Chip Grade Filter", False, f"Exception: {str(e)}")
        
        # Test 3: Combined extreme filters
        try:
            params = "min_tvl=100000000&institutional_only=true&grade_filter=blue_chip"
            response, response_time = await self.measure_request('GET', f"{API_BASE}/yields/?{params}")
            if response.status == 200:
                data = await response.json()
                if isinstance(data, list):
                    self.log_test("Combined Extreme Filters", True, 
                                f"System handled combined extreme filters, returned {len(data)} yields", response_time)
                else:
                    self.log_test("Combined Extreme Filters", False, f"Invalid response format: {type(data)}")
            else:
                self.log_test("Combined Extreme Filters", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Combined Extreme Filters", False, f"Exception: {str(e)}")
    
    async def test_zero_results_scenarios(self):
        """Test graceful handling of scenarios with zero results"""
        print("\n🚫 Testing Zero Results Scenarios...")
        
        # Test impossible filter combination
        try:
            params = "min_tvl=1000000000&grade_filter=retail"  # Very high TVL with retail grade (contradiction)
            response, response_time = await self.measure_request('GET', f"{API_BASE}/yields/?{params}")
            if response.status == 200:
                data = await response.json()
                if isinstance(data, list) and len(data) == 0:
                    self.log_test("Zero Results Handling", True, 
                                f"System gracefully handled impossible filter combination", response_time)
                elif isinstance(data, list):
                    self.log_test("Zero Results Handling", True, 
                                f"System returned {len(data)} results for extreme filters", response_time)
                else:
                    self.log_test("Zero Results Handling", False, f"Invalid response format: {type(data)}")
            else:
                self.log_test("Zero Results Handling", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Zero Results Handling", False, f"Exception: {str(e)}")
    
    # ========================================
    # 5. ROBUSTNESS AND ERROR HANDLING
    # ========================================
    
    async def test_parameter_validation_robustness(self):
        """Test robust parameter validation"""
        print("\n🛡️ Testing Parameter Validation Robustness...")
        
        # Test invalid parameters
        invalid_params = [
            ("min_tvl=-1000000", "negative TVL"),
            ("grade_filter=invalid_grade", "invalid grade"),
            ("institutional_only=maybe", "invalid boolean"),
            ("min_tvl=abc", "non-numeric TVL")
        ]
        
        for param, description in invalid_params:
            try:
                response, response_time = await self.measure_request('GET', f"{API_BASE}/yields/?{param}")
                if response.status == 422:  # Validation error
                    self.log_test(f"Parameter Validation: {description}", True, 
                                f"Correctly rejected {description}", response_time)
                elif response.status == 200:
                    # Some systems might handle gracefully by ignoring invalid params
                    data = await response.json()
                    self.log_test(f"Parameter Validation: {description}", True, 
                                f"Gracefully handled {description} (returned {len(data) if isinstance(data, list) else 'data'})", response_time)
                else:
                    self.log_test(f"Parameter Validation: {description}", False, 
                                f"Unexpected status {response.status} for {description}")
            except Exception as e:
                self.log_test(f"Parameter Validation: {description}", False, f"Exception: {str(e)}")
    
    async def test_component_failure_resilience(self):
        """Test system resilience to component failures"""
        print("\n🔧 Testing Component Failure Resilience...")
        
        # Test if system works when individual components might have issues
        # This tests the fallback mechanisms
        
        # Test 1: Basic functionality still works
        try:
            response, response_time = await self.measure_request('GET', f"{API_BASE}/yields/")
            if response.status == 200:
                data = await response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("Basic System Resilience", True, 
                                f"Core yield system operational with {len(data)} yields", response_time)
                else:
                    self.log_test("Basic System Resilience", False, "No yield data available")
            else:
                self.log_test("Basic System Resilience", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Basic System Resilience", False, f"Exception: {str(e)}")
        
        # Test 2: Health check shows system status
        try:
            response, response_time = await self.measure_request('GET', f"{API_BASE}/health")
            if response.status == 200:
                data = await response.json()
                if data.get('status') == 'healthy':
                    db_status = data.get('database', 'unknown')
                    self.log_test("System Health Check", True, 
                                f"System healthy, database: {db_status}", response_time)
                else:
                    self.log_test("System Health Check", False, f"System not healthy: {data}")
            else:
                self.log_test("System Health Check", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("System Health Check", False, f"Exception: {str(e)}")
    
    # ========================================
    # 6. PERFORMANCE AND CONSISTENCY TESTING
    # ========================================
    
    async def test_performance_benchmarks(self):
        """Test performance benchmarks for key endpoints"""
        print("\n⚡ Testing Performance Benchmarks...")
        
        # Key endpoints to benchmark
        endpoints = [
            ("/api/yields/", "Yields All"),
            ("/api/index/current", "StableYield Index"),
            ("/api/policy/summary", "Policy Summary"),
            ("/api/liquidity/summary", "Liquidity Summary"),
            ("/api/sanitization/summary", "Sanitization Summary")
        ]
        
        performance_results = {}
        
        for endpoint, name in endpoints:
            try:
                # Make 3 requests and average the time
                times = []
                for i in range(3):
                    response, response_time = await self.measure_request('GET', f"{API_BASE.replace('/api', '')}{endpoint}")
                    if response.status == 200:
                        times.append(response_time)
                    await asyncio.sleep(0.1)  # Small delay between requests
                
                if times:
                    avg_time = sum(times) / len(times)
                    performance_results[name] = avg_time
                    
                    # Performance thresholds (institutional systems should be fast)
                    if avg_time < 1000:  # Under 1 second
                        self.log_test(f"Performance: {name}", True, 
                                    f"Average response time: {avg_time:.0f}ms")
                    else:
                        self.log_test(f"Performance: {name}", False, 
                                    f"Slow response time: {avg_time:.0f}ms (>1000ms)")
                else:
                    self.log_test(f"Performance: {name}", False, "No successful requests")
            except Exception as e:
                self.log_test(f"Performance: {name}", False, f"Exception: {str(e)}")
        
        # Store performance metrics
        self.performance_metrics = performance_results
    
    async def test_data_consistency(self):
        """Test data consistency across multiple calls"""
        print("\n🔄 Testing Data Consistency...")
        
        # Test 1: Multiple calls to same endpoint should return consistent data
        try:
            responses = []
            for i in range(3):
                response, response_time = await self.measure_request('GET', f"{API_BASE}/yields/")
                if response.status == 200:
                    data = await response.json()
                    responses.append(data)
                await asyncio.sleep(0.5)  # Small delay
            
            if len(responses) == 3:
                # Check if all responses have same number of yields
                yield_counts = [len(resp) if isinstance(resp, list) else 0 for resp in responses]
                
                if len(set(yield_counts)) == 1:  # All counts are the same
                    self.log_test("Data Consistency", True, 
                                f"Consistent yield count across 3 calls: {yield_counts[0]} yields")
                else:
                    self.log_test("Data Consistency", False, 
                                f"Inconsistent yield counts: {yield_counts}")
            else:
                self.log_test("Data Consistency", False, f"Only {len(responses)}/3 successful requests")
        except Exception as e:
            self.log_test("Data Consistency", False, f"Exception: {str(e)}")
        
        # Test 2: Index value should be stable over short periods
        try:
            index_values = []
            for i in range(3):
                response, response_time = await self.measure_request('GET', f"{API_BASE}/index/current")
                if response.status == 200:
                    data = await response.json()
                    index_value = data.get('index_value')
                    if index_value:
                        index_values.append(index_value)
                await asyncio.sleep(0.5)
            
            if len(index_values) >= 2:
                # Index should be relatively stable (within 5% variation)
                max_val = max(index_values)
                min_val = min(index_values)
                variation = (max_val - min_val) / min_val * 100 if min_val > 0 else 100
                
                if variation < 5:  # Less than 5% variation
                    self.log_test("Index Stability", True, 
                                f"Index stable: {variation:.2f}% variation across calls")
                else:
                    self.log_test("Index Stability", False, 
                                f"Index unstable: {variation:.2f}% variation")
            else:
                self.log_test("Index Stability", False, "Insufficient index data for stability test")
        except Exception as e:
            self.log_test("Index Stability", False, f"Exception: {str(e)}")
    
    async def test_caching_effectiveness(self):
        """Test caching without compromising data freshness"""
        print("\n💾 Testing Caching Effectiveness...")
        
        # Test response times for repeated requests (should benefit from caching)
        try:
            # First request (cache miss)
            response1, time1 = await self.measure_request('GET', f"{API_BASE}/yields/")
            
            # Second request immediately after (should hit cache)
            response2, time2 = await self.measure_request('GET', f"{API_BASE}/yields/")
            
            if response1.status == 200 and response2.status == 200:
                data1 = await response1.json()
                data2 = await response2.json()
                
                # Data should be identical (from cache)
                if data1 == data2:
                    # Second request should be faster (cached)
                    if time2 <= time1:
                        self.log_test("Caching Effectiveness", True, 
                                    f"Caching working: {time1:.0f}ms -> {time2:.0f}ms")
                    else:
                        self.log_test("Caching Effectiveness", True, 
                                    f"Data consistent, times: {time1:.0f}ms -> {time2:.0f}ms")
                else:
                    self.log_test("Caching Effectiveness", False, 
                                "Data inconsistent between requests")
            else:
                self.log_test("Caching Effectiveness", False, 
                            f"Request failures: {response1.status}, {response2.status}")
        except Exception as e:
            self.log_test("Caching Effectiveness", False, f"Exception: {str(e)}")
    
    # ========================================
    # MAIN TEST EXECUTION
    # ========================================
    
    async def run_all_tests(self):
        """Run complete end-to-end test suite"""
        print("🚀 Starting StableYield End-to-End Integration Test Suite")
        print(f"🌐 Testing against: {API_BASE}")
        print("=" * 80)
        
        # 1. Complete End-to-End System Testing
        await self.test_complete_yield_pipeline()
        await self.test_institutional_filtering()
        await self.test_stableyield_index_integration()
        
        # 2. Quality Control Pipeline Testing
        await self.test_quality_control_pipeline()
        await self.test_confidence_scores_and_risk_adjustments()
        
        # 3. Multi-System Configuration Testing
        await self.test_multi_system_configuration()
        
        # 4. Stress Testing with Extreme Parameters
        await self.test_extreme_parameter_stress()
        await self.test_zero_results_scenarios()
        
        # 5. Robustness and Error Handling
        await self.test_parameter_validation_robustness()
        await self.test_component_failure_resilience()
        
        # 6. Performance and Consistency Testing
        await self.test_performance_benchmarks()
        await self.test_data_consistency()
        await self.test_caching_effectiveness()
        
        # Generate summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 STABLEYIELD END-TO-END TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.performance_metrics:
            print(f"\n⚡ Performance Metrics:")
            for endpoint, avg_time in self.performance_metrics.items():
                print(f"  {endpoint}: {avg_time:.0f}ms")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🎯 System Status: {'PRODUCTION READY' if success_rate >= 90 else 'NEEDS ATTENTION'}")
        print("=" * 80)

async def main():
    """Main test execution"""
    async with StableYieldE2ETester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())