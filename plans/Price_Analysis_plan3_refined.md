# Price Analysis Tab - Phase 3 Implementation Plan (Refined)

## Overview
This document provides a detailed implementation plan for Phase 3 of the Price Analysis tab. Phase 3 adds a new "Price - By INN" visualization section that displays price ranges (min, median, max) for different insulin types using International Nonproprietary Names (INN). The implementation follows the existing architecture patterns established in Phase 1 and Phase 2.

## Phase 3 Scope
Phase 3 focuses on building the INN-based price visualization:
- "Price - By INN" section header
- Region and Sector expandable checkbox filters (local to this section)
- Line chart showing Min/Median/Max prices for insulin INN categories (dynamic, alphabetically sorted)
- Informational note about label display
- Interactive hover tooltips for all data points

---

## 1. Section Structure

### 1.1 Section Header

**Location:** `app.py` - Inside `with tab2:` block, after Phase 2 charts (after "Median price - By insulin type and level of care" chart)

**Condition:** Only display when at least one Data Collection Period is selected

**Implementation:**
```python
if st.session_state.selected_periods_price:
    # Section: Price - By INN
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>Price - By INN</h3></div>', unsafe_allow_html=True)
```

**CSS:** Uses existing `.section-header` class (already defined in app.py)

---

## 2. Local Filter Controls (Region and Sector)

### 2.1 Two-Column Layout for Filters

**Location:** Immediately after section header

**Implementation Pattern:**
```python
    # Local filters for INN price analysis
    st.markdown("<br>", unsafe_allow_html=True)
    col1_inn, col2_inn = st.columns(2)
```

### 2.2 Region Checkbox Filter (Column 1)

**Database Query:**
- **Table:** `adl_surveys_repeat`
- **Function:** Reuse existing `get_price_regions()` or create `get_inn_price_regions()`
- **Metric:** `COUNT(DISTINCT form_case__case_id)`
- **Filter:** `WHERE region IS NOT NULL AND region != 'NULL'`
- **Group By:** `region`
- **Sort:** `ORDER BY region ASC`
- **Additional Filters:** Apply selected countries and periods from global filters

**UI Pattern:** Expandable checkbox list (st.expander)

**Implementation:**
```python
with col1_inn:
    st.markdown("**Region**")
    with st.spinner("Loading regions..."):
        # Build global filters dict from session state
        global_filters_inn = {
            'data_collection_period': st.session_state.selected_periods_price,
            'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None
        }

        region_df_inn = get_price_regions(client, config.TABLES["surveys_repeat"], global_filters_inn)

        if region_df_inn is not None and not region_df_inn.empty:
            # Build region options with counts
            region_data_inn = []
            for _, row in region_df_inn.iterrows():
                region = row['region']
                count = row['facility_count']
                region_data_inn.append((region, count))

            total_regions_inn = len(region_data_inn)

            # Initialize checkboxes in session state
            for region, count in region_data_inn:
                checkbox_key = f"price_inn_region_{region}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

            # Count selected items
            selected_count_inn = sum(
                1 for region, _ in region_data_inn
                if st.session_state.get(f"price_inn_region_{region}", True)
            )
            excluded_count_inn = total_regions_inn - selected_count_inn

            # Create expander with selection summary
            with st.expander(
                f"Select Regions ({selected_count_inn}/{total_regions_inn} selected)",
                expanded=False
            ):
                if excluded_count_inn > 0:
                    st.caption(f"🚫 {excluded_count_inn} item{'s' if excluded_count_inn != 1 else ''} excluded")

                # Create checkboxes
                local_regions_inn = []
                for region, count in region_data_inn:
                    checkbox_key = f"price_inn_region_{region}"
                    is_checked = st.checkbox(
                        f"{region} ({count:,})",
                        value=st.session_state.get(checkbox_key, True),
                        key=checkbox_key
                    )
                    if is_checked:
                        local_regions_inn.append(region)
        else:
            local_regions_inn = []
            st.info("No region data available")
```

**Session State Keys:** `price_inn_region_{region_name}` (one per region, boolean)

### 2.3 Sector Checkbox Filter (Column 2)

**Database Query:**
- **Table:** `adl_surveys_repeat`
- **Function:** Reuse existing `get_price_sectors()` or create `get_inn_price_sectors()`
- **Metric:** `COUNT(DISTINCT form_case__case_id)`
- **Filter:** Apply global filters + selected regions from local Region filter
- **Group By:** `sector`
- **Sort:** `ORDER BY sector ASC`

**UI Pattern:** Expandable checkbox list (st.expander)

**Implementation:**
```python
with col2_inn:
    st.markdown("**Sector**")
    with st.spinner("Loading sectors..."):
        sector_df_inn = get_price_sectors(client, config.TABLES["surveys_repeat"], global_filters_inn, local_regions_inn)

        if sector_df_inn is not None and not sector_df_inn.empty:
            # Build sector options with counts
            sector_data_inn = []
            for _, row in sector_df_inn.iterrows():
                sector = row['sector']
                count = row['facility_count']
                sector_data_inn.append((sector, count))

            total_sectors_inn = len(sector_data_inn)

            # Initialize checkboxes in session state
            for sector, count in sector_data_inn:
                checkbox_key = f"price_inn_sector_{sector}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

            # Count selected items
            selected_count_inn_sec = sum(
                1 for sector, _ in sector_data_inn
                if st.session_state.get(f"price_inn_sector_{sector}", True)
            )
            excluded_count_inn_sec = total_sectors_inn - selected_count_inn_sec

            # Create expander with selection summary
            with st.expander(
                f"Select Sectors ({selected_count_inn_sec}/{total_sectors_inn} selected)",
                expanded=False
            ):
                if excluded_count_inn_sec > 0:
                    st.caption(f"🚫 {excluded_count_inn_sec} item{'s' if excluded_count_inn_sec != 1 else ''} excluded")

                # Create checkboxes
                local_sectors_inn = []
                for sector, count in sector_data_inn:
                    checkbox_key = f"price_inn_sector_{sector}"
                    is_checked = st.checkbox(
                        f"{sector} ({count:,})",
                        value=st.session_state.get(checkbox_key, True),
                        key=checkbox_key
                    )
                    if is_checked:
                        local_sectors_inn.append(sector)
        else:
            local_sectors_inn = []
            st.info("No sector data available")
```

**Session State Keys:** `price_inn_sector_{sector_name}` (one per sector, boolean)

---

## 3. Chart: Price - By INN (Line Chart)

### 3.1 Section Header

**Location:** After the Region/Sector filters

**Implementation:**
```python
    # Chart: Price - By INN
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Price - By INN")
```

### 3.2 Chart Specifications

**Chart Type:** Scatter Chart (Plotly Graph Objects) - Dots only, no connecting lines

**Data Source:**
- **Table:** `adl_surveys_repeat`
- **Function:** New function `get_price_by_inn()`

**Axes:**
- **X-axis:** INN Category (dynamic, based on `insulin_inn` column values, alphabetically sorted)
- **Y-axis:** Price - Local (dynamic range: 0 to max price + 15% padding)

**Categories:**
- Dynamic categories from `insulin_inn` column (e.g., Regular, NPH, Glargine, Detemir, etc.)
- Sorted alphabetically (ORDER BY insulin_inn ASC)

**Visual Properties:**
- **Display:** Three sets of dots (Min, Median, Max) - no connecting lines
- **Marker Colors:**
  - Min Price-Local: `#2ca02c` (green)
  - Median Price-Local: `#1f77b4` (blue)
  - Max Price-Local: `#d62728` (red)
- **Marker Size:** 10px circles
- **Text Labels:** Show median price values above median dots only
- **X-axis Labels:** Horizontal text
- **Legend:** Show all three price types

**Data Filtering:**
- Filter by selected regions and sectors
- Include out-of-pocket payments
- Exclude NULL and "---" INN values

### 3.3 Implementation Pattern

```python
    with st.spinner("Loading price by INN data..."):
        # Prepare filters
        inn_price_filters = {
            'data_collection_period': st.session_state.selected_periods_price,
            'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None,
            'region': local_regions_inn if local_regions_inn else None,
            'sector': local_sectors_inn if local_sectors_inn else None
        }

        chart_df_inn = get_price_by_inn(client, config.TABLES["surveys_repeat"], inn_price_filters)

        if chart_df_inn is not None and not chart_df_inn.empty:
            # Create Plotly scatter chart (dots only)
            fig_inn = go.Figure()

            # Calculate dynamic Y-axis range
            max_price = chart_df_inn['max_price_local'].max()
            y_axis_max = max_price * 1.15  # Add 15% padding at top

            # Add Min Price dots
            fig_inn.add_trace(go.Scatter(
                x=chart_df_inn['insulin_inn'].tolist(),
                y=chart_df_inn['min_price_local'].tolist(),
                name='Min Price-Local',
                mode='markers',
                marker=dict(size=10, symbol='circle', color='#2ca02c'),
                hovertemplate='<b>%{x}</b><br>' +
                              'Min Price: %{y:,.2f}<br>' +
                              '<extra></extra>'
            ))

            # Add Median Price dots with text labels
            fig_inn.add_trace(go.Scatter(
                x=chart_df_inn['insulin_inn'].tolist(),
                y=chart_df_inn['median_price_local'].tolist(),
                name='Median Price-Local',
                mode='markers+text',
                marker=dict(size=10, symbol='circle', color='#1f77b4'),
                text=[f'{val:,.0f}' for val in chart_df_inn['median_price_local'].tolist()],
                textposition='top center',
                hovertemplate='<b>%{x}</b><br>' +
                              'Median Price: %{y:,.2f}<br>' +
                              '<extra></extra>'
            ))

            # Add Max Price dots
            fig_inn.add_trace(go.Scatter(
                x=chart_df_inn['insulin_inn'].tolist(),
                y=chart_df_inn['max_price_local'].tolist(),
                name='Max Price-Local',
                mode='markers',
                marker=dict(size=10, symbol='circle', color='#d62728'),
                hovertemplate='<b>%{x}</b><br>' +
                              'Max Price: %{y:,.2f}<br>' +
                              '<extra></extra>'
            ))

            # Update layout
            fig_inn.update_layout(
                title='Price by INN Category',
                xaxis_title='INN Category',
                yaxis_title='Price - Local',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=500,
                yaxis=dict(
                    range=[0, y_axis_max],
                    tickformat=',.0f'
                ),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(t=80, b=80, l=60, r=40),
                hovermode='closest'
            )

            # Display chart
            st.plotly_chart(fig_inn, use_container_width=True)

            # Add informational note below chart
            st.markdown("""
            <div style="text-align: left;" align="left">
                <strong>NOTE:</strong> Label shown for median price only. Hover over points on the chart to see all values.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No price by INN data available for the selected filters")
```

### 3.4 Database Query Specification

**Function Name:** `get_price_by_inn(_client, table_name, filters)`

**Data Source:**
- Uses existing `insulin_inn` column from `adl_surveys_repeat` table
- Calculates median using APPROX_QUANTILES (BigQuery standard approach)
- No complex INN mapping required

**Query Structure:**
```sql
SELECT
  insulin_inn,
  MIN(insulin_standard_price_local) as min_price_local,
  APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(50)] as median_price_local,
  MAX(insulin_standard_price_local) as max_price_local,
  MIN(insulin_standard_price_usd) as min_price_usd,
  APPROX_QUANTILES(insulin_standard_price_usd, 100)[OFFSET(50)] as median_price_usd,
  MAX(insulin_standard_price_usd) as max_price_usd,
  COUNT(1) as product_count
FROM `{project}.{dataset}.{table_name}`
WHERE
  insulin_inn IS NOT NULL
  AND insulin_inn != '---'
  AND (
    insulin_out_of_pocket = 'Yes'
    OR insulin_out_of_pocket = 'Some people pay out of pocket'
  )
  AND data_collection_period IN (...)  -- from filters
  -- Additional filters for country, region, sector
GROUP BY insulin_inn
ORDER BY insulin_inn ASC
```

**Returns:** DataFrame with columns:
- `insulin_inn` (str) - INN category name (e.g., Regular, NPH, Glargine, Detemir)
- `min_price_local` (float)
- `median_price_local` (float)
- `max_price_local` (float)
- `min_price_usd` (float)
- `median_price_usd` (float)
- `max_price_usd` (float)
- `product_count` (int)

---

## 4. Database Functions to Implement

### 4.1 Function Summary

Add to `database/bigquery_client.py`:

| Function Name | Purpose | Table | Returns |
|---------------|---------|-------|---------|
| `get_price_by_inn()` | Get min/median/max prices by INN | `adl_surveys_repeat` | insulin_inn, min/median/max prices (local & USD), product_count |

### 4.2 Function: get_price_by_inn()

```python
@st.cache_data(ttl=600)
def get_price_by_inn(_client, table_name, filters):
    """
    Get min, median, and max insulin prices by INN category.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        filters (dict): Filters (data_collection_period, country, region, sector)

    Returns:
        pandas DataFrame with columns:
            - insulin_inn (str)
            - min_price_local (float)
            - median_price_local (float)
            - max_price_local (float)
            - min_price_usd (float)
            - median_price_usd (float)
            - max_price_usd (float)
            - product_count (int)
    """
    if not filters.get('data_collection_period'):
        return None

    # Build WHERE clause
    where_clauses = ["1=1"]

    # Add data collection period filter
    periods = filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if filters.get('country'):
        countries_str = "', '".join(filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add region filter (optional)
    if filters.get('region'):
        regions_str = "', '".join(filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add sector filter (optional)
    if filters.get('sector'):
        sectors_str = "', '".join(filters['sector'])
        where_clauses.append(f"sector IN ('{sectors_str}')")

    # Insulin INN filters
    where_clauses.append("insulin_inn IS NOT NULL")
    where_clauses.append("insulin_inn != '---'")

    # Out-of-pocket payment filter
    where_clauses.append("(insulin_out_of_pocket = 'Yes' OR insulin_out_of_pocket = 'Some people pay out of pocket')")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
      insulin_inn,
      MIN(insulin_standard_price_local) as min_price_local,
      APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(50)] as median_price_local,
      MAX(insulin_standard_price_local) as max_price_local,
      MIN(insulin_standard_price_usd) as min_price_usd,
      APPROX_QUANTILES(insulin_standard_price_usd, 100)[OFFSET(50)] as median_price_usd,
      MAX(insulin_standard_price_usd) as max_price_usd,
      COUNT(1) as product_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_inn
    ORDER BY insulin_inn ASC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting price by INN: {str(e)}")
        return None
```

---

## 5. Code Organization

### 5.1 File Structure

```
/Users/waqas/HAI_demo/
├── app.py                          # Main application file
│   └── [After Phase 2] Tab 2: Price Analysis
│       ├── Phase 1: Global filters (existing)
│       ├── Phase 2: Median price charts (existing)
│       └── Phase 3: Price by INN (new)
│           ├── Section header
│           ├── Local Region/Sector filters
│           ├── Line chart (Min/Median/Max by INN)
│           └── Informational note
├── database/
│   └── bigquery_client.py         # Add 1 new function
│       └── get_price_by_inn()
├── plans/
│   ├── Price_Analysis_plan3.md    # Original plan
│   └── Price_Analysis_plan3_refined.md  # This document
```

### 5.2 Import Updates

Add to `app.py` imports (around line 10-49):

```python
from database.bigquery_client import (
    # ... existing imports ...
    get_price_by_inn
)
```

---

## 6. Implementation Steps

### Step 1: Add Database Function (20 minutes)
- Add `get_price_by_inn()` function to `database/bigquery_client.py`
- Test query with sample filters
- Verify query results in BigQuery console
- Ensure all INN categories from data are captured

### Step 2: Update Imports (5 minutes)
- Add new function import to `app.py`
- Run syntax check

### Step 3: Add Section Header (5 minutes)
- Add conditional wrapper for selected periods
- Add section header after Phase 2 charts
- Test display when periods selected/unselected

### Step 4: Build Region/Sector Filters (25 minutes)
- Create two-column layout with unique variable names
- Implement Region checkbox expander (reuse Phase 2 pattern)
- Implement Sector checkbox expander (reuse Phase 2 pattern)
- Use unique session state keys (`price_inn_region_*`, `price_inn_sector_*`)
- Test filter interactions and session state

### Step 5: Build Line Chart (40 minutes)
- Add section header
- Implement data fetching with filters
- Create Plotly line chart with three traces (Min, Median, Max)
- Add different colors for each line
- Add markers and text labels (median only)
- Set Y-axis range to 0-5000
- Add styling and formatting
- Test with various filter combinations

### Step 6: Add Informational Note (5 minutes)
- Add HTML-formatted note below chart
- Verify styling and alignment

### Step 7: Testing & Validation (30 minutes)
- Run syntax check
- Manual testing of all features
- Cross-filter testing (global + local filters)
- Edge case testing (no data, missing INN categories, etc.)
- Verify INN categories display correctly

**Total Estimated Time:** ~2.25 hours

---

## 7. Testing Strategy

### 7.1 Manual Testing Checklist

**Section Display:**
- [ ] Section only shows when at least one period is selected
- [ ] Section hides when no periods selected
- [ ] Section header displays correctly

**Filter Functionality:**
- [ ] Region checkboxes load with facility counts
- [ ] Sector checkboxes load with facility counts
- [ ] Region filter affects sector options
- [ ] Expander shows correct selection count (N/M selected)
- [ ] Excluded count displays when items unchecked
- [ ] Checkboxes persist state across reruns
- [ ] All regions/sectors selected by default on first load
- [ ] Filters are independent from Phase 2 filters

**Scatter Chart (Price by INN):**
- [ ] Chart displays with INN categories on X-axis (alphabetically sorted)
- [ ] Three sets of dots displayed (Min, Median, Max) - NO connecting lines
- [ ] Min dots are green (#2ca02c)
- [ ] Median dots are blue (#1f77b4)
- [ ] Max dots are red (#d62728)
- [ ] All dots are 10px circles and clearly visible
- [ ] Y-axis range is dynamic (0 to max price + 15% padding)
- [ ] Y-axis adjusts when filters change
- [ ] Median price labels shown above median dots
- [ ] Legend shows all three price types
- [ ] Hover tooltips show price values for all dots
- [ ] Chart responds to filter changes

**Data Integrity:**
- [ ] INN categories correctly pulled from `insulin_inn` column
- [ ] All INN categories present (based on available data)
- [ ] Min <= Median <= Max for each category
- [ ] Product counts are positive integers
- [ ] No NULL or "---" INN categories displayed
- [ ] Out-of-pocket filter applied correctly

**Informational Note:**
- [ ] Note displays below chart
- [ ] Text formatting is correct
- [ ] Left-aligned as specified

### 7.2 Test Execution Commands

**Syntax Check:**
```bash
python3 -m py_compile app.py
python3 -m py_compile database/bigquery_client.py
```

**Run Application:**
```bash
streamlit run app.py
```

**Test Sequence:**
1. Navigate to Price Analysis tab
2. Select at least one Data Collection Period
3. Scroll to "Price - By INN" section
4. Verify section appears
5. Test Region checkbox filter
6. Test Sector checkbox filter (depends on Region)
7. Verify line chart displays with 3 lines
8. Hover over data points to verify tooltips
9. Verify median labels are visible
10. Change filters and verify chart updates
11. Uncheck all regions - verify info message
12. Deselect all periods - verify section hides

### 7.3 Expected BigQuery Query

**INN Price Query:**
```sql
SELECT
  insulin_inn,
  MIN(insulin_standard_price_local) as min_price_local,
  APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(50)] as median_price_local,
  MAX(insulin_standard_price_local) as max_price_local,
  MIN(insulin_standard_price_usd) as min_price_usd,
  APPROX_QUANTILES(insulin_standard_price_usd, 100)[OFFSET(50)] as median_price_usd,
  MAX(insulin_standard_price_usd) as max_price_usd,
  COUNT(1) as product_count
FROM `hai-dev.facilities.adl_surveys_repeat`
WHERE
  insulin_inn IS NOT NULL
  AND insulin_inn != '---'
  AND (insulin_out_of_pocket = 'Yes' OR insulin_out_of_pocket = 'Some people pay out of pocket')
  AND data_collection_period IN (...)
  -- Additional filters for country, region, sector
GROUP BY insulin_inn
ORDER BY insulin_inn ASC
```

---

## 8. Key Design Decisions

### 8.1 INN Category Source
**Decision:** Use existing `insulin_inn` column directly from database

**Rationale:**
- Leverages existing data structure (no custom mapping needed)
- Dynamic categories based on actual data
- Simpler implementation and maintenance
- Alphabetical sorting makes categories easy to find
- Automatically includes all INN types present in data

### 8.2 Scatter Chart (Dots Only) vs Line Chart
**Decision:** Use scatter chart with dots only (no connecting lines)

**Rationale:**
- Each INN category is independent (not a continuous time series)
- Dots-only display prevents misleading interpretation of trends between categories
- Cleaner visual presentation for categorical data
- Better for showing discrete price points for each INN type
- Still allows easy comparison of min/median/max across categories

### 8.3 Three Price Metrics
**Decision:** Show Min, Median, and Max prices on same chart

**Rationale:**
- Shows price range and variation
- Median provides typical price
- Min/Max show affordability extremes
- All three metrics useful for policy analysis

### 8.4 Median Labels Only
**Decision:** Display text labels on median line only, not min/max

**Rationale:**
- Requirement from original plan
- Reduces visual clutter
- Median is most important metric
- Hover tooltips provide all values

### 8.5 Y-axis Range (Dynamic)
**Decision:** Use dynamic Y-axis range (0 to max price + 15% padding) instead of fixed range

**Rationale:**
- Adapts to actual price ranges in filtered data
- Prevents empty space when prices are low
- Prevents data clipping when prices exceed fixed range
- 15% padding provides visual breathing room above highest price
- Better data visualization practice for varying price ranges across different filter combinations

### 8.6 Local Filters Independent from Phase 2
**Decision:** INN section has its own Region/Sector filters

**Rationale:**
- Allows independent analysis
- Follows pattern from Phase 2
- Prevents unintended filter interactions
- Better user experience for focused analysis

### 8.7 Median Calculation Using APPROX_QUANTILES
**Decision:** Calculate median using APPROX_QUANTILES in query instead of using pre-calculated columns

**Rationale:**
- Pre-calculated median columns (`insulin_standard_price_local_median`) do not exist in the table
- APPROX_QUANTILES is the standard BigQuery approach for median calculation
- Consistent with other price analysis functions (e.g., `get_median_price_by_type`)
- Provides accurate median values based on filtered dataset
- Efficient for BigQuery's distributed architecture

---

## 9. Potential Issues & Solutions

### Issue 1: Missing INN Categories
**Symptom:** Some INN categories have no data for selected filters
**Solution:**
- Display info message when no data available
- Filter combinations may exclude certain INN types
- Test with different filter combinations
- Consider adding note about data availability

### Issue 2: Price Outliers Skewing Chart
**Symptom:** Max prices are extremely high, compressing other data
**Solution:**
- Y-axis already fixed at 0-5000
- Consider capping displayed values at 5000
- Add note about values exceeding range
- Show actual max value in tooltip even if clipped

### Issue 3: Line Chart Lines Overlapping
**Symptom:** Min/Median/Max lines too close together
**Solution:**
- Use distinct colors (green/blue/red)
- Increase marker size for visibility
- Add line width differentiation
- Ensure hover tooltips work for all lines

### Issue 4: Query Performance
**Symptom:** Slow query execution
**Solution:**
- Use caching (@st.cache_data with ttl=600)
- APPROX_QUANTILES is optimized for BigQuery's distributed architecture
- Consider adding indexes on insulin_inn column if needed
- Test query performance in BigQuery console
- Limit data collection periods to reduce data volume

### Issue 5: NULL Price Values
**Symptom:** NULL values in `insulin_standard_price_local` or `insulin_standard_price_usd` columns
**Solution:**
- APPROX_QUANTILES handles NULL values automatically
- MIN/MAX aggregate functions ignore NULL values
- Add WHERE clause filter if needed: `insulin_standard_price_local IS NOT NULL`
- Verify data quality in source table

---

## 10. Acceptance Criteria

Phase 3 implementation is complete when:

- [ ] **AC1:** Section header "Price - By INN" displays
- [ ] **AC2:** Section only shows when at least one period is selected
- [ ] **AC3:** Region checkbox filter loads with facility counts (independent from Phase 2)
- [ ] **AC4:** Sector checkbox filter loads with facility counts (independent from Phase 2)
- [ ] **AC5:** Sector filter options update when Region filter changes
- [ ] **AC6:** Expanders show selection count "N/M selected"
- [ ] **AC7:** Expanders show excluded count when items unchecked
- [ ] **AC8:** All checkboxes selected by default on first load
- [ ] **AC9:** Scatter chart displays with INN categories on X-axis (alphabetically sorted)
- [ ] **AC10:** Three sets of dots displayed (Min Price-Local, Median Price-Local, Max Price-Local) with NO connecting lines
- [ ] **AC11:** Min dots are green (#2ca02c)
- [ ] **AC12:** Median dots are blue (#1f77b4)
- [ ] **AC13:** Max dots are red (#d62728)
- [ ] **AC14:** Y-axis range is dynamic (0 to max price + 15% padding)
- [ ] **AC15:** Dots are 10px circles and clearly visible
- [ ] **AC16:** Median price labels shown above median dots
- [ ] **AC17:** Legend shows all three price types
- [ ] **AC18:** Hover tooltips show price values for all lines
- [ ] **AC19:** Chart updates when filters change
- [ ] **AC20:** Informational note displays below chart
- [ ] **AC21:** Note is left-aligned and mentions median labels
- [ ] **AC22:** INN categories correctly pulled from `insulin_inn` column
- [ ] **AC23:** No errors in console or BigQuery logs
- [ ] **AC24:** Both files pass syntax check

---

## 11. Future Enhancements (Phase 4+)

### Additional INN Categories
- Lispro (Rapid-Acting Analogue)
- Aspart (Rapid-Acting Analogue)
- Mixed Analogue insulins
- Degludec (Ultra-long-acting)

### Alternative Visualizations
- Box plot showing price distribution
- Violin plot for price density
- Separate charts for human vs analogue
- Price comparison by originator vs biosimilar

### USD Currency Toggle
- Add button to switch between local currency and USD
- Update Y-axis labels and values dynamically
- Maintain same chart structure

### Export Functionality
- Download chart data as CSV
- Export chart as PNG image
- Generate price summary report

### Price Trend Analysis
- Add time-based analysis if multiple periods selected
- Show price changes over time
- Highlight increasing/decreasing trends

---

## 12. Dependencies

### Required Packages (Already Installed)
- `streamlit` - UI framework
- `pandas` - Data manipulation
- `plotly` - Charts (plotly.graph_objects)
- `google-cloud-bigquery` - BigQuery client

### Required Files
- `app.py` - Main application (modify)
- `database/bigquery_client.py` - Database functions (add 1 new function)
- `config.py` - Configuration settings (no changes)
- `.env` - Environment variables (no changes)

### BigQuery Requirements
- **Project:** `hai-dev`
- **Dataset:** `facilities`
- **Tables:**
  - `adl_surveys_repeat` (for INN price data and filters)

**Columns needed in adl_surveys_repeat:**
- `form_case__case_id` (STRING)
- `data_collection_period` (STRING)
- `country` (STRING)
- `region` (STRING)
- `sector` (STRING)
- `insulin_inn` (STRING) - INN category name
- `insulin_standard_price_local` (FLOAT64) - Price in local currency
- `insulin_standard_price_usd` (FLOAT64) - Price in USD
- `insulin_out_of_pocket` (STRING) - Out-of-pocket payment indicator

---

## 13. Color Palette Reference

### Chart Colors (Phase 3)
- **Min Price Line:** `#2ca02c` (green)
- **Median Price Line:** `#1f77b4` (blue)
- **Max Price Line:** `#d62728` (red)

### UI Colors (Existing)
- **Primary Blue:** `#1f77b4`
- **Secondary Orange:** `#ff7f0e`
- **Background Light:** `#f8f9fa`
- **Info Box Background:** `#e3f2fd`
- **Info Box Border:** `#2196f3`

---

## 14. Session State Architecture

### New Session State Keys (Phase 3)

**Checkbox States (Dynamic - one per region/sector):**
```python
# Region checkboxes (INN section)
st.session_state.price_inn_region_{region_name}  # bool - one per region

# Sector checkboxes (INN section)
st.session_state.price_inn_sector_{sector_name}  # bool - one per sector
```

**Example:**
```python
st.session_state.price_inn_region_East_Africa = True
st.session_state.price_inn_region_West_Africa = False
st.session_state.price_inn_sector_Public = True
st.session_state.price_inn_sector_Private = True
```

### Existing Session State Keys (Phase 1)
```python
st.session_state.selected_countries_price  # List[str]
st.session_state.selected_regions_price    # List[str]
st.session_state.selected_periods_price    # List[str]
```

### Phase 2 Session State Keys (Not Reused)
```python
st.session_state.price_region_{region_name}  # Phase 2 regions
st.session_state.price_sector_{sector_name}  # Phase 2 sectors
```

**Note:** Phase 3 uses different session state keys to maintain filter independence.

---

## 15. Code Snippet: Complete Section Structure

```python
# Phase 3: Price - By INN Section
if st.session_state.selected_periods_price:
    # Section Header
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>Price - By INN</h3></div>', unsafe_allow_html=True)

    # Local Filters: Region and Sector
    st.markdown("<br>", unsafe_allow_html=True)
    col1_inn, col2_inn = st.columns(2)

    with col1_inn:
        # Region Checkbox Filter
        # ... (implementation from section 2.2)

    with col2_inn:
        # Sector Checkbox Filter
        # ... (implementation from section 2.3)

    # Chart: Price - By INN (Line Chart)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Price - By INN")
    # ... (implementation from section 3.3)

    # Informational Note
    st.markdown("""
    <div style="text-align: left;" align="left">
        <strong>NOTE:</strong> Label shown for median price only. Hover over points on the chart to see all values.
    </div>
    """, unsafe_allow_html=True)
```

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-07 | AI Assistant | Initial refined plan from Price_Analysis_plan3.md |
| 1.1 | 2025-12-07 | AI Assistant | Updated to use `insulin_inn` column and `insulin_standard_price_local_median` (simplified query) |
| 1.2 | 2025-12-08 | AI Assistant | Fixed median calculation - replaced non-existent median columns with APPROX_QUANTILES, updated all query examples and design decisions |

---

**End of Refined Implementation Plan - Phase 3**
