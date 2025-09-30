# Logistics Insight System - Query Usage Guide

This document provides comprehensive examples of all query types supported by the Logistics Insight System, specifically demonstrating the six use case handlers implemented in Task 3.2.

## Quick Start

Run all sample queries:
```bash
python3 sample_queries.py
```

Run specific query types:
```bash
python3 sample_queries.py city        # City delay analysis
python3 sample_queries.py client      # Client failure analysis  
python3 sample_queries.py warehouse   # Warehouse failure analysis
python3 sample_queries.py comparison  # City comparison analysis
python3 sample_queries.py festival    # Festival period analysis
python3 sample_queries.py capacity    # Capacity impact analysis
```

## Supported Query Types

### 1. City Delay Analysis Queries
**Handler:** `generate_city_delay_analysis()`  
**Purpose:** Analyze delivery delays for a specific city on a specific date

**Sample Queries:**
- "Why were deliveries delayed in New Delhi on September 10, 2025?"
- "What caused delivery delays in Mumbai yesterday?"
- "Analyze delivery performance issues for Chennai on a specific day"

**Output Includes:**
- Total orders and success rates
- Traffic and weather impact analysis
- Warehouse performance issues
- Specific failure reasons
- Actionable recommendations for route optimization

### 2. Client Failure Analysis Queries
**Handler:** `generate_client_failure_analysis()`  
**Purpose:** Analyze order failures for a specific client over a time period

**Sample Queries:**
- "Why did Client 409's orders fail in the past week?"
- "What are the failure patterns for Client Saini LLC in August?"
- "Analyze order failures for Client Deol Inc over the past month"

**Output Includes:**
- Client order volume and success rates
- Primary failure reasons and distributions
- Delivery location performance analysis
- Payment mode success rates
- Customer satisfaction insights
- Urgent action recommendations

### 3. Warehouse Failure Analysis Queries
**Handler:** `generate_warehouse_failure_analysis()`  
**Purpose:** Analyze delivery failures linked to specific warehouses

**Sample Queries:**
- "Explain top reasons for delivery failures linked to Warehouse B in August?"
- "What are the main failure causes for Warehouse 5 operations?"
- "Analyze delivery failures originating from Central Warehouse in Q3"

**Output Includes:**
- Warehouse processing volume and success rates
- Picking and dispatch performance metrics
- Primary failure causes (stockout, damage, delays)
- Challenging delivery destinations
- High-volume client analysis
- Operational improvement recommendations

### 4. City Comparison Analysis Queries
**Handler:** `generate_city_comparison()`  
**Purpose:** Compare delivery performance between two cities

**Sample Queries:**
- "Compare delivery failure causes between Delhi and Mumbai last month?"
- "How does delivery performance in Bangalore compare to Chennai?"
- "Analyze delivery success rates: Pune vs Hyderabad in Q3"

**Output Includes:**
- Comparative performance metrics
- Common vs unique failure patterns
- Traffic and weather impact differences
- Delivery time comparisons
- Warehouse performance differences
- Best practice sharing recommendations

### 5. Festival Period Analysis Queries
**Handler:** `generate_festival_period_analysis()`  
**Purpose:** Assess delivery risks during seasonal/festival periods

**Sample Queries:**
- "What are the delivery risks during Diwali festival period?"
- "Analyze delivery performance during Independence Day weekend"
- "What capacity planning is needed for New Year period?"

**Output Includes:**
- Volume surge analysis (vs normal periods)
- Performance impact assessment
- Festival-specific failure patterns
- High-volume city identification
- Capacity scaling recommendations
- Contingency planning suggestions

### 6. Capacity Impact Analysis Queries
**Handler:** `generate_capacity_impact_analysis()`  
**Purpose:** Analyze system capacity impact for new client onboarding

**Sample Queries:**
- "What is the capacity impact of onboarding Client X with 500 additional monthly orders?"
- "How will adding Client Y with 1000 monthly orders affect our operations?"
- "Analyze system capacity for high-volume client onboarding scenario"

**Output Includes:**
- Current vs projected capacity utilization
- Risk assessment based on volume increase
- Predicted failure scenarios
- Warehouse and fleet capacity analysis
- Infrastructure scaling recommendations
- Cost-benefit considerations

## Sample Output Format

All queries return structured insights in the following format:

```
# [Analysis Title]

## Key Metrics
- Metric 1: Value
- Metric 2: Value
- ...

## Key Insights
1. Primary insight with supporting data
2. Secondary insight with context
3. Pattern identification and correlation
...

## Actionable Recommendations
1. Specific operational recommendation
2. Strategic improvement suggestion
3. Risk mitigation strategy
...
```

## Data Requirements

The system requires the following CSV data sources:
- `orders.csv` - Order information with dates, status, locations
- `clients.csv` - Client master data
- `warehouses.csv` - Warehouse information
- `fleet_logs.csv` - Delivery tracking data
- `external_factors.csv` - Traffic, weather conditions
- `feedback.csv` - Customer feedback data
- `warehouse_logs.csv` - Warehouse operation logs
- `drivers.csv` - Driver information

## Technical Implementation

Each query type is handled by a specific method in the `InsightGenerator` class:

1. **Data Aggregation**: Uses `DataAggregator` to merge relevant data sources
2. **Pattern Analysis**: Uses `CorrelationEngine` to identify relationships and patterns
3. **Insight Generation**: Transforms statistical analysis into human-readable narratives
4. **Recommendation Engine**: Provides actionable business recommendations

## Error Handling

The system gracefully handles:
- Missing data for specified time periods
- Non-existent clients, warehouses, or cities
- Incomplete data records
- Date ranges outside available data

## Performance Considerations

- Data is cached after initial load for faster subsequent queries
- Complex aggregations are optimized using pandas operations
- Memory usage is managed through selective data loading
- Response times are typically under 2-3 seconds for most queries

## Integration Examples

```python
from insight_generator import InsightGenerator
from data_aggregator import DataAggregator
from correlation_engine import CorrelationEngine
from data_loader import DataLoader

# Initialize system
data_loader = DataLoader()
data_aggregator = DataAggregator(data_loader)
correlation_engine = CorrelationEngine(data_aggregator)
insight_generator = InsightGenerator(data_aggregator, correlation_engine)

# Run specific analysis
result = insight_generator.generate_city_delay_analysis('Mumbai', datetime(2025, 9, 10))
print(result)
```

This query system transforms raw logistics data into actionable business intelligence that operations managers can immediately understand and act upon.