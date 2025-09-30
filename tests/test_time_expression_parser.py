"""
Comprehensive tests for the TimeExpressionParser class.
Tests various time expressions including relative dates, specific months/years, quarters, and date ranges.
"""

import unittest
from datetime import datetime, timedelta
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from query_processor import TimeExpressionParser


class TestTimeExpressionParser(unittest.TestCase):
    """Test cases for TimeExpressionParser functionality."""
    
    def setUp(self):
        """Set up test fixtures with known data bounds."""
        self.data_start_date = datetime(2025, 1, 1)
        self.data_end_date = datetime(2025, 12, 31)
        self.parser = TimeExpressionParser(self.data_start_date, self.data_end_date)
    
    def test_relative_time_expressions(self):
        """Test parsing of relative time expressions."""
        
        # Test months ago
        start, end = self.parser.parse_flexible_time_expression("3 months ago")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        self.assertLess(start, end)
        
        # Test weeks ago
        start, end = self.parser.parse_flexible_time_expression("6 weeks ago")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        self.assertLess(start, end)
        
        # Test days ago
        start, end = self.parser.parse_flexible_time_expression("10 days ago")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        self.assertLess(start, end)
        
        # Test years ago
        start, end = self.parser.parse_flexible_time_expression("2 years ago")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        self.assertLess(start, end)
        
        # Test alternative phrasings
        start, end = self.parser.parse_flexible_time_expression("past 2 months")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        
        start, end = self.parser.parse_flexible_time_expression("last 4 weeks")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
    
    def test_specific_month_year_expressions(self):
        """Test parsing of specific month/year expressions."""
        
        # Test full month and year
        start, end = self.parser.parse_flexible_time_expression("January 2024")
        self.assertEqual(start.year, 2024)
        self.assertEqual(start.month, 1)
        self.assertEqual(start.day, 1)
        self.assertEqual(end.year, 2024)
        self.assertEqual(end.month, 1)
        self.assertEqual(end.day, 31)
        
        # Test abbreviated month and year
        start, end = self.parser.parse_flexible_time_expression("Mar 2025")
        self.assertEqual(start.year, 2025)
        self.assertEqual(start.month, 3)
        self.assertEqual(start.day, 1)
        self.assertEqual(end.year, 2025)
        self.assertEqual(end.month, 3)
        self.assertEqual(end.day, 31)
        
        # Test month only (should infer appropriate year)
        start, end = self.parser.parse_flexible_time_expression("August")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        self.assertEqual(start.month, 8)
        self.assertEqual(end.month, 8)
        
        # Test February (leap year handling)
        start, end = self.parser.parse_flexible_time_expression("February 2024")
        self.assertEqual(start.year, 2024)
        self.assertEqual(start.month, 2)
        self.assertEqual(start.day, 1)
        self.assertEqual(end.day, 29)  # 2024 is a leap year
    
    def test_quarter_expressions(self):
        """Test parsing of quarter expressions."""
        
        # Test Q1 with year
        start, end = self.parser.parse_flexible_time_expression("Q1 2024")
        self.assertEqual(start.year, 2024)
        self.assertEqual(start.month, 1)
        self.assertEqual(start.day, 1)
        self.assertEqual(end.year, 2024)
        self.assertEqual(end.month, 3)
        self.assertEqual(end.day, 31)
        
        # Test Q2 with year
        start, end = self.parser.parse_flexible_time_expression("Q2 2025")
        self.assertEqual(start.year, 2025)
        self.assertEqual(start.month, 4)
        self.assertEqual(start.day, 1)
        self.assertEqual(end.year, 2025)
        self.assertEqual(end.month, 6)
        self.assertEqual(end.day, 30)
        
        # Test Q3 with year
        start, end = self.parser.parse_flexible_time_expression("Q3 2024")
        self.assertEqual(start.year, 2024)
        self.assertEqual(start.month, 7)
        self.assertEqual(start.day, 1)
        self.assertEqual(end.year, 2024)
        self.assertEqual(end.month, 9)
        self.assertEqual(end.day, 30)
        
        # Test Q4 with year
        start, end = self.parser.parse_flexible_time_expression("Q4 2024")
        self.assertEqual(start.year, 2024)
        self.assertEqual(start.month, 10)
        self.assertEqual(start.day, 1)
        self.assertEqual(end.year, 2024)
        self.assertEqual(end.month, 12)
        self.assertEqual(end.day, 31)
        
        # Test quarter without year
        start, end = self.parser.parse_flexible_time_expression("Q1")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        self.assertEqual(start.month, 1)
        self.assertEqual(end.month, 3)
        
        # Test written quarter forms
        start, end = self.parser.parse_flexible_time_expression("first quarter 2025")
        self.assertEqual(start.year, 2025)
        self.assertEqual(start.month, 1)
        self.assertEqual(end.month, 3)
        
        start, end = self.parser.parse_flexible_time_expression("second quarter 2025")
        self.assertEqual(start.year, 2025)
        self.assertEqual(start.month, 4)
        self.assertEqual(end.month, 6)
    
    def test_year_expressions(self):
        """Test parsing of year expressions."""
        
        start, end = self.parser.parse_flexible_time_expression("2024")
        self.assertEqual(start.year, 2024)
        self.assertEqual(start.month, 1)
        self.assertEqual(start.day, 1)
        self.assertEqual(end.year, 2024)
        self.assertEqual(end.month, 12)
        self.assertEqual(end.day, 31)
        
        start, end = self.parser.parse_flexible_time_expression("2025")
        self.assertEqual(start.year, 2025)
        self.assertEqual(start.month, 1)
        self.assertEqual(start.day, 1)
        self.assertEqual(end.year, 2025)
        self.assertEqual(end.month, 12)
        self.assertEqual(end.day, 31)
    
    def test_date_range_expressions(self):
        """Test parsing of date range expressions."""
        
        # Test month to month with year
        start, end = self.parser.parse_flexible_time_expression("January to March 2024")
        self.assertEqual(start.year, 2024)
        self.assertEqual(start.month, 1)
        self.assertEqual(start.day, 1)
        self.assertEqual(end.year, 2024)
        self.assertEqual(end.month, 3)
        self.assertEqual(end.day, 31)
        
        # Test between format
        start, end = self.parser.parse_flexible_time_expression("between June and August 2025")
        self.assertEqual(start.year, 2025)
        self.assertEqual(start.month, 6)
        self.assertEqual(start.day, 1)
        self.assertEqual(end.year, 2025)
        self.assertEqual(end.month, 8)
        self.assertEqual(end.day, 31)
        
        # Test abbreviated months
        start, end = self.parser.parse_flexible_time_expression("Jan to Mar 2024")
        self.assertEqual(start.year, 2024)
        self.assertEqual(start.month, 1)
        self.assertEqual(end.month, 3)
        
        # Test range without year (should handle gracefully)
        start, end = self.parser.parse_flexible_time_expression("April to June")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        # Note: Without year, the parser may infer different years based on current date
    
    def test_special_cases(self):
        """Test special case expressions."""
        
        # Test yesterday
        start, end = self.parser.parse_flexible_time_expression("yesterday")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        self.assertEqual(start.date(), end.date())
        
        # Test last week
        start, end = self.parser.parse_flexible_time_expression("last week")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        self.assertLess(start, end)
        
        # Test last month
        start, end = self.parser.parse_flexible_time_expression("last month")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        self.assertLess(start, end)
        
        # Test last year
        start, end = self.parser.parse_flexible_time_expression("last year")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        self.assertLess(start, end)
    
    def test_specific_date_formats(self):
        """Test parsing of specific date formats."""
        
        # Test YYYY-MM-DD format
        start, end = self.parser.parse_flexible_time_expression("2025-06-15")
        self.assertEqual(start.year, 2025)
        self.assertEqual(start.month, 6)
        self.assertEqual(start.day, 15)
        self.assertEqual(start.date(), end.date())
        
        # Test MM/DD/YYYY format
        start, end = self.parser.parse_flexible_time_expression("06/15/2025")
        self.assertEqual(start.year, 2025)
        self.assertEqual(start.month, 6)
        self.assertEqual(start.day, 15)
        self.assertEqual(start.date(), end.date())
        
        # Test MM-DD-YYYY format
        start, end = self.parser.parse_flexible_time_expression("06-15-2025")
        self.assertEqual(start.year, 2025)
        self.assertEqual(start.month, 6)
        self.assertEqual(start.day, 15)
        self.assertEqual(start.date(), end.date())
    
    def test_data_availability_validation(self):
        """Test data availability validation."""
        
        # Test date within available range
        start_date = datetime(2025, 6, 1)
        end_date = datetime(2025, 6, 30)
        validation = self.parser.validate_date_availability(start_date, end_date)
        
        self.assertTrue(validation['valid'])
        self.assertEqual(len(validation['warnings']), 0)
        self.assertEqual(validation['adjusted_start_date'], start_date)
        self.assertEqual(validation['adjusted_end_date'], end_date)
        
        # Test date before available range
        start_date = datetime(2024, 6, 1)
        end_date = datetime(2025, 6, 30)
        validation = self.parser.validate_date_availability(start_date, end_date)
        
        self.assertTrue(validation['valid'])
        self.assertGreater(len(validation['warnings']), 0)
        self.assertEqual(validation['adjusted_start_date'], self.data_start_date)
        self.assertEqual(validation['adjusted_end_date'], end_date)
        
        # Test date after available range
        start_date = datetime(2025, 6, 1)
        end_date = datetime(2026, 6, 30)
        validation = self.parser.validate_date_availability(start_date, end_date)
        
        self.assertTrue(validation['valid'])
        self.assertGreater(len(validation['warnings']), 0)
        self.assertEqual(validation['adjusted_start_date'], start_date)
        self.assertEqual(validation['adjusted_end_date'], self.data_end_date)
        
        # Test date completely outside available range
        start_date = datetime(2026, 6, 1)
        end_date = datetime(2026, 6, 30)
        validation = self.parser.validate_date_availability(start_date, end_date)
        
        self.assertFalse(validation['valid'])
        self.assertGreater(len(validation['warnings']), 0)
        self.assertGreater(len(validation['suggestions']), 0)
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        
        # Test invalid expressions (should default to last month)
        start, end = self.parser.parse_flexible_time_expression("invalid expression")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        self.assertLess(start, end)
        
        # Test empty string
        start, end = self.parser.parse_flexible_time_expression("")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        
        # Test whitespace only
        start, end = self.parser.parse_flexible_time_expression("   ")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        
        # Test case insensitivity
        start1, end1 = self.parser.parse_flexible_time_expression("JANUARY 2024")
        start2, end2 = self.parser.parse_flexible_time_expression("january 2024")
        self.assertEqual(start1, start2)
        self.assertEqual(end1, end2)
    
    def test_complex_expressions(self):
        """Test complex time expressions that might appear in real queries."""
        
        # Test expressions with extra words
        start, end = self.parser.parse_flexible_time_expression("in the past 3 months")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        
        # Test expressions with punctuation (should handle gracefully)
        start, end = self.parser.parse_flexible_time_expression("Q1, 2024")
        self.assertIsInstance(start, datetime)
        self.assertIsInstance(end, datetime)
        
        # Test expressions with multiple time references (should pick the first valid one)
        start, end = self.parser.parse_flexible_time_expression("January 2024 and February 2025")
        self.assertEqual(start.year, 2024)
        self.assertEqual(start.month, 1)


if __name__ == '__main__':
    unittest.main()