"""
Integration tests for the Natural Language Interface.
Tests end-to-end query processing functionality.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from natural_language_interface import NaturalLanguageInterface
from query_processor import QueryType


class TestNaturalLanguageInterface(unittest.TestCase):
    """Test cases for NaturalLanguageInterface class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock components
        self.mock_data_aggregator = Mock()
        self.mock_correlation_engine = Mock()
        
        # Set up mock data aggregator methods
        self.mock_data_aggregator.get_orders.return_value = Mock()
        self.mock_data_aggregator.get_clients.return_value = Mock()
        self.mock_data_aggregator.get_warehouses.return_value = Mock()
        
        # Create the interface
        self.interface = NaturalLanguageInterface(
            self.mock_data_aggregator,
            self.mock_correlation_engine
        )
    
    def test_initialization(self):
        """Test NaturalLanguageInterface initialization."""
        self.assertIsNotNone(self.interface.data_aggregator)
        self.assertIsNotNone(self.interface.correlation_engine)
        self.assertIsNotNone(self.interface.insight_generator)
        self.assertIsNotNone(self.interface.query_processor)
        self.assertIsNotNone(self.interface.response_generator)
        self.assertEqual(len(self.interface.query_history), 0)
    
    @patch('natural_language_interface.InsightGenerator')
    def test_process_query_success(self, mock_insight_generator_class):
        """Test successful query processing."""
        # Mock the insight generator
        mock_insight_generator = Mock()
        mock_insight_generator.generate_city_delay_analysis.return_value = "Test analysis result"
        mock_insight_generator_class.return_value = mock_insight_generator
        
        # Create new interface with mocked insight generator
        interface = NaturalLanguageInterface(
            self.mock_data_aggregator,
            self.mock_correlation_engine
        )
        interface.insight_generator = mock_insight_generator
        
        query = "Why were deliveries delayed in Mumbai yesterday?"
        result = interface.process_query(query)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['query'], query)
        self.assertEqual(result['query_type'], QueryType.CITY_DELAY_ANALYSIS.value)
        self.assertIn('parameters', result)
        self.assertIn('analysis_result', result)
        self.assertIn('formatted_response', result)
        self.assertIn('processing_time', result)
        self.assertIn('timestamp', result)
    
    def test_process_query_unknown(self):
        """Test processing of unknown queries."""
        query = "What is the weather today?"
        result = self.interface.process_query(query)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('supported_queries', result)
        self.assertEqual(result['query'], query)
    
    @patch('natural_language_interface.InsightGenerator')
    def test_process_query_with_executive_summary(self, mock_insight_generator_class):
        """Test query processing with executive summary."""
        # Mock the insight generator
        mock_insight_generator = Mock()
        mock_insight_generator.generate_city_delay_analysis.return_value = "Test analysis result"
        mock_insight_generator_class.return_value = mock_insight_generator
        
        # Create new interface with mocked insight generator
        interface = NaturalLanguageInterface(
            self.mock_data_aggregator,
            self.mock_correlation_engine
        )
        interface.insight_generator = mock_insight_generator
        
        query = "Why were deliveries delayed in Mumbai yesterday?"
        result = interface.process_query(query, include_executive_summary=True)
        
        self.assertTrue(result['success'])
        self.assertIn('executive_summary', result)
        self.assertIsNotNone(result['executive_summary'])
    
    def test_resolve_client_id(self):
        """Test client ID resolution from client name."""
        # Mock client data
        import pandas as pd
        mock_clients_df = pd.DataFrame({
            'client_id': [1, 2, 3],
            'client_name': ['ABC Corp', 'XYZ Ltd', 'DEF Inc']
        })
        self.mock_data_aggregator.get_clients.return_value = mock_clients_df
        
        # Test exact match
        client_id = self.interface._resolve_client_id('ABC Corp')
        self.assertEqual(client_id, 1)
        
        # Test case insensitive match
        client_id = self.interface._resolve_client_id('abc corp')
        self.assertEqual(client_id, 1)
        
        # Test partial match
        client_id = self.interface._resolve_client_id('ABC')
        self.assertEqual(client_id, 1)
        
        # Test no match
        client_id = self.interface._resolve_client_id('Unknown Client')
        self.assertIsNone(client_id)
    
    def test_resolve_warehouse_id(self):
        """Test warehouse ID resolution from warehouse name."""
        # Mock warehouse data
        import pandas as pd
        mock_warehouses_df = pd.DataFrame({
            'warehouse_id': [1, 2, 3],
            'warehouse_name': ['Warehouse A', 'Warehouse B', 'Central Hub']
        })
        self.mock_data_aggregator.get_warehouses.return_value = mock_warehouses_df
        
        # Test exact match
        warehouse_id = self.interface._resolve_warehouse_id('Warehouse A')
        self.assertEqual(warehouse_id, 1)
        
        # Test case insensitive match
        warehouse_id = self.interface._resolve_warehouse_id('warehouse a')
        self.assertEqual(warehouse_id, 1)
        
        # Test partial match
        warehouse_id = self.interface._resolve_warehouse_id('Central')
        self.assertEqual(warehouse_id, 3)
        
        # Test no match
        warehouse_id = self.interface._resolve_warehouse_id('Unknown Warehouse')
        self.assertIsNone(warehouse_id)
    
    def test_query_history_tracking(self):
        """Test query history tracking functionality."""
        # Process a successful query
        self.interface._record_query(
            "Test query", 
            QueryType.CITY_DELAY_ANALYSIS, 
            {'city': 'Mumbai'}, 
            True
        )
        
        # Process a failed query
        self.interface._record_query(
            "Invalid query", 
            None, 
            {}, 
            False
        )
        
        self.assertEqual(len(self.interface.query_history), 2)
        
        # Check first query record
        first_record = self.interface.query_history[0]
        self.assertEqual(first_record['query'], "Test query")
        self.assertEqual(first_record['query_type'], QueryType.CITY_DELAY_ANALYSIS.value)
        self.assertTrue(first_record['success'])
        
        # Check second query record
        second_record = self.interface.query_history[1]
        self.assertEqual(second_record['query'], "Invalid query")
        self.assertIsNone(second_record['query_type'])
        self.assertFalse(second_record['success'])
    
    def test_query_statistics(self):
        """Test query statistics generation."""
        # Add some test queries to history
        self.interface._record_query("Query 1", QueryType.CITY_DELAY_ANALYSIS, {}, True)
        self.interface._record_query("Query 2", QueryType.CLIENT_FAILURE_ANALYSIS, {}, True)
        self.interface._record_query("Query 3", None, {}, False)
        
        stats = self.interface.get_query_statistics()
        
        self.assertEqual(stats['total_queries'], 3)
        self.assertEqual(stats['successful_queries'], 2)
        self.assertEqual(stats['success_rate'], 66.67)
        self.assertIn(QueryType.CITY_DELAY_ANALYSIS.value, stats['query_types'])
        self.assertIn(QueryType.CLIENT_FAILURE_ANALYSIS.value, stats['query_types'])
        self.assertEqual(len(stats['recent_queries']), 3)
    
    def test_supported_query_examples(self):
        """Test supported query examples."""
        examples = self.interface.get_supported_query_examples()
        
        self.assertIsInstance(examples, list)
        self.assertTrue(len(examples) > 0)
        
        for example in examples:
            self.assertIn('type', example)
            self.assertIn('example', example)
            self.assertIn('description', example)
    
    def test_system_readiness_validation(self):
        """Test system readiness validation."""
        # Mock successful component checks
        import pandas as pd
        mock_orders_df = pd.DataFrame({'order_id': [1, 2, 3]})
        self.mock_data_aggregator.get_orders.return_value = mock_orders_df
        
        self.mock_correlation_engine.find_patterns_by_city.return_value = {'patterns_found': False}
        
        readiness = self.interface.validate_system_readiness()
        
        self.assertIn('ready', readiness)
        self.assertIn('components', readiness)
        self.assertIn('issues', readiness)
        
        # Check that all expected components are validated
        expected_components = [
            'data_aggregator',
            'correlation_engine',
            'insight_generator',
            'query_processor',
            'response_generator'
        ]
        
        for component in expected_components:
            self.assertIn(component, readiness['components'])
    
    def test_query_history_limit(self):
        """Test that query history is limited to prevent memory issues."""
        # Add more than 100 queries
        for i in range(105):
            self.interface._record_query(
                f"Query {i}", 
                QueryType.CITY_DELAY_ANALYSIS, 
                {}, 
                True
            )
        
        # Should be limited to 100
        self.assertEqual(len(self.interface.query_history), 100)
        
        # Should contain the most recent queries
        self.assertEqual(self.interface.query_history[-1]['query'], "Query 104")
        self.assertEqual(self.interface.query_history[0]['query'], "Query 5")
    
    def test_generate_analysis_error_handling(self):
        """Test error handling in analysis generation."""
        # Test with missing parameters
        result = self.interface._generate_analysis(
            QueryType.CITY_DELAY_ANALYSIS, 
            {}  # Missing required parameters
        )
        
        self.assertIn('Error:', result)
        self.assertIn('Missing required parameters', result)
    
    def test_generate_analysis_client_resolution(self):
        """Test client name resolution in analysis generation."""
        # Mock client data
        import pandas as pd
        mock_clients_df = pd.DataFrame({
            'client_id': [1, 2, 3],
            'client_name': ['ABC Corp', 'XYZ Ltd', 'DEF Inc']
        })
        self.mock_data_aggregator.get_clients.return_value = mock_clients_df
        
        # Mock insight generator
        self.interface.insight_generator.generate_client_failure_analysis = Mock(return_value="Test analysis")
        
        parameters = {
            'client_name': 'ABC Corp',
            'start_date': datetime.now() - timedelta(days=7),
            'end_date': datetime.now()
        }
        
        result = self.interface._generate_analysis(QueryType.CLIENT_FAILURE_ANALYSIS, parameters)
        
        # Should call the insight generator with resolved client_id
        self.interface.insight_generator.generate_client_failure_analysis.assert_called_once()
        call_args = self.interface.insight_generator.generate_client_failure_analysis.call_args[0]
        self.assertEqual(call_args[0], 1)  # Should be resolved client_id


if __name__ == '__main__':
    unittest.main()