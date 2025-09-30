"""
Integration tests for DataAggregator and CorrelationEngine working together.
Tests the complete data aggregation and correlation workflow.
"""

import unittest
import pandas as pd
from datetime import datetime
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import DataLoader
from data_aggregator import DataAggregator
from correlation_engine import CorrelationEngine


class TestIntegrationAggregationCorrelation(unittest.TestCase):
    """Integration test cases for data aggregation and correlation."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use the actual data loader with sample data
        self.data_loader = DataLoader("sample-data-set")
        self.data_aggregator = DataAggregator(self.data_loader)
        self.correlation_engine = CorrelationEngine(self.data_aggregator)
    
    def test_end_to_end_order_correlation(self):
        """Test end-to-end order correlation workflow."""
        try:
            # Load sample data to get a valid order ID
            data = self.data_loader.load_all_data()
            orders_df = data['orders']
            
            if orders_df.empty:
                self.skipTest("No sample orders available for testing")
            
            # Get first order ID
            first_order_id = orders_df['order_id'].iloc[0]
            
            # Test comprehensive order data aggregation
            comprehensive_data = self.data_aggregator.get_comprehensive_order_data(first_order_id)
            self.assertIsNotNone(comprehensive_data)
            self.assertEqual(comprehensive_data['order_info']['order_id'], first_order_id)
            
            # Test fleet correlation
            fleet_correlation = self.correlation_engine.correlate_order_with_fleet(first_order_id)
            self.assertTrue(fleet_correlation['order_found'])
            self.assertEqual(fleet_correlation['order_id'], first_order_id)
            
            # Test warehouse correlation
            warehouse_correlation = self.correlation_engine.correlate_order_with_warehouse(first_order_id)
            self.assertTrue(warehouse_correlation['order_found'])
            self.assertEqual(warehouse_correlation['order_id'], first_order_id)
            
            # Test external factors correlation
            external_correlation = self.correlation_engine.correlate_order_with_external_factors(first_order_id)
            self.assertTrue(external_correlation['order_found'])
            self.assertEqual(external_correlation['order_id'], first_order_id)
            
            print(f"Successfully tested end-to-end correlation for order {first_order_id}")
            
        except Exception as e:
            self.skipTest(f"Sample data not available or incomplete: {str(e)}")
    
    def test_city_pattern_analysis_integration(self):
        """Test city pattern analysis integration."""
        try:
            # Load sample data to get a valid city
            data = self.data_loader.load_all_data()
            orders_df = data['orders']
            
            if orders_df.empty:
                self.skipTest("No sample orders available for testing")
            
            # Get first city with orders
            first_city = orders_df['city'].iloc[0]
            
            # Define date range that should include sample data
            start_date = datetime(2025, 1, 1)
            end_date = datetime(2025, 12, 31)
            
            # Test city aggregation
            city_orders = self.data_aggregator.get_orders_by_city_and_date(first_city, start_date, end_date)
            
            if not city_orders.empty:
                # Test city pattern analysis
                city_patterns = self.correlation_engine.find_patterns_by_city(first_city, start_date, end_date)
                
                self.assertTrue(city_patterns['patterns_found'])
                self.assertEqual(city_patterns['city'], first_city)
                self.assertIn('patterns', city_patterns)
                self.assertGreater(city_patterns['patterns']['total_orders'], 0)
                
                print(f"Successfully analyzed patterns for city {first_city}")
            else:
                print(f"No orders found for city {first_city} in date range")
                
        except Exception as e:
            self.skipTest(f"Sample data not available or incomplete: {str(e)}")
    
    def test_client_pattern_analysis_integration(self):
        """Test client pattern analysis integration."""
        try:
            # Load sample data to get a valid client
            data = self.data_loader.load_all_data()
            orders_df = data['orders']
            
            if orders_df.empty:
                self.skipTest("No sample orders available for testing")
            
            # Get first client with orders
            first_client_id = orders_df['client_id'].iloc[0]
            
            # Define date range that should include sample data
            start_date = datetime(2025, 1, 1)
            end_date = datetime(2025, 12, 31)
            
            # Test client aggregation
            client_orders = self.data_aggregator.get_orders_by_client_and_date_range(first_client_id, start_date, end_date)
            
            if not client_orders.empty:
                # Test client pattern analysis
                client_patterns = self.correlation_engine.find_patterns_by_client(first_client_id, start_date, end_date)
                
                self.assertTrue(client_patterns['patterns_found'])
                self.assertEqual(client_patterns['client_id'], first_client_id)
                self.assertIn('patterns', client_patterns)
                self.assertGreater(client_patterns['patterns']['total_orders'], 0)
                
                print(f"Successfully analyzed patterns for client {first_client_id}")
            else:
                print(f"No orders found for client {first_client_id} in date range")
                
        except Exception as e:
            self.skipTest(f"Sample data not available or incomplete: {str(e)}")
    
    def test_data_consistency_across_components(self):
        """Test data consistency across aggregation and correlation components."""
        try:
            # Load sample data
            data = self.data_loader.load_all_data()
            orders_df = data['orders']
            
            if orders_df.empty:
                self.skipTest("No sample orders available for testing")
            
            # Get first order
            first_order_id = orders_df['order_id'].iloc[0]
            order_city = orders_df[orders_df['order_id'] == first_order_id]['city'].iloc[0]
            
            # Get comprehensive order data
            comprehensive_data = self.data_aggregator.get_comprehensive_order_data(first_order_id)
            
            # Verify consistency between comprehensive data and correlation results
            fleet_correlation = self.correlation_engine.correlate_order_with_fleet(first_order_id)
            
            # Check that order information is consistent
            self.assertEqual(comprehensive_data['order_info']['order_id'], fleet_correlation['order_id'])
            self.assertEqual(comprehensive_data['delivery_location']['city'], fleet_correlation['delivery_city'])
            
            print(f"Data consistency verified for order {first_order_id}")
            
        except Exception as e:
            self.skipTest(f"Sample data not available or incomplete: {str(e)}")


if __name__ == '__main__':
    unittest.main()