"""
Unit tests for DataLoader class.
Tests data loading functionality, validation, and error handling.
"""

import unittest
import pandas as pd
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import DataLoader


class TestDataLoader(unittest.TestCase):
    """Test cases for DataLoader class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for test data
        self.test_data_dir = tempfile.mkdtemp()
        self.data_loader = DataLoader(self.test_data_dir)
        
        # Sample CSV content for testing
        self.sample_orders_csv = """order_id,client_id,customer_name,customer_phone,delivery_address_line1,delivery_address_line2,city,state,pincode,order_date,promised_delivery_date,actual_delivery_date,status,payment_mode,amount,failure_reason,created_at
1,101,John Doe,9876543210,123 Main St,,Mumbai,Maharashtra,400001,2023-01-01,2023-01-02,2023-01-02,delivered,cash,1500.0,,2023-01-01
2,102,Jane Smith,9876543211,456 Oak Ave,,Delhi,Delhi,110001,2023-01-02,2023-01-03,2023-01-04,delayed,card,2000.0,traffic,2023-01-02"""
        
        self.sample_clients_csv = """client_id,client_name,gst_number,contact_person,contact_phone,contact_email,address_line1,address_line2,city,state,pincode,created_at
101,ABC Corp,GST123,John Manager,9876543210,john@abc.com,Business Park,,Mumbai,Maharashtra,400001,2023-01-01
102,XYZ Ltd,GST456,Jane Admin,9876543211,jane@xyz.com,Tech Hub,,Delhi,Delhi,110001,2023-01-01"""
        
        self.sample_drivers_csv = """driver_id,driver_name,phone,license_number,partner_company,city,state,status,created_at
201,Driver One,9876543220,DL123,FastDelivery,Mumbai,Maharashtra,active,2023-01-01
202,Driver Two,9876543221,DL456,QuickTransport,Delhi,Delhi,active,2023-01-01"""
        
        self.sample_warehouses_csv = """warehouse_id,warehouse_name,state,city,pincode,capacity,manager_name,contact_phone,created_at
301,Mumbai Central,Maharashtra,Mumbai,400001,10000,Manager One,9876543230,2023-01-01
302,Delhi Hub,Delhi,Delhi,110001,15000,Manager Two,9876543231,2023-01-01"""
        
        self.sample_fleet_logs_csv = """fleet_log_id,order_id,driver_id,vehicle_number,route_code,gps_delay_notes,departure_time,arrival_time,created_at
401,1,201,MH01AB1234,R001,No delays,2023-01-01 10:00:00,2023-01-01 12:00:00,2023-01-01
402,2,202,DL01CD5678,R002,Traffic jam,2023-01-02 09:00:00,2023-01-02 14:00:00,2023-01-02"""
        
        self.sample_external_factors_csv = """factor_id,order_id,traffic_condition,weather_condition,event_type,recorded_at
501,1,normal,clear,none,2023-01-01 10:00:00
502,2,heavy,rainy,festival,2023-01-02 09:00:00"""
        
        self.sample_feedback_csv = """feedback_id,order_id,customer_name,feedback_text,sentiment,rating,created_at
601,1,John Doe,Great service,positive,5,2023-01-02
602,2,Jane Smith,Delayed delivery,negative,2,2023-01-04"""
        
        self.sample_warehouse_logs_csv = """log_id,order_id,warehouse_id,picking_start,picking_end,dispatch_time,notes
701,1,301,2023-01-01 08:00:00,2023-01-01 09:00:00,2023-01-01 10:00:00,On time
702,2,302,2023-01-02 07:00:00,2023-01-02 08:30:00,2023-01-02 09:00:00,Delayed picking"""
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary directory
        shutil.rmtree(self.test_data_dir)
    
    def _create_test_file(self, filename, content):
        """Helper method to create test CSV files."""
        file_path = os.path.join(self.test_data_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)
    
    def test_init(self):
        """Test DataLoader initialization."""
        loader = DataLoader("test_dir")
        self.assertEqual(loader.data_directory, "test_dir")
        self.assertEqual(len(loader.required_files), 8)
        self.assertIn('orders', loader.required_files)
        self.assertIn('clients', loader.required_files)
    
    def test_validate_file_exists_success(self):
        """Test file existence validation when file exists."""
        self._create_test_file('orders.csv', self.sample_orders_csv)
        result = self.data_loader._validate_file_exists('orders.csv')
        self.assertTrue(result)
    
    def test_validate_file_exists_failure(self):
        """Test file existence validation when file doesn't exist."""
        result = self.data_loader._validate_file_exists('nonexistent.csv')
        self.assertFalse(result)
    
    def test_load_orders_success(self):
        """Test successful loading of orders.csv."""
        self._create_test_file('orders.csv', self.sample_orders_csv)
        df = self.data_loader.load_orders()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn('order_id', df.columns)
        self.assertIn('client_id', df.columns)
        self.assertEqual(df.iloc[0]['customer_name'], 'John Doe')
    
    def test_load_clients_success(self):
        """Test successful loading of clients.csv."""
        self._create_test_file('clients.csv', self.sample_clients_csv)
        df = self.data_loader.load_clients()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn('client_id', df.columns)
        self.assertIn('client_name', df.columns)
        self.assertEqual(df.iloc[0]['client_name'], 'ABC Corp')
    
    def test_load_drivers_success(self):
        """Test successful loading of drivers.csv."""
        self._create_test_file('drivers.csv', self.sample_drivers_csv)
        df = self.data_loader.load_drivers()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn('driver_id', df.columns)
        self.assertIn('driver_name', df.columns)
    
    def test_load_warehouses_success(self):
        """Test successful loading of warehouses.csv."""
        self._create_test_file('warehouses.csv', self.sample_warehouses_csv)
        df = self.data_loader.load_warehouses()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn('warehouse_id', df.columns)
        self.assertIn('warehouse_name', df.columns)
    
    def test_load_fleet_logs_success(self):
        """Test successful loading of fleet_logs.csv."""
        self._create_test_file('fleet_logs.csv', self.sample_fleet_logs_csv)
        df = self.data_loader.load_fleet_logs()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn('fleet_log_id', df.columns)
        self.assertIn('order_id', df.columns)
    
    def test_load_external_factors_success(self):
        """Test successful loading of external_factors.csv."""
        self._create_test_file('external_factors.csv', self.sample_external_factors_csv)
        df = self.data_loader.load_external_factors()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn('factor_id', df.columns)
        self.assertIn('traffic_condition', df.columns)
    
    def test_load_feedback_success(self):
        """Test successful loading of feedback.csv."""
        self._create_test_file('feedback.csv', self.sample_feedback_csv)
        df = self.data_loader.load_feedback()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn('feedback_id', df.columns)
        self.assertIn('feedback_text', df.columns)
    
    def test_load_warehouse_logs_success(self):
        """Test successful loading of warehouse_logs.csv."""
        self._create_test_file('warehouse_logs.csv', self.sample_warehouse_logs_csv)
        df = self.data_loader.load_warehouse_logs()
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn('log_id', df.columns)
        self.assertIn('warehouse_id', df.columns)
    
    def test_load_missing_file(self):
        """Test error handling when CSV file is missing."""
        with self.assertRaises(FileNotFoundError):
            self.data_loader.load_orders()
    
    def test_load_empty_file(self):
        """Test error handling when CSV file is empty."""
        self._create_test_file('orders.csv', '')
        with self.assertRaises(ValueError):
            self.data_loader.load_orders()
    
    def test_load_malformed_csv(self):
        """Test error handling when CSV file is malformed."""
        malformed_csv = "order_id,client_id\n1,101\n2,102,extra_column"
        self._create_test_file('orders.csv', malformed_csv)
        # This should raise a ValueError due to malformed data
        with self.assertRaises(ValueError):
            self.data_loader.load_orders()
    
    def test_date_parsing_validation(self):
        """Test that data loader loads date columns as strings (parsing happens in aggregator)."""
        # Create CSV with various date formats
        date_test_csv = """order_id,client_id,customer_name,customer_phone,delivery_address_line1,delivery_address_line2,city,state,pincode,order_date,promised_delivery_date,actual_delivery_date,status,payment_mode,amount,failure_reason,created_at
1,101,John Doe,9876543210,123 Main St,,Mumbai,Maharashtra,400001,2023-01-01 10:00:00,2023-01-02 10:00:00,2023-01-02 12:00:00,delivered,cash,1500.0,,2023-01-01 09:00:00
2,102,Jane Smith,9876543211,456 Oak Ave,,Delhi,Delhi,110001,invalid_date,2023-01-03 10:00:00,,failed,card,2000.0,address_issue,2023-01-02 09:00:00"""
        
        self._create_test_file('orders.csv', date_test_csv)
        df = self.data_loader.load_orders()
        
        # DataLoader loads dates as strings - datetime parsing happens in DataAggregator
        self.assertTrue(pd.api.types.is_object_dtype(df['order_date']))
        self.assertTrue(pd.api.types.is_object_dtype(df['promised_delivery_date']))
        
        # Verify data is loaded correctly
        self.assertEqual(df.loc[0, 'order_date'], '2023-01-01 10:00:00')
        self.assertEqual(df.loc[1, 'order_date'], 'invalid_date')
    
    def test_data_type_validation(self):
        """Test data type validation for numeric columns."""
        # Create CSV with invalid numeric data
        invalid_numeric_csv = """order_id,client_id,customer_name,customer_phone,delivery_address_line1,delivery_address_line2,city,state,pincode,order_date,promised_delivery_date,actual_delivery_date,status,payment_mode,amount,failure_reason,created_at
1,101,John Doe,9876543210,123 Main St,,Mumbai,Maharashtra,400001,2023-01-01,2023-01-02,2023-01-02,delivered,cash,invalid_amount,,2023-01-01
2,102,Jane Smith,9876543211,456 Oak Ave,,Delhi,Delhi,110001,2023-01-02,2023-01-03,,failed,card,2000.0,traffic,2023-01-02"""
        
        self._create_test_file('orders.csv', invalid_numeric_csv)
        
        # Should handle invalid numeric data gracefully
        df = self.data_loader.load_orders()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
    
    def test_large_dataset_handling(self):
        """Test handling of larger datasets."""
        # Create a larger test dataset
        large_csv_header = "order_id,client_id,customer_name,customer_phone,delivery_address_line1,delivery_address_line2,city,state,pincode,order_date,promised_delivery_date,actual_delivery_date,status,payment_mode,amount,failure_reason,created_at\n"
        large_csv_rows = []
        
        for i in range(1000):
            row = f"{i},101,Customer {i},987654321{i%10},Address {i},,Mumbai,Maharashtra,400001,2023-01-01,2023-01-02,2023-01-02,delivered,cash,{1500 + i},,2023-01-01"
            large_csv_rows.append(row)
        
        large_csv = large_csv_header + "\n".join(large_csv_rows)
        self._create_test_file('orders.csv', large_csv)
        
        df = self.data_loader.load_orders()
        self.assertEqual(len(df), 1000)
        self.assertIn('order_id', df.columns)
    
    def test_memory_efficiency(self):
        """Test memory efficiency with data loading."""
        # Create test files
        self._create_test_file('orders.csv', self.sample_orders_csv)
        self._create_test_file('clients.csv', self.sample_clients_csv)
        
        # Load data multiple times to test memory usage
        for _ in range(5):
            df1 = self.data_loader.load_orders()
            df2 = self.data_loader.load_clients()
            
            # Verify data is loaded correctly each time
            self.assertEqual(len(df1), 2)
            self.assertEqual(len(df2), 2)
            
            # Clean up references
            del df1, df2
    
    def test_load_missing_required_columns(self):
        """Test error handling when required columns are missing."""
        incomplete_csv = "order_id,customer_name\n1,John Doe\n2,Jane Smith"
        self._create_test_file('orders.csv', incomplete_csv)
        with self.assertRaises(ValueError):
            self.data_loader.load_orders()
    
    def test_load_all_data_success(self):
        """Test successful loading of all CSV files."""
        # Create all test files
        self._create_test_file('orders.csv', self.sample_orders_csv)
        self._create_test_file('clients.csv', self.sample_clients_csv)
        self._create_test_file('drivers.csv', self.sample_drivers_csv)
        self._create_test_file('warehouses.csv', self.sample_warehouses_csv)
        self._create_test_file('fleet_logs.csv', self.sample_fleet_logs_csv)
        self._create_test_file('external_factors.csv', self.sample_external_factors_csv)
        self._create_test_file('feedback.csv', self.sample_feedback_csv)
        self._create_test_file('warehouse_logs.csv', self.sample_warehouse_logs_csv)
        
        data = self.data_loader.load_all_data()
        
        self.assertIsInstance(data, dict)
        self.assertEqual(len(data), 8)
        self.assertIn('orders', data)
        self.assertIn('clients', data)
        self.assertIn('drivers', data)
        self.assertIn('warehouses', data)
        self.assertIn('fleet_logs', data)
        self.assertIn('external_factors', data)
        self.assertIn('feedback', data)
        self.assertIn('warehouse_logs', data)
        
        # Verify each DataFrame has data
        for key, df in data.items():
            self.assertIsInstance(df, pd.DataFrame)
            self.assertGreater(len(df), 0)
    
    def test_load_all_data_partial_failure(self):
        """Test load_all_data when some files are missing."""
        # Create only some test files
        self._create_test_file('orders.csv', self.sample_orders_csv)
        self._create_test_file('clients.csv', self.sample_clients_csv)
        # Missing other files
        
        with self.assertRaises(Exception):
            self.data_loader.load_all_data()
    
    def test_validate_data_directory(self):
        """Test data directory validation."""
        # Create some test files
        self._create_test_file('orders.csv', self.sample_orders_csv)
        self._create_test_file('clients.csv', self.sample_clients_csv)
        
        validation_results = self.data_loader.validate_data_directory()
        
        self.assertIsInstance(validation_results, dict)
        self.assertEqual(len(validation_results), 8)
        self.assertTrue(validation_results['orders.csv'])
        self.assertTrue(validation_results['clients.csv'])
        self.assertFalse(validation_results['drivers.csv'])  # Not created


if __name__ == '__main__':
    unittest.main()