"""
Unit tests for DataAggregator class.
Tests data aggregation and merging functionality across multiple CSV sources.
"""

import unittest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_aggregator import DataAggregator
from data_loader import DataLoader


class TestDataAggregator(unittest.TestCase):
    """Test cases for DataAggregator functionality."""
    
    def setUp(self):
        """Set up test fixtures with mock data."""
        self.mock_data_loader = Mock(spec=DataLoader)
        self.aggregator = DataAggregator(self.mock_data_loader)
        
        # Create sample test data
        self.sample_orders = pd.DataFrame({
            'order_id': [1, 2, 3],
            'client_id': [101, 102, 101],
            'customer_name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'customer_phone': ['+911234567890', '+919876543210', '+915555555555'],
            'delivery_address_line1': ['123 Main St', '456 Oak Ave', '789 Pine Rd'],
            'delivery_address_line2': ['Apt 1', '', 'Suite 5'],
            'city': ['Mumbai', 'Delhi', 'Mumbai'],
            'state': ['Maharashtra', 'Delhi', 'Maharashtra'],
            'pincode': ['400001', '110001', '400002'],
            'order_date': ['2025-01-15 10:00:00', '2025-01-16 11:00:00', '2025-01-17 12:00:00'],
            'promised_delivery_date': ['2025-01-17 10:00:00', '2025-01-18 11:00:00', '2025-01-19 12:00:00'],
            'actual_delivery_date': ['2025-01-17 15:00:00', '', '2025-01-19 18:00:00'],
            'status': ['Delivered', 'Failed', 'Delivered'],
            'payment_mode': ['COD', 'Online', 'COD'],
            'amount': [1500.0, 2000.0, 1200.0],
            'failure_reason': ['', 'Address not found', ''],
            'created_at': ['2025-01-15 09:00:00', '2025-01-16 10:00:00', '2025-01-17 11:00:00']
        })
        
        self.sample_clients = pd.DataFrame({
            'client_id': [101, 102],
            'client_name': ['ABC Corp', 'XYZ Ltd'],
            'gst_number': ['27ABCDE0001F1Z1', '27ABCDE0002F1Z2'],
            'contact_person': ['Alice Manager', 'Bob Director'],
            'contact_phone': ['+911111111111', '+912222222222'],
            'contact_email': ['alice@abc.com', 'bob@xyz.com'],
            'created_at': ['2024-01-01 00:00:00', '2024-01-02 00:00:00']
        })
        
        self.sample_fleet_logs = pd.DataFrame({
            'fleet_log_id': [1, 2],
            'order_id': [1, 3],
            'driver_id': [201, 202],
            'vehicle_number': ['MH01AB1234', 'MH02CD5678'],
            'route_code': ['R1', 'R2'],
            'gps_delay_notes': ['Traffic jam', 'Vehicle breakdown'],
            'departure_time': ['2025-01-17 08:00:00', '2025-01-19 09:00:00'],
            'arrival_time': ['2025-01-17 15:00:00', '2025-01-19 18:00:00'],
            'created_at': ['2025-01-17 07:00:00', '2025-01-19 08:00:00']
        })
        
        self.sample_drivers = pd.DataFrame({
            'driver_id': [201, 202],
            'driver_name': ['Driver One', 'Driver Two'],
            'phone': ['+913333333333', '+914444444444'],
            'partner_company': ['Fast Delivery', 'Quick Transport'],
            'city': ['Mumbai', 'Mumbai'],
            'state': ['Maharashtra', 'Maharashtra'],
            'created_at': ['2024-06-01 00:00:00', '2024-06-02 00:00:00']
        })
        
        self.sample_warehouse_logs = pd.DataFrame({
            'log_id': [1, 2],
            'order_id': [1, 3],
            'warehouse_id': [301, 302],
            'picking_start': ['2025-01-17 06:00:00', '2025-01-19 07:00:00'],
            'picking_end': ['2025-01-17 07:00:00', '2025-01-19 08:00:00'],
            'dispatch_time': ['2025-01-17 08:00:00', '2025-01-19 09:00:00'],
            'notes': ['Picked successfully', 'Delayed picking']
        })
        
        self.sample_warehouses = pd.DataFrame({
            'warehouse_id': [301, 302],
            'warehouse_name': ['Mumbai Central', 'Mumbai East'],
            'city': ['Mumbai', 'Mumbai'],
            'state': ['Maharashtra', 'Maharashtra'],
            'capacity': [10000, 8000],
            'manager_name': ['Manager One', 'Manager Two'],
            'contact_phone': ['+915555555555', '+916666666666'],
            'created_at': ['2023-01-01 00:00:00', '2023-01-02 00:00:00']
        })
        
        self.sample_external_factors = pd.DataFrame({
            'factor_id': [1, 2],
            'order_id': [1, 2],
            'traffic_condition': ['Heavy', 'Light'],
            'weather_condition': ['Rainy', 'Clear'],
            'event_type': ['Traffic jam', 'Normal'],
            'recorded_at': ['2025-01-17 10:00:00', '2025-01-16 12:00:00']
        })
        
        self.sample_feedback = pd.DataFrame({
            'feedback_id': [1, 2],
            'order_id': [1, 2],
            'customer_name': ['John Doe', 'Jane Smith'],
            'feedback_text': ['Good service', 'Delivery was late'],
            'sentiment': ['Positive', 'Negative'],
            'rating': [5, 2],
            'created_at': ['2025-01-18 00:00:00', '2025-01-17 00:00:00']
        })
        
        # Mock the load_all_data method
        self.mock_data_loader.load_all_data.return_value = {
            'orders': self.sample_orders,
            'clients': self.sample_clients,
            'drivers': self.sample_drivers,
            'warehouses': self.sample_warehouses,
            'fleet_logs': self.sample_fleet_logs,
            'external_factors': self.sample_external_factors,
            'feedback': self.sample_feedback,
            'warehouse_logs': self.sample_warehouse_logs
        }
    
    def test_parse_datetime_columns(self):
        """Test datetime parsing functionality."""
        # Create test DataFrame with datetime columns
        test_df = pd.DataFrame({
            'id': [1, 2, 3],
            'date_col': ['2025-01-15 10:00:00', '2025-01-16 11:00:00', 'invalid_date'],
            'regular_col': ['A', 'B', 'C']
        })
        
        result_df = self.aggregator._parse_datetime_columns(test_df, ['date_col'])
        
        # Check that datetime column was parsed
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result_df['date_col']))
        # Check that invalid date was converted to NaT
        self.assertTrue(pd.isna(result_df.loc[2, 'date_col']))
        # Check that regular column was not affected
        self.assertEqual(result_df.loc[0, 'regular_col'], 'A')
    
    def test_load_and_cache_data(self):
        """Test data loading and caching functionality."""
        # First call should load data
        data = self.aggregator._load_and_cache_data()
        
        # Verify all data sources are present
        expected_sources = ['orders', 'clients', 'drivers', 'warehouses', 
                          'fleet_logs', 'external_factors', 'feedback', 'warehouse_logs']
        for source in expected_sources:
            self.assertIn(source, data)
        
        # Verify datetime columns were parsed
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(data['orders']['order_date']))
        
        # Second call should use cache (mock should only be called once)
        data2 = self.aggregator._load_and_cache_data()
        self.mock_data_loader.load_all_data.assert_called_once()
    
    def test_get_comprehensive_order_data_existing_order(self):
        """Test getting comprehensive order data for existing order."""
        result = self.aggregator.get_comprehensive_order_data(1)
        
        # Verify structure
        self.assertIsNotNone(result)
        expected_keys = ['order_info', 'client_info', 'delivery_location', 
                        'fleet_activity', 'warehouse_activity', 'external_conditions', 'customer_feedback']
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Verify order info
        self.assertEqual(result['order_info']['order_id'], 1)
        self.assertEqual(result['order_info']['customer_name'], 'John Doe')
        self.assertEqual(result['order_info']['status'], 'Delivered')
        
        # Verify client info
        self.assertEqual(result['client_info']['client_id'], 101)
        self.assertEqual(result['client_info']['client_name'], 'ABC Corp')
        
        # Verify delivery location
        self.assertEqual(result['delivery_location']['city'], 'Mumbai')
        self.assertEqual(result['delivery_location']['state'], 'Maharashtra')
        
        # Verify fleet activity
        self.assertEqual(result['fleet_activity']['driver_id'], 201)
        self.assertEqual(result['fleet_activity']['vehicle_number'], 'MH01AB1234')
        
        # Verify external conditions
        self.assertEqual(result['external_conditions']['traffic_condition'], 'Heavy')
        self.assertEqual(result['external_conditions']['weather_condition'], 'Rainy')
    
    def test_get_comprehensive_order_data_nonexistent_order(self):
        """Test getting comprehensive order data for non-existent order."""
        result = self.aggregator.get_comprehensive_order_data(999)
        self.assertIsNone(result)
    
    def test_get_orders_by_city_and_date(self):
        """Test getting orders by city and date range."""
        start_date = datetime(2025, 1, 15)
        end_date = datetime(2025, 1, 18)
        
        result = self.aggregator.get_orders_by_city_and_date('Mumbai', start_date, end_date)
        
        # Should return orders 1 and 3 (both in Mumbai within date range)
        self.assertEqual(len(result), 2)
        self.assertIn(1, result['order_id'].values)
        self.assertIn(3, result['order_id'].values)
        
        # Verify merged data includes client information
        self.assertIn('client_name', result.columns)
        self.assertEqual(result[result['order_id'] == 1]['client_name'].iloc[0], 'ABC Corp')
    
    def test_get_orders_by_city_and_date_no_results(self):
        """Test getting orders by city and date range with no results."""
        start_date = datetime(2025, 2, 1)
        end_date = datetime(2025, 2, 28)
        
        result = self.aggregator.get_orders_by_city_and_date('Mumbai', start_date, end_date)
        
        # Should return empty DataFrame
        self.assertTrue(result.empty)
    
    def test_get_orders_by_client_and_date_range(self):
        """Test getting orders by client and date range."""
        start_date = datetime(2025, 1, 15)
        end_date = datetime(2025, 1, 18)
        
        result = self.aggregator.get_orders_by_client_and_date_range(101, start_date, end_date)
        
        # Should return orders 1 and 3 (both for client 101 within date range)
        self.assertEqual(len(result), 2)
        self.assertIn(1, result['order_id'].values)
        self.assertIn(3, result['order_id'].values)
    
    def test_get_orders_by_warehouse_and_date_range(self):
        """Test getting orders by warehouse and date range."""
        start_date = datetime(2025, 1, 17)
        end_date = datetime(2025, 1, 20)
        
        result = self.aggregator.get_orders_by_warehouse_and_date_range(301, start_date, end_date)
        
        # Should return order 1 (processed by warehouse 301)
        self.assertEqual(len(result), 1)
        self.assertEqual(result['order_id'].iloc[0], 1)
    
    def test_merge_all_related_data(self):
        """Test merging all related data sources."""
        # Use first order as test case
        test_orders = self.sample_orders.iloc[[0]].copy()
        
        result = self.aggregator._merge_all_related_data(test_orders)
        
        # Verify all expected columns are present
        expected_columns = ['order_id', 'client_name', 'driver_name', 'vehicle_number', 
                          'traffic_condition', 'weather_condition', 'warehouse_name', 'feedback_text']
        for col in expected_columns:
            self.assertIn(col, result.columns)
        
        # Verify data integrity
        self.assertEqual(len(result), 1)
        self.assertEqual(result['order_id'].iloc[0], 1)
        self.assertEqual(result['client_name'].iloc[0], 'ABC Corp')
    
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        # Load data to populate cache
        self.aggregator._load_and_cache_data()
        self.assertTrue(len(self.aggregator._cached_data) > 0)
        
        # Clear cache
        self.aggregator.clear_cache()
        self.assertEqual(len(self.aggregator._cached_data), 0)


if __name__ == '__main__':
    unittest.main()