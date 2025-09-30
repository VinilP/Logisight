# Logistics Insight System - Architecture Diagrams

## High-Level System Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI[Command Line Interface]
        NLI[Natural Language Interface]
        DEMO[Demo Interface]
    end
    
    subgraph "Processing Layer"
        QP[Query Processor]
        IG[Insight Generator]
        RG[Response Generator]
    end
    
    subgraph "Analytics Layer"
        DA[Data Aggregator]
        CE[Correlation Engine]
    end
    
    subgraph "Data Layer"
        DL[Data Loader]
        DV[Data Validation]
        CSV[CSV Data Sources]
    end
    
    CLI --> QP
    NLI --> QP
    DEMO --> QP
    
    QP --> IG
    IG --> RG
    RG --> CLI
    RG --> NLI
    RG --> DEMO
    
    QP --> DA
    IG --> CE
    CE --> DA
    
    DA --> DL
    CE --> DL
    DL --> DV
    DV --> CSV
```

## Data Flow Architecture

```mermaid
graph LR
    subgraph "Data Sources"
        O[orders.csv]
        C[clients.csv]
        D[drivers.csv]
        W[warehouses.csv]
        F[fleet_logs.csv]
        E[external_factors.csv]
        FB[feedback.csv]
        WL[warehouse_logs.csv]
    end
    
    subgraph "Data Processing"
        DL[Data Loader<br/>• Validation<br/>• Error Handling<br/>• Type Checking]
        DA[Data Aggregator<br/>• Order-centric<br/>• Multi-domain<br/>• Time-based]
        CE[Correlation Engine<br/>• Event Linking<br/>• Pattern ID<br/>• Root Cause]
    end
    
    subgraph "Insight Generation"
        IG[Insight Generator<br/>• Use Cases<br/>• Explanations<br/>• Recommendations]
        RG[Response Generator<br/>• Narrative<br/>• Action Items<br/>• Formatting]
    end
    
    O --> DL
    C --> DL
    D --> DL
    W --> DL
    F --> DL
    E --> DL
    FB --> DL
    WL --> DL
    
    DL --> DA
    DA --> CE
    CE --> IG
    IG --> RG
    
    RG --> USER[Human-Readable<br/>Response]
```

## Component Interaction Diagram

```mermaid
sequenceDiagram
    participant User
    participant CLI as Command Line Interface
    participant QP as Query Processor
    participant DA as Data Aggregator
    participant CE as Correlation Engine
    participant IG as Insight Generator
    participant RG as Response Generator
    
    User->>CLI: "Why were deliveries delayed in Mumbai yesterday?"
    CLI->>QP: Process natural language query
    QP->>QP: Extract parameters (city=Mumbai, date=yesterday)
    QP->>DA: Request city-specific data
    DA->>DA: Aggregate orders, fleet, warehouse, external data
    QP->>CE: Correlate events for Mumbai deliveries
    CE->>CE: Link orders with delays, weather, traffic
    QP->>IG: Generate city delay analysis
    IG->>IG: Create narrative explanation
    IG->>RG: Format response with recommendations
    RG->>CLI: Return formatted insight
    CLI->>User: Display human-readable analysis
```

## Data Model Relationships

```mermaid
erDiagram
    ORDERS ||--o{ FLEET_LOGS : "order_id"
    ORDERS ||--o{ WAREHOUSE_LOGS : "order_id"
    ORDERS ||--o{ EXTERNAL_FACTORS : "order_id"
    ORDERS ||--o{ FEEDBACK : "order_id"
    ORDERS }o--|| CLIENTS : "client_id"
    
    FLEET_LOGS }o--|| DRIVERS : "driver_id"
    WAREHOUSE_LOGS }o--|| WAREHOUSES : "warehouse_id"
    
    ORDERS {
        int order_id PK
        int client_id FK
        string customer_name
        string city
        string state
        datetime order_date
        datetime promised_delivery_date
        datetime actual_delivery_date
        string status
        string failure_reason
    }
    
    CLIENTS {
        int client_id PK
        string client_name
        string city
        string state
    }
    
    DRIVERS {
        int driver_id PK
        string driver_name
        string city
        string state
        string status
    }
    
    WAREHOUSES {
        int warehouse_id PK
        string warehouse_name
        string city
        string state
        int capacity
    }
    
    FLEET_LOGS {
        int fleet_log_id PK
        int order_id FK
        int driver_id FK
        string gps_delay_notes
        datetime departure_time
        datetime arrival_time
    }
    
    WAREHOUSE_LOGS {
        int log_id PK
        int order_id FK
        int warehouse_id FK
        datetime picking_start
        datetime picking_end
        datetime dispatch_time
    }
    
    EXTERNAL_FACTORS {
        int factor_id PK
        int order_id FK
        string traffic_condition
        string weather_condition
        string event_type
    }
    
    FEEDBACK {
        int feedback_id PK
        int order_id FK
        string feedback_text
        string sentiment
        int rating
    }
```

## Use Case Processing Flow

```mermaid
flowchart TD
    START([User Query]) --> PARSE[Parse Query Type]
    
    PARSE --> CITY{City Delay<br/>Analysis?}
    PARSE --> CLIENT{Client Failure<br/>Analysis?}
    PARSE --> WAREHOUSE{Warehouse<br/>Analysis?}
    PARSE --> COMPARE{City<br/>Comparison?}
    PARSE --> FESTIVAL{Festival<br/>Analysis?}
    PARSE --> CAPACITY{Capacity<br/>Planning?}
    
    CITY --> CITY_DATA[Aggregate City Data<br/>• Orders by city<br/>• Weather/Traffic<br/>• Warehouse performance]
    CLIENT --> CLIENT_DATA[Aggregate Client Data<br/>• Client orders<br/>• Failure patterns<br/>• Delivery locations]
    WAREHOUSE --> WH_DATA[Aggregate Warehouse Data<br/>• Warehouse logs<br/>• Picking performance<br/>• Dispatch times]
    COMPARE --> COMP_DATA[Aggregate Comparison Data<br/>• Multi-city analysis<br/>• Performance metrics<br/>• Factor differences]
    FESTIVAL --> FEST_DATA[Aggregate Seasonal Data<br/>• Time-based patterns<br/>• Volume analysis<br/>• External events]
    CAPACITY --> CAP_DATA[Aggregate Capacity Data<br/>• Volume projections<br/>• Resource analysis<br/>• Risk assessment]
    
    CITY_DATA --> CORRELATE[Correlate Events]
    CLIENT_DATA --> CORRELATE
    WH_DATA --> CORRELATE
    COMP_DATA --> CORRELATE
    FEST_DATA --> CORRELATE
    CAP_DATA --> CORRELATE
    
    CORRELATE --> INSIGHTS[Generate Insights<br/>• Root cause analysis<br/>• Pattern identification<br/>• Impact assessment]
    
    INSIGHTS --> NARRATIVE[Create Narrative<br/>• Business language<br/>• Clear explanations<br/>• Context setting]
    
    NARRATIVE --> RECOMMENDATIONS[Generate Recommendations<br/>• Actionable items<br/>• Priority ranking<br/>• Implementation guidance]
    
    RECOMMENDATIONS --> RESPONSE[Format Response<br/>• Executive summary<br/>• Detailed analysis<br/>• Action items]
    
    RESPONSE --> END([Deliver to User])
```

## System Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV[Development Machine]
        TESTS[Test Suite]
        DOCS[Documentation]
    end
    
    subgraph "Data Sources"
        CSV_FILES[CSV Data Files<br/>• orders.csv<br/>• clients.csv<br/>• drivers.csv<br/>• warehouses.csv<br/>• fleet_logs.csv<br/>• external_factors.csv<br/>• feedback.csv<br/>• warehouse_logs.csv]
    end
    
    subgraph "Application Runtime"
        PYTHON[Python 3.8+ Runtime]
        PANDAS[Pandas Library]
        APP[Logistics Insight System<br/>• Data Processing<br/>• Analytics Engine<br/>• Query Interface]
    end
    
    subgraph "User Interfaces"
        CLI_INT[Command Line Interface]
        DEMO_INT[Demo Interface]
        SCRIPT_INT[Script Interface]
    end
    
    DEV --> APP
    TESTS --> APP
    CSV_FILES --> APP
    PYTHON --> APP
    PANDAS --> APP
    
    APP --> CLI_INT
    APP --> DEMO_INT
    APP --> SCRIPT_INT
    
    CLI_INT --> USERS[Operations Managers]
    DEMO_INT --> STAKEHOLDERS[Business Stakeholders]
    SCRIPT_INT --> DEVELOPERS[Technical Users]
```

---

*These diagrams illustrate the comprehensive architecture of the Logistics Insight System, showing data flow, component interactions, and system deployment structure.*