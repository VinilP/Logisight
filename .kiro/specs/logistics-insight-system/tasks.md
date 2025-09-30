# Implementation Plan

- [x] 1. Set up project structure and data loading foundation
  - Create main project directory structure with folders for data, src, docs, and tests
  - Implement DataLoader class to read all 8 CSV files from sample-data-set folder
  - Add data validation and error handling for missing files or malformed data
  - Create unit tests for data loading functionality
  - _Requirements: 6.3, 8.1, 8.3_

- [x] 2. Implement core data aggregation and correlation engine
  - [x] 2.1 Create data aggregation utilities
    - Write functions to merge related data across different CSV sources using pandas
    - Implement order-centric data aggregation combining orders with clients, fleet_logs, warehouse_logs, external_factors, and feedback
    - Add date parsing and handling for various datetime columns
    - _Requirements: 1.2, 2.1, 2.2_

  - [x] 2.2 Build correlation engine for event linking
    - Implement correlation logic to link orders with fleet activities using order_id
    - Create correlation functions to connect orders with warehouse activities and external factors
    - Add correlation between delivery locations (city/state) and driver locations
    - Write correlation logic to identify patterns by client, city, warehouse, and time periods
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 3. Develop insight generation engine
  - [x] 3.1 Create base insight generation framework
    - Implement InsightGenerator class with methods for each use case type
    - Create narrative text generation utilities for human-readable explanations
    - Add statistical analysis functions for calculating success rates, delay patterns, and failure distributions
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 3.2 Implement specific use case handlers
    - Write city delay analysis handler for "Why were deliveries delayed in city X yesterday?" queries
    - Implement client failure analysis for "Why did Client X's orders fail in the past week?" queries
    - Create warehouse failure analysis for "Explain top reasons for delivery failures linked to Warehouse B in August?" queries
    - Build city comparison analysis for "Compare delivery failure causes between City A and City B last month?" queries
    - Implement festival period analysis for seasonal delivery risk assessment
    - Create capacity impact analysis for new client onboarding scenarios
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 4. Build natural language query interface
  - [x] 4.1 Create query processing system (with optional LLM enhancement)
    - Implement basic QueryProcessor class using pattern matching for the six specific use cases
    - Add query type detection to route queries to appropriate analysis handlers
    - Create parameter extraction logic to identify cities, clients, warehouses, and date ranges from queries
    - OPTIONAL: Integrate LLM (OpenAI API with key OR local Ollama) for flexible natural language understanding
    - OPTIONAL: Add LLM-powered query intent classification for handling variations in phrasing
    - _Requirements: 7.1, 7.2_

  - [x] 4.2 Enhance time-based query parsing for flexible historical analysis
    - Implement flexible time expression parser to handle relative dates like "3 months ago", "6 weeks ago"
    - Add support for specific month/year queries like "January 2024", "March", "Q1 2024"
    - Create date range parsing for expressions like "January to March 2024", "between June and August"
    - Implement data availability validation to inform users when requested periods exceed available data
    - Add comprehensive time expression testing with various formats and edge cases
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

  - [x] 4.3 Implement response generation (with optional LLM enhancement)
    - Create sophisticated template-based ResponseGenerator class with business context
    - Add recommendation generation based on identified failure patterns using rule-based logic
    - Implement actionable suggestion logic for operational improvements
    - OPTIONAL: Integrate LLM (API-based or local) for more sophisticated, context-aware narrative generation
    - OPTIONAL: Use LLM to generate more nuanced business recommendations based on data insights
    - _Requirements: 3.4, 4.1, 4.2, 4.3, 4.4_

- [x] 5. Create command-line interface and demo program
  - Implement main program entry point with command-line interface
  - Add interactive query input system for demonstration purposes
  - Create sample query execution with all six specified use cases
  - Add program help and usage instructions
  - _Requirements: 6.1, 6.2, 6.4, 8.2_

- [x] 6. Implement comprehensive testing suite
  - [x] 6.1 Create unit tests for core components
    - Write tests for DataLoader class with sample CSV files
    - Create tests for correlation engine with known data relationships
    - Implement tests for insight generation with expected narrative outputs
    - _Requirements: 8.4_

  - [x] 6.2 Build integration tests for end-to-end workflows
    - Create integration tests for complete query processing workflows
    - Test all six sample use cases with expected output validation
    - Add performance tests to ensure reasonable response times for demo scenarios
    - _Requirements: 6.2, 6.4_

- [x] 7. Create documentation and demo materials
  - [x] 7.1 Write professional documentation
    - Create Word document explaining business challenge, solution approach, and use cases
    - Design and include architecture diagram showing data flow from CSV sources to insights
    - Document system capabilities and limitations
    - _Requirements: 7.1, 7.2_

  - [x] 7.2 Prepare demo and delivery materials
    - Create demo script for screen recording with voice walkthrough
    - Prepare sample queries and expected outputs for demonstration
    - Write README.md with setup instructions and usage examples
    - Create GitHub repository structure with organized code and documentation
    - _Requirements: 7.3, 7.4_

- [x] 8. Configure optional LLM integration and finalize deliverables
  - [x] 8.1 Set up optional LLM integration (multiple approaches)
    - OPTION A: Add configuration for OpenAI API (requires API key, ~$5 budget should be sufficient for demo)
    - OPTION B: Integrate local LLM using Ollama (no API key needed, runs locally)
    - OPTION C: Skip LLM integration and use advanced rule-based approach with templates
    - Create environment variable setup for API credentials (if using cloud APIs)
    - Implement graceful fallback to basic functionality when LLM is not available
    - Add usage monitoring and cost estimation for API-based approaches
    - _Requirements: 8.2_

  - [x] 8.2 Package and finalize deliverables
    - Organize final project structure with all code, documentation, and demo materials
    - Create professional email template for client delivery
    - Document both basic and LLM-enhanced modes in README
    - Validate all deliverables work together as a complete solution (with and without LLM)
    - Test final package on clean environment to ensure reproducibility
    - _Requirements: 7.4, 8.2, 8.3, 8.4_