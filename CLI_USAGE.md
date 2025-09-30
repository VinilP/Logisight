# Logistics Insight System - Command-Line Interface Usage Guide

This document provides comprehensive usage instructions for the main command-line interface of the Logistics Insight System.

## Quick Start

The main entry point is `main.py` which provides multiple modes of operation:

```bash
# Show help
python3 main.py --help

# Validate system
python3 main.py --validate

# Run interactive mode
python3 main.py --interactive

# Run demonstration
python3 main.py --demo

# Process single query
python3 main.py --query "Why were deliveries delayed in Mumbai yesterday?"
```

## Command-Line Options

### Basic Options

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | `-h` | Show help message and exit |
| `--interactive` | `-i` | Start interactive query mode |
| `--demo` | `-d` | Run demonstration with all sample use cases |
| `--query TEXT` | `-q` | Process a single query and exit |
| `--stats` | `-s` | Show system statistics |
| `--validate` | | Validate system components and exit |

## Usage Modes

### 1. Interactive Mode (`--interactive`)

Interactive mode allows you to ask questions in a conversational interface:

```bash
python3 main.py --interactive
```

**Features:**
- Real-time query processing
- Executive summaries with option to see full responses
- Built-in help and statistics commands
- Query history tracking
- Graceful error handling

**Interactive Commands:**
- `help` - Show query examples and usage
- `stats` - Display query processing statistics  
- `quit` - Exit the application

**Example Session:**
```
🔍 Your question: Why were deliveries delayed in Mumbai yesterday?
⏳ Processing your query...
⏱️ Processed in 0.002 seconds

📋 Executive Summary:
[Executive summary content]

📄 Show full detailed response? (y/n): y
[Full detailed response]
```

### 2. Demo Mode (`--demo`)

Demo mode showcases all six supported use cases with sample queries:

```bash
python3 main.py --demo
```

**Features:**
- Demonstrates all 6 query types
- Shows processing times and success rates
- Provides executive summaries and response previews
- Interactive pacing (press Enter between queries)
- Comprehensive demo summary

**Use Cases Demonstrated:**
1. City Delay Analysis
2. Client Failure Analysis
3. Warehouse Failure Analysis
4. City Comparison
5. Festival Period Analysis
6. Capacity Impact Analysis

### 3. Single Query Mode (`--query`)

Process a single query and display results:

```bash
python3 main.py --query "Compare delivery failure causes between Delhi and Mumbai last month?"
```

**Features:**
- One-time query processing
- Full response display
- Executive summary included
- Processing time reporting
- Error handling with suggestions

### 4. Validation Mode (`--validate`)

Check system components and data availability:

```bash
python3 main.py --validate
```

**Features:**
- Component status checking
- Data source validation
- Issue identification
- Overall system readiness assessment
- Query processing statistics

### 5. Statistics Mode (`--stats`)

Display query processing statistics:

```bash
python3 main.py --stats
```

**Features:**
- Total queries processed
- Success rates
- Query type distribution
- Recent query history

## Supported Query Types

### 1. City Delay Analysis
**Purpose:** Analyze delivery delays in a specific city for a given date

**Examples:**
- "Why were deliveries delayed in Mumbai yesterday?"
- "What caused delivery delays in Delhi on September 15?"
- "Analyze delivery performance issues for Chennai last Tuesday"

### 2. Client Failure Analysis
**Purpose:** Examine order failure patterns for a specific client over time

**Examples:**
- "Why did Client Mann Group's orders fail in the past week?"
- "What are the failure patterns for Client Kale PLC in August?"
- "Analyze order failures for Client 123 over the past month"

### 3. Warehouse Failure Analysis
**Purpose:** Analyze warehouse-related delivery failures and operational issues

**Examples:**
- "Explain top reasons for delivery failures linked to Warehouse B in August?"
- "What are the main failure causes for Central Warehouse operations?"
- "Analyze delivery failures originating from Warehouse 5 in Q3"

### 4. City Comparison
**Purpose:** Compare delivery performance and failure patterns between cities

**Examples:**
- "Compare delivery failure causes between Delhi and Mumbai last month?"
- "How does delivery performance in Bangalore compare to Chennai?"
- "Analyze delivery success rates: Pune vs Hyderabad in Q3"

### 5. Festival Period Analysis
**Purpose:** Analyze seasonal delivery risks and preparation strategies

**Examples:**
- "What are the likely causes of delivery failures during the festival period?"
- "Analyze delivery performance during Diwali season"
- "What capacity planning is needed for New Year period?"

### 6. Capacity Impact Analysis
**Purpose:** Evaluate capacity impact and risks from onboarding high-volume clients

**Examples:**
- "If we onboard Client XYZ with 20,000 extra monthly orders, what new failure risks should we expect?"
- "What is the capacity impact of adding 5,000 monthly orders?"
- "Analyze system capacity for high-volume client onboarding"

## System Requirements

### Data Files
The system requires CSV files in the `sample-data-set` directory:
- `orders.csv` - Order information with dates, status, locations
- `clients.csv` - Client master data
- `warehouses.csv` - Warehouse information
- `drivers.csv` - Driver information
- `fleet_logs.csv` - Delivery tracking data
- `external_factors.csv` - Traffic, weather conditions
- `feedback.csv` - Customer feedback data
- `warehouse_logs.csv` - Warehouse operation logs

### Python Dependencies
- Python 3.7+
- pandas
- datetime
- logging
- argparse

## Output Format

### Executive Summary
Concise overview with:
- Key performance indicators
- Business impact assessment
- Immediate actions required
- Resource requirements

### Full Response
Comprehensive analysis with:
- Formatted header and context
- Detailed analysis results
- Strategic recommendations with priorities
- Actionable next steps

### Error Handling
- Clear error messages
- Suggested query formats
- System status information
- Graceful degradation

## Performance Characteristics

- **Initialization Time:** 1-3 seconds (data loading)
- **Query Processing:** 0.1-0.5 seconds per query
- **Memory Usage:** ~100-200MB (cached data)
- **Concurrent Queries:** Single-threaded processing

## Troubleshooting

### Common Issues

1. **"System not ready" error**
   - Run `python3 main.py --validate` to check components
   - Ensure all CSV files are present in `sample-data-set/`
   - Check file permissions and data format

2. **"Query not recognized" error**
   - Use `help` command in interactive mode for examples
   - Check supported query formats in this guide
   - Ensure query follows expected patterns

3. **"No data found" responses**
   - Check if requested entities (cities, clients, warehouses) exist in data
   - Verify date ranges are within available data period
   - Use different time periods or entities

### Debug Mode
For detailed logging, set environment variable:
```bash
export PYTHONPATH=./src
python3 -c "import logging; logging.basicConfig(level=logging.DEBUG)"
python3 main.py --validate
```

## Integration Examples

### Batch Processing
```bash
# Process multiple queries
python3 main.py --query "Query 1" > results1.txt
python3 main.py --query "Query 2" > results2.txt
```

### Scripted Usage
```python
import subprocess
import json

def process_query(query):
    result = subprocess.run([
        'python3', 'main.py', '--query', query
    ], capture_output=True, text=True)
    return result.stdout

# Use in scripts
response = process_query("Why were deliveries delayed in Mumbai yesterday?")
print(response)
```

## Advanced Features

### Query History
- Automatic tracking of processed queries
- Success/failure statistics
- Performance metrics
- Recent query display

### System Monitoring
- Component health checking
- Data availability validation
- Performance monitoring
- Error tracking

### Extensibility
- Modular architecture for adding new query types
- Configurable response templates
- Pluggable analysis engines
- Custom recommendation rules

## Best Practices

1. **Start with validation** - Always run `--validate` first
2. **Use demo mode** - Familiarize yourself with capabilities
3. **Interactive exploration** - Use interactive mode for exploration
4. **Specific queries** - Be specific with cities, dates, and entities
5. **Check data availability** - Verify entities exist in your dataset

This CLI provides a comprehensive interface for analyzing logistics data and generating actionable insights for operational improvements.