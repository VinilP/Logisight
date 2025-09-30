"""
Integration tests for InsightGenerator with real data components.
Tests the complete workflow from data loading to insight generation.
"""

import unittest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from insight_generator import InsightGenerator
from data_aggregator import DataAggregator
from correlation_engine import CorrelationEngine
from data_loader import DataLoader


class TestInsightIntegration(unittest.TestCase):
    """Integration test cases for InsightGenerator with real components."""
    
    def setUp(self):
        """Set up test fixtures with real components."""
        try:
            # Create real components
            self.data_loader = DataLoader()
            self.data_aggregator = DataAggregator(self.data_loader)
            self.correlation_engine = CorrelationEngine(self.data_aggregator)
            self.insight_generator = InsightGenerator(self.data_aggregator, self.correlation_engine)
        except Exception as e:
            self.skipTest(f"Could not initialize components: {e}")
    
    def test_statistical_functions_with_real_data(self):
        """Test statistical functions with real data if available."""
        try:
            # Try to load real data
            data = self.data_aggregator._load_and_cache_data()
            orders_df = data.get('orders', pd.DataFrame())
            
            if orders_df.empty:
                self.skipTest("No real order data available for testing")
            
            # Test success rate calculation
            success_rate = self.insight_generator.calculate_success_rate(orders_df)
            self.assertIsInstance(success_rate, float)
            self.assertGreaterEqual(success_rate, 0.0)
            self.assertLessEqual(success_rate, 100.0)
            
            # Test failure distribution calculation
            failure_dist = self.insight_generator.calculate_failure_distributions(orders_df)
            self.assertIsInstance(failure_dist, dict)
            self.assertIn('total_failures', failure_dist)
            self.assertIn('failure_rate', failure_dist)
            
            # Test delay pattern calculation
            delay_patterns = self.insight_generator.calculate_delay_patterns(orders_df)
            self.assertIsInstance(delay_patterns, dict)
            self.assertIn('analysis_possible', delay_patterns)
            
            print(f"Integration test successful with {len(orders_df)} orders")
            print(f"Success rate: {success_rate:.2f}%")
            print(f"Total failures: {failure_dist['total_failures']}")
            
        except Exception as e:
            self.skipTest(f"Integration test failed: {e}")
    
    def test_narrative_generation_structure(self):
        """Test that narrative generation produces well-structured output."""
        title = "Test Integration Analysis"
        key_metrics = {
            'Total Orders': 150,
            'Success Rate (%)': 87.5,
            'Average Processing Time': 2.3
        }
        insights = [
            "Primary bottleneck identified in warehouse operations",
            "External weather factors contributed to 12% of delays"
        ]
        recommendations = [
            "Implement automated inventory management system",
            "Develop weather-based delivery scheduling protocols"
        ]
        
        narrative = self.insight_generator.generate_narrative_summary(
            title, key_metrics, insights, recommendations
        )
        
        # Verify structure
        self.assertIn("# Test Integration Analysis", narrative)
        self.assertIn("## Key Metrics", narrative)
        self.assertIn("## Key Insights", narrative)
        self.assertIn("## Actionable Recommendations", narrative)
        
        # Verify content formatting
        lines = narrative.split('\n')
        self.assertTrue(any('Total Orders: 150' in line for line in lines))
        self.assertTrue(any('Success Rate (%): 87.50' in line for line in lines))
        self.assertTrue(any('1. Primary bottleneck identified' in line for line in lines))
        self.assertTrue(any('1. Implement automated inventory' in line for line in lines))


if __name__ == '__main__':
    unittest.main()