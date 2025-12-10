# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HAI Facilities Data Dashboard - A modern Streamlit application for analyzing healthcare facilities data from Google BigQuery. Focuses on insulin availability, pricing, medical device access, and facility distribution across multiple regions.

## Development Commands

### Running the Application
```bash
streamlit run app.py
```
The app will open at `http://localhost:8501`

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Authentication Setup
**Option A (Recommended for local dev):**
```bash
gcloud auth application-default login
```

**Option B (Service Account):**
Set `GOOGLE_APPLICATION_CREDENTIALS` in `.env` to point to your service account JSON key in `credentials/`

### Testing Syntax
```bash
python3 -m py_compile app.py
python3 -m py_compile database/bigquery_client.py
python3 -m py_compile utils/data_processing.py
```

## Architecture

### Application Structure

**app.py (Main Application)**
- Single-file Streamlit application (~1050 lines)
- Session state management for data persistence (`st.session_state.df`, `st.session_state.selected_table`)
- 6 main tabs: Availability Analysis, Price Analysis, Trends & Insights, Data Explorer, Custom Query, About
- Custom CSS styling with gradient headers, metric cards, and hover effects
- Filter system: Country, Region, Sector dropdowns that cascade to all visualizations

**Key UI Patterns:**
- Metric cards use custom HTML with `unsafe_allow_html=True`
- All visualizations use Plotly for interactivity
- Section headers use consistent styling: `<div class="section-header"><h3>Title</h3></div>`
- Data loading triggered by sidebar button, not automatic on selection change

### Data Layer

**database/bigquery_client.py**
Core functions (all use `@st.cache_data` for performance):
- `get_bigquery_client()` - Singleton pattern, cached connection
- `query_table(client, table_name, limit)` - Fetch table data with LIMIT
- `run_custom_query(client, query)` - Execute user SQL queries
- `get_table_schema(client, table_name)` - Return field metadata
- `get_row_count(client, table_name)` - COUNT(*) query

**utils/data_processing.py**
Helper functions:
- `format_currency(value)` - Format numbers as USD
- `calculate_summary_stats(df, column)` - Mean, median, min, max, std
- `filter_by_country(df, countries)` - DataFrame filtering
- `get_availability_summary(df)` - Scan for *_available columns, calculate percentages
- `clean_price_data(df, price_column)` - Handle nulls and outliers

**config.py**
Loads from `.env` file:
- `GCP_PROJECT_ID` (default: "hai-dev")
- `BQ_DATASET` (default: "facilities")
- `TABLES` - Dictionary mapping friendly names to actual table names

### BigQuery Dataset

**Project:** `hai-dev`
**Dataset:** `facilities`

**Tables:**
- `adl_comparators` - Comparator NCD medications
- `adl_repeat_repivot` - Insulin repeat data (repivoted)
- `adl_surveys` - Main survey responses
- `adl_surveys_repeat` - Insulin survey repeat data
- `adl_surveys_repeat_cgm` - CGM device data

**Expected Column Patterns:**
- Availability: `*_available` (values: "Yes"/"No" or boolean/int)
- Prices: `*_price_usd` or `*_usd`
- Insulin types: `insulin_*_type`, `insulin_human`, `insulin_analogue`
- Brands: `insulin_brand`, `insulin_name`
- Geography: `country`, `region`
- Facilities: `sector`, `level_of_care` or `level`

### Insulin Filters Implementation

**Tab 1: Availability Analysis** contains 10 specialized insulin filters:

1. **Overall** - Aggregate metrics (%, n, unavailability)
2. **By Sector** - Bar chart, responds to Region filter
3. **By Insulin Type** - Human/Analogue/Rapid/Long, bar + pie charts
4. **By Region** - Top 15 horizontal bar chart, responds to Sector filter
5. **Public Sector by Level of Care** - Primary/Secondary/Tertiary breakdown
6. **By INN** - Generic names (Regular, NPH, Lispro, Aspart, Glargine, etc.)
7. **Top 10 Brands** - Donut pie chart, responds to Sector filter
8. **By Presentation** - Vial/Pen/Cartridge/Pre-filled forms
9. **Originator vs Biosimilars** - 3-column comparison with metrics
10. **Comparator Medicines** - Metformin, Glibenclamide, Aspirin, Statins

**Helper Function Pattern:**
```python
def calc_availability(df_subset, col_name):
    # Returns: (available_count, total_count, percentage)
    # Handles: object dtype ("Yes"/"No"), bool, int, float
```

All filters respect the sidebar's Region/Sector dropdown selections via `filtered_df`.

### State Management

**Session State Keys:**
- `st.session_state.df` - Currently loaded DataFrame (None until "Load/Refresh Data" clicked)
- `st.session_state.selected_table` - Friendly name of selected table

**Why This Pattern:**
- Data persists across tab switches
- User controls when expensive BigQuery queries run
- Prevents automatic requerying on every interaction

### Styling System

**Color Palette:**
- Primary: `#1f77b4` (blue)
- Secondary: `#ff7f0e` (orange)
- Background: `#f8f9fa` (light gray)
- Gradient header: `#667eea` to `#764ba2` (purple gradient)

**Reusable CSS Classes:**
- `.main-header` - Gradient hero section
- `.metric-card` - White cards with left border, hover lift effect
- `.section-header` - Light background with left border accent
- `.info-box` - Blue background for definitions/notes
- `.warning-box` - Orange background for alerts

### Adding New Features

**New BigQuery Table:**
1. Add to `config.py` TABLES dictionary
2. Add to `app.py` table_options (line ~203)

**New Data Processing Function:**
1. Add to `utils/data_processing.py`
2. Import in `app.py` (line ~18)
3. Function should return processed DataFrame or dict

**New Visualization:**
1. Use Plotly Express (`px`) or Plotly Graph Objects (`go`)
2. Standard layout: `plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'`
3. Use `st.plotly_chart(fig, use_container_width=True)` for responsiveness

**New Filter/Analysis:**
1. Add after line 838 in app.py (before Product Availability Summary)
2. Use section header: `st.markdown('#### N. Filter Name')`
3. Check for required columns before processing
4. Show `st.info()` message if data unavailable

## Important Patterns

### Data Column Detection
Always check if columns exist before using:
```python
insulin_cols = [col for col in df.columns if 'insulin' in col.lower() and 'available' in col.lower()]
if insulin_cols:
    # Process data
else:
    st.info("Data not available in current dataset")
```

### Filter Cascading
Sidebar filters create `filtered_df`:
```python
filtered_df = df.copy()
if selected_country != 'All':
    filtered_df = filtered_df[filtered_df['country'] == selected_country]
```
All visualizations must use `filtered_df`, not `df`.

### Handling Multiple Data Types
Availability columns can be:
- String: "Yes"/"No" → use `df[col].str.lower() == 'yes'`
- Boolean: True/False → use `df[col].sum()`
- Integer: 1/0 → use `df[col].sum()`

The `calc_availability()` helper handles all cases.

### BigQuery Best Practices
- All BigQuery functions use `@st.cache_data(ttl=600)` (10-minute cache)
- Client creation uses `@st.cache_resource` (persists across reruns)
- Always include `LIMIT` in queries to prevent large data transfers
- Use parameterized queries for table names: `f"{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table}"`

## Common Gotchas

1. **Streamlit reruns the entire script** on every interaction - use session_state and caching
2. **f-strings in st.markdown** with HTML - be careful with `{}` placeholders, use variables outside f-string if needed
3. **DataFrame modifications** - always use `.copy()` when creating filtered versions
4. **Column name case sensitivity** - use `.lower()` when searching column names
5. **Empty DataFrames** - always check `if not df.empty:` before processing
6. **Plotly color scales** - Use named scales (Blues, Greens, RdYlGn) for consistency

## Plans Directory

The `plans/` directory contains feature specifications:
- `UI_initial_plan.md` - Original UI redesign requirements (references Looker Studio)
- `Insulin_filters.md` - Specification for 10 insulin availability filters

When implementing from plans, match the Looker Studio dashboard style and ensure filter dependencies work correctly.
