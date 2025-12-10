# Price Analysis Tab - Phase 6 Implementation Plan (Refined)

## Overview
This document provides a detailed implementation plan for Phase 6 of the Price Analysis tab. Phase 6 adds a new "Median price - By originator brands and biosimilars" visualization section that displays two side-by-side clustered bar charts comparing median prices between Originator Brands and Biosimilars for both Human and Analogue insulin types. The implementation follows the existing architecture patterns established in Phase 1-5.

## Phase 6 Scope
Phase 6 focuses on building originator/biosimilar price comparison visualization:
- "Median price - By originator brands and biosimilars" section header
- Region and Sector expandable checkbox filters (local to this section)
- Two clustered bar charts side by side:
  - Left: Human Insulin (Originator vs Biosimilar)
  - Right: Analogue Insulin (Originator vs Biosimilar)
- Dynamic Y-axis based on price range
- Professional styling with value labels on bars
- Teal/Dark Blue color scheme

---

## 1. Section Structure

### 1.1 Section Header

**Location:** `app.py` - Inside `with tab2:` block, after Phase 5 ("Median price - By presentation" section)

**Condition:** Only display when at least one Data Collection Period is selected

**Implementation:**
```python
if st.session_state.selected_periods_price:
    # Phase 6: Median price - By originator brands and biosimilars Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>Median price - By originator brands and biosimilars</h3></div>', unsafe_allow_html=True)
```

**CSS:** Uses existing `.section-header` class (already defined in app.py)

---

## 2. Local Filter Controls (Region and Sector)

### 2.1 Two-Column Layout for Filters

**Location:** Immediately after section header

**Implementation Pattern:**
```python
    # Local filters for Originator/Biosimilar price analysis
    st.markdown("<br>", unsafe_allow_html=True)
    col1_orig, col2_orig = st.columns(2)
```

### 2.2 Region Checkbox Filter (Column 1)

**Database Query:**
- **Table:** `adl_surveys_repeat`
- **Function:** Reuse existing `get_price_regions()`
- **Metric:** `COUNT(DISTINCT form_case__case_id)`
- **Filter:** `WHERE region IS NOT NULL AND region != 'NULL'`
- **Group By:** `region`
- **Sort:** `ORDER BY region DESC` (as specified in plan)
- **Additional Filters:** Apply selected countries and periods from global filters

**UI Pattern:** Expandable checkbox list (st.expander)

**Implementation:**
```python
with col1_orig:
    st.markdown("**Region**")
    with st.spinner("Loading regions..."):
        # Build global filters dict from session state
        global_filters_orig = {
            'data_collection_period': st.session_state.selected_periods_price,
            'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None
        }

        region_df_orig = get_price_regions(client, config.TABLES["surveys_repeat"], global_filters_orig)

        if region_df_orig is not None and not region_df_orig.empty:
            # Build region options with counts
            region_data_orig = []
            for _, row in region_df_orig.iterrows():
                region = row['region']
                count = row['facility_count']
                region_data_orig.append((region, count))

            total_regions_orig = len(region_data_orig)

            # Initialize checkboxes in session state
            for region, count in region_data_orig:
                checkbox_key = f"price_orig_region_{region}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

            # Count selected items
            selected_count_orig = sum(
                1 for region, _ in region_data_orig
                if st.session_state.get(f"price_orig_region_{region}", True)
            )
            excluded_count_orig = total_regions_orig - selected_count_orig

            # Create expander with selection summary
            with st.expander(
                f"Select Regions ({selected_count_orig}/{total_regions_orig} selected)",
                expanded=False
            ):
                if excluded_count_orig > 0:
                    st.caption(f"🚫 {excluded_count_orig} item{'s' if excluded_count_orig != 1 else ''} excluded")

                # Create checkboxes
                local_regions_orig = []
                for region, count in region_data_orig:
                    checkbox_key = f"price_orig_region_{region}"
                    is_checked = st.checkbox(
                        f"{region} ({count:,})",
                        value=st.session_state.get(checkbox_key, True),
                        key=checkbox_key
                    )
                    if is_checked:
                        local_regions_orig.append(region)
        else:
            local_regions_orig = []
            st.info("No region data available")
```

**Session State Keys:** `price_orig_region_{region_name}` (one per region, boolean)

### 2.3 Sector Checkbox Filter (Column 2)

**Database Query:**
- **Table:** `adl_surveys_repeat`
- **Function:** Reuse existing `get_price_sectors()`
- **Metric:** `COUNT(DISTINCT form_case__case_id)`
- **Filter:** Apply global filters + selected regions from local Region filter
- **Group By:** `sector`
- **Sort:** `ORDER BY sector DESC` (as specified in plan)

**UI Pattern:** Expandable checkbox list (st.expander)

**Implementation:**
```python
with col2_orig:
    st.markdown("**Sector**")
    with st.spinner("Loading sectors..."):
        sector_df_orig = get_price_sectors(client, config.TABLES["surveys_repeat"], global_filters_orig, local_regions_orig)

        if sector_df_orig is not None and not sector_df_orig.empty:
            # Build sector options with counts
            sector_data_orig = []
            for _, row in sector_df_orig.iterrows():
                sector = row['sector']
                count = row['facility_count']
                sector_data_orig.append((sector, count))

            total_sectors_orig = len(sector_data_orig)

            # Initialize checkboxes in session state
            for sector, count in sector_data_orig:
                checkbox_key = f"price_orig_sector_{sector}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

            # Count selected items
            selected_count_orig_sec = sum(
                1 for sector, _ in sector_data_orig
                if st.session_state.get(f"price_orig_sector_{sector}", True)
            )
            excluded_count_orig_sec = total_sectors_orig - selected_count_orig_sec

            # Create expander with selection summary
            with st.expander(
                f"Select Sectors ({selected_count_orig_sec}/{total_sectors_orig} selected)",
                expanded=False
            ):
                if excluded_count_orig_sec > 0:
                    st.caption(f"🚫 {excluded_count_orig_sec} item{'s' if excluded_count_orig_sec != 1 else ''} excluded")

                # Create checkboxes
                local_sectors_orig = []
                for sector, count in sector_data_orig:
                    checkbox_key = f"price_orig_sector_{sector}"
                    is_checked = st.checkbox(
                        f"{sector} ({count:,})",
                        value=st.session_state.get(checkbox_key, True),
                        key=checkbox_key
                    )
                    if is_checked:
                        local_sectors_orig.append(sector)
        else:
            local_sectors_orig = []
            st.info("No sector data available")
```

**Session State Keys:** `price_orig_sector_{sector_name}` (one per sector, boolean)

---

## 3. Charts: Human and Analogue Insulin (Side by Side)

### 3.1 Two-Column Layout for Charts

**Location:** After the Region/Sector filters

**Implementation:**
```python
    # Charts: Human and Analogue side by side
    st.markdown("<br>", unsafe_allow_html=True)
    col_human_orig, col_analogue_orig = st.columns(2)
```

### 3.2 Human Insulin Chart (Left Column)

**Chart Specifications:**
- **Title:** "Human Insulin - Originator vs Biosimilar"
- **Chart Type:** Clustered Bar Chart (Plotly Graph Objects)
- **X-axis:** Categories (Originator Brand, Biosimilar)
- **Y-axis:** Median Price - Local
  - Title: "Median price - Local"
  - Dynamic range: 0 to max median price + 15% padding
  - Tick format: comma-separated
- **Bar Color:** Teal/Dark Blue (`#17becf`)
- **Value Labels:** Display median price value on top of each bar
- **Legend:** "Median Price-Local"

**Data Source:**
- **Table:** `adl_surveys_repeat`
- **Function:** New function `get_median_price_by_originator_human()`
- **Filter:** insulin_type LIKE '%Human%'

**Implementation:**
```python
with col_human_orig:
    st.markdown("#### Human Insulin - Originator vs Biosimilar")

    with st.spinner("Loading human insulin originator/biosimilar data..."):
        # Prepare filters
        orig_filters_human = {
            'data_collection_period': st.session_state.selected_periods_price,
            'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None,
            'region': local_regions_orig if local_regions_orig else None,
            'sector': local_sectors_orig if local_sectors_orig else None
        }

        chart_df_human_orig = get_median_price_by_originator_human(client, config.TABLES["surveys_repeat"], orig_filters_human)

        if chart_df_human_orig is not None and not chart_df_human_orig.empty:
            # Create Plotly bar chart
            fig_human_orig = go.Figure()

            # Calculate dynamic Y-axis range
            max_price = chart_df_human_orig['median_price_local'].max()
            y_axis_max = max_price * 1.15  # Add 15% padding at top

            # Add bar trace
            fig_human_orig.add_trace(go.Bar(
                x=chart_df_human_orig['insulin_originator_biosimilar'].tolist(),
                y=chart_df_human_orig['median_price_local'].tolist(),
                name='Median Price-Local',
                marker=dict(
                    color='#17becf',  # Teal color
                    line=dict(color='#0e7c8f', width=1)
                ),
                text=[f'{val:,.0f}' for val in chart_df_human_orig['median_price_local'].tolist()],
                textposition='outside',
                textfont=dict(size=11),
                hovertemplate='<b>%{x}</b><br>' +
                              'Median Price: %{y:,.2f}<br>' +
                              '<extra></extra>'
            ))

            # Update layout
            fig_human_orig.update_layout(
                xaxis_title='Type',
                yaxis_title='Median price - Local',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=450,
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
                margin=dict(t=40, b=60, l=60, r=20),
                hovermode='closest'
            )

            # Display chart
            st.plotly_chart(fig_human_orig, use_container_width=True)
        else:
            st.info("No human insulin originator/biosimilar data available for the selected filters")
```

### 3.3 Analogue Insulin Chart (Right Column)

**Chart Specifications:**
- **Title:** "Analogue Insulin - Originator vs Biosimilar"
- **Chart Type:** Clustered Bar Chart (Plotly Graph Objects)
- **X-axis:** Categories (Originator Brand, Biosimilar)
- **Y-axis:** Median Price - Local (same specs as Human chart)
- **Bar Color:** Teal/Dark Blue (`#17becf`)
- **Value Labels:** Display median price value on top of each bar
- **Legend:** "Median Price-Local"

**Data Source:**
- **Table:** `adl_surveys_repeat`
- **Function:** New function `get_median_price_by_originator_analogue()`
- **Filter:** insulin_type LIKE '%Analogue%'

**Implementation:**
```python
with col_analogue_orig:
    st.markdown("#### Analogue Insulin - Originator vs Biosimilar")

    with st.spinner("Loading analogue insulin originator/biosimilar data..."):
        # Prepare filters
        orig_filters_analogue = {
            'data_collection_period': st.session_state.selected_periods_price,
            'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None,
            'region': local_regions_orig if local_regions_orig else None,
            'sector': local_sectors_orig if local_sectors_orig else None
        }

        chart_df_analogue_orig = get_median_price_by_originator_analogue(client, config.TABLES["surveys_repeat"], orig_filters_analogue)

        if chart_df_analogue_orig is not None and not chart_df_analogue_orig.empty:
            # Create Plotly bar chart
            fig_analogue_orig = go.Figure()

            # Calculate dynamic Y-axis range
            max_price = chart_df_analogue_orig['median_price_local'].max()
            y_axis_max = max_price * 1.15  # Add 15% padding at top

            # Add bar trace
            fig_analogue_orig.add_trace(go.Bar(
                x=chart_df_analogue_orig['insulin_originator_biosimilar'].tolist(),
                y=chart_df_analogue_orig['median_price_local'].tolist(),
                name='Median Price-Local',
                marker=dict(
                    color='#17becf',  # Teal color
                    line=dict(color='#0e7c8f', width=1)
                ),
                text=[f'{val:,.0f}' for val in chart_df_analogue_orig['median_price_local'].tolist()],
                textposition='outside',
                textfont=dict(size=11),
                hovertemplate='<b>%{x}</b><br>' +
                              'Median Price: %{y:,.2f}<br>' +
                              '<extra></extra>'
            ))

            # Update layout
            fig_analogue_orig.update_layout(
                xaxis_title='Type',
                yaxis_title='Median price - Local',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=450,
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
                margin=dict(t=40, b=60, l=60, r=20),
                hovermode='closest'
            )

            # Display chart
            st.plotly_chart(fig_analogue_orig, use_container_width=True)
        else:
            st.info("No analogue insulin originator/biosimilar data available for the selected filters")
```

---

## 4. Database Functions to Implement

### 4.1 Function Summary

Add to `database/bigquery_client.py`:

| Function Name | Purpose | Table | Returns |
|---------------|---------|-------|---------|
| `get_median_price_by_originator_human()` | Get median prices by originator/biosimilar for human insulin | `adl_surveys_repeat` | originator_biosimilar, median_price_local, product_count |
| `get_median_price_by_originator_analogue()` | Get median prices by originator/biosimilar for analogue insulin | `adl_surveys_repeat` | originator_biosimilar, median_price_local, product_count |

### 4.2 Function: get_median_price_by_originator_human()

```python
@st.cache_data(ttl=600)
def get_median_price_by_originator_human(_client, table_name, filters):
    """
    Get median insulin prices by originator/biosimilar for human insulin.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        filters (dict): Filters (data_collection_period, country, region, sector)

    Returns:
        pandas DataFrame with columns:
            - insulin_originator_biosimilar (str)
            - median_price_local (float)
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

    # Human insulin type filter
    where_clauses.append("insulin_type LIKE '%Human%'")

    # Originator/biosimilar filters
    where_clauses.append("insulin_originator_biosimilar IS NOT NULL")
    where_clauses.append("insulin_originator_biosimilar != '---'")

    # Out-of-pocket payment filter
    where_clauses.append("(insulin_out_of_pocket = 'Yes' OR insulin_out_of_pocket = 'Some people pay out of pocket')")

    where_clause = " AND ".join(where_clauses)

    # Use the complex median calculation from the plan
    query = f"""
    SELECT
      insulin_originator_biosimilar,
      CASE
        WHEN MOD(COUNT(insulin_standard_price_local), 2) = 1 THEN APPROX_QUANTILES(insulin_standard_price_local, 2)[OFFSET(1)]
        WHEN MOD(COUNT(insulin_standard_price_local), 2) = 0 AND COUNT(insulin_standard_price_local) >= 100 THEN APPROX_QUANTILES(insulin_standard_price_local, 2)[OFFSET(1)]
        ELSE (APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(49)] + APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(51)]) / 2
      END as median_price_local,
      COUNT(1) as product_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_originator_biosimilar
    ORDER BY insulin_originator_biosimilar DESC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting median price by originator (human): {str(e)}")
        return None
```

### 4.3 Function: get_median_price_by_originator_analogue()

```python
@st.cache_data(ttl=600)
def get_median_price_by_originator_analogue(_client, table_name, filters):
    """
    Get median insulin prices by originator/biosimilar for analogue insulin.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        filters (dict): Filters (data_collection_period, country, region, sector)

    Returns:
        pandas DataFrame with columns:
            - insulin_originator_biosimilar (str)
            - median_price_local (float)
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

    # Analogue insulin type filter
    where_clauses.append("insulin_type LIKE '%Analogue%'")

    # Originator/biosimilar filters
    where_clauses.append("insulin_originator_biosimilar IS NOT NULL")
    where_clauses.append("insulin_originator_biosimilar != '---'")

    # Out-of-pocket payment filter
    where_clauses.append("(insulin_out_of_pocket = 'Yes' OR insulin_out_of_pocket = 'Some people pay out of pocket')")

    where_clause = " AND ".join(where_clauses)

    # Use the complex median calculation from the plan
    query = f"""
    SELECT
      insulin_originator_biosimilar,
      CASE
        WHEN MOD(COUNT(insulin_standard_price_local), 2) = 1 THEN APPROX_QUANTILES(insulin_standard_price_local, 2)[OFFSET(1)]
        WHEN MOD(COUNT(insulin_standard_price_local), 2) = 0 AND COUNT(insulin_standard_price_local) >= 100 THEN APPROX_QUANTILES(insulin_standard_price_local, 2)[OFFSET(1)]
        ELSE (APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(49)] + APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(51)]) / 2
      END as median_price_local,
      COUNT(1) as product_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_originator_biosimilar
    ORDER BY insulin_originator_biosimilar DESC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting median price by originator (analogue): {str(e)}")
        return None
```

---

## 5. Code Organization

### 5.1 File Structure

```
/Users/waqas/HAI_demo/
├── app.py                          # Main application file
│   └── [After Phase 5] Tab 2: Price Analysis
│       ├── Phase 1: Global filters (existing)
│       ├── Phase 2: Median price charts (existing)
│       ├── Phase 3: Price by INN (existing)
│       ├── Phase 4: Price by Brand (existing)
│       ├── Phase 5: Median price by Presentation (existing)
│       └── Phase 6: Median price by Originator/Biosimilar (new)
│           ├── Section header
│           ├── Local Region/Sector filters
│           └── Two bar charts (Human and Analogue)
├── database/
│   └── bigquery_client.py         # Add 2 new functions
│       ├── get_median_price_by_originator_human()
│       └── get_median_price_by_originator_analogue()
├── plans/
│   ├── Price_Analysis_plan6.md    # Original plan
│   └── Price_Analysis_plan6_refined.md  # This document
```

### 5.2 Import Updates

Add to `app.py` imports (around line 10-57):

```python
from database.bigquery_client import (
    # ... existing imports ...
    get_median_price_by_originator_human,
    get_median_price_by_originator_analogue
)
```

---

## 6. Implementation Steps

### Step 1: Add Database Functions (30 minutes)
- Add `get_median_price_by_originator_human()` function to `database/bigquery_client.py`
- Add `get_median_price_by_originator_analogue()` function to `database/bigquery_client.py`
- Test queries with sample filters in BigQuery console
- Verify originator/biosimilar types are captured correctly
- Ensure median calculation works as expected

### Step 2: Update Imports (5 minutes)
- Add new function imports to `app.py`
- Run syntax check

### Step 3: Add Section Header (5 minutes)
- Add conditional wrapper for selected periods
- Add section header after Phase 5 (Median price by Presentation)
- Test display when periods selected/unselected

### Step 4: Build Region/Sector Filters (25 minutes)
- Create two-column layout with unique variable names (`col1_orig`, `col2_orig`)
- Implement Region checkbox expander (reuse existing pattern)
- Implement Sector checkbox expander (reuse existing pattern)
- Use unique session state keys (`price_orig_region_*`, `price_orig_sector_*`)
- Test filter interactions and session state

### Step 5: Build Human Insulin Chart (30 minutes)
- Add left column layout
- Implement data fetching with filters
- Create Plotly bar chart with proper styling
- Add teal color scheme
- Set dynamic Y-axis range
- Add value labels on bars
- Test with various filter combinations

### Step 6: Build Analogue Insulin Chart (30 minutes)
- Add right column layout
- Implement data fetching with filters (separate from Human)
- Create Plotly bar chart with identical styling
- Test with various filter combinations

### Step 7: Testing & Validation (30 minutes)
- Run syntax check
- Manual testing of all features
- Cross-filter testing (global + local filters)
- Edge case testing (no data, single category, etc.)
- Verify charts display side by side

**Total Estimated Time:** ~2.5 hours

---

## 7. Testing Strategy

### 7.1 Manual Testing Checklist

**Section Display:**
- [ ] Section only shows when at least one period is selected
- [ ] Section hides when no periods selected
- [ ] Section header displays correctly
- [ ] Section appears after Phase 5 (Median price by Presentation)

**Filter Functionality:**
- [ ] Region checkboxes load with facility counts
- [ ] Sector checkboxes load with facility counts
- [ ] Region filter affects sector options
- [ ] Expander shows correct selection count (N/M selected)
- [ ] Excluded count displays when items unchecked
- [ ] Checkboxes persist state across reruns
- [ ] All regions/sectors selected by default on first load
- [ ] Filters are independent from Phase 2, 3, 4, and 5 filters

**Human Insulin Chart:**
- [ ] Chart displays in left column
- [ ] Title: "Human Insulin - Originator vs Biosimilar"
- [ ] X-axis shows Originator Brand and Biosimilar categories
- [ ] Bars are colored in teal (`#17becf`)
- [ ] Each bar shows median price value on top
- [ ] Y-axis title is "Median price - Local"
- [ ] Y-axis range is dynamic (0 to max + 15% padding)
- [ ] Legend shows "Median Price-Local"
- [ ] Hover tooltips show category and price
- [ ] Chart responds to filter changes
- [ ] Only human insulin data displayed

**Analogue Insulin Chart:**
- [ ] Chart displays in right column
- [ ] Title: "Analogue Insulin - Originator vs Biosimilar"
- [ ] X-axis shows Originator Brand and Biosimilar categories
- [ ] Bars are colored in teal (`#17becf`)
- [ ] Each bar shows median price value on top
- [ ] Y-axis title is "Median price - Local"
- [ ] Y-axis range is dynamic (0 to max + 15% padding)
- [ ] Legend shows "Median Price-Local"
- [ ] Hover tooltips show category and price
- [ ] Chart responds to filter changes
- [ ] Only analogue insulin data displayed

**Data Integrity:**
- [ ] Human chart only shows insulin_type LIKE '%Human%'
- [ ] Analogue chart only shows insulin_type LIKE '%Analogue%'
- [ ] No "---" values in originator/biosimilar field
- [ ] Median values are positive numbers
- [ ] Product counts are positive integers
- [ ] Out-of-pocket filter applied correctly
- [ ] Charts display side by side properly

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
3. Scroll to "Median price - By originator brands and biosimilars" section
4. Verify section appears after "Median price - By presentation"
5. Test Region checkbox filter
6. Test Sector checkbox filter (depends on Region)
7. Verify both charts display side by side
8. Verify Human chart shows only human insulin
9. Verify Analogue chart shows only analogue insulin
10. Verify bars are teal colored
11. Verify value labels on bars
12. Hover over bars to verify tooltips
13. Change filters and verify charts update
14. Uncheck all regions - verify info messages
15. Deselect all periods - verify section hides

---

## 8. Key Design Decisions

### 8.1 Two Separate Functions vs Single Function
**Decision:** Create two separate functions for Human and Analogue

**Rationale:**
- Clear separation of concerns
- Easier to maintain and debug
- Allows independent caching
- Follows pattern from Phase 4
- More flexible for future enhancements

### 8.2 Side-by-Side Layout
**Decision:** Display Human and Analogue charts side by side

**Rationale:**
- Easy visual comparison between Human and Analogue
- Consistent with Phase 4 (Brand tables)
- Efficient use of screen space
- Professional dashboard appearance
- Users can compare prices at a glance

### 8.3 Chart Type: Bar Chart
**Decision:** Use vertical bar chart instead of horizontal

**Rationale:**
- Only 2 categories (Originator, Biosimilar) - vertical works well
- Consistent with Phase 5 presentation chart
- Standard for price comparisons
- Easy to compare heights
- Clean, professional appearance

### 8.4 Color Scheme: Single Color
**Decision:** Use single teal color for all bars

**Rationale:**
- Consistent with Phase 5
- Focus on comparing Human vs Analogue, not Originator vs Biosimilar
- Cleaner visual design
- Categories already distinguished by X-axis position
- Specified in plan requirements

### 8.5 Median Calculation Approach
**Decision:** Use complex CASE-based median calculation from plan

**Rationale:**
- Specified in plan requirements
- Handles odd/even count appropriately
- More accurate for different data sizes
- Uses APPROX_QUANTILES for large datasets
- Consistent with Phase 4 and 5

### 8.6 Dynamic Y-axis Range
**Decision:** Use dynamic Y-axis (0 to max + 15% padding) for each chart

**Rationale:**
- Each chart adapts to its own data range
- Human and Analogue may have different price ranges
- Prevents empty space or data clipping
- Better data visualization practice
- Consistent with previous phases

### 8.7 Filter Independence
**Decision:** Phase 6 has its own Region/Sector filters

**Rationale:**
- Allows independent analysis
- Follows pattern from Phase 2-5
- Prevents unintended filter interactions
- Better user experience for focused analysis

---

## 9. Session State Architecture

### 9.1 New Session State Keys (Phase 6)

**Checkbox States (Dynamic - one per region/sector):**
```python
# Region checkboxes (Originator/Biosimilar section)
st.session_state.price_orig_region_{region_name}  # bool - one per region

# Sector checkboxes (Originator/Biosimilar section)
st.session_state.price_orig_sector_{sector_name}  # bool - one per sector
```

**Example:**
```python
st.session_state.price_orig_region_East_Africa = True
st.session_state.price_orig_region_West_Africa = False
st.session_state.price_orig_sector_Public = True
st.session_state.price_orig_sector_Private = True
```

### 9.2 Existing Session State Keys (Not Modified)
```python
# Phase 1 - Global filters
st.session_state.selected_countries_price  # List[str]
st.session_state.selected_periods_price    # List[str]

# Phase 2-5 - Local filters (not reused)
st.session_state.price_region_{region_name}
st.session_state.price_sector_{sector_name}
st.session_state.price_inn_region_{region_name}
st.session_state.price_inn_sector_{sector_name}
st.session_state.price_brand_region_{region_name}
st.session_state.price_brand_sector_{sector_name}
st.session_state.price_pres_region_{region_name}
st.session_state.price_pres_sector_{sector_name}
```

---

## 10. Potential Issues & Solutions

### Issue 1: Only One Category Available
**Symptom:** Only Originator or only Biosimilar data available
**Solution:**
- Chart still displays correctly
- Single bar shown
- This is expected behavior
- Info message if no data at all

### Issue 2: Very Different Price Ranges
**Symptom:** Human and Analogue have vastly different price ranges
**Solution:**
- Each chart uses its own dynamic Y-axis
- Scales independently
- This is intentional design
- Allows proper visualization of each dataset

### Issue 3: Missing originator_biosimilar Data
**Symptom:** Some filters return no data
**Solution:**
- Display info message when no data available
- This is expected behavior
- User can adjust filters
- Clear messaging prevents confusion

### Issue 4: Query Performance
**Symptom:** Slow query execution with complex median calculation
**Solution:**
- Use caching (@st.cache_data with ttl=600)
- BigQuery optimized for this type of aggregation
- Monitor query execution time
- Typically only 2 categories (fast)

### Issue 5: Label Overlap
**Symptom:** "Originator Brand" and "Biosimilar" labels too long
**Solution:**
- X-axis should fit 2 categories easily
- Consider shorter labels if needed
- Test with actual data
- Tooltips show full category name

---

## 11. Acceptance Criteria

Phase 6 implementation is complete when:

- [ ] **AC1:** Section header "Median price - By originator brands and biosimilars" displays
- [ ] **AC2:** Section appears after "Median price - By presentation"
- [ ] **AC3:** Section only shows when at least one period is selected
- [ ] **AC4:** Region checkbox filter loads with facility counts (independent from other phases)
- [ ] **AC5:** Sector checkbox filter loads with facility counts (independent from other phases)
- [ ] **AC6:** Sector filter options update when Region filter changes
- [ ] **AC7:** Expanders show selection count "N/M selected"
- [ ] **AC8:** Expanders show excluded count when items unchecked
- [ ] **AC9:** All checkboxes selected by default on first load
- [ ] **AC10:** Two charts display side by side
- [ ] **AC11:** Human chart shows only human insulin data
- [ ] **AC12:** Analogue chart shows only analogue insulin data
- [ ] **AC13:** Both charts have correct titles
- [ ] **AC14:** Bars are colored in teal (`#17becf`)
- [ ] **AC15:** Value labels displayed on top of bars
- [ ] **AC16:** Y-axis title is "Median price - Local" for both
- [ ] **AC17:** Y-axis range is dynamic for each chart independently
- [ ] **AC18:** Legend shows "Median Price-Local" on both charts
- [ ] **AC19:** Hover tooltips show category and median price
- [ ] **AC20:** Charts respond to filter changes
- [ ] **AC21:** X-axis shows Originator Brand and Biosimilar
- [ ] **AC22:** Info messages display when no data available
- [ ] **AC23:** No errors in console or BigQuery logs
- [ ] **AC24:** Both files pass syntax check

---

## 12. Color Palette Reference

### Chart Colors (Phase 6)
- **Bar Color:** `#17becf` (teal)
- **Bar Border:** `#0e7c8f` (dark teal)

### UI Colors (Existing)
- **Primary Blue:** `#1f77b4`
- **Secondary Orange:** `#ff7f0e`
- **Background Light:** `#f8f9fa`
- **Info Box Background:** `#e3f2fd`
- **Info Box Border:** `#2196f3`

---

## 13. Dependencies

### Required Packages (Already Installed)
- `streamlit` - UI framework
- `pandas` - Data manipulation
- `plotly` - Charts (plotly.graph_objects)
- `google-cloud-bigquery` - BigQuery client

### Required Files
- `app.py` - Main application (modify)
- `database/bigquery_client.py` - Database functions (add 2 new functions)
- `config.py` - Configuration settings (no changes)
- `.env` - Environment variables (no changes)

### BigQuery Requirements
- **Project:** `hai-dev`
- **Dataset:** `facilities`
- **Tables:**
  - `adl_surveys_repeat` (for originator/biosimilar price data and filters)

**Columns needed in adl_surveys_repeat:**
- `form_case__case_id` (STRING)
- `data_collection_period` (STRING)
- `country` (STRING)
- `region` (STRING)
- `sector` (STRING)
- `insulin_type` (STRING) - Contains "Human" or "Analogue"
- `insulin_originator_biosimilar` (STRING) - "Originator Brand" or "Biosimilar"
- `insulin_standard_price_local` (FLOAT64) - Price in local currency
- `insulin_out_of_pocket` (STRING) - Out-of-pocket payment indicator

---

## 14. Expected Categories

**insulin_originator_biosimilar values:**
- Originator Brand
- Biosimilar
- (Any other variations in the data)

**Note:** Actual categories will be dynamic based on data, but typically only 2 categories expected.

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-09 | AI Assistant | Initial refined plan from Price_Analysis_plan6.md |

---

**End of Refined Implementation Plan - Phase 6**
