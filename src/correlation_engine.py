"""
Correlation Engine for the Logistics Insight System.
Implements correlation logic to link orders with fleet activities, warehouse activities,
external factors, and identify patterns by client, city, warehouse, and time periods.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from data_loader import DataLoader
from data_aggregator import DataAggregator

logger = logging.getLogger(__name__)


class CorrelationEngine:
    """
    Handles correlation and pattern identification across multiple data sources.
    Links orders with fleet activities, warehouse activities, external factors,
    and identifies patterns by various dimensions.
    """
    
    def __init__(self, data_aggregator: DataAggregator):
        """
        Initialize CorrelationEngine with a DataAggregator instance.
        
        Args:
            data_aggregator: DataAggregator instance for accessing aggregated data
        """
        self.data_aggregator = data_aggregator
        
    def correlate_order_with_fleet(self, order_id: int) -> Dict[str, Any]:
        """
        Correlate order with fleet activities using order_id.
        
        Args:
            order_id: Order ID to correlate with fleet data
            
        Returns:
            Dictionary containing fleet correlation information
        """
        data = self.data_aggregator._load_and_cache_data()
        
        # Get order information
        orders_df = data['orders']
        order_row = orders_df[orders_df['order_id'] == order_id]
        
        if order_row.empty:
            logger.warning(f"Order {order_id} not found")
            return {'order_found': False, 'correlations': []}
        
        order_info = order_row.iloc[0].to_dict()
        
        # Get fleet logs for this order
        fleet_logs_df = data['fleet_logs']
        fleet_correlations = fleet_logs_df[fleet_logs_df['order_id'] == order_id]
        
        correlations = []
        
        for _, fleet_row in fleet_correlations.iterrows():
            # Get driver information
            drivers_df = data['drivers']
            driver_info = {}
            if pd.notna(fleet_row['driver_id']):
                driver_row = drivers_df[drivers_df['driver_id'] == fleet_row['driver_id']]
                if not driver_row.empty:
                    driver_info = driver_row.iloc[0].to_dict()
            
            # Calculate delivery time metrics
            delivery_metrics = self._calculate_delivery_metrics(order_info, fleet_row)
            
            # Analyze location correlation
            location_correlation = self._analyze_location_correlation(order_info, driver_info)
            
            correlation = {
                'fleet_log_id': fleet_row['fleet_log_id'],
                'driver_id': fleet_row['driver_id'],
                'driver_name': driver_info.get('driver_name', 'Unknown'),
                'driver_location': {
                    'city': driver_info.get('city'),
                    'state': driver_info.get('state')
                },
                'vehicle_number': fleet_row['vehicle_number'],
                'route_code': fleet_row['route_code'],
                'gps_delay_notes': fleet_row['gps_delay_notes'],
                'departure_time': fleet_row['departure_time'],
                'arrival_time': fleet_row['arrival_time'],
                'partner_company': driver_info.get('partner_company'),
                'delivery_metrics': delivery_metrics,
                'location_correlation': location_correlation
            }
            correlations.append(correlation)
        
        return {
            'order_found': True,
            'order_id': order_id,
            'delivery_city': order_info['city'],
            'delivery_state': order_info['state'],
            'order_status': order_info['status'],
            'correlations': correlations
        }
    
    def correlate_order_with_warehouse(self, order_id: int) -> Dict[str, Any]:
        """
        Correlate order with warehouse activities and external factors.
        
        Args:
            order_id: Order ID to correlate with warehouse data
            
        Returns:
            Dictionary containing warehouse correlation information
        """
        data = self.data_aggregator._load_and_cache_data()
        
        # Get order information
        orders_df = data['orders']
        order_row = orders_df[orders_df['order_id'] == order_id]
        
        if order_row.empty:
            logger.warning(f"Order {order_id} not found")
            return {'order_found': False, 'correlations': []}
        
        order_info = order_row.iloc[0].to_dict()
        
        # Get warehouse logs for this order
        warehouse_logs_df = data['warehouse_logs']
        warehouse_correlations = warehouse_logs_df[warehouse_logs_df['order_id'] == order_id]
        
        correlations = []
        
        for _, warehouse_row in warehouse_correlations.iterrows():
            # Get warehouse information
            warehouses_df = data['warehouses']
            warehouse_info = {}
            if pd.notna(warehouse_row['warehouse_id']):
                warehouse_info_row = warehouses_df[warehouses_df['warehouse_id'] == warehouse_row['warehouse_id']]
                if not warehouse_info_row.empty:
                    warehouse_info = warehouse_info_row.iloc[0].to_dict()
            
            # Calculate warehouse performance metrics
            warehouse_metrics = self._calculate_warehouse_metrics(warehouse_row)
            
            # Analyze warehouse-delivery location correlation
            location_correlation = self._analyze_warehouse_location_correlation(order_info, warehouse_info)
            
            correlation = {
                'log_id': warehouse_row['log_id'],
                'warehouse_id': warehouse_row['warehouse_id'],
                'warehouse_name': warehouse_info.get('warehouse_name', 'Unknown'),
                'warehouse_location': {
                    'city': warehouse_info.get('city'),
                    'state': warehouse_info.get('state')
                },
                'warehouse_capacity': warehouse_info.get('capacity'),
                'manager_name': warehouse_info.get('manager_name'),
                'picking_start': warehouse_row['picking_start'],
                'picking_end': warehouse_row['picking_end'],
                'dispatch_time': warehouse_row['dispatch_time'],
                'notes': warehouse_row['notes'],
                'warehouse_metrics': warehouse_metrics,
                'location_correlation': location_correlation
            }
            correlations.append(correlation)
        
        return {
            'order_found': True,
            'order_id': order_id,
            'delivery_city': order_info['city'],
            'delivery_state': order_info['state'],
            'order_status': order_info['status'],
            'correlations': correlations
        }
    
    def correlate_order_with_external_factors(self, order_id: int) -> Dict[str, Any]:
        """
        Correlate order with external factors.
        
        Args:
            order_id: Order ID to correlate with external factors
            
        Returns:
            Dictionary containing external factors correlation information
        """
        data = self.data_aggregator._load_and_cache_data()
        
        # Get order information
        orders_df = data['orders']
        order_row = orders_df[orders_df['order_id'] == order_id]
        
        if order_row.empty:
            logger.warning(f"Order {order_id} not found")
            return {'order_found': False, 'correlations': []}
        
        order_info = order_row.iloc[0].to_dict()
        
        # Get external factors for this order
        external_factors_df = data['external_factors']
        external_correlations = external_factors_df[external_factors_df['order_id'] == order_id]
        
        correlations = []
        
        for _, external_row in external_correlations.iterrows():
            # Analyze impact of external factors
            impact_analysis = self._analyze_external_factor_impact(order_info, external_row)
            
            correlation = {
                'factor_id': external_row['factor_id'],
                'traffic_condition': external_row['traffic_condition'],
                'weather_condition': external_row['weather_condition'],
                'event_type': external_row['event_type'],
                'recorded_at': external_row['recorded_at'],
                'impact_analysis': impact_analysis
            }
            correlations.append(correlation)
        
        return {
            'order_found': True,
            'order_id': order_id,
            'delivery_city': order_info['city'],
            'delivery_state': order_info['state'],
            'order_status': order_info['status'],
            'correlations': correlations
        }
    
    def find_patterns_by_city(self, city: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Identify patterns by city and time period.
        
        Args:
            city: City name to analyze
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary containing city-specific patterns
        """
        # Get aggregated data for the city and date range
        city_orders = self.data_aggregator.get_orders_by_city_and_date(city, start_date, end_date)
        
        if city_orders.empty:
            return {
                'city': city,
                'date_range': {'start': start_date, 'end': end_date},
                'patterns_found': False,
                'message': f'No orders found for {city} in the specified date range'
            }
        
        # Analyze patterns
        patterns = {
            'total_orders': len(city_orders),
            'success_rate': self._calculate_success_rate(city_orders),
            'failure_patterns': self._analyze_failure_patterns(city_orders),
            'delivery_time_patterns': self._analyze_delivery_time_patterns(city_orders),
            'external_factor_patterns': self._analyze_external_factor_patterns(city_orders),
            'warehouse_performance_patterns': self._analyze_warehouse_performance_patterns(city_orders),
            'driver_performance_patterns': self._analyze_driver_performance_patterns(city_orders),
            'client_patterns': self._analyze_client_patterns(city_orders)
        }
        
        return {
            'city': city,
            'date_range': {'start': start_date, 'end': end_date},
            'patterns_found': True,
            'patterns': patterns
        }
    
    def find_patterns_by_client(self, client_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Identify patterns by client and time period.
        
        Args:
            client_id: Client ID to analyze
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary containing client-specific patterns
        """
        # Get aggregated data for the client and date range
        client_orders = self.data_aggregator.get_orders_by_client_and_date_range(client_id, start_date, end_date)
        
        if client_orders.empty:
            return {
                'client_id': client_id,
                'date_range': {'start': start_date, 'end': end_date},
                'patterns_found': False,
                'message': f'No orders found for client {client_id} in the specified date range'
            }
        
        # Get client information
        data = self.data_aggregator._load_and_cache_data()
        clients_df = data['clients']
        client_info = clients_df[clients_df['client_id'] == client_id]
        client_name = client_info['client_name'].iloc[0] if not client_info.empty else 'Unknown'
        
        # Analyze patterns
        patterns = {
            'total_orders': len(client_orders),
            'success_rate': self._calculate_success_rate(client_orders),
            'delivery_location_patterns': self._analyze_delivery_location_patterns(client_orders),
            'payment_mode_patterns': self._analyze_payment_mode_patterns(client_orders),
            'failure_patterns': self._analyze_failure_patterns(client_orders),
            'delivery_time_patterns': self._analyze_delivery_time_patterns(client_orders),
            'feedback_patterns': self._analyze_feedback_patterns(client_orders)
        }
        
        return {
            'client_id': client_id,
            'client_name': client_name,
            'date_range': {'start': start_date, 'end': end_date},
            'patterns_found': True,
            'patterns': patterns
        }
    
    def find_patterns_by_warehouse(self, warehouse_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Identify patterns by warehouse and time period.
        
        Args:
            warehouse_id: Warehouse ID to analyze
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary containing warehouse-specific patterns
        """
        # Get aggregated data for the warehouse and date range
        warehouse_orders = self.data_aggregator.get_orders_by_warehouse_and_date_range(warehouse_id, start_date, end_date)
        
        if warehouse_orders.empty:
            return {
                'warehouse_id': warehouse_id,
                'date_range': {'start': start_date, 'end': end_date},
                'patterns_found': False,
                'message': f'No orders found for warehouse {warehouse_id} in the specified date range'
            }
        
        # Get warehouse information
        data = self.data_aggregator._load_and_cache_data()
        warehouses_df = data['warehouses']
        warehouse_info = warehouses_df[warehouses_df['warehouse_id'] == warehouse_id]
        warehouse_name = warehouse_info['warehouse_name'].iloc[0] if not warehouse_info.empty else 'Unknown'
        
        # Analyze patterns
        patterns = {
            'total_orders': len(warehouse_orders),
            'success_rate': self._calculate_success_rate(warehouse_orders),
            'picking_performance_patterns': self._analyze_picking_performance_patterns(warehouse_orders),
            'dispatch_performance_patterns': self._analyze_dispatch_performance_patterns(warehouse_orders),
            'failure_patterns': self._analyze_failure_patterns(warehouse_orders),
            'delivery_destination_patterns': self._analyze_delivery_destination_patterns(warehouse_orders),
            'client_distribution_patterns': self._analyze_client_distribution_patterns(warehouse_orders)
        }
        
        return {
            'warehouse_id': warehouse_id,
            'warehouse_name': warehouse_name,
            'date_range': {'start': start_date, 'end': end_date},
            'patterns_found': True,
            'patterns': patterns
        }
    
    # Helper methods for calculations and analysis
    
    def _calculate_delivery_metrics(self, order_info: Dict, fleet_row: pd.Series) -> Dict[str, Any]:
        """Calculate delivery time metrics."""
        metrics = {}
        
        if pd.notna(fleet_row['departure_time']) and pd.notna(fleet_row['arrival_time']):
            travel_time = fleet_row['arrival_time'] - fleet_row['departure_time']
            metrics['travel_time_hours'] = travel_time.total_seconds() / 3600
        
        if pd.notna(order_info['promised_delivery_date']) and pd.notna(fleet_row['arrival_time']):
            if fleet_row['arrival_time'] > order_info['promised_delivery_date']:
                delay = fleet_row['arrival_time'] - order_info['promised_delivery_date']
                metrics['delay_hours'] = delay.total_seconds() / 3600
                metrics['is_delayed'] = True
            else:
                metrics['is_delayed'] = False
        
        return metrics
    
    def _analyze_location_correlation(self, order_info: Dict, driver_info: Dict) -> Dict[str, Any]:
        """Analyze correlation between delivery location and driver location."""
        correlation = {
            'same_city': False,
            'same_state': False,
            'distance_category': 'unknown'
        }
        
        if driver_info.get('city') and order_info.get('city'):
            correlation['same_city'] = driver_info['city'].lower() == order_info['city'].lower()
        
        if driver_info.get('state') and order_info.get('state'):
            correlation['same_state'] = driver_info['state'].lower() == order_info['state'].lower()
        
        # Categorize distance based on location correlation
        if correlation['same_city']:
            correlation['distance_category'] = 'local'
        elif correlation['same_state']:
            correlation['distance_category'] = 'intrastate'
        else:
            correlation['distance_category'] = 'interstate'
        
        return correlation
    
    def _calculate_warehouse_metrics(self, warehouse_row: pd.Series) -> Dict[str, Any]:
        """Calculate warehouse performance metrics."""
        metrics = {}
        
        if pd.notna(warehouse_row['picking_start']) and pd.notna(warehouse_row['picking_end']):
            picking_time = warehouse_row['picking_end'] - warehouse_row['picking_start']
            metrics['picking_time_hours'] = picking_time.total_seconds() / 3600
        
        if pd.notna(warehouse_row['picking_end']) and pd.notna(warehouse_row['dispatch_time']):
            dispatch_delay = warehouse_row['dispatch_time'] - warehouse_row['picking_end']
            metrics['dispatch_delay_hours'] = dispatch_delay.total_seconds() / 3600
        
        return metrics
    
    def _analyze_warehouse_location_correlation(self, order_info: Dict, warehouse_info: Dict) -> Dict[str, Any]:
        """Analyze correlation between warehouse location and delivery location."""
        correlation = {
            'same_city': False,
            'same_state': False,
            'logistics_efficiency': 'unknown'
        }
        
        if warehouse_info.get('city') and order_info.get('city'):
            correlation['same_city'] = warehouse_info['city'].lower() == order_info['city'].lower()
        
        if warehouse_info.get('state') and order_info.get('state'):
            correlation['same_state'] = warehouse_info['state'].lower() == order_info['state'].lower()
        
        # Assess logistics efficiency
        if correlation['same_city']:
            correlation['logistics_efficiency'] = 'high'
        elif correlation['same_state']:
            correlation['logistics_efficiency'] = 'medium'
        else:
            correlation['logistics_efficiency'] = 'low'
        
        return correlation
    
    def _analyze_external_factor_impact(self, order_info: Dict, external_row: pd.Series) -> Dict[str, Any]:
        """Analyze impact of external factors on order."""
        impact = {
            'traffic_impact': 'none',
            'weather_impact': 'none',
            'overall_risk': 'low'
        }
        
        # Analyze traffic impact
        traffic_condition = external_row.get('traffic_condition', '').lower()
        if traffic_condition in ['heavy', 'congested', 'jam']:
            impact['traffic_impact'] = 'high'
        elif traffic_condition in ['moderate', 'medium']:
            impact['traffic_impact'] = 'medium'
        
        # Analyze weather impact
        weather_condition = external_row.get('weather_condition', '').lower()
        if weather_condition in ['rainy', 'storm', 'heavy rain', 'cyclone']:
            impact['weather_impact'] = 'high'
        elif weather_condition in ['cloudy', 'light rain']:
            impact['weather_impact'] = 'medium'
        
        # Determine overall risk
        if impact['traffic_impact'] == 'high' or impact['weather_impact'] == 'high':
            impact['overall_risk'] = 'high'
        elif impact['traffic_impact'] == 'medium' or impact['weather_impact'] == 'medium':
            impact['overall_risk'] = 'medium'
        
        return impact
    
    def _calculate_success_rate(self, orders_df: pd.DataFrame) -> float:
        """Calculate success rate for orders."""
        if orders_df.empty:
            return 0.0
        
        successful_orders = orders_df[orders_df['status'].str.lower() == 'delivered']
        return len(successful_orders) / len(orders_df) * 100
    
    def _analyze_failure_patterns(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze failure patterns in orders."""
        failed_orders = orders_df[orders_df['status'].str.lower() == 'failed']
        
        if failed_orders.empty:
            return {'total_failures': 0, 'failure_reasons': {}}
        
        failure_reasons = failed_orders['failure_reason'].value_counts().to_dict()
        
        return {
            'total_failures': len(failed_orders),
            'failure_rate': len(failed_orders) / len(orders_df) * 100,
            'failure_reasons': failure_reasons,
            'most_common_failure': failed_orders['failure_reason'].mode().iloc[0] if not failed_orders['failure_reason'].mode().empty else 'Unknown'
        }
    
    def _analyze_delivery_time_patterns(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze delivery time patterns."""
        delivered_orders = orders_df[
            (orders_df['status'].str.lower() == 'delivered') &
            pd.notna(orders_df['actual_delivery_date']) &
            pd.notna(orders_df['promised_delivery_date'])
        ]
        
        if delivered_orders.empty:
            return {'analysis_possible': False}
        
        # Calculate delays
        delays = (delivered_orders['actual_delivery_date'] - delivered_orders['promised_delivery_date']).dt.total_seconds() / 3600
        delayed_orders = delays[delays > 0]
        
        return {
            'analysis_possible': True,
            'total_delivered': len(delivered_orders),
            'on_time_deliveries': len(delays[delays <= 0]),
            'delayed_deliveries': len(delayed_orders),
            'average_delay_hours': delayed_orders.mean() if not delayed_orders.empty else 0,
            'max_delay_hours': delayed_orders.max() if not delayed_orders.empty else 0
        }
    
    def _analyze_external_factor_patterns(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze external factor patterns."""
        orders_with_factors = orders_df[pd.notna(orders_df['traffic_condition']) | pd.notna(orders_df['weather_condition'])]
        
        if orders_with_factors.empty:
            return {'analysis_possible': False}
        
        traffic_patterns = orders_with_factors['traffic_condition'].value_counts().to_dict()
        weather_patterns = orders_with_factors['weather_condition'].value_counts().to_dict()
        
        return {
            'analysis_possible': True,
            'orders_with_external_factors': len(orders_with_factors),
            'traffic_patterns': traffic_patterns,
            'weather_patterns': weather_patterns
        }
    
    def _analyze_warehouse_performance_patterns(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze warehouse performance patterns."""
        orders_with_warehouse = orders_df[pd.notna(orders_df['warehouse_name'])]
        
        if orders_with_warehouse.empty:
            return {'analysis_possible': False}
        
        warehouse_performance = orders_with_warehouse.groupby('warehouse_name').agg({
            'status': lambda x: (x == 'Delivered').sum() / len(x) * 100,
            'order_id': 'count'
        }).to_dict()
        
        return {
            'analysis_possible': True,
            'warehouse_success_rates': warehouse_performance.get('status', {}),
            'warehouse_order_counts': warehouse_performance.get('order_id', {})
        }
    
    def _analyze_driver_performance_patterns(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze driver performance patterns."""
        orders_with_driver = orders_df[pd.notna(orders_df['driver_name'])]
        
        if orders_with_driver.empty:
            return {'analysis_possible': False}
        
        driver_performance = orders_with_driver.groupby('driver_name').agg({
            'status': lambda x: (x == 'Delivered').sum() / len(x) * 100,
            'order_id': 'count'
        }).to_dict()
        
        return {
            'analysis_possible': True,
            'driver_success_rates': driver_performance.get('status', {}),
            'driver_order_counts': driver_performance.get('order_id', {})
        }
    
    def _analyze_client_patterns(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze client patterns."""
        client_patterns = orders_df.groupby('client_name').agg({
            'status': lambda x: (x == 'Delivered').sum() / len(x) * 100,
            'order_id': 'count',
            'amount': 'sum'
        }).to_dict()
        
        return {
            'client_success_rates': client_patterns.get('status', {}),
            'client_order_counts': client_patterns.get('order_id', {}),
            'client_total_amounts': client_patterns.get('amount', {})
        }
    
    def _analyze_delivery_location_patterns(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze delivery location patterns for client."""
        location_patterns = orders_df.groupby(['city', 'state']).agg({
            'status': lambda x: (x == 'Delivered').sum() / len(x) * 100,
            'order_id': 'count'
        }).to_dict()
        
        return {
            'location_success_rates': location_patterns.get('status', {}),
            'location_order_counts': location_patterns.get('order_id', {})
        }
    
    def _analyze_payment_mode_patterns(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze payment mode patterns."""
        payment_patterns = orders_df.groupby('payment_mode').agg({
            'status': lambda x: (x == 'Delivered').sum() / len(x) * 100,
            'order_id': 'count',
            'amount': 'mean'
        }).to_dict()
        
        return {
            'payment_success_rates': payment_patterns.get('status', {}),
            'payment_order_counts': payment_patterns.get('order_id', {}),
            'payment_average_amounts': payment_patterns.get('amount', {})
        }
    
    def _analyze_feedback_patterns(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze customer feedback patterns."""
        orders_with_feedback = orders_df[pd.notna(orders_df['feedback_text'])]
        
        if orders_with_feedback.empty:
            return {'analysis_possible': False}
        
        sentiment_patterns = orders_with_feedback['sentiment'].value_counts().to_dict()
        rating_stats = orders_with_feedback['rating'].describe().to_dict()
        
        return {
            'analysis_possible': True,
            'orders_with_feedback': len(orders_with_feedback),
            'sentiment_distribution': sentiment_patterns,
            'rating_statistics': rating_stats
        }
    
    def _analyze_picking_performance_patterns(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze picking performance patterns for warehouse."""
        orders_with_picking = orders_df[
            pd.notna(orders_df['picking_start']) & pd.notna(orders_df['picking_end'])
        ]
        
        if orders_with_picking.empty:
            return {'analysis_possible': False}
        
        picking_times = (orders_with_picking['picking_end'] - orders_with_picking['picking_start']).dt.total_seconds() / 3600
        
        return {
            'analysis_possible': True,
            'average_picking_time_hours': picking_times.mean(),
            'max_picking_time_hours': picking_times.max(),
            'min_picking_time_hours': picking_times.min()
        }
    
    def _analyze_dispatch_performance_patterns(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze dispatch performance patterns for warehouse."""
        orders_with_dispatch = orders_df[
            pd.notna(orders_df['picking_end']) & pd.notna(orders_df['dispatch_time'])
        ]
        
        if orders_with_dispatch.empty:
            return {'analysis_possible': False}
        
        dispatch_delays = (orders_with_dispatch['dispatch_time'] - orders_with_dispatch['picking_end']).dt.total_seconds() / 3600
        
        return {
            'analysis_possible': True,
            'average_dispatch_delay_hours': dispatch_delays.mean(),
            'max_dispatch_delay_hours': dispatch_delays.max(),
            'min_dispatch_delay_hours': dispatch_delays.min()
        }
    
    def _analyze_delivery_destination_patterns(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze delivery destination patterns for warehouse."""
        destination_patterns = orders_df.groupby(['city', 'state']).agg({
            'status': lambda x: (x == 'Delivered').sum() / len(x) * 100,
            'order_id': 'count'
        }).to_dict()
        
        return {
            'destination_success_rates': destination_patterns.get('status', {}),
            'destination_order_counts': destination_patterns.get('order_id', {})
        }
    
    def _analyze_client_distribution_patterns(self, orders_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze client distribution patterns for warehouse."""
        client_patterns = orders_df.groupby('client_name').agg({
            'status': lambda x: (x == 'Delivered').sum() / len(x) * 100,
            'order_id': 'count',
            'amount': 'sum'
        }).to_dict()
        
        return {
            'client_success_rates': client_patterns.get('status', {}),
            'client_order_counts': client_patterns.get('order_id', {}),
            'client_total_amounts': client_patterns.get('amount', {})
        }