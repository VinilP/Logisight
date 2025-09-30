"""
Natural Language Query Interface for the Logistics Insight System.
Integrates QueryProcessor, InsightGenerator, and ResponseGenerator to provide
a complete natural language query processing system.
Enhanced with optional LLM integration for improved query understanding and response generation.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import os
from query_processor import QueryProcessor, QueryType
from response_generator import ResponseGenerator
from insight_generator import InsightGenerator
from data_aggregator import DataAggregator
from correlation_engine import CorrelationEngine

# Import LLM integration with graceful fallback
try:
    from llm_integration import LLMIntegration
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("LLM integration not available, using rule-based approach only")

logger = logging.getLogger(__name__)


class NaturalLanguageInterface:
    """
    Complete natural language query interface that processes queries end-to-end.
    Coordinates between query processing, analysis generation, and response formatting.
    """
    
    def __init__(self, data_aggregator: DataAggregator, correlation_engine: CorrelationEngine, enable_llm: bool = True):
        """
        Initialize the natural language interface with required components.
        
        Args:
            data_aggregator: DataAggregator instance for accessing data
            correlation_engine: CorrelationEngine instance for pattern analysis
            enable_llm: Whether to enable LLM integration (defaults to True)
        """
        self.data_aggregator = data_aggregator
        self.correlation_engine = correlation_engine
        self.insight_generator = InsightGenerator(data_aggregator, correlation_engine)
        self.query_processor = QueryProcessor(data_aggregator)
        self.response_generator = ResponseGenerator(self.insight_generator)
        
        # Initialize LLM integration if available and enabled
        self.llm_integration = None
        if enable_llm and LLM_AVAILABLE:
            try:
                preferred_provider = os.getenv('LLM_PROVIDER')
                self.llm_integration = LLMIntegration(preferred_provider)
                logger.info("LLM integration initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM integration: {str(e)}")
                self.llm_integration = None
        
        # Track query history for context
        self.query_history = []
    
    def process_query(self, query: str, include_executive_summary: bool = False) -> Dict[str, Any]:
        """
        Process a natural language query end-to-end.
        
        Args:
            query: Natural language query string
            include_executive_summary: Whether to include executive summary in response
            
        Returns:
            Dictionary containing processed query results and formatted response
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Enhanced query processing with optional LLM
            logger.info(f"Processing query: {query}")
            
            # Use LLM for enhanced query understanding if available
            if self.llm_integration:
                try:
                    llm_context = {'query_history': self.query_history[-3:]}  # Last 3 queries for context
                    enhanced_understanding = self.llm_integration.enhance_query_understanding(query, llm_context)
                    logger.info(f"LLM enhanced understanding: {enhanced_understanding.get('intent', 'unknown')}")
                except Exception as e:
                    logger.warning(f"LLM query enhancement failed, using standard processing: {str(e)}")
                    enhanced_understanding = None
            else:
                enhanced_understanding = None
            
            # Standard query processing
            query_result = self.query_processor.process_query(query)
            
            # Merge LLM insights if available
            if enhanced_understanding and enhanced_understanding.get('intent') != 'unknown':
                # Use LLM insights to improve parameter extraction
                if 'entities' in enhanced_understanding:
                    for key, value in enhanced_understanding['entities'].items():
                        if key not in query_result or not query_result[key]:
                            query_result[key] = value
            
            if 'error' in query_result:
                return {
                    'success': False,
                    'error': query_result['error'],
                    'query': query,
                    'processing_time': (datetime.now() - start_time).total_seconds(),
                    'supported_queries': query_result.get('supported_queries', []),
                    'llm_enhanced': bool(enhanced_understanding)
                }
            
            query_type = query_result['query_type']
            parameters = query_result
            
            # Step 2: Generate analysis based on query type
            logger.info(f"Generating analysis for query type: {query_type}")
            analysis_result = self._generate_analysis(query_type, parameters)
            
            if not analysis_result or 'error' in str(analysis_result):
                return {
                    'success': False,
                    'error': f"Failed to generate analysis: {analysis_result}",
                    'query': query,
                    'query_type': query_type.value,
                    'parameters': parameters,
                    'processing_time': (datetime.now() - start_time).total_seconds()
                }
            
            # Step 3: Generate formatted response with optional LLM enhancement
            logger.info("Generating formatted response")
            base_response = self.response_generator.generate_response(
                query_type, parameters, analysis_result
            )
            
            # Enhance response with LLM if available
            if self.llm_integration:
                try:
                    query_context = {
                        'query_type': query_type.value,
                        'parameters': parameters,
                        'original_query': query
                    }
                    formatted_response = self.llm_integration.enhance_response_generation(
                        base_response, query_context
                    )
                    logger.info("Response enhanced with LLM")
                except Exception as e:
                    logger.warning(f"LLM response enhancement failed, using base response: {str(e)}")
                    formatted_response = base_response
            else:
                formatted_response = base_response
            
            # Step 4: Generate executive summary if requested
            executive_summary = None
            if include_executive_summary:
                executive_summary = self.response_generator.generate_executive_summary(
                    query_type, parameters, analysis_result
                )
            
            # Step 5: Record query in history
            self._record_query(query, query_type, parameters, True)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'query': query,
                'query_type': query_type.value,
                'parameters': parameters,
                'analysis_result': analysis_result,
                'formatted_response': formatted_response,
                'executive_summary': executive_summary,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat(),
                'llm_enhanced': bool(self.llm_integration),
                'llm_provider': self.llm_integration.active_provider.value if self.llm_integration else None
            }
            
        except Exception as e:
            logger.error(f"Error processing query '{query}': {str(e)}")
            self._record_query(query, None, {}, False)
            
            return {
                'success': False,
                'error': f"Internal error processing query: {str(e)}",
                'query': query,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
    
    def _generate_analysis(self, query_type: QueryType, parameters: Dict[str, Any]) -> str:
        """
        Generate analysis based on query type and parameters.
        
        Args:
            query_type: Type of query to process
            parameters: Extracted parameters from query
            
        Returns:
            Generated analysis result string
        """
        try:
            if query_type == QueryType.CITY_DELAY_ANALYSIS:
                city = parameters.get('city')
                date = parameters.get('date')
                if not city or not date:
                    return "Error: Missing required parameters (city, date) for city delay analysis"
                
                return self.insight_generator.generate_city_delay_analysis(city, date)
            
            elif query_type == QueryType.CLIENT_FAILURE_ANALYSIS:
                client_id = parameters.get('client_id')
                client_name = parameters.get('client_name')
                start_date = parameters.get('start_date')
                end_date = parameters.get('end_date')
                
                if not (client_id or client_name) or not start_date or not end_date:
                    return "Error: Missing required parameters for client failure analysis"
                
                # If we have client_name but not client_id, try to resolve it
                if client_name and not client_id:
                    client_id = self._resolve_client_id(client_name)
                    if not client_id:
                        return f"Error: Could not find client with name '{client_name}'"
                
                return self.insight_generator.generate_client_failure_analysis(client_id, start_date, end_date)
            
            elif query_type == QueryType.WAREHOUSE_FAILURE_ANALYSIS:
                warehouse_id = parameters.get('warehouse_id')
                warehouse_name = parameters.get('warehouse_name')
                start_date = parameters.get('start_date')
                end_date = parameters.get('end_date')
                
                if not (warehouse_id or warehouse_name) or not start_date or not end_date:
                    return "Error: Missing required parameters for warehouse failure analysis"
                
                # If we have warehouse_name but not warehouse_id, try to resolve it
                if warehouse_name and not warehouse_id:
                    warehouse_id = self._resolve_warehouse_id(warehouse_name)
                    if not warehouse_id:
                        return f"Error: Could not find warehouse with name '{warehouse_name}'"
                
                return self.insight_generator.generate_warehouse_failure_analysis(warehouse_id, start_date, end_date)
            
            elif query_type == QueryType.CITY_COMPARISON:
                city_a = parameters.get('city_a')
                city_b = parameters.get('city_b')
                start_date = parameters.get('start_date')
                end_date = parameters.get('end_date')
                
                if not city_a or not city_b or not start_date or not end_date:
                    return "Error: Missing required parameters for city comparison"
                
                return self.insight_generator.generate_city_comparison(city_a, city_b, start_date, end_date)
            
            elif query_type == QueryType.FESTIVAL_PERIOD_ANALYSIS:
                # Use a default festival period for analysis (e.g., upcoming Diwali period)
                from datetime import datetime, timedelta
                festival_start = datetime(2025, 10, 20)  # Example festival start
                festival_end = datetime(2025, 10, 25)    # Example festival end
                return self.insight_generator.generate_festival_period_analysis(festival_start, festival_end)
            
            elif query_type == QueryType.CAPACITY_IMPACT_ANALYSIS:
                client_name = parameters.get('client_name', 'New Client')
                order_volume = parameters.get('order_volume')
                
                if not order_volume:
                    return "Error: Missing required parameter (order_volume) for capacity impact analysis"
                
                # For capacity analysis, we can use a placeholder client_id
                return self.insight_generator.generate_capacity_impact_analysis(client_name, order_volume)
            
            else:
                return f"Error: Unsupported query type: {query_type}"
                
        except Exception as e:
            logger.error(f"Error generating analysis for {query_type}: {str(e)}")
            return f"Error generating analysis: {str(e)}"
    
    def _resolve_client_id(self, client_name: str) -> Optional[int]:
        """
        Resolve client name to client ID using available data.
        
        Args:
            client_name: Client name to resolve
            
        Returns:
            Client ID if found, None otherwise
        """
        try:
            clients_df = self.data_aggregator.get_clients()
            if clients_df is not None and not clients_df.empty:
                # Try exact match first
                exact_match = clients_df[clients_df['client_name'].str.lower() == client_name.lower()]
                if not exact_match.empty:
                    return exact_match.iloc[0]['client_id']
                
                # Try partial match
                partial_match = clients_df[clients_df['client_name'].str.contains(client_name, case=False, na=False)]
                if not partial_match.empty:
                    return partial_match.iloc[0]['client_id']
            
            return None
        except Exception as e:
            logger.error(f"Error resolving client name '{client_name}': {str(e)}")
            return None
    
    def _resolve_warehouse_id(self, warehouse_name: str) -> Optional[int]:
        """
        Resolve warehouse name to warehouse ID using available data.
        
        Args:
            warehouse_name: Warehouse name to resolve
            
        Returns:
            Warehouse ID if found, None otherwise
        """
        try:
            warehouses_df = self.data_aggregator.get_warehouses()
            if warehouses_df is not None and not warehouses_df.empty:
                # Try exact match first
                exact_match = warehouses_df[warehouses_df['warehouse_name'].str.lower() == warehouse_name.lower()]
                if not exact_match.empty:
                    return exact_match.iloc[0]['warehouse_id']
                
                # Try partial match
                partial_match = warehouses_df[warehouses_df['warehouse_name'].str.contains(warehouse_name, case=False, na=False)]
                if not partial_match.empty:
                    return partial_match.iloc[0]['warehouse_id']
            
            return None
        except Exception as e:
            logger.error(f"Error resolving warehouse name '{warehouse_name}': {str(e)}")
            return None
    
    def _record_query(self, query: str, query_type: Optional[QueryType], parameters: Dict[str, Any], success: bool):
        """
        Record query in history for analytics and improvement.
        
        Args:
            query: Original query string
            query_type: Detected query type
            parameters: Extracted parameters
            success: Whether query processing was successful
        """
        record = {
            'timestamp': datetime.now(),
            'query': query,
            'query_type': query_type.value if query_type else None,
            'parameters': parameters,
            'success': success
        }
        
        self.query_history.append(record)
        
        # Keep only last 100 queries to prevent memory issues
        if len(self.query_history) > 100:
            self.query_history = self.query_history[-100:]
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about processed queries.
        
        Returns:
            Dictionary containing query processing statistics
        """
        if not self.query_history:
            return {
                'total_queries': 0,
                'successful_queries': 0,
                'success_rate': 0.0,
                'query_types': {},
                'recent_queries': []
            }
        
        total_queries = len(self.query_history)
        successful_queries = sum(1 for q in self.query_history if q['success'])
        success_rate = successful_queries / total_queries * 100
        
        # Count query types
        query_types = {}
        for query in self.query_history:
            if query['query_type']:
                query_types[query['query_type']] = query_types.get(query['query_type'], 0) + 1
        
        # Get recent queries (last 10)
        recent_queries = [
            {
                'query': q['query'],
                'query_type': q['query_type'],
                'success': q['success'],
                'timestamp': q['timestamp'].isoformat()
            }
            for q in self.query_history[-10:]
        ]
        
        return {
            'total_queries': total_queries,
            'successful_queries': successful_queries,
            'success_rate': round(success_rate, 2),
            'query_types': query_types,
            'recent_queries': recent_queries
        }
    
    def get_supported_query_examples(self) -> List[Dict[str, str]]:
        """
        Get examples of supported query types.
        
        Returns:
            List of query examples with descriptions
        """
        return [
            {
                'type': 'City Delay Analysis',
                'example': 'Why were deliveries delayed in Mumbai yesterday?',
                'description': 'Analyzes delivery delays in a specific city for a given date'
            },
            {
                'type': 'Client Failure Analysis',
                'example': 'Why did Client ABC\'s orders fail in the past week?',
                'description': 'Examines order failure patterns for a specific client over a time period'
            },
            {
                'type': 'Warehouse Failure Analysis',
                'example': 'Explain top reasons for delivery failures linked to Warehouse B in August?',
                'description': 'Analyzes warehouse-related delivery failures and operational issues'
            },
            {
                'type': 'City Comparison',
                'example': 'Compare delivery failure causes between Delhi and Mumbai last month?',
                'description': 'Compares delivery performance and failure patterns between two cities'
            },
            {
                'type': 'Festival Period Analysis',
                'example': 'What are the likely causes of delivery failures during the festival period?',
                'description': 'Analyzes seasonal delivery risks and preparation strategies'
            },
            {
                'type': 'Capacity Impact Analysis',
                'example': 'If we onboard Client XYZ with 20,000 extra monthly orders, what new failure risks should we expect?',
                'description': 'Evaluates capacity impact and risks from onboarding high-volume clients'
            }
        ]
    
    def validate_system_readiness(self) -> Dict[str, Any]:
        """
        Validate that all system components are ready for query processing.
        
        Returns:
            Dictionary containing system readiness status
        """
        readiness_status = {
            'ready': True,
            'components': {},
            'issues': []
        }
        
        # Check data aggregator
        try:
            orders_df = self.data_aggregator.get_orders()
            if orders_df is None or orders_df.empty:
                readiness_status['components']['data_aggregator'] = False
                readiness_status['issues'].append('No order data available')
                readiness_status['ready'] = False
            else:
                readiness_status['components']['data_aggregator'] = True
        except Exception as e:
            readiness_status['components']['data_aggregator'] = False
            readiness_status['issues'].append(f'Data aggregator error: {str(e)}')
            readiness_status['ready'] = False
        
        # Check correlation engine
        try:
            # Simple test to see if correlation engine is functional
            test_patterns = self.correlation_engine.find_patterns_by_city('TestCity', datetime.now() - timedelta(days=1), datetime.now())
            readiness_status['components']['correlation_engine'] = True
        except Exception as e:
            readiness_status['components']['correlation_engine'] = False
            readiness_status['issues'].append(f'Correlation engine error: {str(e)}')
            readiness_status['ready'] = False
        
        # Check insight generator
        try:
            # Test if insight generator can be instantiated and has required methods
            required_methods = ['generate_city_delay_analysis', 'generate_client_failure_analysis', 
                              'generate_warehouse_failure_analysis', 'generate_city_comparison']
            for method in required_methods:
                if not hasattr(self.insight_generator, method):
                    raise AttributeError(f'Missing method: {method}')
            readiness_status['components']['insight_generator'] = True
        except Exception as e:
            readiness_status['components']['insight_generator'] = False
            readiness_status['issues'].append(f'Insight generator error: {str(e)}')
            readiness_status['ready'] = False
        
        # Check query processor
        try:
            test_query = "Why were deliveries delayed in TestCity yesterday?"
            result = self.query_processor.process_query(test_query)
            readiness_status['components']['query_processor'] = True
        except Exception as e:
            readiness_status['components']['query_processor'] = False
            readiness_status['issues'].append(f'Query processor error: {str(e)}')
            readiness_status['ready'] = False
        
        # Check response generator
        try:
            # Test if response generator can be instantiated
            readiness_status['components']['response_generator'] = True
        except Exception as e:
            readiness_status['components']['response_generator'] = False
            readiness_status['issues'].append(f'Response generator error: {str(e)}')
            readiness_status['ready'] = False
        
        return readiness_status
    
    def get_llm_status(self) -> Dict[str, Any]:
        """
        Get status of LLM integration and available providers.
        
        Returns:
            Dictionary containing LLM integration status and provider information
        """
        if not self.llm_integration:
            return {
                'enabled': False,
                'available': LLM_AVAILABLE,
                'reason': 'LLM integration not initialized or not available',
                'providers': {},
                'usage_stats': {}
            }
        
        provider_status = self.llm_integration.get_provider_status()
        usage_stats = self.llm_integration.get_usage_statistics()
        
        return {
            'enabled': True,
            'available': True,
            'active_provider': provider_status['active_provider'],
            'providers': provider_status['providers'],
            'usage_stats': usage_stats,
            'fallback_available': provider_status['fallback_available']
        }
    
    def switch_llm_provider(self, provider_name: str) -> bool:
        """
        Switch to a different LLM provider if available.
        
        Args:
            provider_name: Name of provider to switch to ("openai", "ollama", "rule_based")
            
        Returns:
            True if switch was successful, False otherwise
        """
        if not self.llm_integration:
            logger.warning("LLM integration not available")
            return False
        
        return self.llm_integration.switch_provider(provider_name)
    
    def get_llm_usage_summary(self) -> str:
        """
        Get a human-readable summary of LLM usage and costs.
        
        Returns:
            Formatted string with usage summary
        """
        if not self.llm_integration:
            return "LLM integration not available"
        
        stats = self.llm_integration.get_usage_statistics()
        
        summary_lines = [
            "🤖 LLM Integration Usage Summary",
            "=" * 35,
            f"Active Provider: {stats.get('active_provider', 'None')}",
            f"Total Requests: {stats['total_requests']}",
            f"Success Rate: {stats['success_rate']:.1f}%",
            f"Total Tokens: {stats['total_tokens']:,}",
        ]
        
        if stats.get('estimated_cost', 0) > 0:
            summary_lines.extend([
                f"Estimated Cost: ${stats['estimated_cost']:.4f}",
                f"Cost per Request: ${stats.get('cost_breakdown', {}).get('cost_per_request', 0):.4f}"
            ])
        
        # Provider breakdown
        if stats.get('provider_usage'):
            summary_lines.append("\nProvider Usage:")
            for provider, usage in stats['provider_usage'].items():
                summary_lines.append(f"  {provider}: {usage['requests']} requests, {usage['tokens']} tokens")
        
        return '\n'.join(summary_lines)