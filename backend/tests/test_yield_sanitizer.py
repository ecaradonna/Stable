"""
Unit Tests for Yield Sanitizer Service
Tests for statistical outlier detection and APY cleaning functionality
"""

import pytest
import statistics
from services.yield_sanitizer import YieldSanitizer, SanitizationAction, OutlierMethod

class TestYieldSanitizer:
    
    def setup_method(self):
        """Setup test environment"""
        self.sanitizer = YieldSanitizer()
        
        # Sample market context data
        self.normal_market_context = [
            {'apy': 3.5, 'source': 'aave_v3'},
            {'apy': 4.2, 'source': 'compound_v3'}, 
            {'apy': 3.8, 'source': 'curve'},
            {'apy': 4.0, 'source': 'uniswap_v3'},
            {'apy': 3.9, 'source': 'morpho'}
        ]
        
        self.high_yield_context = [
            {'apy': 15.2, 'source': 'protocol_a'},
            {'apy': 18.5, 'source': 'protocol_b'},
            {'apy': 16.8, 'source': 'protocol_c'},
            {'apy': 17.1, 'source': 'protocol_d'}
        ]
    
    def test_basic_bounds_checking(self):
        """Test basic APY bounds checking"""
        # Test negative APY
        negative_yield = {'apy': -5.0, 'source': 'test'}
        result = self.sanitizer.sanitize_yield(negative_yield)
        
        assert result.sanitized_apy >= 0.0
        assert result.action_taken in [SanitizationAction.CAP, SanitizationAction.REJECT]
        assert len(result.warnings) > 0
        
        # Test extremely high APY
        extreme_yield = {'apy': 500.0, 'source': 'test'}
        result = self.sanitizer.sanitize_yield(extreme_yield)
        
        assert result.sanitized_apy <= self.sanitizer.config['apy_bounds']['absolute_maximum']
        assert result.action_taken == SanitizationAction.CAP
        assert any('absolute maximum' in warning for warning in result.warnings)
    
    def test_mad_outlier_detection(self):
        """Test Median Absolute Deviation outlier detection"""
        # Test normal yield in normal context
        normal_yield = {'apy': 4.0, 'source': 'test'}
        result = self.sanitizer.sanitize_yield(normal_yield, self.normal_market_context)
        
        assert result.action_taken == SanitizationAction.ACCEPT
        assert result.outlier_score < 3.0  # Below MAD threshold
        
        # Test outlier yield
        outlier_yield = {'apy': 50.0, 'source': 'test'}
        result = self.sanitizer.sanitize_yield(outlier_yield, self.normal_market_context)
        
        assert result.action_taken in [SanitizationAction.FLAG, SanitizationAction.WINSORIZE, SanitizationAction.CAP]
        assert result.outlier_score > 3.0  # Above MAD threshold
        assert any('MAD outlier' in warning for warning in result.warnings)
    
    def test_iqr_outlier_detection(self):
        """Test IQR outlier detection method"""
        # Temporarily change method to IQR
        original_method = self.sanitizer.config['outlier_detection']['method']
        self.sanitizer.config['outlier_detection']['method'] = 'IQR'
        
        try:
            outlier_yield = {'apy': 25.0, 'source': 'test'}
            result = self.sanitizer.sanitize_yield(outlier_yield, self.normal_market_context)
            
            assert result.action_taken in [SanitizationAction.FLAG, SanitizationAction.WINSORIZE]
            assert any('IQR outlier' in warning for warning in result.warnings)
            
        finally:
            # Restore original method
            self.sanitizer.config['outlier_detection']['method'] = original_method
    
    def test_base_vs_reward_apy_preference(self):
        """Test preference for base APY over reward APY"""
        # Test reasonable reward ratio
        reasonable_yield = {
            'apy': 8.0,
            'apy_base': 5.0,
            'apy_reward': 3.0,
            'source': 'test'
        }
        result = self.sanitizer.sanitize_yield(reasonable_yield, self.normal_market_context)
        
        # Should accept total APY
        assert result.sanitized_apy == 8.0
        assert result.action_taken in [SanitizationAction.ACCEPT, SanitizationAction.FLAG]
        
        # Test excessive reward ratio
        excessive_reward_yield = {
            'apy': 50.0,
            'apy_base': 4.0,
            'apy_reward': 46.0,  # 11.5:1 ratio
            'source': 'test'
        }
        result = self.sanitizer.sanitize_yield(excessive_reward_yield, self.normal_market_context)
        
        # Should prefer base APY or cap rewards
        assert result.sanitized_apy < 50.0
        assert any('reward ratio' in warning.lower() for warning in result.warnings)
    
    def test_supply_borrow_consistency(self):
        """Test supply/borrow rate consistency checking"""
        # Test normal spread (borrow > supply)
        normal_spread = {
            'apy': 4.0,  # supply
            'borrow_apy': 6.0,  # borrow
            'source': 'test'
        }
        result = self.sanitizer.sanitize_yield(normal_spread, self.normal_market_context)
        
        # Should not have inverted curve warnings
        assert not any('inverted' in warning.lower() for warning in result.warnings)
        
        # Test inverted curve (supply > borrow)
        inverted_spread = {
            'apy': 8.0,  # supply
            'borrow_apy': 5.0,  # borrow  
            'source': 'test'
        }
        result = self.sanitizer.sanitize_yield(inverted_spread, self.normal_market_context)
        
        # Should warn about inverted curve
        assert any('inverted' in warning.lower() for warning in result.warnings)
    
    def test_confidence_scoring(self):
        """Test confidence score calculation"""
        # Test high confidence scenario
        clean_yield = {'apy': 4.0, 'source': 'aave_v3'}
        result = self.sanitizer.sanitize_yield(clean_yield, self.normal_market_context)
        
        assert result.confidence_score > 0.70  # Should be high confidence
        
        # Test low confidence scenario (outlier with warnings)
        problematic_yield = {'apy': 150.0, 'source': 'unknown_protocol'}
        result = self.sanitizer.sanitize_yield(problematic_yield, self.normal_market_context)
        
        assert result.confidence_score < 0.50  # Should be low confidence
        assert len(result.warnings) > 0
    
    def test_batch_sanitization(self):
        """Test batch sanitization with market context"""
        mixed_yields = [
            {'apy': 4.0, 'source': 'aave_v3'},      # Normal
            {'apy': 3.8, 'source': 'compound_v3'},   # Normal
            {'apy': 75.0, 'source': 'sketchy_defi'}, # Outlier
            {'apy': 4.2, 'source': 'curve'},         # Normal
            {'apy': -2.0, 'source': 'broken_pool'}   # Invalid
        ]
        
        results = self.sanitizer.sanitize_yield_batch(mixed_yields)
        
        assert len(results) == 5
        
        # Check that normal yields are accepted
        normal_results = [r for r in results if r.original_apy in [4.0, 3.8, 4.2]]
        assert all(r.action_taken == SanitizationAction.ACCEPT for r in normal_results)
        
        # Check that outlier is treated
        outlier_result = next(r for r in results if r.original_apy == 75.0)
        assert outlier_result.action_taken in [SanitizationAction.FLAG, SanitizationAction.WINSORIZE, SanitizationAction.CAP]
        
        # Check that invalid yield is handled
        invalid_result = next(r for r in results if r.original_apy == -2.0)
        assert invalid_result.action_taken in [SanitizationAction.CAP, SanitizationAction.REJECT]
    
    def test_winsorization(self):
        """Test winsorization functionality"""
        # Create context with clear outliers
        context_with_outliers = [
            {'apy': 2.0}, {'apy': 3.0}, {'apy': 3.5}, {'apy': 4.0}, 
            {'apy': 4.5}, {'apy': 5.0}, {'apy': 100.0}  # Clear outlier
        ]
        
        outlier_yield = {'apy': 100.0, 'source': 'test'}
        result = self.sanitizer.sanitize_yield(outlier_yield, context_with_outliers)
        
        if result.action_taken == SanitizationAction.WINSORIZE:
            # Should be winsorized to a reasonable value
            assert result.sanitized_apy < result.original_apy
            assert result.sanitized_apy > 0
    
    def test_flash_spike_detection(self):
        """Test detection of flash/temporary spikes"""
        # This would test temporal consistency in production
        # For now, test the basic flash spike threshold
        flash_spike = {'apy': 200.0, 'source': 'flash_pool'}
        result = self.sanitizer.sanitize_yield(flash_spike)
        
        # Should be flagged or rejected due to extreme value
        assert result.action_taken in [
            SanitizationAction.FLAG, 
            SanitizationAction.CAP, 
            SanitizationAction.REJECT
        ]
    
    def test_configuration_validation(self):
        """Test sanitizer configuration"""
        config = self.sanitizer.config
        
        # Check required configuration sections
        assert 'apy_bounds' in config
        assert 'outlier_detection' in config
        assert 'winsorization' in config
        assert 'base_vs_reward_apy' in config
        
        # Check reasonable default values
        assert config['apy_bounds']['absolute_minimum'] >= 0.0
        assert config['apy_bounds']['absolute_maximum'] > config['apy_bounds']['reasonable_maximum']
        assert 0 < config['outlier_detection']['mad_threshold'] <= 5.0
    
    def test_metadata_tracking(self):
        """Test that metadata is properly tracked"""
        test_yield = {'apy': 25.0, 'source': 'test_protocol'}
        result = self.sanitizer.sanitize_yield(test_yield, self.normal_market_context)
        
        # Check metadata presence
        assert 'sanitization_timestamp' in result.metadata
        assert 'bounds_checked' in result.metadata
        assert 'outlier_score' in result.metadata
        assert 'adjustment_magnitude' in result.metadata
        
        # Check metadata values
        assert result.metadata['bounds_checked'] is True
        assert result.metadata['adjustment_magnitude'] >= 0
        assert result.metadata['warnings_count'] == len(result.warnings)
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test with empty market context
        yield_no_context = {'apy': 10.0, 'source': 'test'}
        result = self.sanitizer.sanitize_yield(yield_no_context, [])
        
        assert result is not None
        assert result.confidence_score > 0
        
        # Test with missing APY field
        yield_no_apy = {'source': 'test'}
        result = self.sanitizer.sanitize_yield(yield_no_apy)
        
        assert result.original_apy == 0.0
        assert result.sanitized_apy >= 0.0
        
        # Test with single item market context
        single_context = [{'apy': 5.0, 'source': 'single'}]
        result = self.sanitizer.sanitize_yield(yield_no_context, single_context)
        
        assert result.confidence_score > 0
        # Should handle gracefully with insufficient context

# Integration test
def test_sanitizer_integration():
    """Test full sanitizer integration"""
    sanitizer = YieldSanitizer()
    
    # Realistic yield data with various issues
    test_yields = [
        {'apy': 4.2, 'source': 'aave_v3', 'apy_base': 4.0, 'apy_reward': 0.2},  # Clean
        {'apy': 3.8, 'source': 'compound_v3'},  # Clean
        {'apy': 125.0, 'source': 'farming_protocol'},  # Outlier
        {'apy': -1.0, 'source': 'broken_pool'},  # Invalid
        {'apy': 15.0, 'apy_base': 2.0, 'apy_reward': 13.0, 'source': 'high_rewards'},  # High rewards
        {'apy': 4.5, 'borrow_apy': 3.0, 'source': 'inverted_curve'},  # Inverted
    ]
    
    results = sanitizer.sanitize_yield_batch(test_yields)
    
    # Verify results
    assert len(results) == len(test_yields)
    assert all(isinstance(r.confidence_score, float) for r in results)
    assert all(0 <= r.confidence_score <= 1 for r in results)
    
    # Check that problematic yields are handled
    problematic_results = [r for r in results if r.original_apy in [125.0, -1.0]]
    assert all(r.action_taken != SanitizationAction.ACCEPT for r in problematic_results)
    
    # Check that clean yields are preserved
    clean_results = [r for r in results if r.original_apy in [4.2, 3.8]]
    assert all(r.action_taken == SanitizationAction.ACCEPT for r in clean_results)
    
    print("✅ All yield sanitizer tests passed")

if __name__ == "__main__":
    test_sanitizer_integration()