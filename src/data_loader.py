"""
DataLoader class for loading and validating CSV data files.
Handles all 8 CSV files from the sample-data-set folder with error handling.
"""

import pandas as pd
import os
from typing import Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """
    Loads and validates CSV data files for the Logistics Insight System.
    Handles missing files and malformed data with appropriate error handling.
    """
    
    def __init__(self, data_directory: str = "sample-data-set"):
        """
        Initialize DataLoader with data directory path.
        
        Args:
            data_directory: Path to directory containing CSV files
        """
        self.data_directory = data_directory
        self.required_files = {
            'orders': 'orders.csv',
            'clients': 'clients.csv', 
            'drivers': 'drivers.csv',
            'warehouses': 'warehouses.csv',
            'fleet_logs': 'fleet_logs.csv',
            'external_factors': 'external_factors.csv',
            'feedback': 'feedback.csv',
            'warehouse_logs': 'warehouse_logs.csv'
        }
        
    def _validate_file_exists(self, filename: str) -> bool:
        """Check if CSV file exists in data directory."""
        file_path = os.path.join(self.data_directory, filename)
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
        return True
    
    def _load_csv_with_validation(self, filename: str, required_columns: Optional[list] = None) -> pd.DataFrame:
        """
        Load CSV file with validation and error handling.
        
        Args:
            filename: Name of CSV file to load
            required_columns: List of required column names (optional)
            
        Returns:
            pandas DataFrame with loaded data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If required columns are missing or data is malformed
        """
        file_path = os.path.join(self.data_directory, filename)
        
        if not self._validate_file_exists(filename):
            raise FileNotFoundError(f"Required file not found: {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Successfully loaded {filename}: {len(df)} rows")
            
            # Validate required columns if specified
            if required_columns:
                missing_columns = set(required_columns) - set(df.columns)
                if missing_columns:
                    raise ValueError(f"Missing required columns in {filename}: {missing_columns}")
            
            # Check for completely empty DataFrame
            if df.empty:
                logger.warning(f"File {filename} is empty")
            
            return df
            
        except pd.errors.EmptyDataError:
            logger.error(f"File {filename} is empty or contains no data")
            raise ValueError(f"File {filename} contains no data")
        except pd.errors.ParserError as e:
            logger.error(f"Error parsing {filename}: {str(e)}")
            raise ValueError(f"Malformed data in {filename}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error loading {filename}: {str(e)}")
            raise
    
    def load_orders(self) -> pd.DataFrame:
        """Load orders.csv with validation."""
        required_columns = ['order_id', 'client_id', 'customer_name', 'city', 'state', 
                          'order_date', 'status', 'payment_mode', 'amount']
        return self._load_csv_with_validation('orders.csv', required_columns)
    
    def load_clients(self) -> pd.DataFrame:
        """Load clients.csv with validation."""
        required_columns = ['client_id', 'client_name', 'city', 'state']
        return self._load_csv_with_validation('clients.csv', required_columns)
    
    def load_drivers(self) -> pd.DataFrame:
        """Load drivers.csv with validation."""
        required_columns = ['driver_id', 'driver_name', 'phone', 'city', 'state', 'status']
        return self._load_csv_with_validation('drivers.csv', required_columns)
    
    def load_warehouses(self) -> pd.DataFrame:
        """Load warehouses.csv with validation."""
        required_columns = ['warehouse_id', 'warehouse_name', 'city', 'state', 'capacity']
        return self._load_csv_with_validation('warehouses.csv', required_columns)
    
    def load_fleet_logs(self) -> pd.DataFrame:
        """Load fleet_logs.csv with validation."""
        required_columns = ['fleet_log_id', 'order_id', 'driver_id', 'vehicle_number']
        return self._load_csv_with_validation('fleet_logs.csv', required_columns)
    
    def load_external_factors(self) -> pd.DataFrame:
        """Load external_factors.csv with validation."""
        required_columns = ['factor_id', 'order_id', 'traffic_condition', 'weather_condition']
        return self._load_csv_with_validation('external_factors.csv', required_columns)
    
    def load_feedback(self) -> pd.DataFrame:
        """Load feedback.csv with validation."""
        required_columns = ['feedback_id', 'order_id', 'customer_name', 'feedback_text', 'rating']
        return self._load_csv_with_validation('feedback.csv', required_columns)
    
    def load_warehouse_logs(self) -> pd.DataFrame:
        """Load warehouse_logs.csv with validation."""
        required_columns = ['log_id', 'order_id', 'warehouse_id']
        return self._load_csv_with_validation('warehouse_logs.csv', required_columns)
    
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all CSV files and return as dictionary.
        
        Returns:
            Dictionary with data source names as keys and DataFrames as values
            
        Raises:
            Exception: If any required file fails to load
        """
        data = {}
        load_methods = {
            'orders': self.load_orders,
            'clients': self.load_clients,
            'drivers': self.load_drivers,
            'warehouses': self.load_warehouses,
            'fleet_logs': self.load_fleet_logs,
            'external_factors': self.load_external_factors,
            'feedback': self.load_feedback,
            'warehouse_logs': self.load_warehouse_logs
        }
        
        failed_loads = []
        
        for data_source, load_method in load_methods.items():
            try:
                data[data_source] = load_method()
                logger.info(f"Successfully loaded {data_source}")
            except Exception as e:
                logger.error(f"Failed to load {data_source}: {str(e)}")
                failed_loads.append(data_source)
        
        if failed_loads:
            raise Exception(f"Failed to load the following data sources: {failed_loads}")
        
        logger.info(f"Successfully loaded all {len(data)} data sources")
        return data
    
    def validate_data_directory(self) -> Dict[str, bool]:
        """
        Validate that all required CSV files exist in the data directory.
        
        Returns:
            Dictionary with filename as key and existence status as boolean value
        """
        validation_results = {}
        
        for data_source, filename in self.required_files.items():
            validation_results[filename] = self._validate_file_exists(filename)
        
        return validation_results