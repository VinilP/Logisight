"""
Unit tests for the InsightGenerator class.
Tests narrative generation, statistical analysis, and use case handlers.
"""

import unittest
from unittest.mock import Mock, patch
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from insight_generator import InsightGenerator
from data_aggregator import DataAggregator
from correlation_engine import CorrelationEngine


class TestInsightGenerator(unittest.TestCase):
    """Test cases for InsightGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock dependencies
        self.mock_data_aggregator = Mock(spec=DataAggregator)
        self.mock_correlation_engine = Mock(spec=CorrelationEngine)
        
        # Create InsightGenerator instance
        self.insight_generator = InsightGenerator(
            self.mock_data_aggregator,
            self.mock_correlation_engine
        )
        
        # Sample test data
        self.sample_orders_df = pd.DataFrame({
            'order_id': [1, 2, 3, 4, 5],
            'status': ['Delivered', 'Failed', 'Delivered', 'Delivered', 'Failed'],
            'failure_reason': [None, 'Address not found', None, None, 'Payment failed'],
            'promised_delivery_date': [
                datetime(2024, 1, 1, 10, 0),
                datetime(2024, 1, 2, 10, 0),
                datetime(2024, 1, 3, 10, 0),
                datetime(2024, 1, 4, 10, 0),
                datetime(2024, 1, 5, 10, 0)
            ],
            'actual_delivery_date': [
                datetime(2024, 1, 1, 12, 0),  # 2 hours late
                None,  # Failed delivery
                datetime(2024, 1, 3, 9, 0),   # 1 hour early
                datetime(2024, 1, 4, 14, 0),  # 4 hours late
                None   # Failed delivery
            ]
        })
    
    def test_calculate_success_rate(self):
        """Test success rate calculation."""
        # Test with sample data (3 delivered out of 5 = 60%)
        success_rate = self.insight_generator.calculate_success_rate(self.sample_orders_df)
        self.assertEqual(success_rate, 60.0)
        
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        success_rate_empty = self.insight_generator.calculate_success_rate(empty_df)
        self.assertEqual(success_rate_empty, 0.0)
        
        # Test with all successful orders
        all_success_df = pd.DataFrame({
            'status': ['Delivered', 'Delivered', 'Delivered']
        })
        success_rate_all = self.insight_generator.calculate_success_rate(all_success_df)
        self.assertEqual(success_rate_all, 100.0)
    
    def test_calculate_delay_patterns(self):
        """Test delay pattern calculation."""
        delay_patterns = self.insight_generator.calculate_delay_patterns(self.sample_orders_df)
        
        self.assertTrue(delay_patterns['analysis_possible'])
        self.assertEqual(delay_patterns['total_orders'], 5)
        self.assertEqual(delay_patterns['delivered_orders'], 3)
        self.assertEqual(delay_patterns['on_time_deliveries'], 1)  # Only one early delivery
        self.assertEqual(delay_patterns['delayed_deliveries'], 2)  # Two late deliveries
        self.assertAlmostEqual(delay_patterns['average_delay_hours'], 3.0)  # (2+4)/2 = 3
        self.assertEqual(delay_patterns['max_delay_hours'], 4.0)
    
    def test_calculate_failure_distributions(self):
        """Test failure distribution calculation."""
        failure_dist = self.insight_generator.calculate_failure_distributions(self.sample_orders_df)
        
        self.assertEqual(failure_dist['total_failures'], 2)
        self.assertEqual(failure_dist['failure_rate'], 40.0)  # 2 out of 5 = 40%
        self.assertIn('Address not found', failure_dist['failure_reasons'])
        self.assertIn('Payment failed', failure_dist['failure_reasons'])
        self.assertEqual(failure_dist['failure_reasons']['Address not found'], 1)
        self.assertEqual(failure_dist['failure_reasons']['Payment failed'], 1)
    
    def test_generate_narrative_summary(self):
        """Test narrative summary generation."""
        title = "Test Analysis"
        key_metrics = {
            'Total Orders': 100,
            'Success Rate': 85.5,
            'Average Delay': 2.3
        }
        insights = [
            "Primary issue is address verification",
            "Weather conditions impacted 15% of deliveries"
        ]
        recommendations = [
            "Implement address validation system",
            "Develop weather contingency plans"
        ]
        
        narrative = self.insight_generator.generate_narrative_summary(
            title, key_metrics, insights, recommendations
        )
        
        # Check that all sections are included
        self.assertIn("# Test Analysis", narrative)
        self.assertIn("## Key Metrics", narrative)
        self.assertIn("## Key Insights", narrative)
        self.assertIn("## Actionable Recommendations", narrative)
        
        # Check that content is included
        self.assertIn("Total Orders: 100", narrative)
        self.assertIn("Success Rate: 85.50", narrative)
        self.assertIn("1. Primary issue is address verification", narrative)
        self.assertIn("1. Implement address validation system", narrative)


    def test_generate_city_delay_analysis(self):
        """Test city delay analysis generation."""
        # Mock correlation engine response
        mock_city_patterns = {
            'patterns_found': True,
            'patterns': {
                'total_orders': 50,
                'success_rate': 75.0,
                'failure_patterns': {
                    'total_failures': 12,
                    'failure_rate': 24.0,
                    'most_common_failure': 'Address not found',
                    'failure_reason_distribution': {'Address not found': 60.0, 'Payment failed': 40.0}
                },
                'delivery_time_patterns': {
                    'analysis_possible': True,
                    'delivered_orders': 38,
                    'delayed_deliveries': 15,
                    'average_delay_hours': 3.5
                },
                'external_factor_patterns': {
                    'analysis_possible': True,
                    'traffic_patterns': {'heavy': 10, 'moderate': 5},
                    'weather_patterns': {'rainy': 8}
                },
                'warehouse_performance_patterns': {
                    'analysis_possible': True,
                    'warehouse_success_rates': {'Warehouse A': 70.0, 'Warehouse B': 85.0}
                }
            }
        }
        
        self.mock_correlation_engine.find_patterns_by_city.return_value = mock_city_patterns
        
        # Test city delay analysis
        test_date = datetime(2024, 1, 15)
        result = self.insight_generator.generate_city_delay_analysis('Mumbai', test_date)
        
        # Verify the analysis contains expected elements
        self.assertIn('Delivery Delay Analysis for Mumbai', result)
        self.assertIn('Total Orders: 50', result)
        self.assertIn('Success Rate (%): 75.0', result)
        self.assertIn('Address not found', result)
        self.assertIn('delayed with an average delay of 3.5 hours', result)
        self.assertIn('Traffic conditions contributed to delays', result)
        
        # Verify correlation engine was called correctly
        self.mock_correlation_engine.find_patterns_by_city.assert_called_once()
    
    def test_generate_client_failure_analysis(self):
        """Test client failure analysis generation."""
        # Mock correlation engine response
        mock_client_patterns = {
            'patterns_found': True,
            'client_name': 'ABC Corp',
            'patterns': {
                'total_orders': 100,
                'success_rate': 80.0,
                'failure_patterns': {
                    'total_failures': 20,
                    'failure_rate': 20.0,
                    'most_common_failure': 'Payment failed',
                    'failure_reason_distribution': {'Payment failed': 70.0, 'Address not found': 30.0}
                },
                'delivery_location_patterns': {
                    'location_success_rates': {('Delhi', 'Delhi'): 85.0, ('Mumbai', 'Maharashtra'): 75.0}
                },
                'payment_mode_patterns': {
                    'payment_success_rates': {'COD': 75.0, 'Online': 85.0}
                },
                'delivery_time_patterns': {
                    'analysis_possible': True,
                    'delivered_orders': 80,
                    'delayed_deliveries': 25,
                    'average_delay_hours': 2.5
                },
                'feedback_patterns': {
                    'analysis_possible': True,
                    'sentiment_distribution': {'negative': 5, 'positive': 15}
                }
            }
        }
        
        self.mock_correlation_engine.find_patterns_by_client.return_value = mock_client_patterns
        
        # Test client failure analysis
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 7)
        result = self.insight_generator.generate_client_failure_analysis(123, start_date, end_date)
        
        # Verify the analysis contains expected elements
        self.assertIn('Order Failure Analysis for ABC Corp', result)
        self.assertIn('Client Name: ABC Corp', result)
        self.assertIn('Total Orders: 100', result)
        self.assertIn('Payment failed', result)
        self.assertIn('70.0% of failures', result)
        
        # Verify correlation engine was called correctly
        self.mock_correlation_engine.find_patterns_by_client.assert_called_once_with(123, start_date, end_date)
    
    def test_generate_warehouse_failure_analysis(self):
        """Test warehouse failure analysis generation."""
        # Mock correlation engine response
        mock_warehouse_patterns = {
            'patterns_found': True,
            'warehouse_name': 'Central Warehouse',
            'patterns': {
                'total_orders': 200,
                'success_rate': 85.0,
                'failure_patterns': {
                    'total_failures': 30,
                    'failure_rate': 15.0,
                    'most_common_failure': 'Stock unavailable',
                    'failure_reasons': {'Stock unavailable': 20, 'Damage in transit': 10}
                },
                'picking_performance_patterns': {
                    'analysis_possible': True,
                    'average_picking_time_hours': 1.5,
                    'max_picking_time_hours': 4.0
                },
                'dispatch_performance_patterns': {
                    'analysis_possible': True,
                    'average_dispatch_delay_hours': 0.5,
                    'max_dispatch_delay_hours': 2.0
                },
                'delivery_destination_patterns': {
                    'destination_success_rates': {('Delhi', 'Delhi'): 90.0, ('Gurgaon', 'Haryana'): 80.0}
                },
                'client_distribution_patterns': {
                    'client_order_counts': {'Client A': 50, 'Client B': 30}
                }
            }
        }
        
        self.mock_correlation_engine.find_patterns_by_warehouse.return_value = mock_warehouse_patterns
        
        # Test warehouse failure analysis
        start_date = datetime(2024, 8, 1)
        end_date = datetime(2024, 8, 31)
        result = self.insight_generator.generate_warehouse_failure_analysis(456, start_date, end_date)
        
        # Verify the analysis contains expected elements
        self.assertIn('Delivery Failure Analysis for Central Warehouse', result)
        self.assertIn('Warehouse Name: Central Warehouse', result)
        self.assertIn('Total Orders Processed: 200', result)
        self.assertIn('Stock unavailable', result)
        self.assertIn('Average 1.5 hours', result)
        
        # Verify correlation engine was called correctly
        self.mock_correlation_engine.find_patterns_by_warehouse.assert_called_once_with(456, start_date, end_date)
    
    def test_generate_city_comparison(self):
        """Test city comparison analysis generation."""
        # Mock correlation engine responses for both cities
        mock_patterns_a = {
            'patterns_found': True,
            'patterns': {
                'total_orders': 100,
                'success_rate': 85.0,
                'failure_patterns': {
                    'failure_rate': 15.0,
                    'failure_reasons': {'Address not found': 10, 'Payment failed': 5}
                },
                'delivery_time_patterns': {
                    'analysis_possible': True,
                    'average_delay_hours': 2.0
                },
                'external_factor_patterns': {
                    'analysis_possible': True,
                    'traffic_patterns': {'heavy': 20},
                    'weather_patterns': {'rainy': 10}
                },
                'warehouse_performance_patterns': {
                    'analysis_possible': True,
                    'warehouse_success_rates': {'Warehouse A': 85.0}
                }
            }
        }
        
        mock_patterns_b = {
            'patterns_found': True,
            'patterns': {
                'total_orders': 80,
                'success_rate': 75.0,
                'failure_patterns': {
                    'failure_rate': 25.0,
                    'failure_reasons': {'Traffic delay': 15, 'Address not found': 5}
                },
                'delivery_time_patterns': {
                    'analysis_possible': True,
                    'average_delay_hours': 3.5
                },
                'external_factor_patterns': {
                    'analysis_possible': True,
                    'traffic_patterns': {'congested': 25},
                    'weather_patterns': {'sunny': 50}
                },
                'warehouse_performance_patterns': {
                    'analysis_possible': True,
                    'warehouse_success_rates': {'Warehouse B': 75.0}
                }
            }
        }
        
        self.mock_correlation_engine.find_patterns_by_city.side_effect = [mock_patterns_a, mock_patterns_b]
        
        # Test city comparison
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        result = self.insight_generator.generate_city_comparison('Delhi', 'Mumbai', start_date, end_date)
        
        # Verify the analysis contains expected elements
        self.assertIn('Delivery Performance Comparison: Delhi vs Mumbai', result)
        self.assertIn('Delhi - Total Orders: 100', result)
        self.assertIn('Mumbai - Total Orders: 80', result)
        self.assertIn('Delhi significantly outperforms Mumbai', result)
        self.assertIn('10.0% higher success rate', result)
        
        # Verify correlation engine was called for both cities
        self.assertEqual(self.mock_correlation_engine.find_patterns_by_city.call_count, 2)
    
    def test_generate_festival_period_analysis(self):
        """Test festival period analysis generation."""
        from datetime import datetime
        import pandas as pd
        
        # Mock the data aggregator's load method
        mock_orders_data = pd.DataFrame({
            'order_id': range(1, 101),
            'order_date': pd.date_range('2024-09-15', periods=100, freq='D'),
            'status': ['Delivered'] * 80 + ['Failed'] * 20,
            'promised_delivery_date': pd.date_range('2024-09-16', periods=100, freq='D'),
            'actual_delivery_date': pd.date_range('2024-09-16', periods=100, freq='D'),
            'failure_reason': [None] * 80 + ['Address not found'] * 20
        })
        
        self.mock_data_aggregator._load_and_cache_data.return_value = {
            'orders': mock_orders_data
        }
        
        festival_start = datetime(2024, 10, 1)
        festival_end = datetime(2024, 10, 31)
        
        result = self.insight_generator.generate_festival_period_analysis(festival_start, festival_end)
        
        # Verify the analysis contains expected elements
        self.assertIn('Festival Period Delivery Risk Analysis', result)
        self.assertIn('Seasonal Impact Assessment', result)
        self.assertIn('Preparation Recommendations', result)
        self.assertIn('increased order volumes', result)
        self.assertIn('traffic congestion', result)
    
    def test_generate_capacity_impact_analysis(self):
        """Test capacity impact analysis generation."""
        import pandas as pd
        
        # Mock the data aggregator's load method
        mock_orders_data = pd.DataFrame({
            'order_id': range(1, 1001),
            'client_id': [123] * 500 + [456] * 500,
            'status': ['Delivered'] * 800 + ['Failed'] * 200,
            'order_date': pd.date_range('2024-01-01', periods=1000, freq='D')
        })
        
        mock_clients_data = pd.DataFrame({
            'client_id': [123, 456],
            'client_name': ['Test Client', 'Other Client']
        })
        
        self.mock_data_aggregator._load_and_cache_data.return_value = {
            'orders': mock_orders_data,
            'clients': mock_clients_data
        }
        
        result = self.insight_generator.generate_capacity_impact_analysis(123, 25000)
        
        # Verify the analysis contains expected elements
        self.assertIn('Capacity Impact Analysis', result)
        self.assertIn('Client 123', result)
        self.assertIn('25,000', result)
        self.assertIn('Risk Assessment', result)
        self.assertIn('Mitigation Strategies', result)
    
    def test_narrative_generation_with_empty_data(self):
        """Test narrative generation with empty or missing data."""
        title = "Empty Data Analysis"
        key_metrics = {}
        insights = []
        recommendations = []
        
        narrative = self.insight_generator.generate_narrative_summary(
            title, key_metrics, insights, recommendations
        )
        
        # Should handle empty data gracefully - only title is included when data is empty
        self.assertIn("# Empty Data Analysis", narrative)
        # Empty sections are not included in the output
        self.assertNotIn("## Key Metrics", narrative)
        self.assertNotIn("## Key Insights", narrative)
        self.assertNotIn("## Actionable Recommendations", narrative)
    
    def test_statistical_edge_cases(self):
        """Test statistical calculations with edge cases."""
        # Test with single order
        single_order_df = pd.DataFrame({
            'status': ['Delivered'],
            'promised_delivery_date': [datetime(2024, 1, 1, 10, 0)],
            'actual_delivery_date': [datetime(2024, 1, 1, 12, 0)]
        })
        
        success_rate = self.insight_generator.calculate_success_rate(single_order_df)
        self.assertEqual(success_rate, 100.0)
        
        delay_patterns = self.insight_generator.calculate_delay_patterns(single_order_df)
        self.assertTrue(delay_patterns['analysis_possible'])
        self.assertEqual(delay_patterns['total_orders'], 1)
        self.assertEqual(delay_patterns['delivered_orders'], 1)
        
        # Test with all failed orders
        all_failed_df = pd.DataFrame({
            'status': ['Failed', 'Failed', 'Failed'],
            'failure_reason': ['Address not found', 'Payment failed', 'Address not found']
        })
        
        success_rate = self.insight_generator.calculate_success_rate(all_failed_df)
        self.assertEqual(success_rate, 0.0)
        
        failure_dist = self.insight_generator.calculate_failure_distributions(all_failed_df)
        self.assertEqual(failure_dist['failure_rate'], 100.0)
        self.assertEqual(failure_dist['failure_reasons']['Address not found'], 2)
    
    def test_narrative_formatting_consistency(self):
        """Test consistency of narrative formatting."""
        title = "Formatting Test Analysis"
        key_metrics = {
            'Total Orders': 1500,
            'Success Rate (%)': 87.33,
            'Average Delay (hours)': 2.567
        }
        insights = [
            "First insight with detailed explanation",
            "Second insight about performance metrics"
        ]
        recommendations = [
            "Implement immediate action plan",
            "Schedule follow-up review in 30 days"
        ]
        
        narrative = self.insight_generator.generate_narrative_summary(
            title, key_metrics, insights, recommendations
        )
        
        # Check formatting consistency
        lines = narrative.split('\n')
        
        # Check header formatting
        header_lines = [line for line in lines if line.startswith('#')]
        self.assertTrue(len(header_lines) >= 4)  # Title + 3 sections
        
        # Check metric formatting (should have consistent decimal places)
        metric_lines = [line for line in lines if 'Success Rate' in line]
        self.assertTrue(any('87.33' in line for line in metric_lines))
        
        # Check numbered list formatting
        insight_lines = [line for line in lines if line.strip().startswith('1.') or line.strip().startswith('2.')]
        self.assertTrue(len(insight_lines) >= 4)  # 2 insights + 2 recommendations
    
    def test_error_handling_in_analysis_generation(self):
        """Test error handling in analysis generation methods."""
        # Test with correlation engine returning no patterns
        self.mock_correlation_engine.find_patterns_by_city.return_value = {
            'patterns_found': False,
            'message': 'No data found for specified city and date range'
        }
        
        result = self.insight_generator.generate_city_delay_analysis('NonExistentCity', datetime(2024, 1, 1))
        
        # Should handle gracefully and provide meaningful message
        self.assertIn('No delivery data found', result)
        self.assertIn('NonExistentCity', result)
        self.assertIn('2024-01-01', result)
    
    def test_performance_with_large_datasets(self):
        """Test performance with large datasets."""
        # Create large test dataset
        large_orders_df = pd.DataFrame({
            'order_id': range(1, 10001),
            'status': ['Delivered'] * 8000 + ['Failed'] * 2000,
            'failure_reason': [None] * 8000 + ['Address not found'] * 1000 + ['Payment failed'] * 1000,
            'promised_delivery_date': [datetime(2024, 1, 1, 10, 0)] * 10000,
            'actual_delivery_date': [datetime(2024, 1, 1, 12, 0)] * 8000 + [None] * 2000
        })
        
        import time
        
        # Test success rate calculation performance
        start_time = time.time()
        success_rate = self.insight_generator.calculate_success_rate(large_orders_df)
        end_time = time.time()
        
        self.assertLess(end_time - start_time, 1.0)  # Should complete within 1 second
        self.assertEqual(success_rate, 80.0)  # 8000 out of 10000
        
        # Test failure distribution calculation performance
        start_time = time.time()
        failure_dist = self.insight_generator.calculate_failure_distributions(large_orders_df)
        end_time = time.time()
        
        self.assertLess(end_time - start_time, 1.0)  # Should complete within 1 second
        self.assertEqual(failure_dist['total_failures'], 2000)


if __name__ == '__main__':
    unittest.main()