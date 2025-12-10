# Price Analysis Tab - Phase 5 Implementation Plan (Refined)

## Overview
This document provides a detailed implementation plan for Phase 5 of the Price Analysis tab. Phase 5 adds a new "Median price - By presentation" visualization section that displays a clustered bar chart showing median prices for different insulin presentation types (Vial, Pre-filled Pen, Cartridge, etc.). The implementation follows the existing architecture patterns established in Phase 1-4.

## Phase 5 Scope
Phase 5 focuses on building presentation-based price visualization:
- "Median price - By presentation" section header
- Region and Sector expandable checkbox filters (local to this section)
- Clustered bar chart showing median prices by presentation type
- Dynamic Y-axis based on price range
- Professional styling with value labels on bars
- Angled X-axis labels for readability

---

## 1. Section Structure

### 1.1 Section Header

**Location:** `app.py` - Inside `with tab2:` block, after Phase 4 ("Price - By Brand" section)

**Condition:** Only display when at least one Data Collection Period is selected

**Implementation:**
```python
if st.session_state.selected_periods_price:
    # Phase 5: Median price - By presentation Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>Median price - By presentation</h3></div>', unsafe_allow_html=True)
```

**CSS:** Uses existing `.section-header` class (already defined in app.py)

---

## 2. Local Filter Controls (Region and Sector)

### 2.1 Two-Column Layout for Filters

**Location:** Immediately after section header

**Implementation Pattern:**
```python
    # Local filters for Presentation price analysis
    st.markdown("<br>", unsafe_allow_html=True)
    col1_pres, col2_pres = st.columns(2)
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
with col1_pres:
    st.markdown("**Region**")
    with st.spinner("Loading regions..."):
        # Build global filters dict from session state
        global_filters_pres = {
            'data_collection_period': st.session_state.selected_periods_price,
            'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None
        }

        region_df_pres = get_price_regions(client, config.TABLES["surveys_repeat"], global_filters_pres)

        if region_df_pres is not None and not region_df_pres.empty:
            # Build region options with counts
            region_data_pres = []
            for _, row in region_df_pres.iterrows():
                region = row['region']
                count = row['facility_count']
                region_data_pres.append((region, count))

            total_regions_pres = len(region_data_pres)

            # Initialize checkboxes in session state
            for region, count in region_data_pres:
                checkbox_key = f"price_pres_region_{region}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

            # Count selected items
            selected_count_pres = sum(
                1 for region, _ in region_data_pres
                if st.session_state.get(f"price_pres_region_{region}", True)
            )
            excluded_count_pres = total_regions_pres - selected_count_pres

            # Create expander with selection summary
            with st.expander(
                f"Select Regions ({selected_count_pres}/{total_regions_pres} selected)",
                expanded=False
            ):
                if excluded_count_pres > 0:
                    st.caption(f"🚫 {excluded_count_pres} item{'s' if excluded_count_pres != 1 else ''} excluded")

                # Create checkboxes
                local_regions_pres = []
                for region, count in region_data_pres:
                    checkbox_key = f"price_pres_region_{region}"
                    is_checked = st.checkbox(
                        f"{region} ({count:,})",
                        value=st.session_state.get(checkbox_key, True),
                        key=checkbox_key
                    )
                    if is_checked:
                        local_regions_pres.append(region)
        else:
            local_regions_pres = []
            st.info("No region data available")
```

**Session State Keys:** `price_pres_region_{region_name}` (one per region, boolean)

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
with col2_pres:
    st.markdown("**Sector**")
    with st.spinner("Loading sectors..."):
        sector_df_pres = get_price_sectors(client, config.TABLES["surveys_repeat"], global_filters_pres, local_regions_pres)

        if sector_df_pres is not None and not sector_df_pres.empty:
            # Build sector options with counts
            sector_data_pres = []
            for _, row in sector_df_pres.iterrows():
                sector = row['sector']
                count = row['facility_count']
                sector_data_pres.append((sector, count))

            total_sectors_pres = len(sector_data_pres)

            # Initialize checkboxes in session state
            for sector, count in sector_data_pres:
                checkbox_key = f"price_pres_sector_{sector}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

            # Count selected items
            selected_count_pres_sec = sum(
                1 for sector, _ in sector_data_pres
                if st.session_state.get(f"price_pres_sector_{sector}", True)
            )
            excluded_count_pres_sec = total_sectors_pres - selected_count_pres_sec

            # Create expander with selection summary
            with st.expander(
                f"Select Sectors ({selected_count_pres_sec}/{total_sectors_pres} selected)",
                expanded=False
            ):
                if excluded_count_pres_sec > 0:
                    st.caption(f"🚫 {excluded_count_pres_sec} item{'s' if excluded_count_pres_sec != 1 else ''} excluded")

                # Create checkboxes
                local_sectors_pres = []
                for sector, count in sector_data_pres:
                    checkbox_key = f"price_pres_sector_{sector}"
                    is_checked = st.checkbox(
                        f"{sector} ({count:,})",
                        value=st.session_state.get(checkbox_key, True),
                        key=checkbox_key
                    )
                    if is_checked:
                        local_sectors_pres.append(sector)
        else:
            local_sectors_pres = []
            st.info("No sector data available")
```

**Session State Keys:** `price_pres_sector_{sector_name}` (one per sector, boolean)

---

## 3. Chart: Median price - By presentation (Clustered Bar Chart)

### 3.1 Section Header

**Location:** After the Region/Sector filters

**Implementation:**
```python
    # Chart: Median price - By presentation
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Median price - By presentation")
```

### 3.2 Chart Specifications

**Chart Type:** Clustered Bar Chart (Plotly Graph Objects)

**Data Source:**
- **Table:** `adl_surveys_repeat`
- **Function:** New function `get_median_price_by_presentation()`

**Axes:**
- **X-axis:** Insulin Presentation (dynamic, based on `insulin_presentation` column values)
  - Examples: Vial, Pre-filled Pen, Cartridge, etc.
  - Labels angled at -45° for readability (if needed)
  - Sorted by presentation name (ORDER BY insulin_presentation DESC per plan)
- **Y-axis:** Median Price - Local
  - Title: "Median price - Local"
  - Dynamic range: 0 to max median price + 15% padding
  - Tick format: comma-separated with 2 decimals

**Visual Properties:**
- **Bar Color:** Teal/Dark Blue (`#17becf` or `#1f77b4`)
- **Bar Shading:** Each bar shows the median price value
- **Value Labels:** Display median price value on top of each bar
- **Legend:** Single legend entry "Median Price-Local"
- **Layout:** Clean, professional appearance with transparent background

**Data Filtering:**
- Filter by selected regions and sectors
- Include out-of-pocket payments
- Exclude NULL presentation values

### 3.3 Implementation Pattern

```python
    with st.spinner("Loading median price by presentation data..."):
        # Prepare filters
        pres_price_filters = {
            'data_collection_period': st.session_state.selected_periods_price,
            'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None,
            'region': local_regions_pres if local_regions_pres else None,
            'sector': local_sectors_pres if local_sectors_pres else None
        }

        chart_df_pres = get_median_price_by_presentation(client, config.TABLES["surveys_repeat"], pres_price_filters)

        if chart_df_pres is not None and not chart_df_pres.empty:
            # Create Plotly bar chart
            fig_pres = go.Figure()

            # Calculate dynamic Y-axis range
            max_price = chart_df_pres['median_price_local'].max()
            y_axis_max = max_price * 1.15  # Add 15% padding at top

            # Add bar trace
            fig_pres.add_trace(go.Bar(
                x=chart_df_pres['insulin_presentation'].tolist(),
                y=chart_df_pres['median_price_local'].tolist(),
                name='Median Price-Local',
                marker=dict(
                    color='#17becf',  # Teal color
                    line=dict(color='#0e7c8f', width=1)
                ),
                text=[f'{val:,.0f}' for val in chart_df_pres['median_price_local'].tolist()],
                textposition='outside',
                textfont=dict(size=11),
                hovertemplate='<b>%{x}</b><br>' +
                              'Median Price: %{y:,.2f}<br>' +
                              '<extra></extra>'
            ))

            # Update layout
            fig_pres.update_layout(
                title='Median Price by Insulin Presentation',
                xaxis_title='Insulin Presentation',
                yaxis_title='Median price - Local',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=500,
                xaxis=dict(
                    tickangle=-45,  # Angle labels for readability
                    tickfont=dict(size=11)
                ),
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
                margin=dict(t=80, b=120, l=60, r=40),
                hovermode='closest'
            )

            # Display chart
            st.plotly_chart(fig_pres, use_container_width=True)
        else:
            st.info("No median price by presentation data available for the selected filters")
```

### 3.4 Database Query Specification

**Function Name:** `get_median_price_by_presentation(_client, table_name, filters)`

**Data Source:**
- Uses `insulin_presentation` column from `adl_surveys_repeat` table
- Calculates median using complex CASE-based logic (from plan spec)
- Groups by presentation type

**Query Structure:**
```sql
SELECT
  insulin_presentation,
  CASE
    WHEN MOD(COUNT(insulin_standard_price_local), 2) = 1 THEN APPROX_QUANTILES(insulin_standard_price_local, 2)[OFFSET(1)]
    WHEN MOD(COUNT(insulin_standard_price_local), 2) = 0 AND COUNT(insulin_standard_price_local) >= 100 THEN APPROX_QUANTILES(insulin_standard_price_local, 2)[OFFSET(1)]
    ELSE (APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(49)] + APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(51)]) / 2
  END as median_price_local,
  COUNT(1) as product_count
FROM `{project}.{dataset}.{table_name}`
WHERE
  insulin_presentation IS NOT NULL
  AND (
    insulin_out_of_pocket = 'Yes'
    OR insulin_out_of_pocket = 'Some people pay out of pocket'
  )
  AND data_collection_period IN (...)  -- from filters
  -- Additional filters for country, region, sector
GROUP BY insulin_presentation
ORDER BY insulin_presentation DESC
```

**Returns:** DataFrame with columns:
- `insulin_presentation` (str) - Presentation type (e.g., Vial, Pre-filled Pen, Cartridge)
- `median_price_local` (float) - Median price in local currency
- `product_count` (int) - Number of products

**Optional Metrics (for future enhancement):**
- `median_price_usd` (float) - Median price in USD using same CASE logic

---

## 4. Database Functions to Implement

### 4.1 Function Summary

Add to `database/bigquery_client.py`:

| Function Name | Purpose | Table | Returns |
|---------------|---------|-------|---------|
| `get_median_price_by_presentation()` | Get median prices by presentation type | `adl_surveys_repeat` | presentation, median_price_local, product_count |

### 4.2 Function: get_median_price_by_presentation()

```python
@st.cache_data(ttl=600)
def get_median_price_by_presentation(_client, table_name, filters):
    """
    Get median insulin prices by presentation type.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        filters (dict): Filters (data_collection_period, country, region, sector)

    Returns:
        pandas DataFrame with columns:
            - insulin_presentation (str)
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

    # Presentation filters
    where_clauses.append("insulin_presentation IS NOT NULL")

    # Out-of-pocket payment filter
    where_clauses.append("(insulin_out_of_pocket = 'Yes' OR insulin_out_of_pocket = 'Some people pay out of pocket')")

    where_clause = " AND ".join(where_clauses)

    # Use the complex median calculation from the plan
    query = f"""
    SELECT
      insulin_presentation,
      CASE
        WHEN MOD(COUNT(insulin_standard_price_local), 2) = 1 THEN APPROX_QUANTILES(insulin_standard_price_local, 2)[OFFSET(1)]
        WHEN MOD(COUNT(insulin_standard_price_local), 2) = 0 AND COUNT(insulin_standard_price_local) >= 100 THEN APPROX_QUANTILES(insulin_standard_price_local, 2)[OFFSET(1)]
        ELSE (APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(49)] + APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(51)]) / 2
      END as median_price_local,
      COUNT(1) as product_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_presentation
    ORDER BY insulin_presentation DESC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting median price by presentation: {str(e)}")
        return None
```

---

## 5. Code Organization

### 5.1 File Structure

```
/Users/waqas/HAI_demo/
├── app.py                          # Main application file
│   └── [After Phase 4] Tab 2: Price Analysis
│       ├── Phase 1: Global filters (existing)
│       ├── Phase 2: Median price charts (existing)
│       ├── Phase 3: Price by INN (existing)
│       ├── Phase 4: Price by Brand (existing)
│       └── Phase 5: Median price by Presentation (new)
│           ├── Section header
│           ├── Local Region/Sector filters
│           └── Clustered bar chart
├── database/
│   └── bigquery_client.py         # Add 1 new function
│       └── get_median_price_by_presentation()
├── plans/
│   ├── Price_Analysis_plan5.md    # Original plan
│   └── Price_Analysis_plan5_refined.md  # This document
```

### 5.2 Import Updates

Add to `app.py` imports (around line 10-56):

```python
from database.bigquery_client import (
    # ... existing imports ...
    get_median_price_by_presentation
)
```

---

## 6. Implementation Steps

### Step 1: Add Database Function (25 minutes)
- Add `get_median_price_by_presentation()` function to `database/bigquery_client.py`
- Test query with sample filters in BigQuery console
- Verify presentation types are captured correctly
- Ensure median calculation works as expected

### Step 2: Update Imports (5 minutes)
- Add new function import to `app.py`
- Run syntax check

### Step 3: Add Section Header (5 minutes)
- Add conditional wrapper for selected periods
- Add section header after Phase 4 (Price By Brand)
- Test display when periods selected/unselected

### Step 4: Build Region/Sector Filters (25 minutes)
- Create two-column layout with unique variable names (`col1_pres`, `col2_pres`)
- Implement Region checkbox expander (reuse existing pattern)
- Implement Sector checkbox expander (reuse existing pattern)
- Use unique session state keys (`price_pres_region_*`, `price_pres_sector_*`)
- Test filter interactions and session state

### Step 5: Build Clustered Bar Chart (40 minutes)
- Add section header
- Implement data fetching with filters
- Create Plotly bar chart with proper styling
- Add teal/dark blue color scheme
- Set dynamic Y-axis range
- Add value labels on bars
- Angle X-axis labels at -45°
- Add legend
- Test with various filter combinations

### Step 6: Testing & Validation (30 minutes)
- Run syntax check
- Manual testing of all features
- Cross-filter testing (global + local filters)
- Edge case testing (no data, single presentation, etc.)
- Verify chart responsiveness

**Total Estimated Time:** ~2.25 hours

---

## 7. Testing Strategy

### 7.1 Manual Testing Checklist

**Section Display:**
- [ ] Section only shows when at least one period is selected
- [ ] Section hides when no periods selected
- [ ] Section header displays correctly
- [ ] Section appears after Phase 4 (Price By Brand)

**Filter Functionality:**
- [ ] Region checkboxes load with facility counts
- [ ] Sector checkboxes load with facility counts
- [ ] Region filter affects sector options
- [ ] Expander shows correct selection count (N/M selected)
- [ ] Excluded count displays when items unchecked
- [ ] Checkboxes persist state across reruns
- [ ] All regions/sectors selected by default on first load
- [ ] Filters are independent from Phase 2, 3, and 4 filters

**Clustered Bar Chart:**
- [ ] Chart displays with presentation types on X-axis
- [ ] Bars are sorted by presentation name (descending)
- [ ] Bars are colored in teal/dark blue
- [ ] Each bar shows median price value
- [ ] Value labels displayed on top of bars
- [ ] X-axis labels angled at -45° for readability
- [ ] Y-axis title is "Median price - Local"
- [ ] Y-axis range is dynamic (0 to max + 15% padding)
- [ ] Y-axis adjusts when filters change
- [ ] Legend shows "Median Price-Local"
- [ ] Hover tooltips show presentation and price
- [ ] Chart responds to filter changes
- [ ] Professional appearance with transparent background

**Data Integrity:**
- [ ] Presentation types correctly pulled from `insulin_presentation` column
- [ ] All presentation types present (based on available data)
- [ ] Median values are positive numbers
- [ ] Product counts are positive integers
- [ ] No NULL presentation types displayed
- [ ] Out-of-pocket filter applied correctly

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
3. Scroll to "Median price - By presentation" section
4. Verify section appears after "Price - By Brand"
5. Test Region checkbox filter
6. Test Sector checkbox filter (depends on Region)
7. Verify bar chart displays with teal/dark blue bars
8. Verify value labels on bars
9. Verify angled X-axis labels
10. Hover over bars to verify tooltips
11. Change filters and verify chart updates
12. Uncheck all regions - verify info message
13. Deselect all periods - verify section hides

---

## 8. Key Design Decisions

### 8.1 Chart Type: Clustered Bar Chart
**Decision:** Use clustered bar chart (vertical bars) instead of horizontal bars

**Rationale:**
- Vertical bars are standard for price comparisons
- X-axis can accommodate angled labels for readability
- Better visual hierarchy for categorical data
- Consistent with dashboard design patterns
- Easier to compare heights than horizontal lengths

### 8.2 Color Scheme: Teal/Dark Blue
**Decision:** Use teal (`#17becf`) as primary bar color

**Rationale:**
- Specified in plan requirements
- Distinct from other chart colors in dashboard
- Professional and modern appearance
- Good contrast against white background
- Accessible for color-blind users

### 8.3 Median Calculation Approach
**Decision:** Use the complex CASE-based median calculation from plan

**Rationale:**
- Specified in plan requirements
- Handles odd/even count appropriately
- More accurate for different data sizes
- Uses APPROX_QUANTILES for large datasets
- Consistent with other price functions

### 8.4 X-axis Label Rotation
**Decision:** Angle labels at -45°

**Rationale:**
- Specified in plan ("if needed")
- Prevents label overlap for long presentation names
- Standard practice for categorical charts
- Improves readability
- Professional appearance

### 8.5 Dynamic Y-axis Range
**Decision:** Use dynamic Y-axis (0 to max + 15% padding) instead of fixed range

**Rationale:**
- Adapts to actual price ranges in filtered data
- Prevents empty space when prices are low
- Prevents data clipping when prices are high
- 15% padding provides visual breathing room
- Better data visualization practice

### 8.6 Single Bar Color vs Multiple Colors
**Decision:** Use single color (teal) for all bars

**Rationale:**
- Simplified visual design
- Focuses attention on price values, not categories
- Cleaner legend (single entry)
- No need to differentiate by color
- Presentation type already distinguished by X-axis position

### 8.7 Value Labels on Bars
**Decision:** Display median price value on top of each bar

**Rationale:**
- Provides exact values without hovering
- Improves data readability
- Standard practice for bar charts
- Helps with quick comparisons
- Professional dashboard appearance

---

## 9. Session State Architecture

### 9.1 New Session State Keys (Phase 5)

**Checkbox States (Dynamic - one per region/sector):**
```python
# Region checkboxes (Presentation section)
st.session_state.price_pres_region_{region_name}  # bool - one per region

# Sector checkboxes (Presentation section)
st.session_state.price_pres_sector_{sector_name}  # bool - one per sector
```

**Example:**
```python
st.session_state.price_pres_region_East_Africa = True
st.session_state.price_pres_region_West_Africa = False
st.session_state.price_pres_sector_Public = True
st.session_state.price_pres_sector_Private = True
```

### 9.2 Existing Session State Keys (Not Modified)
```python
# Phase 1 - Global filters
st.session_state.selected_countries_price  # List[str]
st.session_state.selected_periods_price    # List[str]

# Phase 2 - Local filters
st.session_state.price_region_{region_name}
st.session_state.price_sector_{sector_name}

# Phase 3 - INN local filters
st.session_state.price_inn_region_{region_name}
st.session_state.price_inn_sector_{region_name}

# Phase 4 - Brand local filters
st.session_state.price_brand_region_{region_name}
st.session_state.price_brand_sector_{sector_name}
st.session_state.price_brand_human_page  # int
st.session_state.price_brand_analogue_page  # int
```

---

## 10. Potential Issues & Solutions

### Issue 1: Long Presentation Names
**Symptom:** Presentation names too long for X-axis labels
**Solution:**
- Angle labels at -45° (already planned)
- Increase bottom margin if needed
- Consider abbreviations in tooltips
- Test with actual data to verify readability

### Issue 2: Few Presentation Types
**Symptom:** Only 2-3 presentation types available
**Solution:**
- Chart still displays correctly
- Bars may appear wider
- This is expected behavior
- No action needed

### Issue 3: Very High Price Values
**Symptom:** Extreme outliers skew Y-axis range
**Solution:**
- Dynamic Y-axis already handles this
- 15% padding prevents clipping
- Consider adding note about outliers
- Hover tooltips show exact values

### Issue 4: Missing Presentation Data
**Symptom:** Some filters return no data
**Solution:**
- Display info message when no data available
- This is expected behavior
- User can adjust filters
- Clear messaging prevents confusion

### Issue 5: Query Performance
**Symptom:** Slow query execution with complex median calculation
**Solution:**
- Use caching (@st.cache_data with ttl=600)
- BigQuery optimized for this type of aggregation
- Monitor query execution time
- Presentation types typically fewer than brands/INNs

---

## 11. Acceptance Criteria

Phase 5 implementation is complete when:

- [ ] **AC1:** Section header "Median price - By presentation" displays
- [ ] **AC2:** Section appears after "Price - By Brand"
- [ ] **AC3:** Section only shows when at least one period is selected
- [ ] **AC4:** Region checkbox filter loads with facility counts (independent from other phases)
- [ ] **AC5:** Sector checkbox filter loads with facility counts (independent from other phases)
- [ ] **AC6:** Sector filter options update when Region filter changes
- [ ] **AC7:** Expanders show selection count "N/M selected"
- [ ] **AC8:** Expanders show excluded count when items unchecked
- [ ] **AC9:** All checkboxes selected by default on first load
- [ ] **AC10:** Clustered bar chart displays with presentation types on X-axis
- [ ] **AC11:** Bars are colored in teal/dark blue (`#17becf`)
- [ ] **AC12:** Each bar shows median price value on top
- [ ] **AC13:** X-axis labels angled at -45° for readability
- [ ] **AC14:** Y-axis title is "Median price - Local"
- [ ] **AC15:** Y-axis range is dynamic (0 to max + 15% padding)
- [ ] **AC16:** Legend shows "Median Price-Local"
- [ ] **AC17:** Hover tooltips show presentation and median price
- [ ] **AC18:** Chart responds to filter changes
- [ ] **AC19:** Presentation types sorted by name (descending)
- [ ] **AC20:** Info message displays when no data available
- [ ] **AC21:** No errors in console or BigQuery logs
- [ ] **AC22:** Both files pass syntax check

---

## 12. Color Palette Reference

### Chart Colors (Phase 5)
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
- `database/bigquery_client.py` - Database functions (add 1 new function)
- `config.py` - Configuration settings (no changes)
- `.env` - Environment variables (no changes)

### BigQuery Requirements
- **Project:** `hai-dev`
- **Dataset:** `facilities`
- **Tables:**
  - `adl_surveys_repeat` (for presentation price data and filters)

**Columns needed in adl_surveys_repeat:**
- `form_case__case_id` (STRING)
- `data_collection_period` (STRING)
- `country` (STRING)
- `region` (STRING)
- `sector` (STRING)
- `insulin_presentation` (STRING) - Presentation type (Vial, Pre-filled Pen, etc.)
- `insulin_standard_price_local` (FLOAT64) - Price in local currency
- `insulin_out_of_pocket` (STRING) - Out-of-pocket payment indicator

---

## 14. Expected Presentation Types

Based on common insulin packaging:
- Vial
- Pre-filled Pen
- Cartridge
- Pen Cartridge
- Prefilled Syringe
- Other variations

**Note:** Actual presentation types will be dynamic based on data in the `insulin_presentation` column.

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-09 | AI Assistant | Initial refined plan from Price_Analysis_plan5.md |

---

**End of Refined Implementation Plan - Phase 5**
