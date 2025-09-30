"""
Insight Generation Engine for the Logistics Insight System.
Implements InsightGenerator class with methods for each use case type.
Creates narrative text generation utilities for human-readable explanations.
Adds statistical analysis functions for calculating success rates, delay patterns, and failure distributions.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from data_aggregator import DataAggregator
from correlation_engine import CorrelationEngine

logger = logging.getLogger(__name__)


class InsightGenerator:
    """
    Generates human-readable insights and actionable recommendations from correlated logistics data.
    Transforms statistical analysis into narrative explanations for business stakeholders.
    """
    
    def __init__(self, data_aggregator: DataAggregator, correlation_engine: CorrelationEngine):
        """
        Initialize InsightGenerator with data aggregator and correlation engine.
        
        Args:
            data_aggregator: DataAggregator instance for accessing aggregated data
            correlation_engine: CorrelationEngine instance for pattern analysis
        """
        self.data_aggregator = data_aggregator
        self.correlation_engine = correlation_engine
    
    def calculate_success_rate(self, orders_df: pd.DataFrame) -> float:
        """
        Calculate success rate for a set of orders.
        
        Args:
            orders_df: DataFrame containing order data
            
        Returns:
            Success rate as percentage (0-100)
        """
        if orders_df.empty:
            return 0.0
        
        successful_orders = orders_df[orders_df['status'].str.lower() == 'delivered']
        return len(successful_orders) / len(orders_df) * 100
    
    def calculate_delay_patterns(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate delay patterns and statistics for orders.
        
        Args:
            orders_df: DataFrame containing order data with delivery dates
            
        Returns:
            Dictionary containing delay statistics and patterns
        """
        delivered_orders = orders_df[
            (orders_df['status'].str.lower() == 'delivered') &
            pd.notna(orders_df['actual_delivery_date']) &
            pd.notna(orders_df['promised_delivery_date'])
        ]
        
        if delivered_orders.empty:
            return {
                'analysis_possible': False,
                'total_orders': len(orders_df),
                'delivered_orders': 0
            }
        
        # Calculate delays in hours
        delays = (delivered_orders['actual_delivery_date'] - delivered_orders['promised_delivery_date']).dt.total_seconds() / 3600
        delayed_orders = delays[delays > 0]
        on_time_orders = delays[delays <= 0]
        
        return {
            'analysis_possible': True,
            'total_orders': len(orders_df),
            'delivered_orders': len(delivered_orders),
            'on_time_deliveries': len(on_time_orders),
            'delayed_deliveries': len(delayed_orders),
            'on_time_percentage': len(on_time_orders) / len(delivered_orders) * 100,
            'delayed_percentage': len(delayed_orders) / len(delivered_orders) * 100,
            'average_delay_hours': delayed_orders.mean() if not delayed_orders.empty else 0,
            'max_delay_hours': delayed_orders.max() if not delayed_orders.empty else 0,
            'median_delay_hours': delayed_orders.median() if not delayed_orders.empty else 0
        }
    
    def calculate_failure_distributions(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate failure distributions and patterns for orders.
        
        Args:
            orders_df: DataFrame containing order data
            
        Returns:
            Dictionary containing failure statistics and distributions
        """
        failed_orders = orders_df[orders_df['status'].str.lower() == 'failed']
        
        if failed_orders.empty:
            return {
                'total_failures': 0,
                'failure_rate': 0.0,
                'failure_reasons': {},
                'most_common_failure': None
            }
        
        failure_reasons = failed_orders['failure_reason'].value_counts().to_dict()
        
        return {
            'total_failures': len(failed_orders),
            'failure_rate': len(failed_orders) / len(orders_df) * 100,
            'failure_reasons': failure_reasons,
            'most_common_failure': failed_orders['failure_reason'].mode().iloc[0] if not failed_orders['failure_reason'].mode().empty else 'Unknown',
            'failure_reason_distribution': {reason: count/len(failed_orders)*100 for reason, count in failure_reasons.items()}
        }
    
    def generate_narrative_summary(self, title: str, key_metrics: Dict[str, Any], insights: List[str], recommendations: List[str]) -> str:
        """
        Generate a human-readable narrative summary from analysis results.
        
        Args:
            title: Title for the analysis
            key_metrics: Dictionary of key metrics to highlight
            insights: List of key insights discovered
            recommendations: List of actionable recommendations
            
        Returns:
            Formatted narrative text
        """
        narrative = f"# {title}\n\n"
        
        # Add key metrics section
        if key_metrics:
            narrative += "## Key Metrics\n"
            for metric, value in key_metrics.items():
                if isinstance(value, float):
                    narrative += f"- {metric}: {value:.2f}\n"
                else:
                    narrative += f"- {metric}: {value}\n"
            narrative += "\n"
        
        # Add insights section
        if insights:
            narrative += "## Key Insights\n"
            for i, insight in enumerate(insights, 1):
                narrative += f"{i}. {insight}\n"
            narrative += "\n"
        
        # Add recommendations section
        if recommendations:
            narrative += "## Actionable Recommendations\n"
            for i, recommendation in enumerate(recommendations, 1):
                narrative += f"{i}. {recommendation}\n"
            narrative += "\n"
        
        return narrative
    
    def generate_city_delay_analysis(self, city: str, date: datetime) -> str:
        """
        Generate city delay analysis for "Why were deliveries delayed in city X yesterday?" queries.
        
        Args:
            city: City name to analyze
            date: Date to analyze (typically yesterday)
            
        Returns:
            Human-readable analysis of city delivery delays
        """
        # Define date range (single day)
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        # Get city patterns
        city_patterns = self.correlation_engine.find_patterns_by_city(city, start_date, end_date)
        
        if not city_patterns['patterns_found']:
            return f"No delivery data found for {city} on {date.strftime('%Y-%m-%d')}. Unable to analyze delays."
        
        patterns = city_patterns['patterns']
        
        # Calculate key metrics
        key_metrics = {
            'Total Orders': patterns['total_orders'],
            'Success Rate (%)': round(patterns['success_rate'], 2),
            'Failed Orders': patterns['failure_patterns']['total_failures'],
            'Failure Rate (%)': round(patterns['failure_patterns'].get('failure_rate', 0), 2)
        }
        
        # Generate insights
        insights = []
        recommendations = []
        
        # Analyze delivery time patterns
        if patterns['delivery_time_patterns'].get('analysis_possible'):
            delay_data = patterns['delivery_time_patterns']
            if delay_data.get('delayed_deliveries', 0) > 0:
                avg_delay = delay_data.get('average_delay_hours', 0)
                delivered_orders = delay_data.get('delivered_orders', 0)
                delayed_deliveries = delay_data.get('delayed_deliveries', 0)
                insights.append(f"Out of {delivered_orders} delivered orders, {delayed_deliveries} were delayed with an average delay of {avg_delay:.1f} hours")
                
                if avg_delay > 4:
                    recommendations.append("Investigate route optimization and driver scheduling to reduce significant delays")
                elif avg_delay > 2:
                    recommendations.append("Review dispatch timing and traffic patterns to minimize moderate delays")
        
        # Analyze external factors
        if patterns['external_factor_patterns']['analysis_possible']:
            external_data = patterns['external_factor_patterns']
            traffic_issues = [condition for condition in external_data['traffic_patterns'].keys() 
                            if condition and condition.lower() in ['heavy', 'congested', 'jam']]
            weather_issues = [condition for condition in external_data['weather_patterns'].keys() 
                            if condition and condition.lower() in ['rainy', 'storm', 'heavy rain']]
            
            if traffic_issues:
                insights.append(f"Traffic conditions contributed to delays: {', '.join(traffic_issues)}")
                recommendations.append("Consider alternative routes or adjusted delivery windows during peak traffic hours")
            
            if weather_issues:
                insights.append(f"Weather conditions impacted deliveries: {', '.join(weather_issues)}")
                recommendations.append("Implement weather-based contingency plans and customer communication protocols")
        
        # Analyze warehouse performance
        if patterns['warehouse_performance_patterns']['analysis_possible']:
            warehouse_data = patterns['warehouse_performance_patterns']
            poor_performing_warehouses = [wh for wh, rate in warehouse_data['warehouse_success_rates'].items() 
                                        if rate < 80]
            
            if poor_performing_warehouses:
                insights.append(f"Warehouses with below-average performance: {', '.join(poor_performing_warehouses)}")
                recommendations.append("Review warehouse operations and staffing for underperforming locations")
        
        # Analyze failure patterns
        if patterns['failure_patterns'].get('most_common_failure'):
            most_common = patterns['failure_patterns']['most_common_failure']
            insights.append(f"Most common failure reason: {most_common}")
            
            # Provide specific recommendations based on failure type
            if 'address' in most_common.lower():
                recommendations.append("Implement address verification system and customer contact protocols")
            elif 'payment' in most_common.lower():
                recommendations.append("Enhance payment verification and alternative payment method options")
            elif 'customer' in most_common.lower():
                recommendations.append("Improve customer communication and delivery scheduling coordination")
        
        # Generate narrative
        title = f"Delivery Delay Analysis for {city} on {date.strftime('%B %d, %Y')}"
        
        return self.generate_narrative_summary(title, key_metrics, insights, recommendations)    

    def generate_client_failure_analysis(self, client_id: int, start_date: datetime, end_date: datetime) -> str:
        """
        Generate client failure analysis for "Why did Client X's orders fail in the past week?" queries.
        
        Args:
            client_id: Client ID to analyze
            start_date: Start date for analysis period
            end_date: End date for analysis period
            
        Returns:
            Human-readable analysis of client order failures
        """
        # Get client patterns
        client_patterns = self.correlation_engine.find_patterns_by_client(client_id, start_date, end_date)
        
        if not client_patterns['patterns_found']:
            return f"No order data found for Client {client_id} between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}."
        
        patterns = client_patterns['patterns']
        client_name = client_patterns['client_name']
        
        # Calculate key metrics
        key_metrics = {
            'Client Name': client_name,
            'Total Orders': patterns['total_orders'],
            'Success Rate (%)': round(patterns['success_rate'], 2),
            'Failed Orders': patterns['failure_patterns']['total_failures'],
            'Failure Rate (%)': round(patterns['failure_patterns'].get('failure_rate', 0), 2)
        }
        
        # Generate insights
        insights = []
        recommendations = []
        
        # Analyze failure patterns
        if patterns['failure_patterns']['total_failures'] > 0:
            failure_data = patterns['failure_patterns']
            most_common = failure_data.get('most_common_failure')
            
            # Check if failure_reason_distribution exists, if not calculate it
            if 'failure_reason_distribution' in failure_data:
                failure_distribution = failure_data['failure_reason_distribution']
                insights.append(f"Primary failure reason: {most_common} ({failure_distribution.get(most_common, 0):.1f}% of failures)")
                
                # Analyze all failure reasons
                for reason, percentage in failure_distribution.items():
                    if percentage > 20:  # Significant failure reasons
                        insights.append(f"Significant issue: {reason} accounts for {percentage:.1f}% of failures")
            else:
                # Calculate distribution from failure_reasons if available
                if 'failure_reasons' in failure_data and failure_data['failure_reasons']:
                    total_failures = failure_data['total_failures']
                    failure_distribution = {reason: count/total_failures*100 for reason, count in failure_data['failure_reasons'].items()}
                    insights.append(f"Primary failure reason: {most_common} ({failure_distribution.get(most_common, 0):.1f}% of failures)")
                    
                    for reason, percentage in failure_distribution.items():
                        if percentage > 20:  # Significant failure reasons
                            insights.append(f"Significant issue: {reason} accounts for {percentage:.1f}% of failures")
                else:
                    insights.append(f"Primary failure reason: {most_common}")
        
        # Analyze delivery location patterns
        if patterns['delivery_location_patterns']:
            location_data = patterns['delivery_location_patterns']
            problematic_locations = [(location, rate) for location, rate in location_data['location_success_rates'].items() 
                                   if rate < 70]
            
            if problematic_locations:
                insights.append(f"Delivery locations with low success rates: {', '.join([f'{loc} ({rate:.1f}%)' for loc, rate in problematic_locations])}")
                recommendations.append("Review address accuracy and accessibility for problematic delivery locations")
        
        # Analyze payment mode patterns
        if patterns['payment_mode_patterns']:
            payment_data = patterns['payment_mode_patterns']
            problematic_payments = [(mode, rate) for mode, rate in payment_data['payment_success_rates'].items() 
                                  if rate < 80]
            
            if problematic_payments:
                insights.append(f"Payment modes with issues: {', '.join([f'{mode} ({rate:.1f}% success)' for mode, rate in problematic_payments])}")
                recommendations.append("Address payment processing issues and offer alternative payment methods")
        
        # Analyze delivery time patterns
        if patterns['delivery_time_patterns'].get('analysis_possible'):
            delay_data = patterns['delivery_time_patterns']
            if delay_data.get('delayed_deliveries', 0) > 0:
                delivered_orders = delay_data.get('delivered_orders', 0)
                delayed_deliveries = delay_data.get('delayed_deliveries', 0)
                avg_delay = delay_data.get('average_delay_hours', 0)
                insights.append(f"Delivery delays: {delayed_deliveries} out of {delivered_orders} delivered orders were delayed (avg: {avg_delay:.1f} hours)")
                recommendations.append("Improve delivery time estimation and customer communication for this client")
        
        # Analyze feedback patterns
        if patterns['feedback_patterns']['analysis_possible']:
            feedback_data = patterns['feedback_patterns']
            negative_feedback = feedback_data['sentiment_distribution'].get('negative', 0)
            if negative_feedback > 0:
                insights.append(f"Customer satisfaction concerns: {negative_feedback} negative feedback entries recorded")
                recommendations.append("Implement proactive customer service outreach and service recovery protocols")
        
        # Generate specific recommendations based on client patterns
        failure_rate = patterns['failure_patterns'].get('failure_rate', 0)
        if failure_rate > 20:
            recommendations.append("Schedule urgent review meeting with client to address service quality issues")
        elif failure_rate > 10:
            recommendations.append("Implement enhanced monitoring and quality assurance for this client's orders")
        
        # Generate narrative
        title = f"Order Failure Analysis for {client_name} ({start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')})"
        
        return self.generate_narrative_summary(title, key_metrics, insights, recommendations)    

    def generate_warehouse_failure_analysis(self, warehouse_id: int, start_date: datetime, end_date: datetime) -> str:
        """
        Generate warehouse failure analysis for "Explain top reasons for delivery failures linked to Warehouse B in August?" queries.
        
        Args:
            warehouse_id: Warehouse ID to analyze
            start_date: Start date for analysis period
            end_date: End date for analysis period
            
        Returns:
            Human-readable analysis of warehouse-linked delivery failures
        """
        # Get warehouse patterns
        warehouse_patterns = self.correlation_engine.find_patterns_by_warehouse(warehouse_id, start_date, end_date)
        
        if not warehouse_patterns['patterns_found']:
            return f"No order data found for Warehouse {warehouse_id} between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}."
        
        patterns = warehouse_patterns['patterns']
        warehouse_name = warehouse_patterns['warehouse_name']
        
        # Calculate key metrics
        key_metrics = {
            'Warehouse Name': warehouse_name,
            'Total Orders Processed': patterns['total_orders'],
            'Success Rate (%)': round(patterns['success_rate'], 2),
            'Failed Orders': patterns['failure_patterns']['total_failures'],
            'Failure Rate (%)': round(patterns['failure_patterns'].get('failure_rate', 0), 2)
        }
        
        # Generate insights
        insights = []
        recommendations = []
        
        # Analyze picking performance
        if patterns['picking_performance_patterns']['analysis_possible']:
            picking_data = patterns['picking_performance_patterns']
            avg_picking_time = picking_data['average_picking_time_hours']
            max_picking_time = picking_data['max_picking_time_hours']
            
            insights.append(f"Picking performance: Average {avg_picking_time:.1f} hours, Maximum {max_picking_time:.1f} hours")
            
            if avg_picking_time > 2:
                recommendations.append("Review picking processes and consider workflow optimization or additional staffing")
            elif max_picking_time > 6:
                recommendations.append("Investigate causes of exceptionally long picking times and implement process improvements")
        
        # Analyze dispatch performance
        if patterns['dispatch_performance_patterns']['analysis_possible']:
            dispatch_data = patterns['dispatch_performance_patterns']
            avg_dispatch_delay = dispatch_data['average_dispatch_delay_hours']
            max_dispatch_delay = dispatch_data['max_dispatch_delay_hours']
            
            insights.append(f"Dispatch performance: Average delay {avg_dispatch_delay:.1f} hours, Maximum delay {max_dispatch_delay:.1f} hours")
            
            if avg_dispatch_delay > 1:
                recommendations.append("Streamline dispatch processes and improve coordination between picking and shipping teams")
        
        # Analyze failure patterns
        if patterns['failure_patterns']['total_failures'] > 0:
            failure_data = patterns['failure_patterns']
            most_common = failure_data.get('most_common_failure')
            if most_common:
                insights.append(f"Primary failure reason: {most_common}")
            
            # Provide warehouse-specific recommendations based on failure types
            for reason, count in failure_data['failure_reasons'].items():
                percentage = count / failure_data['total_failures'] * 100
                if percentage > 15:  # Significant failure reasons
                    insights.append(f"Significant issue: {reason} ({percentage:.1f}% of failures)")
                    
                    if 'stock' in reason.lower() or 'inventory' in reason.lower():
                        recommendations.append("Implement better inventory management and stock level monitoring")
                    elif 'damage' in reason.lower() or 'quality' in reason.lower():
                        recommendations.append("Review packaging and handling procedures to prevent damage")
                    elif 'delay' in reason.lower() or 'time' in reason.lower():
                        recommendations.append("Optimize warehouse operations and resource allocation")
        
        # Analyze delivery destination patterns
        if patterns['delivery_destination_patterns']:
            destination_data = patterns['delivery_destination_patterns']
            problematic_destinations = [(dest, rate) for dest, rate in destination_data['destination_success_rates'].items() 
                                      if rate < 75]
            
            if problematic_destinations:
                insights.append(f"Challenging delivery destinations: {', '.join([f'{dest} ({rate:.1f}% success)' for dest, rate in problematic_destinations[:3]])}")
                recommendations.append("Develop specialized handling procedures for challenging delivery routes")
        
        # Analyze client distribution
        if patterns['client_distribution_patterns']:
            client_data = patterns['client_distribution_patterns']
            high_volume_clients = [(client, count) for client, count in client_data['client_order_counts'].items() 
                                 if count > patterns['total_orders'] * 0.1]  # Clients with >10% of orders
            
            if high_volume_clients:
                insights.append(f"High-volume clients served: {', '.join([f'{client} ({count} orders)' for client, count in high_volume_clients])}")
                recommendations.append("Ensure adequate capacity and specialized handling for high-volume client requirements")
        
        # Generate performance-based recommendations
        if patterns['success_rate'] < 85:
            recommendations.append("Implement comprehensive warehouse performance improvement program")
        elif patterns['success_rate'] < 95:
            recommendations.append("Focus on addressing top failure causes to improve overall performance")
        
        # Generate narrative
        title = f"Delivery Failure Analysis for {warehouse_name} ({start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')})"
        
        return self.generate_narrative_summary(title, key_metrics, insights, recommendations)
    
    def generate_city_comparison(self, city_a: str, city_b: str, start_date: datetime, end_date: datetime) -> str:
        """
        Generate city comparison analysis for "Compare delivery failure causes between City A and City B last month?" queries.
        
        Args:
            city_a: First city to compare
            city_b: Second city to compare
            start_date: Start date for comparison period
            end_date: End date for comparison period
            
        Returns:
            Human-readable comparison analysis between two cities
        """
        # Get patterns for both cities
        patterns_a = self.correlation_engine.find_patterns_by_city(city_a, start_date, end_date)
        patterns_b = self.correlation_engine.find_patterns_by_city(city_b, start_date, end_date)
        
        if not patterns_a['patterns_found'] and not patterns_b['patterns_found']:
            return f"No delivery data found for either {city_a} or {city_b} in the specified period."
        elif not patterns_a['patterns_found']:
            return f"No delivery data found for {city_a} in the specified period. Cannot perform comparison."
        elif not patterns_b['patterns_found']:
            return f"No delivery data found for {city_b} in the specified period. Cannot perform comparison."
        
        data_a = patterns_a['patterns']
        data_b = patterns_b['patterns']
        
        # Calculate comparative metrics
        key_metrics = {
            f'{city_a} - Total Orders': data_a['total_orders'],
            f'{city_a} - Success Rate (%)': round(data_a['success_rate'], 2),
            f'{city_a} - Failure Rate (%)': round(data_a['failure_patterns'].get('failure_rate', 0), 2),
            f'{city_b} - Total Orders': data_b['total_orders'],
            f'{city_b} - Success Rate (%)': round(data_b['success_rate'], 2),
            f'{city_b} - Failure Rate (%)': round(data_b['failure_patterns'].get('failure_rate', 0), 2)
        }
        
        # Generate comparative insights
        insights = []
        recommendations = []
        
        # Compare overall performance
        success_diff = data_a['success_rate'] - data_b['success_rate']
        if abs(success_diff) > 5:
            better_city = city_a if success_diff > 0 else city_b
            worse_city = city_b if success_diff > 0 else city_a
            insights.append(f"{better_city} significantly outperforms {worse_city} with {abs(success_diff):.1f}% higher success rate")
            recommendations.append(f"Investigate best practices from {better_city} operations for implementation in {worse_city}")
        else:
            insights.append(f"Both cities show similar overall performance (difference: {abs(success_diff):.1f}%)")
        
        # Compare failure patterns
        failures_a = data_a['failure_patterns']['failure_reasons']
        failures_b = data_b['failure_patterns']['failure_reasons']
        
        common_failures = set(failures_a.keys()) & set(failures_b.keys())
        unique_a = set(failures_a.keys()) - set(failures_b.keys())
        unique_b = set(failures_b.keys()) - set(failures_a.keys())
        
        if common_failures:
            insights.append(f"Common failure types: {', '.join(list(common_failures)[:3])}")
        
        if unique_a:
            insights.append(f"Unique challenges in {city_a}: {', '.join(list(unique_a)[:2])}")
        
        if unique_b:
            insights.append(f"Unique challenges in {city_b}: {', '.join(list(unique_b)[:2])}")
        
        # Compare external factors
        if (data_a['external_factor_patterns']['analysis_possible'] and 
            data_b['external_factor_patterns']['analysis_possible']):
            
            traffic_a = set(data_a['external_factor_patterns']['traffic_patterns'].keys())
            traffic_b = set(data_b['external_factor_patterns']['traffic_patterns'].keys())
            weather_a = set(data_a['external_factor_patterns']['weather_patterns'].keys())
            weather_b = set(data_b['external_factor_patterns']['weather_patterns'].keys())
            
            if traffic_a != traffic_b:
                insights.append(f"Different traffic challenges: {city_a} faces {', '.join(traffic_a)}, {city_b} faces {', '.join(traffic_b)}")
                recommendations.append("Develop city-specific traffic management and routing strategies")
            
            if weather_a != weather_b:
                insights.append(f"Different weather impacts: {city_a} affected by {', '.join(weather_a)}, {city_b} by {', '.join(weather_b)}")
                recommendations.append("Implement weather-specific contingency plans tailored to each city")
        
        # Compare delivery time patterns
        if (data_a['delivery_time_patterns']['analysis_possible'] and 
            data_b['delivery_time_patterns']['analysis_possible']):
            
            delay_a = data_a['delivery_time_patterns']['average_delay_hours']
            delay_b = data_b['delivery_time_patterns']['average_delay_hours']
            delay_diff = delay_a - delay_b
            
            if abs(delay_diff) > 1:
                faster_city = city_a if delay_diff < 0 else city_b
                slower_city = city_b if delay_diff < 0 else city_a
                insights.append(f"{faster_city} has {abs(delay_diff):.1f} hours shorter average delays than {slower_city}")
                recommendations.append(f"Analyze {faster_city}'s delivery processes for optimization opportunities in {slower_city}")
        
        # Compare warehouse performance
        if (data_a['warehouse_performance_patterns']['analysis_possible'] and 
            data_b['warehouse_performance_patterns']['analysis_possible']):
            
            warehouses_a = data_a['warehouse_performance_patterns']['warehouse_success_rates']
            warehouses_b = data_b['warehouse_performance_patterns']['warehouse_success_rates']
            
            avg_warehouse_performance_a = sum(warehouses_a.values()) / len(warehouses_a) if warehouses_a else 0
            avg_warehouse_performance_b = sum(warehouses_b.values()) / len(warehouses_b) if warehouses_b else 0
            
            if abs(avg_warehouse_performance_a - avg_warehouse_performance_b) > 5:
                better_warehouse_city = city_a if avg_warehouse_performance_a > avg_warehouse_performance_b else city_b
                insights.append(f"Warehouse operations in {better_warehouse_city} show superior performance")
                recommendations.append("Share warehouse best practices between cities to improve overall performance")
        
        # Generate strategic recommendations
        if success_diff > 10:
            recommendations.append("Conduct detailed operational audit to identify transferable best practices")
        elif abs(success_diff) < 2:
            recommendations.append("Both cities performing similarly - focus on addressing common failure patterns")
        
        # Generate narrative
        title = f"Delivery Performance Comparison: {city_a} vs {city_b} ({start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')})"
        
        return self.generate_narrative_summary(title, key_metrics, insights, recommendations)   
 
    def generate_festival_period_analysis(self, festival_start: datetime, festival_end: datetime) -> str:
        """
        Generate festival period analysis for seasonal delivery risk assessment.
        
        Args:
            festival_start: Start date of festival period
            festival_end: End date of festival period
            
        Returns:
            Human-readable analysis of festival period delivery risks and preparation recommendations
        """
        # Get data for festival period and compare with normal period
        normal_start = festival_start - timedelta(days=30)  # 30 days before festival
        normal_end = festival_start - timedelta(days=1)
        
        # Load all data to analyze patterns
        data = self.data_aggregator._load_and_cache_data()
        orders_df = data['orders']
        
        # Filter orders for festival and normal periods
        festival_orders = orders_df[
            (orders_df['order_date'] >= festival_start) &
            (orders_df['order_date'] <= festival_end)
        ]
        
        normal_orders = orders_df[
            (orders_df['order_date'] >= normal_start) &
            (orders_df['order_date'] <= normal_end)
        ]
        
        if festival_orders.empty:
            return f"No order data available for festival period ({festival_start.strftime('%Y-%m-%d')} to {festival_end.strftime('%Y-%m-%d')})."
        
        # Calculate comparative metrics
        festival_daily_avg = len(festival_orders) / ((festival_end - festival_start).days + 1)
        normal_daily_avg = len(normal_orders) / ((normal_end - normal_start).days + 1) if not normal_orders.empty else 0
        volume_increase = ((festival_daily_avg - normal_daily_avg) / normal_daily_avg * 100) if normal_daily_avg > 0 else 0
        
        festival_success_rate = self.calculate_success_rate(festival_orders)
        normal_success_rate = self.calculate_success_rate(normal_orders) if not normal_orders.empty else 0
        
        festival_failures = self.calculate_failure_distributions(festival_orders)
        festival_delays = self.calculate_delay_patterns(festival_orders)
        
        # Calculate key metrics
        key_metrics = {
            'Festival Period Orders': len(festival_orders),
            'Daily Average (Festival)': round(festival_daily_avg, 1),
            'Daily Average (Normal)': round(normal_daily_avg, 1),
            'Volume Increase (%)': round(volume_increase, 1),
            'Festival Success Rate (%)': round(festival_success_rate, 2),
            'Normal Success Rate (%)': round(normal_success_rate, 2),
            'Performance Impact (%)': round(festival_success_rate - normal_success_rate, 2)
        }
        
        # Generate insights
        insights = []
        recommendations = []
        
        # Volume impact analysis
        if volume_increase > 50:
            insights.append(f"Significant volume surge: {volume_increase:.1f}% increase in daily orders during festival period")
            recommendations.append("Scale up warehouse staffing and delivery capacity by at least 50% during festival periods")
        elif volume_increase > 20:
            insights.append(f"Moderate volume increase: {volume_increase:.1f}% higher daily order volume during festivals")
            recommendations.append("Increase operational capacity by 25-30% and implement surge pricing if applicable")
        
        # Performance impact analysis
        performance_drop = normal_success_rate - festival_success_rate
        if performance_drop > 10:
            insights.append(f"Significant performance degradation: {performance_drop:.1f}% drop in success rate during festivals")
            recommendations.append("Implement festival-specific quality assurance protocols and additional monitoring")
        elif performance_drop > 5:
            insights.append(f"Moderate performance impact: {performance_drop:.1f}% decrease in delivery success rate")
            recommendations.append("Enhance coordination between teams and implement proactive issue resolution")
        
        # Failure pattern analysis
        if festival_failures['total_failures'] > 0:
            top_failure = festival_failures['most_common_failure']
            insights.append(f"Primary festival failure cause: {top_failure} ({festival_failures['failure_reason_distribution'].get(top_failure, 0):.1f}% of failures)")
            
            if 'address' in top_failure.lower():
                recommendations.append("Implement enhanced address verification and customer contact protocols for festival orders")
            elif 'capacity' in top_failure.lower() or 'stock' in top_failure.lower():
                recommendations.append("Ensure adequate inventory levels and implement dynamic stock allocation during festivals")
            elif 'delay' in top_failure.lower():
                recommendations.append("Extend delivery windows and improve customer communication about potential delays")
        
        # Delay pattern analysis
        if festival_delays['analysis_possible'] and festival_delays['delayed_deliveries'] > 0:
            avg_delay = festival_delays['average_delay_hours']
            insights.append(f"Festival delivery delays: {festival_delays['delayed_percentage']:.1f}% of deliveries delayed by average {avg_delay:.1f} hours")
            
            if avg_delay > 6:
                recommendations.append("Implement festival-specific delivery scheduling with extended time windows")
            
        # City-specific analysis
        city_performance = festival_orders.groupby('city').agg({
            'status': lambda x: (x == 'Delivered').sum() / len(x) * 100,
            'order_id': 'count'
        })
        
        high_volume_cities = city_performance[city_performance['order_id'] > len(festival_orders) * 0.1]
        if not high_volume_cities.empty:
            insights.append(f"High-volume festival cities: {', '.join(high_volume_cities.index.tolist()[:3])}")
            recommendations.append("Deploy additional resources to high-volume cities during festival periods")
        
        # Generate strategic recommendations
        recommendations.extend([
            "Establish festival period contingency plans with pre-positioned inventory and staff",
            "Implement dynamic pricing and delivery slot management during peak periods",
            "Create customer communication templates for festival-related delays and issues",
            "Develop partnerships with additional logistics providers for surge capacity"
        ])
        
        # Generate narrative
        title = f"Festival Period Delivery Risk Analysis ({festival_start.strftime('%B %d')} - {festival_end.strftime('%B %d, %Y')})"
        
        return self.generate_narrative_summary(title, key_metrics, insights, recommendations)
    
    def generate_capacity_impact_analysis(self, client_id: int, additional_monthly_orders: int) -> str:
        """
        Generate capacity impact analysis for new client onboarding scenarios.
        
        Args:
            client_id: Client ID for the new high-volume client
            additional_monthly_orders: Expected additional monthly order volume
            
        Returns:
            Human-readable analysis of capacity impact and mitigation strategies
        """
        # Get historical data to establish baseline
        data = self.data_aggregator._load_and_cache_data()
        orders_df = data['orders']
        clients_df = data['clients']
        
        # Get client information
        client_info = clients_df[clients_df['client_id'] == client_id]
        client_name = client_info['client_name'].iloc[0] if not client_info.empty else f'Client {client_id}'
        
        # Calculate current system capacity metrics
        current_monthly_orders = len(orders_df[orders_df['order_date'] >= (datetime.now() - timedelta(days=30))])
        current_success_rate = self.calculate_success_rate(orders_df)
        
        # Estimate capacity impact
        capacity_increase_percentage = (additional_monthly_orders / current_monthly_orders * 100) if current_monthly_orders > 0 else 0
        
        # Analyze current failure patterns to predict new risks
        current_failures = self.calculate_failure_distributions(orders_df)
        
        # Calculate key metrics
        key_metrics = {
            'New Client': client_name,
            'Additional Monthly Orders': additional_monthly_orders,
            'Current Monthly Volume': current_monthly_orders,
            'Capacity Increase (%)': round(capacity_increase_percentage, 1),
            'Current System Success Rate (%)': round(current_success_rate, 2)
        }
        
        # Generate insights and risk predictions
        insights = []
        recommendations = []
        
        # Volume impact assessment
        if capacity_increase_percentage > 30:
            insights.append(f"Major capacity impact: {capacity_increase_percentage:.1f}% increase in monthly order volume")
            insights.append("High risk of system strain and performance degradation without capacity expansion")
            recommendations.append("Implement comprehensive capacity expansion plan including warehouse, fleet, and staff scaling")
        elif capacity_increase_percentage > 15:
            insights.append(f"Significant capacity impact: {capacity_increase_percentage:.1f}% increase in order volume")
            insights.append("Moderate risk of performance issues during peak periods")
            recommendations.append("Scale operations by 20-25% and implement load balancing strategies")
        else:
            insights.append(f"Manageable capacity impact: {capacity_increase_percentage:.1f}% volume increase")
            insights.append("Low risk with current infrastructure, minor adjustments needed")
        
        # Predict failure risk scenarios based on current patterns
        if current_failures['failure_rate'] > 10:
            predicted_additional_failures = additional_monthly_orders * (current_failures['failure_rate'] / 100)
            insights.append(f"Predicted additional failures: ~{predicted_additional_failures:.0f} orders per month based on current {current_failures['failure_rate']:.1f}% failure rate")
            
            # Analyze top failure causes for risk mitigation
            for reason, percentage in list(current_failures['failure_reason_distribution'].items())[:3]:
                if percentage > 20:
                    insights.append(f"High-risk failure type: {reason} ({percentage:.1f}% of current failures)")
                    
                    if 'address' in reason.lower():
                        recommendations.append("Implement enhanced address verification system before client onboarding")
                    elif 'capacity' in reason.lower() or 'stock' in reason.lower():
                        recommendations.append("Ensure inventory levels can support additional volume from new client")
                    elif 'payment' in reason.lower():
                        recommendations.append("Establish robust payment processing protocols for high-volume client")
        
        # Warehouse capacity analysis
        warehouse_orders = orders_df.groupby('city').size().to_dict()
        if client_info.empty:
            insights.append("Client delivery locations unknown - conduct geographic impact assessment")
            recommendations.append("Analyze client's delivery location distribution to identify warehouse capacity needs")
        else:
            # Assume client orders will be distributed similarly to current patterns
            insights.append("Warehouse capacity assessment needed based on client's delivery location profile")
            recommendations.append("Conduct detailed warehouse capacity analysis for client's primary delivery regions")
        
        # Fleet capacity analysis
        daily_additional_orders = additional_monthly_orders / 30
        insights.append(f"Fleet impact: ~{daily_additional_orders:.0f} additional daily deliveries required")
        
        if daily_additional_orders > 50:
            recommendations.append("Expand delivery fleet capacity or establish partnerships with additional logistics providers")
        elif daily_additional_orders > 20:
            recommendations.append("Optimize route planning and consider additional delivery vehicles during peak periods")
        
        # Risk mitigation strategies
        recommendations.extend([
            "Conduct pilot program with gradual volume ramp-up to test system capacity",
            "Implement real-time monitoring and alerting for capacity utilization",
            "Establish service level agreements with clear performance metrics and escalation procedures",
            "Create dedicated account management and support protocols for high-volume client",
            "Develop contingency plans for peak period management and surge capacity"
        ])
        
        # Financial impact considerations
        if capacity_increase_percentage > 20:
            recommendations.append("Conduct cost-benefit analysis for infrastructure investments vs. service quality maintenance")
            recommendations.append("Consider premium pricing structure to offset additional operational complexity")
        
        # Generate narrative
        title = f"Capacity Impact Analysis for {client_name} Onboarding (~{additional_monthly_orders:,} Monthly Orders)"
        
        return self.generate_narrative_summary(title, key_metrics, insights, recommendations)