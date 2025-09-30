"""
Unit tests for the ResponseGenerator class.
Tests response generation, recommendation logic, and template formatting.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from response_generator import ResponseGenerator, RecommendationPriority
from query_processor import QueryType


class TestResponseGenerator(unittest.TestCase):
    """Test cases for ResponseGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock insight generator
        self.mock_insight_generator = Mock()
        self.response_generator = ResponseGenerator(self.mock_insight_generator)
    
    def test_initialization(self):
        """Test ResponseGenerator initialization."""
        self.assertIsNotNone(self.response_generator.insight_generator)
        self.assertIsNotNone(self.response_generator.templates)
        self.assertIsNotNone(self.response_generator.recommendation_rules)
        self.assertIsNotNone(self.response_generator.failure_reason_recommendations)
    
    def test_template_setup(self):
        """Test that templates are properly set up for all query types."""
        expected_query_types = [
            QueryType.CITY_DELAY_ANALYSIS,
            QueryType.CLIENT_FAILURE_ANALYSIS,
            QueryType.WAREHOUSE_FAILURE_ANALYSIS,
            QueryType.CITY_COMPARISON,
            QueryType.FESTIVAL_PERIOD_ANALYSIS,
            QueryType.CAPACITY_IMPACT_ANALYSIS
        ]
        
        for query_type in expected_query_types:
            with self.subTest(query_type=query_type):
                self.assertIn(query_type, self.response_generator.templates)
                template = self.response_generator.templates[query_type]
                self.assertIn('header', template)
                self.assertIn('summary_template', template)
                self.assertIn('context_template', template)
                self.assertIn('footer_template', template)
    
    def test_recommendation_rules_setup(self):
        """Test that recommendation rules are properly configured."""
        expected_rules = [
            'high_failure_rate',
            'moderate_failure_rate',
            'low_success_rate',
            'significant_delays',
            'moderate_delays',
            'high_volume_client',
            'capacity_strain'
        ]
        
        for rule_name in expected_rules:
            with self.subTest(rule_name=rule_name):
                self.assertIn(rule_name, self.response_generator.recommendation_rules)
                rule = self.response_generator.recommendation_rules[rule_name]
                self.assertIn('condition', rule)
                self.assertIn('priority', rule)
                self.assertIn('template', rule)
                self.assertIsInstance(rule['priority'], RecommendationPriority)
    
    def test_failure_reason_recommendations_setup(self):
        """Test that failure reason recommendations are properly configured."""
        expected_reasons = [
            'address',
            'payment',
            'customer unavailable',
            'weather',
            'traffic',
            'warehouse',
            'vehicle'
        ]
        
        for reason in expected_reasons:
            with self.subTest(reason=reason):
                self.assertIn(reason, self.response_generator.failure_reason_recommendations)
                config = self.response_generator.failure_reason_recommendations[reason]
                self.assertIn('priority', config)
                self.assertIn('recommendations', config)
                self.assertIsInstance(config['priority'], RecommendationPriority)
                self.assertIsInstance(config['recommendations'], list)
    
    def test_metrics_extraction(self):
        """Test extraction of metrics from analysis results."""
        analysis_text = """
        Analysis Results:
        - Success Rate: 85.5%
        - Failure Rate: 14.5%
        - Total Orders: 1,250
        - Average Delay: 3.2 hours
        """
        
        metrics = self.response_generator._extract_metrics_from_analysis(analysis_text)
        
        self.assertEqual(metrics['success_rate'], 85.5)
        self.assertEqual(metrics['failure_rate'], 14.5)
        self.assertEqual(metrics['total_orders'], 1250)
        self.assertEqual(metrics['average_delay_hours'], 3.2)
    
    def test_recommendation_rule_application(self):
        """Test application of recommendation rules based on metrics."""
        # Test high failure rate rule
        high_failure_metrics = {'failure_rate': 25.0}
        recommendations = self.response_generator._apply_recommendation_rules(high_failure_metrics)
        
        self.assertTrue(len(recommendations) > 0)
        high_failure_rec = next((r for r in recommendations if r['rule'] == 'high_failure_rate'), None)
        self.assertIsNotNone(high_failure_rec)
        self.assertEqual(high_failure_rec['priority'], RecommendationPriority.CRITICAL)
        
        # Test moderate delay rule
        moderate_delay_metrics = {'average_delay_hours': 3.0}
        recommendations = self.response_generator._apply_recommendation_rules(moderate_delay_metrics)
        
        moderate_delay_rec = next((r for r in recommendations if r['rule'] == 'moderate_delays'), None)
        self.assertIsNotNone(moderate_delay_rec)
        self.assertEqual(moderate_delay_rec['priority'], RecommendationPriority.MEDIUM)
    
    def test_failure_reason_recommendations(self):
        """Test generation of failure reason specific recommendations."""
        analysis_with_address_issues = "Primary failure reason: address verification failed"
        recommendations = self.response_generator._generate_failure_reason_recommendations(analysis_with_address_issues)
        
        self.assertTrue(len(recommendations) > 0)
        address_recs = [r for r in recommendations if r['reason'] == 'address']
        self.assertTrue(len(address_recs) > 0)
        
        for rec in address_recs:
            self.assertEqual(rec['priority'], RecommendationPriority.HIGH)
            self.assertIn('address', rec['text'].lower())
    
    def test_priority_ordering(self):
        """Test priority ordering functionality."""
        priorities = [
            RecommendationPriority.LOW,
            RecommendationPriority.CRITICAL,
            RecommendationPriority.MEDIUM,
            RecommendationPriority.HIGH
        ]
        
        orders = [self.response_generator._get_priority_order(p) for p in priorities]
        expected_orders = [4, 1, 3, 2]  # Critical=1, High=2, Medium=3, Low=4
        
        self.assertEqual(orders, expected_orders)
    
    def test_priority_icons(self):
        """Test priority icon mapping."""
        expected_icons = {
            RecommendationPriority.CRITICAL: "🚨",
            RecommendationPriority.HIGH: "⚠️",
            RecommendationPriority.MEDIUM: "💡",
            RecommendationPriority.LOW: "📝"
        }
        
        for priority, expected_icon in expected_icons.items():
            with self.subTest(priority=priority):
                icon = self.response_generator._get_priority_icon(priority)
                self.assertEqual(icon, expected_icon)
    
    def test_template_formatting(self):
        """Test template string formatting with parameters."""
        template = "Analysis for {city} on {date} with {total_orders} orders"
        parameters = {
            'city': 'Mumbai',
            'date': datetime(2023, 8, 15),
            'total_orders': 1500
        }
        
        formatted = self.response_generator._format_template_string(template, parameters)
        expected = "Analysis for Mumbai on August 15, 2023 with 1500 orders"
        self.assertEqual(formatted, expected)
    
    def test_template_formatting_missing_params(self):
        """Test template formatting with missing parameters."""
        template = "Analysis for {city} on {date}"
        parameters = {'city': 'Mumbai'}  # Missing 'date'
        
        # Should return original template when parameters are missing
        formatted = self.response_generator._format_template_string(template, parameters)
        self.assertEqual(formatted, template)
    
    def test_generate_response_city_delay(self):
        """Test response generation for city delay analysis."""
        query_type = QueryType.CITY_DELAY_ANALYSIS
        parameters = {
            'city': 'Mumbai',
            'date': datetime(2023, 8, 15),
            'original_query': 'Why were deliveries delayed in Mumbai yesterday?'
        }
        analysis_result = "Test analysis result with Success Rate: 80% and Failure Rate: 20%"
        
        response = self.response_generator.generate_response(query_type, parameters, analysis_result)
        
        self.assertIn('City Delivery Delay Analysis', response)
        self.assertIn('Mumbai', response)
        self.assertIn('August 15, 2023', response)
        self.assertIn(analysis_result, response)
        self.assertIn('Strategic Recommendations', response)
    
    def test_generate_response_unknown_query(self):
        """Test response generation for unknown query types."""
        original_query = "What is the weather today?"
        response = self.response_generator._generate_unknown_query_response(original_query)
        
        self.assertIn('Query Not Recognized', response)
        self.assertIn(original_query, response)
        self.assertIn('Supported Query Types', response)
        self.assertIn('City Delay Analysis', response)
        self.assertIn('Client Failure Analysis', response)
    
    def test_executive_summary_generation(self):
        """Test executive summary generation."""
        query_type = QueryType.CLIENT_FAILURE_ANALYSIS
        parameters = {
            'client_name': 'ABC Corp',
            'start_date': datetime(2023, 8, 1),
            'end_date': datetime(2023, 8, 31)
        }
        analysis_result = "Analysis shows Success Rate: 75% and Failure Rate: 25% with Total Orders: 2000"
        
        summary = self.response_generator.generate_executive_summary(query_type, parameters, analysis_result)
        
        self.assertIn('EXECUTIVE SUMMARY', summary)
        self.assertIn('Key Performance Indicators', summary)
        self.assertIn('Business Impact', summary)
        self.assertIn('75.0%', summary)  # Success rate
        self.assertIn('25.0%', summary)  # Failure rate
    
    def test_business_impact_assessment(self):
        """Test business impact assessment logic."""
        # High impact scenario
        high_impact_metrics = {'failure_rate': 25.0, 'success_rate': 70.0}
        impact = self.response_generator._assess_business_impact(high_impact_metrics)
        self.assertIn('HIGH', impact)
        self.assertIn('🚨', impact)
        
        # Medium impact scenario
        medium_impact_metrics = {'failure_rate': 15.0, 'success_rate': 82.0}
        impact = self.response_generator._assess_business_impact(medium_impact_metrics)
        self.assertIn('MEDIUM', impact)
        self.assertIn('⚠️', impact)
        
        # Low impact scenario
        low_impact_metrics = {'failure_rate': 5.0, 'success_rate': 95.0}
        impact = self.response_generator._assess_business_impact(low_impact_metrics)
        self.assertIn('LOW', impact)
        self.assertIn('✅', impact)
    
    def test_resource_requirements_assessment(self):
        """Test resource requirements assessment."""
        # High failure rate scenario
        high_failure_metrics = {'failure_rate': 25.0}
        resources = self.response_generator._assess_resource_requirements(high_failure_metrics, QueryType.CLIENT_FAILURE_ANALYSIS)
        self.assertIn('emergency response', resources.lower())
        
        # High volume scenario
        high_volume_metrics = {'order_volume': 20000}
        resources = self.response_generator._assess_resource_requirements(high_volume_metrics, QueryType.CAPACITY_IMPACT_ANALYSIS)
        self.assertIn('capacity expansion', resources.lower())
        
        # Normal scenario
        normal_metrics = {'failure_rate': 5.0}
        resources = self.response_generator._assess_resource_requirements(normal_metrics, QueryType.CITY_DELAY_ANALYSIS)
        self.assertIn('standard operational', resources.lower())
    
    def test_type_specific_recommendations(self):
        """Test generation of query type specific recommendations."""
        # Test city delay analysis recommendations
        city_params = {'city': 'Mumbai'}
        city_metrics = {}
        city_recs = self.response_generator._generate_type_specific_recommendations(
            QueryType.CITY_DELAY_ANALYSIS, city_params, city_metrics
        )
        
        self.assertTrue(len(city_recs) > 0)
        mumbai_rec = next((r for r in city_recs if 'Mumbai' in r['text']), None)
        self.assertIsNotNone(mumbai_rec)
        
        # Test festival period analysis recommendations
        festival_recs = self.response_generator._generate_type_specific_recommendations(
            QueryType.FESTIVAL_PERIOD_ANALYSIS, {}, {}
        )
        
        self.assertTrue(len(festival_recs) > 0)
        seasonal_rec = next((r for r in festival_recs if 'seasonal' in r['text'].lower()), None)
        self.assertIsNotNone(seasonal_rec)


if __name__ == '__main__':
    unittest.main()