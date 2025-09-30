"""
Unit tests for CorrelationEngine class.
Tests correlation logic and pattern identification functionality.
"""

import unittest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from correlation_engine import CorrelationEngine
from data_aggregator import DataAggregator
from data_loader import DataLoader


class TestCorrelationEngine(unittest.TestCase):
    """Test cases for CorrelationEngine functionality."""
    
    def setUp(self):
        """Set up test fixtures with mock data."""
        self.mock_data_loader = Mock(spec=DataLoader)
        self.mock_data_aggregator = Mock(spec=DataAggregator)
        self.correlation_engine = CorrelationEngine(self.mock_data_aggregator)
        
        # Create sample test data
        self.sample_orders = pd.DataFrame({
            'order_id': [1, 2, 3],
            'client_id': [101, 102, 101],
            'customer_name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'city': ['Mumbai', 'Delhi', 'Mumbai'],
            'state': ['Maharashtra', 'Delhi', 'Maharashtra'],
            'order_date': pd.to_datetime(['2025-01-15 10:00:00', '2025-01-16 11:00:00', '2025-01-17 12:00:00']),
            'promised_delivery_date': pd.to_datetime(['2025-01-17 10:00:00', '2025-01-18 11:00:00', '2025-01-19 12:00:00']),
            'actual_delivery_date': pd.to_datetime(['2025-01-17 15:00:00', pd.NaT, '2025-01-19 18:00:00']),
            'status': ['Delivered', 'Failed', 'Delivered'],
            'payment_mode': ['COD', 'Online', 'COD'],
            'amount': [1500.0, 2000.0, 1200.0],
            'failure_reason': ['', 'Address not found', '']
        })
        
        self.sample_fleet_logs = pd.DataFrame({
            'fleet_log_id': [1, 2],
            'order_id': [1, 3],
            'driver_id': [201, 202],
            'vehicle_number': ['MH01AB1234', 'MH02CD5678'],
            'route_code': ['R1', 'R2'],
            'gps_delay_notes': ['Traffic jam', 'Vehicle breakdown'],
            'departure_time': pd.to_datetime(['2025-01-17 08:00:00', '2025-01-19 09:00:00']),
            'arrival_time': pd.to_datetime(['2025-01-17 15:00:00', '2025-01-19 18:00:00'])
        })
        
        self.sample_drivers = pd.DataFrame({
            'driver_id': [201, 202],
            'driver_name': ['Driver One', 'Driver Two'],
            'phone': ['+913333333333', '+914444444444'],
            'partner_company': ['Fast Delivery', 'Quick Transport'],
            'city': ['Mumbai', 'Pune'],
            'state': ['Maharashtra', 'Maharashtra']
        })
        
        self.sample_warehouse_logs = pd.DataFrame({
            'log_id': [1, 2],
            'order_id': [1, 3],
            'warehouse_id': [301, 302],
            'picking_start': pd.to_datetime(['2025-01-17 06:00:00', '2025-01-19 07:00:00']),
            'picking_end': pd.to_datetime(['2025-01-17 07:00:00', '2025-01-19 08:00:00']),
            'dispatch_time': pd.to_datetime(['2025-01-17 08:00:00', '2025-01-19 09:00:00']),
            'notes': ['Picked successfully', 'Delayed picking']
        })
        
        self.sample_warehouses = pd.DataFrame({
            'warehouse_id': [301, 302],
            'warehouse_name': ['Mumbai Central', 'Mumbai East'],
            'city': ['Mumbai', 'Mumbai'],
            'state': ['Maharashtra', 'Maharashtra'],
            'capacity': [10000, 8000],
            'manager_name': ['Manager One', 'Manager Two']
        })
        
        self.sample_external_factors = pd.DataFrame({
            'factor_id': [1, 2],
            'order_id': [1, 2],
            'traffic_condition': ['Heavy', 'Light'],
            'weather_condition': ['Rainy', 'Clear'],
            'event_type': ['Traffic jam', 'Normal'],
            'recorded_at': pd.to_datetime(['2025-01-17 10:00:00', '2025-01-16 12:00:00'])
        })
        
        # Mock the _load_and_cache_data method
        self.mock_data_aggregator._load_and_cache_data.return_value = {
            'orders': self.sample_orders,
            'drivers': self.sample_drivers,
            'warehouses': self.sample_warehouses,
            'fleet_logs': self.sample_fleet_logs,
            'external_factors': self.sample_external_factors,
            'warehouse_logs': self.sample_warehouse_logs
        }
    
    def test_correlate_order_with_fleet_existing_order(self):
        """Test fleet correlation for existing order."""
        result = self.correlation_engine.correlate_order_with_fleet(1)
        
        # Verify structure
        self.assertTrue(result['order_found'])
        self.assertEqual(result['order_id'], 1)
        self.assertEqual(result['delivery_city'], 'Mumbai')
        self.assertEqual(result['order_status'], 'Delivered')
        
        # Verify correlations
        self.assertEqual(len(result['correlations']), 1)
        correlation = result['correlations'][0]
        
        self.assertEqual(correlation['fleet_log_id'], 1)
        self.assertEqual(correlation['driver_id'], 201)
        self.assertEqual(correlation['driver_name'], 'Driver One')
        self.assertEqual(correlation['vehicle_number'], 'MH01AB1234')
        self.assertEqual(correlation['route_code'], 'R1')
        
        # Verify location correlation
        self.assertIn('location_correlation', correlation)
        self.assertTrue(correlation['location_correlation']['same_city'])
        self.assertTrue(correlation['location_correlation']['same_state'])
        self.assertEqual(correlation['location_correlation']['distance_category'], 'local')
        
        # Verify delivery metrics
        self.assertIn('delivery_metrics', correlation)
        self.assertEqual(correlation['delivery_metrics']['travel_time_hours'], 7.0)  # 8 AM to 3 PM
        self.assertTrue(correlation['delivery_metrics']['is_delayed'])  # Arrived at 3 PM, promised 10 AM
    
    def test_correlate_order_with_fleet_nonexistent_order(self):
        """Test fleet correlation for non-existent order."""
        result = self.correlation_engine.correlate_order_with_fleet(999)
        
        self.assertFalse(result['order_found'])
        self.assertEqual(result['correlations'], [])
    
    def test_correlate_order_with_warehouse_existing_order(self):
        """Test warehouse correlation for existing order."""
        result = self.correlation_engine.correlate_order_with_warehouse(1)
        
        # Verify structure
        self.assertTrue(result['order_found'])
        self.assertEqual(result['order_id'], 1)
        self.assertEqual(result['delivery_city'], 'Mumbai')
        
        # Verify correlations
        self.assertEqual(len(result['correlations']), 1)
        correlation = result['correlations'][0]
        
        self.assertEqual(correlation['log_id'], 1)
        self.assertEqual(correlation['warehouse_id'], 301)
        self.assertEqual(correlation['warehouse_name'], 'Mumbai Central')
        
        # Verify location correlation
        self.assertIn('location_correlation', correlation)
        self.assertTrue(correlation['location_correlation']['same_city'])
        self.assertEqual(correlation['location_correlation']['logistics_efficiency'], 'high')
        
        # Verify warehouse metrics
        self.assertIn('warehouse_metrics', correlation)
        self.assertEqual(correlation['warehouse_metrics']['picking_time_hours'], 1.0)  # 1 hour picking
        self.assertEqual(correlation['warehouse_metrics']['dispatch_delay_hours'], 1.0)  # 1 hour dispatch delay
    
    def test_correlate_order_with_external_factors_existing_order(self):
        """Test external factors correlation for existing order."""
        result = self.correlation_engine.correlate_order_with_external_factors(1)
        
        # Verify structure
        self.assertTrue(result['order_found'])
        self.assertEqual(result['order_id'], 1)
        
        # Verify correlations
        self.assertEqual(len(result['correlations']), 1)
        correlation = result['correlations'][0]
        
        self.assertEqual(correlation['factor_id'], 1)
        self.assertEqual(correlation['traffic_condition'], 'Heavy')
        self.assertEqual(correlation['weather_condition'], 'Rainy')
        self.assertEqual(correlation['event_type'], 'Traffic jam')
        
        # Verify impact analysis
        self.assertIn('impact_analysis', correlation)
        self.assertEqual(correlation['impact_analysis']['traffic_impact'], 'high')
        self.assertEqual(correlation['impact_analysis']['weather_impact'], 'high')
        self.assertEqual(correlation['impact_analysis']['overall_risk'], 'high')
    
    def test_calculate_delivery_metrics(self):
        """Test delivery metrics calculation."""
        order_info = {
            'promised_delivery_date': pd.to_datetime('2025-01-17 10:00:00')
        }
        fleet_row = pd.Series({
            'departure_time': pd.to_datetime('2025-01-17 08:00:00'),
            'arrival_time': pd.to_datetime('2025-01-17 15:00:00')
        })
        
        metrics = self.correlation_engine._calculate_delivery_metrics(order_info, fleet_row)
        
        self.assertEqual(metrics['travel_time_hours'], 7.0)
        self.assertTrue(metrics['is_delayed'])
        self.assertEqual(metrics['delay_hours'], 5.0)  # Arrived 5 hours late
    
    def test_analyze_location_correlation(self):
        """Test location correlation analysis."""
        order_info = {'city': 'Mumbai', 'state': 'Maharashtra'}
        driver_info = {'city': 'Mumbai', 'state': 'Maharashtra'}
        
        correlation = self.correlation_engine._analyze_location_correlation(order_info, driver_info)
        
        self.assertTrue(correlation['same_city'])
        self.assertTrue(correlation['same_state'])
        self.assertEqual(correlation['distance_category'], 'local')
        
        # Test interstate scenario
        driver_info_interstate = {'city': 'Delhi', 'state': 'Delhi'}
        correlation_interstate = self.correlation_engine._analyze_location_correlation(order_info, driver_info_interstate)
        
        self.assertFalse(correlation_interstate['same_city'])
        self.assertFalse(correlation_interstate['same_state'])
        self.assertEqual(correlation_interstate['distance_category'], 'interstate')
    
    def test_analyze_external_factor_impact(self):
        """Test external factor impact analysis."""
        order_info = {'city': 'Mumbai'}
        external_row = pd.Series({
            'traffic_condition': 'Heavy',
            'weather_condition': 'Rainy'
        })
        
        impact = self.correlation_engine._analyze_external_factor_impact(order_info, external_row)
        
        self.assertEqual(impact['traffic_impact'], 'high')
        self.assertEqual(impact['weather_impact'], 'high')
        self.assertEqual(impact['overall_risk'], 'high')
        
        # Test low impact scenario
        external_row_low = pd.Series({
            'traffic_condition': 'Light',
            'weather_condition': 'Clear'
        })
        
        impact_low = self.correlation_engine._analyze_external_factor_impact(order_info, external_row_low)
        
        self.assertEqual(impact_low['traffic_impact'], 'none')
        self.assertEqual(impact_low['weather_impact'], 'none')
        self.assertEqual(impact_low['overall_risk'], 'low')
    
    def test_calculate_success_rate(self):
        """Test success rate calculation."""
        # Test with sample orders (2 delivered out of 3)
        success_rate = self.correlation_engine._calculate_success_rate(self.sample_orders)
        self.assertAlmostEqual(success_rate, 66.67, places=1)
        
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        success_rate_empty = self.correlation_engine._calculate_success_rate(empty_df)
        self.assertEqual(success_rate_empty, 0.0)
    
    def test_analyze_failure_patterns(self):
        """Test failure pattern analysis."""
        patterns = self.correlation_engine._analyze_failure_patterns(self.sample_orders)
        
        self.assertEqual(patterns['total_failures'], 1)
        self.assertAlmostEqual(patterns['failure_rate'], 33.33, places=1)
        self.assertIn('Address not found', patterns['failure_reasons'])
        self.assertEqual(patterns['most_common_failure'], 'Address not found')
    
    def test_analyze_delivery_time_patterns(self):
        """Test delivery time pattern analysis."""
        patterns = self.correlation_engine._analyze_delivery_time_patterns(self.sample_orders)
        
        self.assertTrue(patterns['analysis_possible'])
        self.assertEqual(patterns['total_delivered'], 2)
        self.assertEqual(patterns['on_time_deliveries'], 0)  # Both were delayed
        self.assertEqual(patterns['delayed_deliveries'], 2)
        self.assertGreater(patterns['average_delay_hours'], 0)
    
    def test_find_patterns_by_city_with_mock_data(self):
        """Test finding patterns by city with mocked aggregated data."""
        # Create mock aggregated data for city
        mock_city_orders = pd.DataFrame({
            'order_id': [1, 3],
            'status': ['Delivered', 'Delivered'],
            'client_name': ['ABC Corp', 'ABC Corp'],
            'warehouse_name': ['Mumbai Central', 'Mumbai East'],
            'driver_name': ['Driver One', 'Driver Two'],
            'traffic_condition': ['Heavy', 'Light'],
            'weather_condition': ['Rainy', 'Clear'],
            'amount': [1500.0, 1200.0],
            'promised_delivery_date': pd.to_datetime(['2025-01-17 10:00:00', '2025-01-19 12:00:00']),
            'actual_delivery_date': pd.to_datetime(['2025-01-17 15:00:00', '2025-01-19 18:00:00'])
        })
        
        self.mock_data_aggregator.get_orders_by_city_and_date.return_value = mock_city_orders
        
        start_date = datetime(2025, 1, 15)
        end_date = datetime(2025, 1, 20)
        
        result = self.correlation_engine.find_patterns_by_city('Mumbai', start_date, end_date)
        
        # Verify structure
        self.assertTrue(result['patterns_found'])
        self.assertEqual(result['city'], 'Mumbai')
        
        # Verify patterns
        patterns = result['patterns']
        self.assertEqual(patterns['total_orders'], 2)
        self.assertEqual(patterns['success_rate'], 100.0)  # Both delivered
        
        # Verify external factor patterns
        self.assertTrue(patterns['external_factor_patterns']['analysis_possible'])
        self.assertIn('Heavy', patterns['external_factor_patterns']['traffic_patterns'])
        self.assertIn('Rainy', patterns['external_factor_patterns']['weather_patterns'])
    
    def test_find_patterns_by_city_no_data(self):
        """Test finding patterns by city with no data."""
        self.mock_data_aggregator.get_orders_by_city_and_date.return_value = pd.DataFrame()
        
        start_date = datetime(2025, 2, 1)
        end_date = datetime(2025, 2, 28)
        
        result = self.correlation_engine.find_patterns_by_city('NonExistentCity', start_date, end_date)
        
        self.assertFalse(result['patterns_found'])
        self.assertIn('No orders found', result['message'])
    
    def test_find_patterns_by_client_with_mock_data(self):
        """Test finding patterns by client with mocked data."""
        # Create mock aggregated data for client
        mock_client_orders = pd.DataFrame({
            'order_id': [1, 3],
            'status': ['Delivered', 'Delivered'],
            'city': ['Mumbai', 'Mumbai'],
            'state': ['Maharashtra', 'Maharashtra'],
            'payment_mode': ['COD', 'COD'],
            'amount': [1500.0, 1200.0],
            'feedback_text': ['Good service', 'Excellent'],
            'sentiment': ['Positive', 'Positive'],
            'rating': [5, 5],
            'promised_delivery_date': pd.to_datetime(['2025-01-17 10:00:00', '2025-01-19 12:00:00']),
            'actual_delivery_date': pd.to_datetime(['2025-01-17 15:00:00', '2025-01-19 18:00:00'])
        })
        
        # Mock client info
        mock_clients_df = pd.DataFrame({
            'client_id': [101],
            'client_name': ['ABC Corp']
        })
        
        self.mock_data_aggregator.get_orders_by_client_and_date_range.return_value = mock_client_orders
        self.mock_data_aggregator._load_and_cache_data.return_value['clients'] = mock_clients_df
        
        start_date = datetime(2025, 1, 15)
        end_date = datetime(2025, 1, 20)
        
        result = self.correlation_engine.find_patterns_by_client(101, start_date, end_date)
        
        # Verify structure
        self.assertTrue(result['patterns_found'])
        self.assertEqual(result['client_id'], 101)
        self.assertEqual(result['client_name'], 'ABC Corp')
        
        # Verify patterns
        patterns = result['patterns']
        self.assertEqual(patterns['total_orders'], 2)
        self.assertEqual(patterns['success_rate'], 100.0)
        
        # Verify payment mode patterns
        self.assertIn('COD', patterns['payment_mode_patterns']['payment_success_rates'])
        
        # Verify feedback patterns
        self.assertTrue(patterns['feedback_patterns']['analysis_possible'])
        self.assertEqual(patterns['feedback_patterns']['orders_with_feedback'], 2)
    
    def test_find_patterns_by_warehouse_with_mock_data(self):
        """Test finding patterns by warehouse with mocked data."""
        # Create mock aggregated data for warehouse
        mock_warehouse_orders = pd.DataFrame({
            'order_id': [1],
            'status': ['Delivered'],
            'city': ['Mumbai'],
            'state': ['Maharashtra'],
            'client_name': ['ABC Corp'],
            'amount': [1500.0],
            'picking_start': pd.to_datetime(['2025-01-17 06:00:00']),
            'picking_end': pd.to_datetime(['2025-01-17 07:00:00']),
            'dispatch_time': pd.to_datetime(['2025-01-17 08:00:00'])
        })
        
        # Mock warehouse info
        mock_warehouses_df = pd.DataFrame({
            'warehouse_id': [301],
            'warehouse_name': ['Mumbai Central']
        })
        
        self.mock_data_aggregator.get_orders_by_warehouse_and_date_range.return_value = mock_warehouse_orders
        self.mock_data_aggregator._load_and_cache_data.return_value['warehouses'] = mock_warehouses_df
        
        start_date = datetime(2025, 1, 15)
        end_date = datetime(2025, 1, 20)
        
        result = self.correlation_engine.find_patterns_by_warehouse(301, start_date, end_date)
        
        # Verify structure
        self.assertTrue(result['patterns_found'])
        self.assertEqual(result['warehouse_id'], 301)
        self.assertEqual(result['warehouse_name'], 'Mumbai Central')
        
        # Verify patterns
        patterns = result['patterns']
        self.assertEqual(patterns['total_orders'], 1)
        self.assertEqual(patterns['success_rate'], 100.0)
        
        # Verify picking performance patterns
        self.assertTrue(patterns['picking_performance_patterns']['analysis_possible'])
        self.assertEqual(patterns['picking_performance_patterns']['average_picking_time_hours'], 1.0)
        
        # Verify dispatch performance patterns
        self.assertTrue(patterns['dispatch_performance_patterns']['analysis_possible'])
        self.assertEqual(patterns['dispatch_performance_patterns']['average_dispatch_delay_hours'], 1.0)
    
    def test_correlation_with_missing_data(self):
        """Test correlation handling when related data is missing."""
        # Test order with no fleet logs
        result = self.correlation_engine.correlate_order_with_fleet(2)  # Order 2 has no fleet logs
        
        self.assertTrue(result['order_found'])
        self.assertEqual(result['order_id'], 2)
        self.assertEqual(len(result['correlations']), 0)
        # Method returns empty correlations list when no fleet logs found
        self.assertIsInstance(result['correlations'], list)
    
    def test_correlation_performance_with_large_dataset(self):
        """Test correlation performance with larger datasets."""
        # Create larger mock datasets with all required fields
        large_orders = pd.DataFrame({
            'order_id': range(1, 1001),
            'client_id': [101] * 1000,
            'city': ['Mumbai'] * 500 + ['Delhi'] * 500,
            'state': ['Maharashtra'] * 500 + ['Delhi'] * 500,
            'order_date': pd.to_datetime(['2025-01-15'] * 1000),
            'promised_delivery_date': pd.to_datetime(['2025-01-16'] * 1000),
            'status': ['Delivered'] * 800 + ['Failed'] * 200
        })
        
        large_fleet_logs = pd.DataFrame({
            'fleet_log_id': range(1, 801),
            'order_id': range(1, 801),  # Only first 800 orders have fleet logs
            'driver_id': [201] * 800,
            'vehicle_number': ['MH01AB1234'] * 800,
            'route_code': ['R1'] * 800,
            'gps_delay_notes': ['No delays'] * 800,
            'departure_time': pd.to_datetime(['2025-01-15 08:00:00'] * 800),
            'arrival_time': pd.to_datetime(['2025-01-15 15:00:00'] * 800)
        })
        
        # Update mock data with all required datasets
        mock_data = self.mock_data_aggregator._load_and_cache_data.return_value.copy()
        mock_data['orders'] = large_orders
        mock_data['fleet_logs'] = large_fleet_logs
        self.mock_data_aggregator._load_and_cache_data.return_value = mock_data
        
        # Test correlation with large dataset
        import time
        start_time = time.time()
        result = self.correlation_engine.correlate_order_with_fleet(500)
        end_time = time.time()
        
        # Should complete within reasonable time (< 1 second)
        self.assertLess(end_time - start_time, 1.0)
        self.assertTrue(result['order_found'])
    
    def test_edge_case_date_handling(self):
        """Test edge cases in date handling and calculations."""
        # Test with orders that have same departure and arrival times
        same_time_fleet = pd.DataFrame({
            'fleet_log_id': [1],
            'order_id': [1],
            'driver_id': [201],
            'vehicle_number': ['MH01AB1234'],
            'route_code': ['R1'],
            'gps_delay_notes': ['No delays'],
            'departure_time': pd.to_datetime(['2025-01-17 10:00:00']),
            'arrival_time': pd.to_datetime(['2025-01-17 10:00:00'])  # Same time
        })
        
        # Update mock data
        mock_data = self.mock_data_aggregator._load_and_cache_data.return_value.copy()
        mock_data['fleet_logs'] = same_time_fleet
        self.mock_data_aggregator._load_and_cache_data.return_value = mock_data
        
        result = self.correlation_engine.correlate_order_with_fleet(1)
        
        self.assertTrue(result['order_found'])
        correlation = result['correlations'][0]
        self.assertEqual(correlation['delivery_metrics']['travel_time_hours'], 0.0)
    
    def test_correlation_data_integrity(self):
        """Test data integrity in correlation results."""
        result = self.correlation_engine.correlate_order_with_fleet(1)
        
        # Verify all required fields are present
        required_fields = ['order_found', 'order_id', 'delivery_city', 'order_status', 'correlations']
        for field in required_fields:
            self.assertIn(field, result)
        
        if result['correlations']:
            correlation = result['correlations'][0]
            required_correlation_fields = [
                'fleet_log_id', 'driver_id', 'driver_name', 'vehicle_number',
                'location_correlation', 'delivery_metrics'
            ]
            for field in required_correlation_fields:
                self.assertIn(field, correlation)
    
    def test_statistical_calculations_accuracy(self):
        """Test accuracy of statistical calculations."""
        # Test success rate calculation with known data
        test_orders = pd.DataFrame({
            'status': ['Delivered', 'Delivered', 'Failed', 'Delivered', 'Failed'],
            'failure_reason': [None, None, 'Address not found', None, 'Payment failed']
        })
        
        success_rate = self.correlation_engine._calculate_success_rate(test_orders)
        self.assertEqual(success_rate, 60.0)  # 3 out of 5 = 60%
        
        # Test failure pattern analysis
        patterns = self.correlation_engine._analyze_failure_patterns(test_orders)
        self.assertEqual(patterns['total_failures'], 2)
        self.assertEqual(patterns['failure_rate'], 40.0)  # 2 out of 5 = 40%


if __name__ == '__main__':
    unittest.main()