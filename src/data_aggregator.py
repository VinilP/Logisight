"""
Data Aggregation utilities for the Logistics Insight System.
Provides functions to merge related data across different CSV sources using pandas.
Implements order-centric data aggregation combining orders with all related data sources.
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Optional, List
import logging
from data_loader import DataLoader

logger = logging.getLogger(__name__)


class DataAggregator:
    """
    Handles data aggregation and merging across multiple CSV data sources.
    Provides order-centric aggregation combining orders with clients, fleet_logs, 
    warehouse_logs, external_factors, and feedback.
    """
    
    def __init__(self, data_loader: DataLoader):
        """
        Initialize DataAggregator with a DataLoader instance.
        
        Args:
            data_loader: DataLoader instance for accessing CSV data
        """
        self.data_loader = data_loader
        self._cached_data = {}
        
    def _parse_datetime_columns(self, df: pd.DataFrame, datetime_columns: List[str]) -> pd.DataFrame:
        """
        Parse datetime columns in DataFrame with error handling.
        
        Args:
            df: DataFrame to process
            datetime_columns: List of column names to parse as datetime
            
        Returns:
            DataFrame with parsed datetime columns
        """
        df_copy = df.copy()
        
        for col in datetime_columns:
            if col in df_copy.columns:
                try:
                    # Handle various datetime formats and empty values
                    df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce')
                    logger.debug(f"Parsed datetime column: {col}")
                except Exception as e:
                    logger.warning(f"Failed to parse datetime column {col}: {str(e)}")
                    
        return df_copy
    
    def _load_and_cache_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all data sources and cache them with datetime parsing.
        
        Returns:
            Dictionary of cached DataFrames with parsed datetime columns
        """
        if not self._cached_data:
            logger.info("Loading and caching all data sources...")
            
            # Load all data
            raw_data = self.data_loader.load_all_data()
            
            # Define datetime columns for each data source
            datetime_columns = {
                'orders': ['order_date', 'promised_delivery_date', 'actual_delivery_date', 'created_at'],
                'clients': ['created_at'],
                'drivers': ['created_at'],
                'warehouses': ['created_at'],
                'fleet_logs': ['departure_time', 'arrival_time', 'created_at'],
                'external_factors': ['recorded_at'],
                'feedback': ['created_at'],
                'warehouse_logs': ['picking_start', 'picking_end', 'dispatch_time']
            }
            
            # Parse datetime columns for each data source
            for source, df in raw_data.items():
                if source in datetime_columns:
                    self._cached_data[source] = self._parse_datetime_columns(df, datetime_columns[source])
                else:
                    self._cached_data[source] = df
                    
            logger.info(f"Successfully cached {len(self._cached_data)} data sources")
            
        return self._cached_data
    
    def get_comprehensive_order_data(self, order_id: int) -> Optional[Dict]:
        """
        Get comprehensive order data by aggregating all related information.
        
        Args:
            order_id: Order ID to aggregate data for
            
        Returns:
            Dictionary containing comprehensive order information or None if order not found
        """
        data = self._load_and_cache_data()
        
        # Get base order information
        orders_df = data['orders']
        order_row = orders_df[orders_df['order_id'] == order_id]
        
        if order_row.empty:
            logger.warning(f"Order {order_id} not found")
            return None
            
        order_info = order_row.iloc[0].to_dict()
        
        # Get client information
        client_info = {}
        if 'client_id' in order_info and pd.notna(order_info['client_id']):
            clients_df = data['clients']
            client_row = clients_df[clients_df['client_id'] == order_info['client_id']]
            if not client_row.empty:
                client_info = client_row.iloc[0].to_dict()
        
        # Get fleet activity information
        fleet_activity = {}
        fleet_logs_df = data['fleet_logs']
        fleet_row = fleet_logs_df[fleet_logs_df['order_id'] == order_id]
        if not fleet_row.empty:
            fleet_info = fleet_row.iloc[0].to_dict()
            
            # Get driver information
            if 'driver_id' in fleet_info and pd.notna(fleet_info['driver_id']):
                drivers_df = data['drivers']
                driver_row = drivers_df[drivers_df['driver_id'] == fleet_info['driver_id']]
                if not driver_row.empty:
                    driver_info = driver_row.iloc[0].to_dict()
                    fleet_activity = {**fleet_info, **driver_info}
                else:
                    fleet_activity = fleet_info
            else:
                fleet_activity = fleet_info
        
        # Get warehouse activity information
        warehouse_activity = {}
        warehouse_logs_df = data['warehouse_logs']
        warehouse_log_row = warehouse_logs_df[warehouse_logs_df['order_id'] == order_id]
        if not warehouse_log_row.empty:
            warehouse_log_info = warehouse_log_row.iloc[0].to_dict()
            
            # Get warehouse information
            if 'warehouse_id' in warehouse_log_info and pd.notna(warehouse_log_info['warehouse_id']):
                warehouses_df = data['warehouses']
                warehouse_row = warehouses_df[warehouses_df['warehouse_id'] == warehouse_log_info['warehouse_id']]
                if not warehouse_row.empty:
                    warehouse_info = warehouse_row.iloc[0].to_dict()
                    warehouse_activity = {**warehouse_log_info, **warehouse_info}
                else:
                    warehouse_activity = warehouse_log_info
            else:
                warehouse_activity = warehouse_log_info
        
        # Get external conditions
        external_conditions = {}
        external_factors_df = data['external_factors']
        external_row = external_factors_df[external_factors_df['order_id'] == order_id]
        if not external_row.empty:
            external_conditions = external_row.iloc[0].to_dict()
        
        # Get customer feedback
        customer_feedback = {}
        feedback_df = data['feedback']
        feedback_row = feedback_df[feedback_df['order_id'] == order_id]
        if not feedback_row.empty:
            customer_feedback = feedback_row.iloc[0].to_dict()
        
        # Construct comprehensive order view
        comprehensive_order = {
            'order_info': {
                'order_id': order_info.get('order_id'),
                'customer_name': order_info.get('customer_name'),
                'customer_phone': order_info.get('customer_phone'),
                'order_date': order_info.get('order_date'),
                'promised_delivery_date': order_info.get('promised_delivery_date'),
                'actual_delivery_date': order_info.get('actual_delivery_date'),
                'status': order_info.get('status'),
                'payment_mode': order_info.get('payment_mode'),
                'amount': order_info.get('amount'),
                'failure_reason': order_info.get('failure_reason')
            },
            'client_info': {
                'client_id': client_info.get('client_id'),
                'client_name': client_info.get('client_name'),
                'gst_number': client_info.get('gst_number'),
                'contact_person': client_info.get('contact_person'),
                'contact_phone': client_info.get('contact_phone'),
                'contact_email': client_info.get('contact_email')
            },
            'delivery_location': {
                'delivery_address_line1': order_info.get('delivery_address_line1'),
                'delivery_address_line2': order_info.get('delivery_address_line2'),
                'city': order_info.get('city'),
                'state': order_info.get('state'),
                'pincode': order_info.get('pincode')
            },
            'fleet_activity': {
                'driver_id': fleet_activity.get('driver_id'),
                'driver_name': fleet_activity.get('driver_name'),
                'vehicle_number': fleet_activity.get('vehicle_number'),
                'route_code': fleet_activity.get('route_code'),
                'gps_delay_notes': fleet_activity.get('gps_delay_notes'),
                'departure_time': fleet_activity.get('departure_time'),
                'arrival_time': fleet_activity.get('arrival_time'),
                'partner_company': fleet_activity.get('partner_company')
            },
            'warehouse_activity': {
                'warehouse_id': warehouse_activity.get('warehouse_id'),
                'warehouse_name': warehouse_activity.get('warehouse_name'),
                'picking_start': warehouse_activity.get('picking_start'),
                'picking_end': warehouse_activity.get('picking_end'),
                'dispatch_time': warehouse_activity.get('dispatch_time'),
                'notes': warehouse_activity.get('notes')
            },
            'external_conditions': {
                'traffic_condition': external_conditions.get('traffic_condition'),
                'weather_condition': external_conditions.get('weather_condition'),
                'event_type': external_conditions.get('event_type')
            },
            'customer_feedback': {
                'feedback_text': customer_feedback.get('feedback_text'),
                'sentiment': customer_feedback.get('sentiment'),
                'rating': customer_feedback.get('rating')
            }
        }
        
        return comprehensive_order
    
    def get_orders_by_city_and_date(self, city: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Get all orders for a specific city within a date range with aggregated data.
        
        Args:
            city: City name to filter by
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            DataFrame with aggregated order data for the specified city and date range
        """
        data = self._load_and_cache_data()
        orders_df = data['orders']
        
        # Filter orders by city and date range
        city_orders = orders_df[
            (orders_df['city'].str.lower() == city.lower()) &
            (orders_df['order_date'] >= start_date) &
            (orders_df['order_date'] <= end_date)
        ].copy()
        
        if city_orders.empty:
            logger.info(f"No orders found for city {city} between {start_date} and {end_date}")
            return pd.DataFrame()
        
        # Merge with client information
        clients_df = data['clients']
        city_orders = city_orders.merge(
            clients_df[['client_id', 'client_name', 'contact_person']], 
            on='client_id', 
            how='left',
            suffixes=('', '_client')
        )
        
        # Merge with fleet logs
        fleet_logs_df = data['fleet_logs']
        city_orders = city_orders.merge(
            fleet_logs_df[['order_id', 'driver_id', 'vehicle_number', 'gps_delay_notes', 'departure_time', 'arrival_time']], 
            on='order_id', 
            how='left'
        )
        
        # Merge with driver information
        drivers_df = data['drivers']
        city_orders = city_orders.merge(
            drivers_df[['driver_id', 'driver_name', 'partner_company']], 
            on='driver_id', 
            how='left',
            suffixes=('', '_driver')
        )
        
        # Merge with external factors
        external_factors_df = data['external_factors']
        city_orders = city_orders.merge(
            external_factors_df[['order_id', 'traffic_condition', 'weather_condition', 'event_type']], 
            on='order_id', 
            how='left'
        )
        
        # Merge with warehouse logs
        warehouse_logs_df = data['warehouse_logs']
        city_orders = city_orders.merge(
            warehouse_logs_df[['order_id', 'warehouse_id', 'picking_start', 'picking_end', 'dispatch_time', 'notes']], 
            on='order_id', 
            how='left',
            suffixes=('', '_warehouse_log')
        )
        
        # Merge with warehouse information
        warehouses_df = data['warehouses']
        city_orders = city_orders.merge(
            warehouses_df[['warehouse_id', 'warehouse_name', 'manager_name']], 
            on='warehouse_id', 
            how='left',
            suffixes=('', '_warehouse')
        )
        
        # Merge with feedback
        feedback_df = data['feedback']
        city_orders = city_orders.merge(
            feedback_df[['order_id', 'feedback_text', 'sentiment', 'rating']], 
            on='order_id', 
            how='left'
        )
        
        logger.info(f"Retrieved {len(city_orders)} orders for city {city}")
        return city_orders
    
    def get_orders_by_client_and_date_range(self, client_id: int, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Get all orders for a specific client within a date range with aggregated data.
        
        Args:
            client_id: Client ID to filter by
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            DataFrame with aggregated order data for the specified client and date range
        """
        data = self._load_and_cache_data()
        orders_df = data['orders']
        
        # Filter orders by client and date range
        client_orders = orders_df[
            (orders_df['client_id'] == client_id) &
            (orders_df['order_date'] >= start_date) &
            (orders_df['order_date'] <= end_date)
        ].copy()
        
        if client_orders.empty:
            logger.info(f"No orders found for client {client_id} between {start_date} and {end_date}")
            return pd.DataFrame()
        
        # Apply the same merging logic as city orders
        return self._merge_all_related_data(client_orders)
    
    def get_orders_by_warehouse_and_date_range(self, warehouse_id: int, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Get all orders for a specific warehouse within a date range with aggregated data.
        
        Args:
            warehouse_id: Warehouse ID to filter by
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            DataFrame with aggregated order data for the specified warehouse and date range
        """
        data = self._load_and_cache_data()
        warehouse_logs_df = data['warehouse_logs']
        
        # Filter warehouse logs by warehouse and get order IDs
        warehouse_orders_logs = warehouse_logs_df[
            (warehouse_logs_df['warehouse_id'] == warehouse_id) &
            (warehouse_logs_df['picking_start'] >= start_date) &
            (warehouse_logs_df['picking_start'] <= end_date)
        ]
        
        if warehouse_orders_logs.empty:
            logger.info(f"No orders found for warehouse {warehouse_id} between {start_date} and {end_date}")
            return pd.DataFrame()
        
        # Get orders for these order IDs
        orders_df = data['orders']
        warehouse_orders = orders_df[
            orders_df['order_id'].isin(warehouse_orders_logs['order_id'])
        ].copy()
        
        return self._merge_all_related_data(warehouse_orders)
    
    def _merge_all_related_data(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        """
        Helper method to merge all related data sources with orders DataFrame.
        
        Args:
            orders_df: Base orders DataFrame to merge with
            
        Returns:
            DataFrame with all related data merged
        """
        data = self._load_and_cache_data()
        result_df = orders_df.copy()
        
        # Merge with client information
        clients_df = data['clients']
        result_df = result_df.merge(
            clients_df[['client_id', 'client_name', 'contact_person', 'contact_phone', 'contact_email']], 
            on='client_id', 
            how='left',
            suffixes=('', '_client')
        )
        
        # Merge with fleet logs
        fleet_logs_df = data['fleet_logs']
        result_df = result_df.merge(
            fleet_logs_df[['order_id', 'driver_id', 'vehicle_number', 'route_code', 'gps_delay_notes', 'departure_time', 'arrival_time']], 
            on='order_id', 
            how='left'
        )
        
        # Merge with driver information
        drivers_df = data['drivers']
        result_df = result_df.merge(
            drivers_df[['driver_id', 'driver_name', 'phone', 'partner_company', 'city', 'state']], 
            on='driver_id', 
            how='left',
            suffixes=('', '_driver')
        )
        
        # Merge with external factors
        external_factors_df = data['external_factors']
        result_df = result_df.merge(
            external_factors_df[['order_id', 'traffic_condition', 'weather_condition', 'event_type', 'recorded_at']], 
            on='order_id', 
            how='left'
        )
        
        # Merge with warehouse logs
        warehouse_logs_df = data['warehouse_logs']
        result_df = result_df.merge(
            warehouse_logs_df[['order_id', 'warehouse_id', 'picking_start', 'picking_end', 'dispatch_time', 'notes']], 
            on='order_id', 
            how='left',
            suffixes=('', '_warehouse_log')
        )
        
        # Merge with warehouse information
        warehouses_df = data['warehouses']
        result_df = result_df.merge(
            warehouses_df[['warehouse_id', 'warehouse_name', 'city', 'state', 'capacity', 'manager_name', 'contact_phone']], 
            on='warehouse_id', 
            how='left',
            suffixes=('', '_warehouse')
        )
        
        # Merge with feedback
        feedback_df = data['feedback']
        result_df = result_df.merge(
            feedback_df[['order_id', 'feedback_text', 'sentiment', 'rating']], 
            on='order_id', 
            how='left'
        )
        
        return result_df
    
    def get_orders(self) -> pd.DataFrame:
        """
        Get orders DataFrame.
        
        Returns:
            DataFrame containing all orders data
        """
        data = self._load_and_cache_data()
        return data['orders']
    
    def get_clients(self) -> pd.DataFrame:
        """
        Get clients DataFrame.
        
        Returns:
            DataFrame containing all clients data
        """
        data = self._load_and_cache_data()
        return data['clients']
    
    def get_warehouses(self) -> pd.DataFrame:
        """
        Get warehouses DataFrame.
        
        Returns:
            DataFrame containing all warehouses data
        """
        data = self._load_and_cache_data()
        return data['warehouses']
    
    def get_drivers(self) -> pd.DataFrame:
        """
        Get drivers DataFrame.
        
        Returns:
            DataFrame containing all drivers data
        """
        data = self._load_and_cache_data()
        return data['drivers']
    
    def get_fleet_logs(self) -> pd.DataFrame:
        """
        Get fleet logs DataFrame.
        
        Returns:
            DataFrame containing all fleet logs data
        """
        data = self._load_and_cache_data()
        return data['fleet_logs']
    
    def get_external_factors(self) -> pd.DataFrame:
        """
        Get external factors DataFrame.
        
        Returns:
            DataFrame containing all external factors data
        """
        data = self._load_and_cache_data()
        return data['external_factors']
    
    def get_feedback(self) -> pd.DataFrame:
        """
        Get feedback DataFrame.
        
        Returns:
            DataFrame containing all feedback data
        """
        data = self._load_and_cache_data()
        return data['feedback']
    
    def get_warehouse_logs(self) -> pd.DataFrame:
        """
        Get warehouse logs DataFrame.
        
        Returns:
            DataFrame containing all warehouse logs data
        """
        data = self._load_and_cache_data()
        return data['warehouse_logs']

    def clear_cache(self):
        """Clear cached data to force reload on next access."""
        self._cached_data = {}
        logger.info("Data cache cleared")