"""
Query Processing System for the Logistics Insight System.
Implements basic QueryProcessor class using pattern matching for the six specific use cases.
Adds query type detection to route queries to appropriate analysis handlers.
Creates parameter extraction logic to identify cities, clients, warehouses, and date ranges from queries.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from enum import Enum
import calendar

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Enumeration of supported query types."""
    CITY_DELAY_ANALYSIS = "city_delay_analysis"
    CLIENT_FAILURE_ANALYSIS = "client_failure_analysis"
    WAREHOUSE_FAILURE_ANALYSIS = "warehouse_failure_analysis"
    CITY_COMPARISON = "city_comparison"
    FESTIVAL_PERIOD_ANALYSIS = "festival_period_analysis"
    CAPACITY_IMPACT_ANALYSIS = "capacity_impact_analysis"
    UNKNOWN = "unknown"


class TimeExpressionParser:
    """
    Advanced time expression parser for flexible historical analysis.
    Handles relative dates, specific months/years, quarters, and date ranges.
    """
    
    def __init__(self, data_start_date: Optional[datetime] = None, data_end_date: Optional[datetime] = None):
        """
        Initialize TimeExpressionParser with optional data availability bounds.
        
        Args:
            data_start_date: Earliest date available in the dataset
            data_end_date: Latest date available in the dataset
        """
        self.data_start_date = data_start_date or datetime(2025, 1, 1)  # Default based on sample data
        self.data_end_date = data_end_date or datetime(2025, 12, 31)    # Default based on sample data
        
        # Month name mappings
        self.months = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
        
        # Quarter mappings
        self.quarters = {
            'q1': (1, 3), 'quarter 1': (1, 3), 'first quarter': (1, 3),
            'q2': (4, 6), 'quarter 2': (4, 6), 'second quarter': (4, 6),
            'q3': (7, 9), 'quarter 3': (7, 9), 'third quarter': (7, 9),
            'q4': (10, 12), 'quarter 4': (10, 12), 'fourth quarter': (10, 12)
        }
    
    def parse_flexible_time_expression(self, time_expr: str) -> Tuple[datetime, datetime]:
        """
        Parse flexible time expressions into start and end datetime objects.
        
        Args:
            time_expr: Time expression string (e.g., "3 months ago", "January 2024", "Q1 2024")
            
        Returns:
            Tuple of (start_date, end_date)
        """
        time_expr = time_expr.strip().lower()
        
        # Handle relative time expressions
        relative_result = self._parse_relative_time(time_expr)
        if relative_result:
            return relative_result
        
        # Handle date range expressions first (more specific)
        range_result = self._parse_date_range(time_expr)
        if range_result:
            return range_result
        
        # Handle specific month/year expressions
        month_year_result = self._parse_month_year(time_expr)
        if month_year_result:
            return month_year_result
        
        # Handle quarter expressions
        quarter_result = self._parse_quarter(time_expr)
        if quarter_result:
            return quarter_result
        
        # Handle year expressions
        year_result = self._parse_year(time_expr)
        if year_result:
            return year_result
        
        # Handle specific date expressions
        date_result = self._parse_specific_date(time_expr)
        if date_result:
            return date_result
        
        # Default fallback
        logger.warning(f"Could not parse time expression '{time_expr}', defaulting to last month")
        return self._get_last_month()
    
    def _parse_relative_time(self, time_expr: str) -> Optional[Tuple[datetime, datetime]]:
        """Parse relative time expressions like '3 months ago', '6 weeks ago'."""
        
        # Pattern for relative time expressions
        patterns = [
            r'(\d+)\s+(months?|weeks?|days?|years?)\s+ago',
            r'(\d+)\s+(months?|weeks?|days?|years?)\s+back',
            r'past\s+(\d+)\s+(months?|weeks?|days?|years?)',
            r'last\s+(\d+)\s+(months?|weeks?|days?|years?)',
            r'previous\s+(\d+)\s+(months?|weeks?|days?|years?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, time_expr)
            if match:
                number = int(match.group(1))
                unit = match.group(2).rstrip('s')  # Remove plural 's'
                
                end_date = datetime.now()
                
                if unit == 'day':
                    start_date = end_date - timedelta(days=number)
                elif unit == 'week':
                    start_date = end_date - timedelta(weeks=number)
                elif unit == 'month':
                    # Approximate months as 30 days for simplicity
                    start_date = end_date - timedelta(days=number * 30)
                elif unit == 'year':
                    # More accurate year calculation
                    try:
                        start_date = end_date.replace(year=end_date.year - number)
                    except ValueError:
                        # Handle leap year edge case
                        start_date = end_date - timedelta(days=number * 365)
                else:
                    continue
                
                return start_date, end_date
        
        # Handle special cases
        if 'yesterday' in time_expr:
            yesterday = datetime.now() - timedelta(days=1)
            return yesterday.replace(hour=0, minute=0, second=0, microsecond=0), \
                   yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        if 'last week' in time_expr or 'past week' in time_expr:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            return start_date, end_date
        
        if 'last month' in time_expr or 'past month' in time_expr:
            return self._get_last_month()
        
        if 'last year' in time_expr or 'past year' in time_expr:
            current_year = datetime.now().year
            return datetime(current_year - 1, 1, 1), datetime(current_year - 1, 12, 31, 23, 59, 59)
        
        return None
    
    def _parse_month_year(self, time_expr: str) -> Optional[Tuple[datetime, datetime]]:
        """Parse month/year expressions like 'January 2024', 'March', 'Jan 2025'."""
        
        # Pattern for month and year
        month_year_pattern = r'(\w+)\s+(\d{4})'
        match = re.search(month_year_pattern, time_expr)
        
        if match:
            month_name = match.group(1).lower()
            year = int(match.group(2))
            
            if month_name in self.months:
                month = self.months[month_name]
                start_date = datetime(year, month, 1)
                
                # Get last day of the month
                last_day = calendar.monthrange(year, month)[1]
                end_date = datetime(year, month, last_day, 23, 59, 59)
                
                return start_date, end_date
        
        # Pattern for month only (assume current year or most recent occurrence)
        month_only_pattern = r'^(\w+)$'
        match = re.search(month_only_pattern, time_expr)
        
        if match:
            month_name = match.group(1).lower()
            
            if month_name in self.months:
                month = self.months[month_name]
                current_year = datetime.now().year
                current_month = datetime.now().month
                
                # If the month is in the future, assume previous year
                year = current_year if month <= current_month else current_year - 1
                
                start_date = datetime(year, month, 1)
                last_day = calendar.monthrange(year, month)[1]
                end_date = datetime(year, month, last_day, 23, 59, 59)
                
                return start_date, end_date
        
        return None
    
    def _parse_quarter(self, time_expr: str) -> Optional[Tuple[datetime, datetime]]:
        """Parse quarter expressions like 'Q1 2024', 'first quarter 2025'."""
        
        # Pattern for quarter and year
        quarter_year_patterns = [
            r'(q[1-4])\s+(\d{4})',
            r'(quarter\s+[1-4])\s+(\d{4})',
            r'(\w+\s+quarter)\s+(\d{4})'
        ]
        
        for pattern in quarter_year_patterns:
            match = re.search(pattern, time_expr)
            if match:
                quarter_str = match.group(1).lower()
                year = int(match.group(2))
                
                if quarter_str in self.quarters:
                    start_month, end_month = self.quarters[quarter_str]
                    start_date = datetime(year, start_month, 1)
                    
                    # Get last day of the end month
                    last_day = calendar.monthrange(year, end_month)[1]
                    end_date = datetime(year, end_month, last_day, 23, 59, 59)
                    
                    return start_date, end_date
        
        # Pattern for quarter only (assume current year or most recent occurrence)
        quarter_only_patterns = [r'^(q[1-4])$', r'^(quarter\s+[1-4])$', r'^(\w+\s+quarter)$']
        
        for pattern in quarter_only_patterns:
            match = re.search(pattern, time_expr)
            if match:
                quarter_str = match.group(1).lower()
                
                if quarter_str in self.quarters:
                    current_year = datetime.now().year
                    current_quarter = (datetime.now().month - 1) // 3 + 1
                    
                    # Extract quarter number
                    if 'q' in quarter_str:
                        quarter_num = int(quarter_str[1])
                    elif 'first' in quarter_str:
                        quarter_num = 1
                    elif 'second' in quarter_str:
                        quarter_num = 2
                    elif 'third' in quarter_str:
                        quarter_num = 3
                    elif 'fourth' in quarter_str:
                        quarter_num = 4
                    else:
                        quarter_num = int(re.search(r'(\d)', quarter_str).group(1))
                    
                    # If the quarter is in the future, assume previous year
                    year = current_year if quarter_num <= current_quarter else current_year - 1
                    
                    start_month, end_month = self.quarters[quarter_str]
                    start_date = datetime(year, start_month, 1)
                    
                    last_day = calendar.monthrange(year, end_month)[1]
                    end_date = datetime(year, end_month, last_day, 23, 59, 59)
                    
                    return start_date, end_date
        
        return None
    
    def _parse_year(self, time_expr: str) -> Optional[Tuple[datetime, datetime]]:
        """Parse year expressions like '2024', '2023'."""
        
        year_pattern = r'^(\d{4})$'
        match = re.search(year_pattern, time_expr)
        
        if match:
            year = int(match.group(1))
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31, 23, 59, 59)
            return start_date, end_date
        
        return None
    
    def _parse_date_range(self, time_expr: str) -> Optional[Tuple[datetime, datetime]]:
        """Parse date range expressions like 'January to March 2024', 'between June and August'."""
        
        # Pattern for month to month with year
        range_patterns = [
            r'(\w+)\s+to\s+(\w+)\s+(\d{4})',
            r'(\w+)\s+-\s+(\w+)\s+(\d{4})',
            r'between\s+(\w+)\s+and\s+(\w+)\s+(\d{4})',
            r'from\s+(\w+)\s+to\s+(\w+)\s+(\d{4})'
        ]
        
        for pattern in range_patterns:
            match = re.search(pattern, time_expr)
            if match:
                start_month_name = match.group(1).lower()
                end_month_name = match.group(2).lower()
                year = int(match.group(3))
                
                if start_month_name in self.months and end_month_name in self.months:
                    start_month = self.months[start_month_name]
                    end_month = self.months[end_month_name]
                    
                    start_date = datetime(year, start_month, 1)
                    last_day = calendar.monthrange(year, end_month)[1]
                    end_date = datetime(year, end_month, last_day, 23, 59, 59)
                    
                    return start_date, end_date
        
        # Pattern for month to month without year (assume current year)
        range_no_year_patterns = [
            r'(\w+)\s+to\s+(\w+)',
            r'(\w+)\s+-\s+(\w+)',
            r'between\s+(\w+)\s+and\s+(\w+)',
            r'from\s+(\w+)\s+to\s+(\w+)'
        ]
        
        for pattern in range_no_year_patterns:
            match = re.search(pattern, time_expr)
            if match:
                start_month_name = match.group(1).lower()
                end_month_name = match.group(2).lower()
                
                if start_month_name in self.months and end_month_name in self.months:
                    start_month = self.months[start_month_name]
                    end_month = self.months[end_month_name]
                    
                    # Determine appropriate year
                    current_year = datetime.now().year
                    current_month = datetime.now().month
                    
                    # If end month is before current month, assume current year
                    # If end month is after current month, could be current or previous year
                    year = current_year if end_month <= current_month else current_year - 1
                    
                    start_date = datetime(year, start_month, 1)
                    last_day = calendar.monthrange(year, end_month)[1]
                    end_date = datetime(year, end_month, last_day, 23, 59, 59)
                    
                    return start_date, end_date
        
        return None
    
    def _parse_specific_date(self, time_expr: str) -> Optional[Tuple[datetime, datetime]]:
        """Parse specific date expressions."""
        
        # YYYY-MM-DD format
        yyyy_mm_dd_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', time_expr)
        if yyyy_mm_dd_match:
            try:
                year, month, day = int(yyyy_mm_dd_match.group(1)), int(yyyy_mm_dd_match.group(2)), int(yyyy_mm_dd_match.group(3))
                date = datetime(year, month, day)
                return date.replace(hour=0, minute=0, second=0, microsecond=0), \
                       date.replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                pass
        
        # YYYY/MM/DD format
        yyyy_mm_dd_slash_match = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', time_expr)
        if yyyy_mm_dd_slash_match:
            try:
                year, month, day = int(yyyy_mm_dd_slash_match.group(1)), int(yyyy_mm_dd_slash_match.group(2)), int(yyyy_mm_dd_slash_match.group(3))
                date = datetime(year, month, day)
                return date.replace(hour=0, minute=0, second=0, microsecond=0), \
                       date.replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                pass
        
        # MM/DD/YYYY format (US format)
        mm_dd_yyyy_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', time_expr)
        if mm_dd_yyyy_match:
            try:
                month, day, year = int(mm_dd_yyyy_match.group(1)), int(mm_dd_yyyy_match.group(2)), int(mm_dd_yyyy_match.group(3))
                date = datetime(year, month, day)
                return date.replace(hour=0, minute=0, second=0, microsecond=0), \
                       date.replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                pass
        
        # DD/MM/YYYY format (European format) - try if MM/DD/YYYY failed
        dd_mm_yyyy_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', time_expr)
        if dd_mm_yyyy_match:
            try:
                day, month, year = int(dd_mm_yyyy_match.group(1)), int(dd_mm_yyyy_match.group(2)), int(dd_mm_yyyy_match.group(3))
                # Only try this if day > 12 (clearly not a month)
                if day > 12:
                    date = datetime(year, month, day)
                    return date.replace(hour=0, minute=0, second=0, microsecond=0), \
                           date.replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                pass
        
        # MM-DD-YYYY format
        mm_dd_yyyy_dash_match = re.search(r'(\d{1,2})-(\d{1,2})-(\d{4})', time_expr)
        if mm_dd_yyyy_dash_match:
            try:
                month, day, year = int(mm_dd_yyyy_dash_match.group(1)), int(mm_dd_yyyy_dash_match.group(2)), int(mm_dd_yyyy_dash_match.group(3))
                date = datetime(year, month, day)
                return date.replace(hour=0, minute=0, second=0, microsecond=0), \
                       date.replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                pass
        
        # DD-MM-YYYY format - try if MM-DD-YYYY failed
        dd_mm_yyyy_dash_match = re.search(r'(\d{1,2})-(\d{1,2})-(\d{4})', time_expr)
        if dd_mm_yyyy_dash_match:
            try:
                day, month, year = int(dd_mm_yyyy_dash_match.group(1)), int(dd_mm_yyyy_dash_match.group(2)), int(dd_mm_yyyy_dash_match.group(3))
                # Only try this if day > 12 (clearly not a month)
                if day > 12:
                    date = datetime(year, month, day)
                    return date.replace(hour=0, minute=0, second=0, microsecond=0), \
                           date.replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                pass
        
        return None
    
    def _get_last_month(self) -> Tuple[datetime, datetime]:
        """Get the date range for last month."""
        today = datetime.now()
        if today.month == 1:
            start_date = datetime(today.year - 1, 12, 1)
            end_date = datetime(today.year, 1, 1) - timedelta(days=1)
        else:
            start_date = datetime(today.year, today.month - 1, 1)
            end_date = datetime(today.year, today.month, 1) - timedelta(days=1)
        
        return start_date, end_date.replace(hour=23, minute=59, second=59)
    
    def validate_date_availability(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Validate if the requested date range is within available data bounds.
        
        Args:
            start_date: Requested start date
            end_date: Requested end date
            
        Returns:
            Dictionary with validation results and suggestions
        """
        validation_result = {
            'valid': True,
            'warnings': [],
            'suggestions': [],
            'adjusted_start_date': start_date,
            'adjusted_end_date': end_date,
            'data_start_date': self.data_start_date,
            'data_end_date': self.data_end_date
        }
        
        # Check if requested range is completely outside available data
        if end_date < self.data_start_date or start_date > self.data_end_date:
            validation_result['valid'] = False
            validation_result['warnings'].append(
                f"Requested date range ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}) "
                f"is outside available data range ({self.data_start_date.strftime('%Y-%m-%d')} to {self.data_end_date.strftime('%Y-%m-%d')})"
            )
            validation_result['suggestions'].append(
                f"Try a date range between {self.data_start_date.strftime('%Y-%m-%d')} and {self.data_end_date.strftime('%Y-%m-%d')}"
            )
            return validation_result
        
        # Check if start date is before available data
        if start_date < self.data_start_date:
            validation_result['warnings'].append(
                f"Requested start date ({start_date.strftime('%Y-%m-%d')}) is before available data starts ({self.data_start_date.strftime('%Y-%m-%d')})"
            )
            validation_result['adjusted_start_date'] = self.data_start_date
            validation_result['suggestions'].append(
                f"Analysis will start from {self.data_start_date.strftime('%Y-%m-%d')} instead"
            )
        
        # Check if end date is after available data
        if end_date > self.data_end_date:
            validation_result['warnings'].append(
                f"Requested end date ({end_date.strftime('%Y-%m-%d')}) is after available data ends ({self.data_end_date.strftime('%Y-%m-%d')})"
            )
            validation_result['adjusted_end_date'] = self.data_end_date
            validation_result['suggestions'].append(
                f"Analysis will end at {self.data_end_date.strftime('%Y-%m-%d')} instead"
            )
        
        return validation_result


class QueryProcessor:
    """
    Processes natural language queries and routes them to appropriate analysis handlers.
    Uses pattern matching to identify query types and extract relevant parameters.
    """
    
    def __init__(self, data_aggregator=None, data_start_date=None, data_end_date=None):
        """
        Initialize QueryProcessor with optional data aggregator for parameter validation.
        
        Args:
            data_aggregator: Optional DataAggregator instance for validating extracted parameters
            data_start_date: Earliest date available in the dataset
            data_end_date: Latest date available in the dataset
        """
        self.data_aggregator = data_aggregator
        self.time_parser = TimeExpressionParser(data_start_date, data_end_date)
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Set up regex patterns for query type detection and parameter extraction."""
        
        # City delay analysis patterns (more flexible time expressions)
        self.city_delay_patterns = [
            r"why\s+were\s+deliveries\s+delayed\s+in\s+(?:city\s+)?([a-zA-Z\s]+?)(?:\s+.+?)?(?:\?|$)",
            r"what\s+caused\s+delays\s+in\s+(?:city\s+)?([a-zA-Z\s]+?)(?:\s+.+?)?(?:\?|$)",
            r"analyze\s+delays\s+in\s+(?:city\s+)?([a-zA-Z\s]+?)(?:\s+.+?)?(?:\?|$)",
            r"delivery\s+delays?\s+in\s+(?:city\s+)?([a-zA-Z\s]+?)(?:\s+.+?)?(?:\?|$)"
        ]
        
        # Client failure analysis patterns (more specific to avoid conflicts)
        self.client_failure_patterns = [
            r"why\s+did\s+client\s+([a-zA-Z0-9\s]+?)(?:'s)?\s+orders?\s+fail(?:\s+.+?)?(?:\?|$)",
            r"what\s+caused\s+client\s+([a-zA-Z0-9\s]+?)(?:'s)?\s+(?:order\s+)?failures?(?:\s+.+?)?(?:\?|$)",
            r"analyze\s+client\s+([a-zA-Z0-9\s]+?)(?:'s)?\s+(?:order\s+)?failures?(?:\s+.+?)?(?:\?|$)",
            r"client\s+([a-zA-Z0-9\s]+?)\s+(?:order\s+)?failure\s+analysis(?:\s+.+?)?(?:\?|$)"
        ]
        
        # Warehouse failure analysis patterns (more flexible time expressions)
        self.warehouse_failure_patterns = [
            r"explain\s+(?:the\s+)?top\s+reasons?\s+for\s+delivery\s+failures?\s+linked\s+to\s+warehouse\s+([a-zA-Z0-9\s]+?)(?:\s+.+?)?(?:\?|$)",
            r"what\s+are\s+the\s+main\s+failure\s+causes?\s+for\s+warehouse\s+([a-zA-Z0-9\s]+?)(?:\s+.+?)?(?:\?|$)",
            r"analyze\s+(?:delivery\s+)?failures?\s+(?:from\s+|for\s+)?warehouse\s+([a-zA-Z0-9\s]+?)(?:\s+.+?)?(?:\?|$)",
            r"warehouse\s+([a-zA-Z0-9\s]+?)\s+failure\s+analysis(?:\s+.+?)?(?:\?|$)"
        ]
        
        # City comparison patterns (more flexible time expressions)
        self.city_comparison_patterns = [
            r"compare\s+delivery\s+failure\s+causes?\s+between\s+(?:city\s+)?([a-zA-Z\s]+?)\s+and\s+(?:city\s+)?([a-zA-Z\s]+?)(?:\s+.+?)?(?:\?|$)",
            r"what\s+are\s+the\s+differences?\s+in\s+failures?\s+between\s+(?:city\s+)?([a-zA-Z\s]+?)\s+and\s+(?:city\s+)?([a-zA-Z\s]+?)(?:\s+.+?)?(?:\?|$)",
            r"analyze\s+(?:delivery\s+)?(?:failure\s+)?differences?\s+between\s+(?:city\s+)?([a-zA-Z\s]+?)\s+(?:and\s+|vs\s+)(?:city\s+)?([a-zA-Z\s]+?)(?:\s+.+?)?(?:\?|$)",
            r"(?:city\s+)?([a-zA-Z\s]+?)\s+vs\s+(?:city\s+)?([a-zA-Z\s]+?)\s+(?:delivery\s+)?(?:failure\s+)?comparison(?:\s+.+?)?(?:\?|$)"
        ]
        
        # Festival period analysis patterns
        self.festival_period_patterns = [
            r"what\s+are\s+the\s+likely\s+causes?\s+of\s+delivery\s+failures?\s+during\s+(?:the\s+)?festival\s+period",
            r"analyze\s+(?:delivery\s+)?failures?\s+during\s+(?:the\s+)?(?:festival|holiday)\s+(?:period|season)",
            r"how\s+should\s+we\s+prepare\s+for\s+(?:the\s+)?festival\s+(?:period|season)",
            r"festival\s+(?:period|season)\s+(?:delivery\s+)?failure\s+analysis",
            r"seasonal\s+(?:delivery\s+)?(?:failure\s+)?analysis\s+(?:for\s+)?(?:festival|holiday)"
        ]
        
        # Capacity impact analysis patterns
        self.capacity_impact_patterns = [
            r"if\s+we\s+onboard\s+client\s+.+?\s+with\s+.+?\s+orders?",
            r"what\s+(?:new\s+)?failure\s+risks?\s+.+?\s+orders?",
            r"analyze\s+(?:the\s+)?impact\s+of\s+.+?\s+orders?",
            r"capacity\s+impact\s+analysis\s+.+?\s+orders?"
        ]
    
    def detect_query_type(self, query: str) -> QueryType:
        """
        Detect the type of query based on pattern matching.
        
        Args:
            query: Natural language query string
            
        Returns:
            QueryType enum value indicating the detected query type
        """
        query_lower = query.lower().strip()
        
        # Check city delay analysis patterns
        for pattern in self.city_delay_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return QueryType.CITY_DELAY_ANALYSIS
        
        # Check client failure analysis patterns
        for pattern in self.client_failure_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return QueryType.CLIENT_FAILURE_ANALYSIS
        
        # Check warehouse failure analysis patterns
        for pattern in self.warehouse_failure_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return QueryType.WAREHOUSE_FAILURE_ANALYSIS
        
        # Check city comparison patterns
        for pattern in self.city_comparison_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return QueryType.CITY_COMPARISON
        
        # Check festival period analysis patterns
        for pattern in self.festival_period_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return QueryType.FESTIVAL_PERIOD_ANALYSIS
        
        # Check capacity impact analysis patterns
        for pattern in self.capacity_impact_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return QueryType.CAPACITY_IMPACT_ANALYSIS
        
        return QueryType.UNKNOWN
    
    def extract_city_delay_parameters(self, query: str) -> Dict[str, Any]:
        """
        Extract parameters for city delay analysis queries.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary containing extracted parameters (city, date)
        """
        query_lower = query.lower().strip()
        
        # More specific patterns for city extraction (flexible time expressions)
        city_patterns = [
            r"(?:in|for)\s+(?:city\s+)?([a-zA-Z\s]+?)(?:\s+.+?|\s*\?|$)",
            r"delayed\s+in\s+([a-zA-Z\s]+?)(?:\s+.+?|\s*\?|$)",
            r"delays\s+in\s+([a-zA-Z\s]+?)(?:\s+.+?|\s*\?|$)"
        ]
        
        city = None
        date_str = None
        
        # Extract city
        for pattern in city_patterns:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                city = match.group(1).strip().title()
                break
        
        # Extract date
        date_match = re.search(r"on\s+([0-9\-/]+)", query_lower)
        if date_match:
            date_str = date_match.group(1)
        
        if city:
            # Use enhanced time parsing
            time_params = self.extract_enhanced_time_parameters(query)
            
            return {
                'city': city,
                'date': time_params['start_date'],  # For single day analysis, use start date
                'start_date': time_params['start_date'],
                'end_date': time_params['end_date'],
                'time_expression': time_params['original_time_expression'],
                'time_validation': time_params['validation'],
                'query_type': QueryType.CITY_DELAY_ANALYSIS
            }
        
        return {'error': 'Could not extract city delay parameters'}
    
    def extract_client_failure_parameters(self, query: str) -> Dict[str, Any]:
        """
        Extract parameters for client failure analysis queries.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary containing extracted parameters (client_id/name, date_range)
        """
        query_lower = query.lower().strip()
        
        # More specific patterns for client extraction
        client_patterns = [
            r"client\s+([a-zA-Z0-9\s]+?)(?:'s|\s+orders?|\s+order\s+|\s+failure|\s+fail|\s*\?|$)",
            r"(?:did|caused)\s+client\s+([a-zA-Z0-9\s]+?)(?:'s|\s+orders?|\s+order\s+|\s+failure|\s+fail|\s*\?|$)"
        ]
        
        client_identifier = None
        date_range_str = None
        
        # Extract client
        for pattern in client_patterns:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                client_identifier = match.group(1).strip()
                break
        
        # Extract date range
        date_match = re.search(r"(?:in\s+the\s+past\s+week|last\s+week|in\s+([0-9\-/\s]+))", query_lower)
        if date_match and date_match.group(1):
            date_range_str = date_match.group(1)
        
        if client_identifier:
            # Try to parse as client ID (numeric) or keep as client name
            try:
                client_id = int(client_identifier)
                client_name = None
            except ValueError:
                client_id = None
                client_name = client_identifier.title()
            
            # Use enhanced time parsing
            time_params = self.extract_enhanced_time_parameters(query)
            
            return {
                'client_id': client_id,
                'client_name': client_name,
                'start_date': time_params['start_date'],
                'end_date': time_params['end_date'],
                'time_expression': time_params['original_time_expression'],
                'time_validation': time_params['validation'],
                'query_type': QueryType.CLIENT_FAILURE_ANALYSIS
            }
        
        return {'error': 'Could not extract client failure parameters'}
    
    def extract_warehouse_failure_parameters(self, query: str) -> Dict[str, Any]:
        """
        Extract parameters for warehouse failure analysis queries.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary containing extracted parameters (warehouse_id/name, date_range)
        """
        query_lower = query.lower().strip()
        
        # More specific patterns for warehouse extraction
        warehouse_patterns = [
            r"warehouse\s+([a-zA-Z0-9\s]+?)(?:\s+in\s+|\s+failure|\s*\?|$)",
            r"(?:to|for|from)\s+warehouse\s+([a-zA-Z0-9\s]+?)(?:\s+in\s+|\s+failure|\s*\?|$)"
        ]
        
        warehouse_identifier = None
        date_range_str = None
        
        # Extract warehouse
        for pattern in warehouse_patterns:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                warehouse_identifier = match.group(1).strip()
                break
        
        # Extract date range
        date_match = re.search(r"in\s+([a-zA-Z0-9\-/\s]+?)(?:\?|$)", query_lower)
        if date_match:
            date_range_str = date_match.group(1).strip()
        
        if warehouse_identifier:
            # Try to parse as warehouse ID (numeric) or keep as warehouse name
            try:
                warehouse_id = int(warehouse_identifier)
                warehouse_name = None
            except ValueError:
                warehouse_id = None
                warehouse_name = warehouse_identifier.title()
            
            # Use enhanced time parsing
            time_params = self.extract_enhanced_time_parameters(query)
            
            return {
                'warehouse_id': warehouse_id,
                'warehouse_name': warehouse_name,
                'start_date': time_params['start_date'],
                'end_date': time_params['end_date'],
                'time_expression': time_params['original_time_expression'],
                'time_validation': time_params['validation'],
                'query_type': QueryType.WAREHOUSE_FAILURE_ANALYSIS
            }
        
        return {'error': 'Could not extract warehouse failure parameters'}
    
    def extract_city_comparison_parameters(self, query: str) -> Dict[str, Any]:
        """
        Extract parameters for city comparison queries.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary containing extracted parameters (city_a, city_b, date_range)
        """
        query_lower = query.lower().strip()
        
        for pattern in self.city_comparison_patterns:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                city_a = match.group(1).strip().title()
                city_b = match.group(2).strip().title()
                date_range_str = match.group(3) if len(match.groups()) > 2 and match.group(3) else None
                
                # Use enhanced time parsing
                time_params = self.extract_enhanced_time_parameters(query)
                
                return {
                    'city_a': city_a,
                    'city_b': city_b,
                    'start_date': time_params['start_date'],
                    'end_date': time_params['end_date'],
                    'time_expression': time_params['original_time_expression'],
                    'time_validation': time_params['validation'],
                    'query_type': QueryType.CITY_COMPARISON
                }
        
        return {'error': 'Could not extract city comparison parameters'}
    
    def extract_capacity_impact_parameters(self, query: str) -> Dict[str, Any]:
        """
        Extract parameters for capacity impact analysis queries.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary containing extracted parameters (client_name, order_volume)
        """
        query_lower = query.lower().strip()
        
        # Extract client name
        client_match = re.search(r"client\s+([a-zA-Z0-9\s]+?)(?:\s+with|\s*\?|$)", query_lower)
        client_name = None
        if client_match:
            client_name = client_match.group(1).strip().title()
        
        # Extract order volume
        volume_match = re.search(r"(?:~|approximately\s+|about\s+)?([0-9,]+)\s+(?:extra\s+|additional\s+|new\s+)?(?:monthly\s+)?orders?", query_lower)
        order_volume = None
        if volume_match:
            order_volume = int(volume_match.group(1).replace(',', ''))
        
        if order_volume:
            return {
                'client_name': client_name,
                'order_volume': order_volume,
                'query_type': QueryType.CAPACITY_IMPACT_ANALYSIS
            }
        
        return {'error': 'Could not extract capacity impact parameters'}
    
    def extract_parameters(self, query: str, query_type: QueryType) -> Dict[str, Any]:
        """
        Extract parameters from query based on detected query type.
        
        Args:
            query: Natural language query string
            query_type: Detected query type
            
        Returns:
            Dictionary containing extracted parameters specific to query type
        """
        if query_type == QueryType.CITY_DELAY_ANALYSIS:
            return self.extract_city_delay_parameters(query)
        elif query_type == QueryType.CLIENT_FAILURE_ANALYSIS:
            return self.extract_client_failure_parameters(query)
        elif query_type == QueryType.WAREHOUSE_FAILURE_ANALYSIS:
            return self.extract_warehouse_failure_parameters(query)
        elif query_type == QueryType.CITY_COMPARISON:
            return self.extract_city_comparison_parameters(query)
        elif query_type == QueryType.FESTIVAL_PERIOD_ANALYSIS:
            return {'query_type': QueryType.FESTIVAL_PERIOD_ANALYSIS}
        elif query_type == QueryType.CAPACITY_IMPACT_ANALYSIS:
            return self.extract_capacity_impact_parameters(query)
        else:
            return {'error': f'Unknown query type: {query_type}'}
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query and extract all relevant information.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary containing query type and extracted parameters
        """
        # Detect query type
        query_type = self.detect_query_type(query)
        
        if query_type == QueryType.UNKNOWN:
            return {
                'query_type': QueryType.UNKNOWN,
                'error': 'Could not identify query type. Please rephrase your question.',
                'supported_queries': [
                    'Why were deliveries delayed in [city] yesterday?',
                    'Why did Client [X]\'s orders fail in the past week?',
                    'Explain top reasons for delivery failures linked to Warehouse [B] in [month]?',
                    'Compare delivery failure causes between City [A] and City [B] last month?',
                    'What are the likely causes of delivery failures during the festival period?',
                    'If we onboard Client [Y] with ~[X] extra monthly orders, what new failure risks should we expect?'
                ]
            }
        
        # Extract parameters based on query type
        parameters = self.extract_parameters(query, query_type)
        
        # Add original query for reference
        parameters['original_query'] = query
        
        return parameters
    
    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse various date string formats into datetime object.
        Uses the enhanced TimeExpressionParser for better flexibility.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Parsed datetime object, defaults to yesterday if parsing fails
        """
        try:
            start_date, end_date = self.time_parser.parse_flexible_time_expression(date_str)
            return start_date
        except Exception as e:
            logger.warning(f"Could not parse date '{date_str}' using enhanced parser: {e}, defaulting to yesterday")
            return datetime.now() - timedelta(days=1)
    
    def _parse_date_range(self, date_range_str: str) -> Tuple[datetime, datetime]:
        """
        Parse date range string into start and end datetime objects.
        Uses the enhanced TimeExpressionParser for better flexibility.
        
        Args:
            date_range_str: Date range string (e.g., "August", "last month", "2023-08-01 to 2023-08-31")
            
        Returns:
            Tuple of (start_date, end_date)
        """
        try:
            return self.time_parser.parse_flexible_time_expression(date_range_str)
        except Exception as e:
            logger.warning(f"Could not parse date range '{date_range_str}' using enhanced parser: {e}, defaulting to last month")
            return self.time_parser._get_last_month()
    
    def parse_flexible_time_expressions(self, time_expr: str) -> Tuple[datetime, datetime]:
        """
        Parse flexible time expressions using the enhanced TimeExpressionParser.
        
        Args:
            time_expr: Time expression string
            
        Returns:
            Tuple of (start_date, end_date)
        """
        return self.time_parser.parse_flexible_time_expression(time_expr)
    
    def validate_date_availability(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Validate if the requested date range is within available data bounds.
        
        Args:
            start_date: Requested start date
            end_date: Requested end date
            
        Returns:
            Dictionary with validation results and suggestions
        """
        return self.time_parser.validate_date_availability(start_date, end_date)
    
    def extract_enhanced_time_parameters(self, query: str) -> Dict[str, Any]:
        """
        Extract time parameters from query using enhanced flexible parsing.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary containing extracted time parameters and validation results
        """
        query_lower = query.lower().strip()
        
        # Enhanced time expression patterns (ordered by specificity)
        time_patterns = [
            # Date range expressions (most specific first)
            r'((?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\s+to\s+(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)(?:\s+\d{4})?)',
            r'(between\s+(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\s+and\s+(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)(?:\s+\d{4})?)',
            r'(from\s+(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\s+to\s+(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)(?:\s+\d{4})?)',
            
            # Relative time expressions
            r'(\d+\s+(?:months?|weeks?|days?|years?)\s+ago)',
            r'(past\s+\d+\s+(?:months?|weeks?|days?|years?))',
            r'(last\s+\d+\s+(?:months?|weeks?|days?|years?))',
            r'(previous\s+\d+\s+(?:months?|weeks?|days?|years?))',
            
            # Quarter expressions
            r'(q[1-4]\s+\d{4})',
            r'(quarter\s+[1-4]\s+\d{4})',
            r'((?:first|second|third|fourth)\s+quarter\s+\d{4})',
            r'(q[1-4])',
            r'(quarter\s+[1-4])',
            r'((?:first|second|third|fourth)\s+quarter)',
            
            # Specific month/year expressions
            r'((?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\s+\d{4})',
            
            # Specific date formats
            r'(\d{4}-\d{1,2}-\d{1,2})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{1,2}-\d{1,2}-\d{4})',
            
            # Year expressions (less specific)
            r'(\d{4})',
            
            # Month only (less specific)
            r'((?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec))',
            
            # Special cases
            r'(yesterday)',
            r'(last\s+week)',
            r'(past\s+week)',
            r'(last\s+month)',
            r'(past\s+month)',
            r'(last\s+year)',
            r'(past\s+year)',
        ]
        
        extracted_time_expr = None
        
        # Find the first matching time expression
        for pattern in time_patterns:
            match = re.search(pattern, query_lower)
            if match:
                extracted_time_expr = match.group(1).strip()
                break
        
        if not extracted_time_expr:
            # Default to "last month" if no time expression found
            extracted_time_expr = "last month"
        
        # Parse the time expression
        start_date, end_date = self.parse_flexible_time_expressions(extracted_time_expr)
        
        # Validate date availability
        validation_result = self.validate_date_availability(start_date, end_date)
        
        return {
            'original_time_expression': extracted_time_expr,
            'start_date': validation_result['adjusted_start_date'],
            'end_date': validation_result['adjusted_end_date'],
            'validation': validation_result
        }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted parameters against available data (if data_aggregator is available).
        
        Args:
            parameters: Dictionary of extracted parameters
            
        Returns:
            Dictionary with validation results and suggestions
        """
        if not self.data_aggregator:
            return parameters
        
        validation_results = {'valid': True, 'warnings': [], 'suggestions': []}
        
        # Validate city names
        if 'city' in parameters:
            # This would require access to available cities in the dataset
            # For now, just add to parameters
            pass
        
        if 'city_a' in parameters and 'city_b' in parameters:
            # This would require access to available cities in the dataset
            # For now, just add to parameters
            pass
        
        # Validate client information
        if 'client_id' in parameters or 'client_name' in parameters:
            # This would require access to available clients in the dataset
            # For now, just add to parameters
            pass
        
        # Validate warehouse information
        if 'warehouse_id' in parameters or 'warehouse_name' in parameters:
            # This would require access to available warehouses in the dataset
            # For now, just add to parameters
            pass
        
        parameters['validation'] = validation_results
        return parameters