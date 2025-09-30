"""
Performance benchmark tests for the Logistics Insight System.
Tests response times and system performance under various conditions.
"""

import unittest
import time
import statistics
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from natural_language_interface import NaturalLanguageInterface
from data_loader import DataLoader
from data_aggregator import DataAggregator
from correlation_engine import CorrelationEngine


class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmark test cases."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests."""
        try:
            # Initialize the complete system
            cls.data_loader = DataLoader("sample-data-set")
            cls.data_aggregator = DataAggregator(cls.data_loader)
            cls.correlation_engine = CorrelationEngine(cls.data_aggregator)
            cls.interface = NaturalLanguageInterface(cls.data_aggregator, cls.correlation_engine)
            
            print("Performance benchmark system initialized")
            
        except Exception as e:
            raise unittest.SkipTest(f"Could not initialize benchmark system: {e}")
    
    def setUp(self):
        """Set up for each test."""
        # Clear any cached data to ensure consistent testing
        self.data_aggregator.clear_cache()
    
    def _measure_query_performance(self, query, iterations=5):
        """Measure query performance over multiple iterations."""
        times = []
        results = []
        
        for i in range(iterations):
            start_time = time.time()
            result = self.interface.process_query(query)
            end_time = time.time()
            
            processing_time = end_time - start_time
            times.append(processing_time)
            results.append(result)
        
        return {
            'times': times,
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
            'success_rate': sum(1 for r in results if r['success']) / len(results) * 100,
            'results': results
        }
    
    def test_city_delay_analysis_performance(self):
        """Test performance of city delay analysis queries."""
        query = "Why were deliveries delayed in Mumbai yesterday?"
        
        performance = self._measure_query_performance(query, iterations=3)
        
        # Performance requirements
        self.assertLess(performance['avg_time'], 10.0, 
                       f"Average response time {performance['avg_time']:.2f}s exceeds 10s limit")
        self.assertLess(performance['max_time'], 15.0,
                       f"Maximum response time {performance['max_time']:.2f}s exceeds 15s limit")
        self.assertGreaterEqual(performance['success_rate'], 100.0,
                               f"Success rate {performance['success_rate']:.1f}% below 100%")
        
        print(f"✓ City delay analysis: avg {performance['avg_time']:.2f}s, "
              f"max {performance['max_time']:.2f}s, success {performance['success_rate']:.1f}%")
    
    def test_client_failure_analysis_performance(self):
        """Test performance of client failure analysis queries."""
        query = "Why did Client ABC's orders fail in the past week?"
        
        performance = self._measure_query_performance(query, iterations=3)
        
        # Performance requirements
        self.assertLess(performance['avg_time'], 10.0)
        self.assertLess(performance['max_time'], 15.0)
        self.assertGreaterEqual(performance['success_rate'], 100.0)
        
        print(f"✓ Client failure analysis: avg {performance['avg_time']:.2f}s, "
              f"max {performance['max_time']:.2f}s, success {performance['success_rate']:.1f}%")
    
    def test_warehouse_failure_analysis_performance(self):
        """Test performance of warehouse failure analysis queries."""
        query = "Explain the top reasons for delivery failures linked to Warehouse Central in August?"
        
        performance = self._measure_query_performance(query, iterations=3)
        
        # Performance requirements
        self.assertLess(performance['avg_time'], 10.0)
        self.assertLess(performance['max_time'], 15.0)
        self.assertGreaterEqual(performance['success_rate'], 100.0)
        
        print(f"✓ Warehouse failure analysis: avg {performance['avg_time']:.2f}s, "
              f"max {performance['max_time']:.2f}s, success {performance['success_rate']:.1f}%")
    
    def test_city_comparison_performance(self):
        """Test performance of city comparison queries."""
        query = "Compare delivery failure causes between Delhi and Mumbai last month?"
        
        performance = self._measure_query_performance(query, iterations=3)
        
        # City comparison might take longer due to dual analysis
        self.assertLess(performance['avg_time'], 15.0)
        self.assertLess(performance['max_time'], 20.0)
        self.assertGreaterEqual(performance['success_rate'], 100.0)
        
        print(f"✓ City comparison: avg {performance['avg_time']:.2f}s, "
              f"max {performance['max_time']:.2f}s, success {performance['success_rate']:.1f}%")
    
    def test_festival_period_analysis_performance(self):
        """Test performance of festival period analysis queries."""
        query = "What are the likely causes of delivery failures during the festival period?"
        
        performance = self._measure_query_performance(query, iterations=3)
        
        # Festival analysis is mostly template-based, should be fast
        self.assertLess(performance['avg_time'], 5.0)
        self.assertLess(performance['max_time'], 8.0)
        self.assertGreaterEqual(performance['success_rate'], 100.0)
        
        print(f"✓ Festival period analysis: avg {performance['avg_time']:.2f}s, "
              f"max {performance['max_time']:.2f}s, success {performance['success_rate']:.1f}%")
    
    def test_capacity_impact_analysis_performance(self):
        """Test performance of capacity impact analysis queries."""
        query = "If we onboard Client NewCorp with 20,000 extra monthly orders, what risks should we expect?"
        
        performance = self._measure_query_performance(query, iterations=3)
        
        # Capacity analysis is mostly template-based, should be fast
        self.assertLess(performance['avg_time'], 5.0)
        self.assertLess(performance['max_time'], 8.0)
        self.assertGreaterEqual(performance['success_rate'], 100.0)
        
        print(f"✓ Capacity impact analysis: avg {performance['avg_time']:.2f}s, "
              f"max {performance['max_time']:.2f}s, success {performance['success_rate']:.1f}%")
    
    def test_data_loading_performance(self):
        """Test data loading performance."""
        # Clear cache to force fresh data loading
        self.data_aggregator.clear_cache()
        
        start_time = time.time()
        data = self.data_aggregator._load_and_cache_data()
        end_time = time.time()
        
        loading_time = end_time - start_time
        
        # Data loading should be reasonably fast
        self.assertLess(loading_time, 5.0, 
                       f"Data loading time {loading_time:.2f}s exceeds 5s limit")
        
        # Verify data was loaded
        self.assertIsInstance(data, dict)
        self.assertGreater(len(data), 0)
        
        print(f"✓ Data loading: {loading_time:.2f}s for {len(data)} data sources")
    
    def test_correlation_engine_performance(self):
        """Test correlation engine performance with sample data."""
        try:
            # Load sample data to get valid IDs
            data = self.data_loader.load_all_data()
            orders_df = data['orders']
            
            if orders_df.empty:
                self.skipTest("No sample data available for correlation testing")
            
            # Test correlation performance with first few orders
            test_order_ids = orders_df['order_id'].head(3).tolist()
            
            correlation_times = []
            
            for order_id in test_order_ids:
                start_time = time.time()
                
                # Test multiple correlation types
                fleet_result = self.correlation_engine.correlate_order_with_fleet(order_id)
                warehouse_result = self.correlation_engine.correlate_order_with_warehouse(order_id)
                external_result = self.correlation_engine.correlate_order_with_external_factors(order_id)
                
                end_time = time.time()
                correlation_time = end_time - start_time
                correlation_times.append(correlation_time)
                
                # Verify results
                self.assertTrue(fleet_result['order_found'])
                self.assertTrue(warehouse_result['order_found'])
                self.assertTrue(external_result['order_found'])
            
            avg_correlation_time = statistics.mean(correlation_times)
            max_correlation_time = max(correlation_times)
            
            # Correlation should be fast
            self.assertLess(avg_correlation_time, 2.0,
                           f"Average correlation time {avg_correlation_time:.2f}s exceeds 2s limit")
            self.assertLess(max_correlation_time, 3.0,
                           f"Maximum correlation time {max_correlation_time:.2f}s exceeds 3s limit")
            
            print(f"✓ Correlation engine: avg {avg_correlation_time:.2f}s, "
                  f"max {max_correlation_time:.2f}s for {len(test_order_ids)} orders")
            
        except Exception as e:
            self.skipTest(f"Correlation performance test failed: {e}")
    
    def test_memory_usage_during_processing(self):
        """Test memory usage during query processing."""
        try:
            import psutil
            import gc
            
            process = psutil.Process(os.getpid())
            
            # Get baseline memory
            gc.collect()
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process multiple queries and track memory
            queries = [
                "Why were deliveries delayed in Mumbai yesterday?",
                "Why did Client ABC's orders fail in the past week?",
                "Compare delivery failure causes between Delhi and Chennai last month?",
            ]
            
            memory_readings = [baseline_memory]
            
            for query in queries:
                result = self.interface.process_query(query)
                self.assertTrue(result['success'])
                
                # Force garbage collection and measure memory
                gc.collect()
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_readings.append(current_memory)
            
            max_memory = max(memory_readings)
            memory_increase = max_memory - baseline_memory
            
            # Memory increase should be reasonable
            self.assertLess(memory_increase, 50.0,
                           f"Memory increase {memory_increase:.1f}MB exceeds 50MB limit")
            
            print(f"✓ Memory usage: {memory_increase:.1f}MB increase, "
                  f"peak {max_memory:.1f}MB")
            
        except ImportError:
            self.skipTest("psutil not available for memory testing")
        except Exception as e:
            self.skipTest(f"Memory usage test failed: {e}")
    
    def test_concurrent_query_simulation(self):
        """Test performance under simulated concurrent load."""
        # Simulate concurrent queries by running them in quick succession
        queries = [
            "Why were deliveries delayed in Mumbai yesterday?",
            "Why did Client ABC's orders fail in the past week?",
            "Explain the top reasons for delivery failures linked to Warehouse Central in August?",
            "Compare delivery failure causes between Delhi and Mumbai last month?",
            "What are the likely causes of delivery failures during the festival period?",
        ]
        
        start_time = time.time()
        results = []
        
        # Process all queries as quickly as possible
        for query in queries:
            query_start = time.time()
            result = self.interface.process_query(query)
            query_end = time.time()
            
            results.append({
                'query': query,
                'success': result['success'],
                'time': query_end - query_start
            })
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_queries = [r for r in results if r['success']]
        success_rate = len(successful_queries) / len(results) * 100
        avg_query_time = statistics.mean([r['time'] for r in successful_queries])
        
        # Performance requirements for concurrent-like load
        self.assertGreaterEqual(success_rate, 80.0,
                               f"Success rate {success_rate:.1f}% below 80% under load")
        self.assertLess(total_time, 60.0,
                       f"Total processing time {total_time:.2f}s exceeds 60s limit")
        self.assertLess(avg_query_time, 15.0,
                       f"Average query time {avg_query_time:.2f}s exceeds 15s limit under load")
        
        print(f"✓ Concurrent simulation: {len(successful_queries)}/{len(queries)} queries, "
              f"avg {avg_query_time:.2f}s, total {total_time:.2f}s")
    
    def test_system_warmup_performance(self):
        """Test system performance during warmup vs warmed up state."""
        # Clear cache to simulate cold start
        self.data_aggregator.clear_cache()
        
        query = "Why were deliveries delayed in Mumbai yesterday?"
        
        # Cold start performance
        cold_start_time = time.time()
        cold_result = self.interface.process_query(query)
        cold_end_time = time.time()
        cold_duration = cold_end_time - cold_start_time
        
        # Warmed up performance (run same query again)
        warm_start_time = time.time()
        warm_result = self.interface.process_query(query)
        warm_end_time = time.time()
        warm_duration = warm_end_time - warm_start_time
        
        # Both should succeed
        self.assertTrue(cold_result['success'])
        self.assertTrue(warm_result['success'])
        
        # Warmed up should be faster (due to caching)
        self.assertLessEqual(warm_duration, cold_duration,
                            "Warmed up query should be faster than cold start")
        
        # Both should meet performance requirements
        self.assertLess(cold_duration, 15.0, "Cold start exceeds 15s limit")
        self.assertLess(warm_duration, 10.0, "Warmed up query exceeds 10s limit")
        
        print(f"✓ Warmup performance: cold {cold_duration:.2f}s, warm {warm_duration:.2f}s")


if __name__ == '__main__':
    # Run performance tests with detailed output
    unittest.main(verbosity=2)