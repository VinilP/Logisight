"""
Response Generation System for the Logistics Insight System.
Creates sophisticated template-based ResponseGenerator class with business context.
Adds recommendation generation based on identified failure patterns using rule-based logic.
Implements actionable suggestion logic for operational improvements.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from enum import Enum
from query_processor import QueryType
from insight_generator import InsightGenerator

logger = logging.getLogger(__name__)


class RecommendationPriority(Enum):
    """Priority levels for recommendations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ResponseGenerator:
    """
    Generates sophisticated, context-aware responses with actionable recommendations.
    Uses template-based approach with business intelligence for operational improvements.
    """
    
    def __init__(self, insight_generator: InsightGenerator):
        """
        Initialize ResponseGenerator with insight generator.
        
        Args:
            insight_generator: InsightGenerator instance for generating analysis
        """
        self.insight_generator = insight_generator
        self._setup_templates()
        self._setup_recommendation_rules()
    
    def _setup_templates(self):
        """Set up response templates for different query types."""
        
        self.templates = {
            QueryType.CITY_DELAY_ANALYSIS: {
                'header': "🚚 City Delivery Delay Analysis",
                'summary_template': "Analysis of delivery delays in {city} on {date}",
                'context_template': "This analysis examines delivery performance, external factors, and operational challenges affecting {city} on the specified date.",
                'footer_template': "💡 Recommendations are prioritized by potential impact on delivery performance."
            },
            
            QueryType.CLIENT_FAILURE_ANALYSIS: {
                'header': "👤 Client Order Failure Analysis", 
                'summary_template': "Analysis of order failures for {client_name} from {start_date} to {end_date}",
                'context_template': "This analysis examines order patterns, failure causes, and service quality issues for the specified client and time period.",
                'footer_template': "💡 Recommendations focus on improving client satisfaction and reducing future failures."
            },
            
            QueryType.WAREHOUSE_FAILURE_ANALYSIS: {
                'header': "🏭 Warehouse Performance Analysis",
                'summary_template': "Analysis of delivery failures linked to {warehouse_name} from {start_date} to {end_date}",
                'context_template': "This analysis examines warehouse operations, processing efficiency, and downstream delivery impacts for the specified facility and time period.",
                'footer_template': "💡 Recommendations target operational efficiency and quality improvements."
            },
            
            QueryType.CITY_COMPARISON: {
                'header': "🔄 City Performance Comparison",
                'summary_template': "Comparative analysis of delivery performance between {city_a} and {city_b} from {start_date} to {end_date}",
                'context_template': "This analysis compares delivery success rates, failure patterns, and operational challenges between two cities to identify best practices and improvement opportunities.",
                'footer_template': "💡 Recommendations focus on standardizing best practices and addressing location-specific challenges."
            },
            
            QueryType.FESTIVAL_PERIOD_ANALYSIS: {
                'header': "🎉 Festival Period Risk Analysis",
                'summary_template': "Analysis of delivery failure risks and preparation strategies for festival periods",
                'context_template': "This analysis examines seasonal patterns, capacity constraints, and external factors that typically impact delivery performance during high-demand festival periods.",
                'footer_template': "💡 Recommendations provide proactive strategies for managing seasonal demand spikes."
            },
            
            QueryType.CAPACITY_IMPACT_ANALYSIS: {
                'header': "📈 Capacity Impact Assessment",
                'summary_template': "Analysis of potential failure risks from onboarding {client_name} with {order_volume:,} additional monthly orders",
                'context_template': "This analysis evaluates system capacity, resource requirements, and potential failure points when scaling operations for new high-volume clients.",
                'footer_template': "💡 Recommendations focus on risk mitigation and capacity planning for successful client onboarding."
            }
        }
    
    def _setup_recommendation_rules(self):
        """Set up rule-based recommendation generation logic."""
        
        self.recommendation_rules = {
            # Failure rate based recommendations
            'high_failure_rate': {
                'condition': lambda metrics: metrics.get('failure_rate', 0) > 20,
                'priority': RecommendationPriority.CRITICAL,
                'template': "URGENT: Failure rate of {failure_rate:.1f}% requires immediate intervention. Implement emergency response protocols and conduct root cause analysis.",
                'actions': [
                    "Schedule emergency operations review meeting",
                    "Implement enhanced monitoring and alerting",
                    "Deploy additional quality assurance resources"
                ]
            },
            
            'moderate_failure_rate': {
                'condition': lambda metrics: 10 < metrics.get('failure_rate', 0) <= 20,
                'priority': RecommendationPriority.HIGH,
                'template': "Elevated failure rate of {failure_rate:.1f}% indicates systemic issues requiring attention.",
                'actions': [
                    "Conduct detailed failure pattern analysis",
                    "Review and optimize operational procedures",
                    "Increase customer communication protocols"
                ]
            },
            
            # Success rate based recommendations
            'low_success_rate': {
                'condition': lambda metrics: metrics.get('success_rate', 100) < 80,
                'priority': RecommendationPriority.HIGH,
                'template': "Success rate of {success_rate:.1f}% is below acceptable standards. Focus on operational improvements.",
                'actions': [
                    "Implement performance improvement program",
                    "Review resource allocation and staffing",
                    "Enhance training and quality control measures"
                ]
            },
            
            # Delay based recommendations
            'significant_delays': {
                'condition': lambda metrics: metrics.get('average_delay_hours', 0) > 4,
                'priority': RecommendationPriority.HIGH,
                'template': "Average delays of {average_delay_hours:.1f} hours significantly impact customer satisfaction.",
                'actions': [
                    "Optimize route planning and scheduling",
                    "Review traffic patterns and delivery windows",
                    "Consider additional delivery capacity during peak times"
                ]
            },
            
            'moderate_delays': {
                'condition': lambda metrics: 2 < metrics.get('average_delay_hours', 0) <= 4,
                'priority': RecommendationPriority.MEDIUM,
                'template': "Moderate delays of {average_delay_hours:.1f} hours suggest room for efficiency improvements.",
                'actions': [
                    "Fine-tune delivery scheduling algorithms",
                    "Implement predictive traffic analysis",
                    "Optimize warehouse dispatch timing"
                ]
            },
            
            # Volume based recommendations
            'high_volume_client': {
                'condition': lambda metrics: metrics.get('total_orders', 0) > 1000,
                'priority': RecommendationPriority.MEDIUM,
                'template': "High order volume of {total_orders:,} orders requires specialized handling procedures.",
                'actions': [
                    "Assign dedicated account management resources",
                    "Implement priority processing workflows",
                    "Establish direct communication channels"
                ]
            },
            
            # Capacity based recommendations
            'capacity_strain': {
                'condition': lambda metrics: metrics.get('order_volume', 0) > 15000,
                'priority': RecommendationPriority.CRITICAL,
                'template': "Adding {order_volume:,} monthly orders will strain current capacity. Immediate scaling required.",
                'actions': [
                    "Conduct comprehensive capacity assessment",
                    "Plan infrastructure and staffing expansion",
                    "Implement phased onboarding approach"
                ]
            }
        }
        
        # Failure reason specific recommendations
        self.failure_reason_recommendations = {
            'address': {
                'priority': RecommendationPriority.HIGH,
                'recommendations': [
                    "Implement automated address verification system",
                    "Establish customer contact protocols for address confirmation",
                    "Create address quality scoring and validation workflows",
                    "Train customer service team on address resolution procedures"
                ]
            },
            
            'payment': {
                'priority': RecommendationPriority.HIGH,
                'recommendations': [
                    "Enhance payment verification processes",
                    "Offer multiple payment method options",
                    "Implement payment retry mechanisms",
                    "Provide clear payment status communication to customers"
                ]
            },
            
            'customer unavailable': {
                'priority': RecommendationPriority.MEDIUM,
                'recommendations': [
                    "Implement flexible delivery scheduling options",
                    "Enhance customer notification and communication systems",
                    "Offer alternative delivery locations (pickup points)",
                    "Provide real-time delivery tracking and updates"
                ]
            },
            
            'weather': {
                'priority': RecommendationPriority.MEDIUM,
                'recommendations': [
                    "Develop weather-based contingency plans",
                    "Implement weather monitoring and alert systems",
                    "Create alternative routing for weather-affected areas",
                    "Establish customer communication protocols for weather delays"
                ]
            },
            
            'traffic': {
                'priority': RecommendationPriority.MEDIUM,
                'recommendations': [
                    "Optimize delivery routes using real-time traffic data",
                    "Adjust delivery windows based on traffic patterns",
                    "Consider alternative transportation methods for congested areas",
                    "Implement dynamic route optimization algorithms"
                ]
            },
            
            'warehouse': {
                'priority': RecommendationPriority.HIGH,
                'recommendations': [
                    "Review warehouse operational procedures",
                    "Optimize picking and packing workflows",
                    "Implement inventory management improvements",
                    "Enhance warehouse staff training and performance monitoring"
                ]
            },
            
            'vehicle': {
                'priority': RecommendationPriority.HIGH,
                'recommendations': [
                    "Implement preventive vehicle maintenance programs",
                    "Establish backup vehicle availability protocols",
                    "Review vehicle capacity and route assignments",
                    "Create vehicle breakdown response procedures"
                ]
            }
        }
    
    def generate_response(self, query_type: QueryType, parameters: Dict[str, Any], analysis_result: str) -> str:
        """
        Generate a comprehensive response with business context and recommendations.
        
        Args:
            query_type: Type of query being processed
            parameters: Extracted parameters from the query
            analysis_result: Raw analysis result from InsightGenerator
            
        Returns:
            Formatted response with context, analysis, and recommendations
        """
        if query_type not in self.templates:
            return self._generate_unknown_query_response(parameters.get('original_query', ''))
        
        template = self.templates[query_type]
        
        # Build response components
        response_parts = []
        
        # Add header
        response_parts.append(f"{template['header']}\n{'=' * len(template['header'])}\n")
        
        # Add summary
        summary = self._format_template_string(template['summary_template'], parameters)
        response_parts.append(f"**Summary:** {summary}\n")
        
        # Add context
        context = self._format_template_string(template['context_template'], parameters)
        response_parts.append(f"**Context:** {context}\n")
        
        # Add timestamp
        response_parts.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Add main analysis
        response_parts.append("## Analysis Results\n")
        response_parts.append(analysis_result)
        
        # Generate and add recommendations
        recommendations = self._generate_recommendations(query_type, parameters, analysis_result)
        if recommendations:
            response_parts.append("\n## Strategic Recommendations\n")
            response_parts.append(recommendations)
        
        # Add footer
        response_parts.append(f"\n---\n{template['footer_template']}")
        
        return '\n'.join(response_parts)
    
    def _generate_recommendations(self, query_type: QueryType, parameters: Dict[str, Any], analysis_result: str) -> str:
        """
        Generate actionable recommendations based on analysis results and business rules.
        
        Args:
            query_type: Type of query being processed
            parameters: Extracted parameters from the query
            analysis_result: Raw analysis result from InsightGenerator
            
        Returns:
            Formatted recommendations string
        """
        recommendations = []
        
        # Extract metrics from analysis result (simplified approach)
        metrics = self._extract_metrics_from_analysis(analysis_result)
        
        # Apply rule-based recommendations
        rule_recommendations = self._apply_recommendation_rules(metrics)
        recommendations.extend(rule_recommendations)
        
        # Add failure reason specific recommendations
        failure_recommendations = self._generate_failure_reason_recommendations(analysis_result)
        recommendations.extend(failure_recommendations)
        
        # Add query type specific recommendations
        type_recommendations = self._generate_type_specific_recommendations(query_type, parameters, metrics)
        recommendations.extend(type_recommendations)
        
        if not recommendations:
            return "No specific recommendations generated. Continue monitoring performance metrics."
        
        # Sort by priority and format
        recommendations.sort(key=lambda x: self._get_priority_order(x.get('priority', RecommendationPriority.LOW)))
        
        formatted_recommendations = []
        for i, rec in enumerate(recommendations[:8], 1):  # Limit to top 8 recommendations
            priority_icon = self._get_priority_icon(rec.get('priority', RecommendationPriority.LOW))
            formatted_recommendations.append(f"{i}. {priority_icon} {rec['text']}")
            
            if 'actions' in rec and rec['actions']:
                for action in rec['actions'][:3]:  # Limit to top 3 actions per recommendation
                    formatted_recommendations.append(f"   • {action}")
        
        return '\n'.join(formatted_recommendations)
    
    def _apply_recommendation_rules(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply rule-based recommendation logic based on extracted metrics.
        
        Args:
            metrics: Dictionary of extracted metrics
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        for rule_name, rule in self.recommendation_rules.items():
            if rule['condition'](metrics):
                rec_text = rule['template'].format(**metrics)
                recommendation = {
                    'text': rec_text,
                    'priority': rule['priority'],
                    'actions': rule.get('actions', []),
                    'rule': rule_name
                }
                recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_failure_reason_recommendations(self, analysis_result: str) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on identified failure reasons in the analysis.
        
        Args:
            analysis_result: Raw analysis result text
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        analysis_lower = analysis_result.lower()
        
        for reason_key, reason_config in self.failure_reason_recommendations.items():
            if reason_key in analysis_lower:
                for rec_text in reason_config['recommendations'][:2]:  # Limit to top 2 per reason
                    recommendation = {
                        'text': rec_text,
                        'priority': reason_config['priority'],
                        'reason': reason_key
                    }
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_type_specific_recommendations(self, query_type: QueryType, parameters: Dict[str, Any], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations specific to the query type.
        
        Args:
            query_type: Type of query being processed
            parameters: Extracted parameters from the query
            metrics: Extracted metrics from analysis
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        if query_type == QueryType.CITY_DELAY_ANALYSIS:
            city = parameters.get('city', 'Unknown')
            recommendations.append({
                'text': f"Establish city-specific performance monitoring dashboard for {city} to track improvement progress",
                'priority': RecommendationPriority.MEDIUM
            })
            
        elif query_type == QueryType.CLIENT_FAILURE_ANALYSIS:
            client_name = parameters.get('client_name', 'the client')
            recommendations.append({
                'text': f"Schedule quarterly business review with {client_name} to discuss service improvements and expectations",
                'priority': RecommendationPriority.MEDIUM
            })
            
        elif query_type == QueryType.WAREHOUSE_FAILURE_ANALYSIS:
            warehouse_name = parameters.get('warehouse_name', 'the warehouse')
            recommendations.append({
                'text': f"Conduct operational audit of {warehouse_name} to identify process optimization opportunities",
                'priority': RecommendationPriority.MEDIUM
            })
            
        elif query_type == QueryType.CITY_COMPARISON:
            city_a = parameters.get('city_a', 'City A')
            city_b = parameters.get('city_b', 'City B')
            recommendations.append({
                'text': f"Create best practice sharing program between {city_a} and {city_b} operations teams",
                'priority': RecommendationPriority.MEDIUM
            })
            
        elif query_type == QueryType.FESTIVAL_PERIOD_ANALYSIS:
            recommendations.extend([
                {
                    'text': "Develop seasonal capacity planning model with 6-month advance preparation timeline",
                    'priority': RecommendationPriority.HIGH
                },
                {
                    'text': "Create festival period customer communication templates and proactive notification systems",
                    'priority': RecommendationPriority.MEDIUM
                }
            ])
            
        elif query_type == QueryType.CAPACITY_IMPACT_ANALYSIS:
            order_volume = parameters.get('order_volume', 0)
            if order_volume > 0:
                recommendations.append({
                    'text': f"Implement phased onboarding approach with {order_volume//4:,} orders per week ramp-up to minimize risk",
                    'priority': RecommendationPriority.HIGH
                })
        
        return recommendations
    
    def _extract_metrics_from_analysis(self, analysis_result: str) -> Dict[str, Any]:
        """
        Extract key metrics from analysis result text (simplified pattern matching).
        
        Args:
            analysis_result: Raw analysis result text
            
        Returns:
            Dictionary of extracted metrics
        """
        metrics = {}
        
        # Extract common metrics using regex patterns
        import re
        
        # Success rate
        success_match = re.search(r'success rate[:\s]+([0-9.]+)%?', analysis_result.lower())
        if success_match:
            metrics['success_rate'] = float(success_match.group(1))
        
        # Failure rate
        failure_match = re.search(r'failure rate[:\s]+([0-9.]+)%?', analysis_result.lower())
        if failure_match:
            metrics['failure_rate'] = float(failure_match.group(1))
        
        # Total orders
        orders_match = re.search(r'total orders[:\s]+([0-9,]+)', analysis_result.lower())
        if orders_match:
            metrics['total_orders'] = int(orders_match.group(1).replace(',', ''))
        
        # Average delay
        delay_match = re.search(r'average delay[:\s]+([0-9.]+)\s*hours?', analysis_result.lower())
        if delay_match:
            metrics['average_delay_hours'] = float(delay_match.group(1))
        
        # Order volume (for capacity analysis)
        volume_match = re.search(r'([0-9,]+)\s+(?:additional|extra|new)\s+(?:monthly\s+)?orders?', analysis_result.lower())
        if volume_match:
            metrics['order_volume'] = int(volume_match.group(1).replace(',', ''))
        
        return metrics
    
    def _format_template_string(self, template: str, parameters: Dict[str, Any]) -> str:
        """
        Format template string with parameters, handling missing values gracefully.
        
        Args:
            template: Template string with placeholders
            parameters: Dictionary of parameter values
            
        Returns:
            Formatted string with placeholders replaced
        """
        try:
            # Handle date formatting
            formatted_params = {}
            for key, value in parameters.items():
                if isinstance(value, datetime):
                    formatted_params[key] = value.strftime('%B %d, %Y')
                else:
                    formatted_params[key] = value
            
            return template.format(**formatted_params)
        except KeyError as e:
            logger.warning(f"Missing parameter for template formatting: {e}")
            return template
        except Exception as e:
            logger.error(f"Error formatting template: {e}")
            return template
    
    def _generate_unknown_query_response(self, original_query: str) -> str:
        """
        Generate response for unknown or unsupported query types.
        
        Args:
            original_query: Original query string
            
        Returns:
            Formatted error response with guidance
        """
        response = [
            "❓ Query Not Recognized",
            "=" * 25,
            "",
            f"**Original Query:** {original_query}",
            "",
            "**Issue:** The system could not identify the type of analysis you're requesting.",
            "",
            "**Supported Query Types:**",
            "",
            "1. **City Delay Analysis**",
            "   - Example: 'Why were deliveries delayed in Mumbai yesterday?'",
            "",
            "2. **Client Failure Analysis**", 
            "   - Example: 'Why did Client ABC's orders fail in the past week?'",
            "",
            "3. **Warehouse Failure Analysis**",
            "   - Example: 'Explain top reasons for delivery failures linked to Warehouse B in August?'",
            "",
            "4. **City Comparison**",
            "   - Example: 'Compare delivery failure causes between Delhi and Mumbai last month?'",
            "",
            "5. **Festival Period Analysis**",
            "   - Example: 'What are the likely causes of delivery failures during the festival period?'",
            "",
            "6. **Capacity Impact Analysis**",
            "   - Example: 'If we onboard Client XYZ with 20,000 extra monthly orders, what new failure risks should we expect?'",
            "",
            "**Suggestion:** Please rephrase your question using one of the supported formats above."
        ]
        
        return '\n'.join(response)
    
    def _get_priority_order(self, priority: RecommendationPriority) -> int:
        """Get numeric order for priority sorting."""
        order_map = {
            RecommendationPriority.CRITICAL: 1,
            RecommendationPriority.HIGH: 2,
            RecommendationPriority.MEDIUM: 3,
            RecommendationPriority.LOW: 4
        }
        return order_map.get(priority, 5)
    
    def _get_priority_icon(self, priority: RecommendationPriority) -> str:
        """Get icon for priority level."""
        icon_map = {
            RecommendationPriority.CRITICAL: "🚨",
            RecommendationPriority.HIGH: "⚠️",
            RecommendationPriority.MEDIUM: "💡",
            RecommendationPriority.LOW: "📝"
        }
        return icon_map.get(priority, "📝")
    
    def generate_executive_summary(self, query_type: QueryType, parameters: Dict[str, Any], analysis_result: str) -> str:
        """
        Generate a concise executive summary for leadership consumption.
        
        Args:
            query_type: Type of query being processed
            parameters: Extracted parameters from the query
            analysis_result: Raw analysis result from InsightGenerator
            
        Returns:
            Formatted executive summary
        """
        metrics = self._extract_metrics_from_analysis(analysis_result)
        
        summary_parts = []
        
        # Executive header
        summary_parts.append("📊 EXECUTIVE SUMMARY")
        summary_parts.append("=" * 20)
        summary_parts.append("")
        
        # Key metrics
        if metrics:
            summary_parts.append("**Key Performance Indicators:**")
            if 'success_rate' in metrics:
                status = "✅ Good" if metrics['success_rate'] >= 90 else "⚠️ Needs Attention" if metrics['success_rate'] >= 80 else "🚨 Critical"
                summary_parts.append(f"- Success Rate: {metrics['success_rate']:.1f}% ({status})")
            
            if 'failure_rate' in metrics:
                status = "✅ Good" if metrics['failure_rate'] <= 5 else "⚠️ Elevated" if metrics['failure_rate'] <= 15 else "🚨 High"
                summary_parts.append(f"- Failure Rate: {metrics['failure_rate']:.1f}% ({status})")
            
            if 'total_orders' in metrics:
                summary_parts.append(f"- Volume: {metrics['total_orders']:,} orders analyzed")
            
            summary_parts.append("")
        
        # Business impact assessment
        impact_level = self._assess_business_impact(metrics)
        summary_parts.append(f"**Business Impact:** {impact_level}")
        summary_parts.append("")
        
        # Top 3 critical actions
        recommendations = self._generate_recommendations(query_type, parameters, analysis_result)
        if recommendations:
            critical_actions = [rec for rec in recommendations.split('\n') if '🚨' in rec or '⚠️' in rec][:3]
            if critical_actions:
                summary_parts.append("**Immediate Actions Required:**")
                for action in critical_actions:
                    summary_parts.append(action)
                summary_parts.append("")
        
        # Resource requirements
        resource_needs = self._assess_resource_requirements(metrics, query_type)
        if resource_needs:
            summary_parts.append(f"**Resource Requirements:** {resource_needs}")
        
        return '\n'.join(summary_parts)
    
    def _assess_business_impact(self, metrics: Dict[str, Any]) -> str:
        """Assess business impact level based on metrics."""
        failure_rate = metrics.get('failure_rate', 0)
        success_rate = metrics.get('success_rate', 100)
        
        if failure_rate > 20 or success_rate < 75:
            return "🚨 HIGH - Immediate intervention required"
        elif failure_rate > 10 or success_rate < 85:
            return "⚠️ MEDIUM - Operational improvements needed"
        else:
            return "✅ LOW - Performance within acceptable range"
    
    def _assess_resource_requirements(self, metrics: Dict[str, Any], query_type: QueryType) -> str:
        """Assess resource requirements based on analysis."""
        failure_rate = metrics.get('failure_rate', 0)
        order_volume = metrics.get('order_volume', 0)
        
        if failure_rate > 20:
            return "Additional operations staff, emergency response team activation"
        elif failure_rate > 10:
            return "Process improvement resources, enhanced monitoring tools"
        elif order_volume > 15000:
            return "Capacity expansion, additional infrastructure planning"
        else:
            return "Standard operational resources sufficient"