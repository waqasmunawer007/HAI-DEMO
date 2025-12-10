# Codebase Structure

## Directory Layout
```
HAI_demo/
├── app.py                    # Main Streamlit application (~1050 lines)
├── config.py                 # Configuration (GCP_PROJECT_ID, BQ_DATASET, TABLES)
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in git)
├── CLAUDE.md                 # Instructions for Claude Code
├── README.md                 # Project documentation
├── database/
│   └── bigquery_client.py    # BigQuery connection and query functions
├── utils/
│   └── data_processing.py    # Helper functions for data manipulation
├── credentials/              # Service account keys (not in git)
├── plans/                    # Feature specifications
│   ├── UI_initial_plan.md
│   ├── Insulin_filters.md
│   └── Availability_analysis_plan1.md
└── __pycache__/              # Python cache files

## Key Files

### app.py (Main Application)
- Single-file Streamlit app with 6 tabs
- Session state management
- Custom CSS styling
- Filter system with Country, Region, Sector dropdowns
- 10 insulin availability filters
- Plotly visualizations

### database/bigquery_client.py
Core functions:
- `get_bigquery_client()` - Cached connection
- `query_table(client, table_name, limit)` - Fetch table data
- `run_custom_query(client, query)` - Execute SQL queries
- `get_table_schema(client, table_name)` - Field metadata
- `get_row_count(client, table_name)` - COUNT(*) query

### utils/data_processing.py
Helper functions:
- `format_currency(value)` - Format as USD
- `calculate_summary_stats(df, column)` - Statistical summaries
- `filter_by_country(df, countries)` - DataFrame filtering
- `get_availability_summary(df)` - Availability percentages
- `clean_price_data(df, price_column)` - Handle nulls/outliers

### config.py
Loads from `.env`:
- `GCP_PROJECT_ID` (default: "hai-dev")
- `BQ_DATASET` (default: "facilities")
- `TABLES` - Dictionary mapping friendly names to table names