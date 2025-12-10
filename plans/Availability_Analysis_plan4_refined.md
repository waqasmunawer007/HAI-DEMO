# Dashboard UI Revamp - Plan 4: Insulin Availability - By Sector Component

## Task Overview
Implement the "Insulin Availability - By Sector" component with a local Region filter dropdown and a Plotly bar chart showing percentage availability by sector.

**Use Serena MCP:** Define todo items list and solve them one by one according to this detailed plan.

**Current Phase:** Backend Integration and UI Implementation with Plotly Visualization
**Prerequisites:** Plan 3 completed (Insulin Availability - Overall component)

---

## Component Placement

**Location:** Add after "Insulin Availability - Overall" component in app.py (after Plan 3 scorecards, before next component/tab)

**Visual Hierarchy:**
```
[Insulin Availability - Overall component]
    ↓
<br><br> spacing
    ↓
[Sub-heading: "Insulin availability - By sector"]
    ↓
[Single-column filter row: Region]
    ↓
[Bar Chart: "Facilities with Availability (%)"]
```

---

## Component Structure

### 1. Sub-heading
```python
st.markdown("#### Insulin availability - By sector")
```

### 2. Single-Column Filter Layout

**Region Dropdown**
- Expandable dropdown (st.expander) containing checkbox list
- Dropdown label shows: "Select Regions (X/Y selected)" where X=selected, Y=total
- Default state: Collapsed (expanded=False)
- Inside dropdown: Individual checkboxes for each region
- Each checkbox shows: "Region Name (count)" format
- Displays excluded items count inside dropdown: "🚫 X items excluded"
- Filters data within this component only
- Independent from global Data Selectors Region filter
- Default: All regions selected (all checkboxes checked)
- Unchecked items are excluded from analysis

### 3. Bar Chart Visualization

**Chart Title:** "Facilities with Availability (%)"

**Chart Type:** Plotly Bar Chart (using **plotly.graph_objects.Bar** for explicit data type control)

**Chart Specifications:**
- **Y-axis:** Percentage values (0-100%)
  - Label: "Availability (%)"
  - Format: Show percentage symbol
  - Grid lines: Enabled for readability
- **X-axis:** Sector names
  - Label: "Sector"
  - Values: Display full sector names (e.g., "Public sector: MINSA", "Public sector: EsSalud", "Private sector")
  - Rotation: Angle labels if needed for long names
- **Bars:**
  - Color: Use single color from existing palette (e.g., `#1f77b4` or gradient)
  - Width: Appropriate spacing between bars
  - Shaded area: Represents percentage value
  - Data labels: Show percentage value on top of each bar (e.g., "75.5%")
  - Hover info: Display sector name, percentage value, and facility counts
- **Layout:**
  - Responsive: Use `use_container_width=True`
  - Background: Transparent (`plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'`)
  - Height: ~400-500px for optimal viewing

**Example Bar Chart Data:**
| Sector | Availability (%) |
|--------|------------------|
| Public sector: MINSA | 75.5 |
| Public sector: EsSalud | 82.3 |
| Private sector | 68.9 |

---

## Filter Behavior & Scope

### Global Filters (From Data Selectors)
These filters apply to ALL components including this one:
- ✅ Data Collection Period (REQUIRED)
- ✅ Country (optional)
- ✅ Region (optional) - **Note:** If global Region is selected, it restricts the local Region dropdown options

### Local Filters (Component-Specific)
These filters ONLY affect this component's bar chart:
- ✅ Local Region dropdown (filters within component)

### Filter Cascade Logic
```
Global Filters → Applied first to narrow dataset
    ↓
Local Region dropdown → Shows only regions within global filter constraints
    ↓
Bar Chart → Displays data filtered by global + local region filters, grouped by sector
```

**Example:**
- User selects: Global Period = "Y1/P1", Global Country = "Tanzania", Local Region = "Eastern"
- Component behavior:
  - Local Region dropdown: Shows all regions in Tanzania for Y1/P1
  - Bar Chart: Shows availability percentages by sector for facilities in "Eastern" region during "Y1/P1"

---

## Database Query Specifications

### Common Parameters
- **Source Table:** `adl_surveys`
- **Applied Global Filters:**
  - `data_collection_period IN (selected_periods)` (REQUIRED)
  - `country IN (selected_countries)` (if selected)
  - `region IN (selected_regions)` (if selected from global Data Selectors)

### Query 1: Region Dropdown Options

**Purpose:** Populate local Region dropdown with options

**SQL Pattern:**
```sql
SELECT
    region,
    COUNT(DISTINCT form_case__case_id) as facility_count
FROM `{GCP_PROJECT_ID}.{BQ_DATASET}.adl_surveys`
WHERE
    data_collection_period IN ({selected_periods})
    AND ({country_filter})  -- if global country selected
    AND ({region_filter})   -- if global region selected
    AND region IS NOT NULL
    AND TRIM(region) != ''
    AND region != 'NULL'
GROUP BY region
ORDER BY region DESC
```

**Expected Output:** DataFrame with columns: region, facility_count

**Notes:**
- Filter excludes NULL/empty regions as per plan specification
- Sorted DESC as per plan requirement

---

### Query 2: Bar Chart Data - Availability by Sector

**Purpose:** Calculate percentage of facilities with insulin availability for each sector

**Column Assumptions:**
- `insulin_available_num`: Integer column (1 = available, 0 = not available)
- `sector_order`: STRING column (stored as text, cast to INT64 for sorting)
- `sector`: String column with sector names

**SQL Pattern:**
```sql
SELECT
    sector,
    SAFE_CAST(sector_order AS INT64) as sector_order,
    COUNT(DISTINCT form_case__case_id) as total_facilities,
    SUM(COALESCE(insulin_available_num, 0)) as facilities_with_insulin,
    CASE
        WHEN COUNT(DISTINCT form_case__case_id) > 0
        THEN ROUND((SUM(COALESCE(insulin_available_num, 0)) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
        ELSE 0
    END as availability_percentage
FROM `{GCP_PROJECT_ID}.{BQ_DATASET}.adl_surveys`
WHERE
    data_collection_period IN ({selected_periods})
    AND ({country_filter})  -- if global country selected
    AND ({region_filter})   -- if global region selected
    AND ({local_region_filter})  -- if local region selected in component
    AND sector IS NOT NULL
    AND TRIM(sector) != ''
GROUP BY sector, sector_order
ORDER BY SAFE_CAST(sector_order AS INT64) ASC NULLS LAST, sector ASC
```

**Important Notes:**
- **sector_order Data Type:** The column is stored as STRING in the database, so we use `SAFE_CAST(sector_order AS INT64)` to convert it to integer for proper sorting
- **Sorting Logic:** `ORDER BY SAFE_CAST(sector_order AS INT64) ASC NULLS LAST, sector ASC` ensures NULL values appear last and ties are broken alphabetically by sector name
- **Type Safety:** Using `SAFE_CAST` instead of `CAST` prevents errors if conversion fails (returns NULL instead)

**Expected Output:** DataFrame with columns:
- `sector` (string): Sector name
- `sector_order` (int): Order value for sorting
- `total_facilities` (int): Total facilities in sector
- `facilities_with_insulin` (int): Facilities with insulin available
- `availability_percentage` (float): Percentage (0-100, 1 decimal place)

**Validation Rules:**
- If result is empty, show "No data available" message
- `availability_percentage` should be between 0 and 100
- `facilities_with_insulin` ≤ `total_facilities`
- Sorted by `sector_order ASC` for consistent bar ordering

---

## Implementation Functions

### Function 1: get_insulin_by_sector_regions()

```python
@st.cache_data(ttl=600)
def get_insulin_by_sector_regions(_client, table_name, global_filters):
    """
    Get regions for local Region dropdown in Insulin Availability - By Sector component.

    Args:
        _client: BigQuery client
        table_name: Table name
        global_filters (dict): Global filters from Data Selectors
            {
                'data_collection_period': ['Y1/P1'],
                'country': ['Tanzania'],
                'region': ['Eastern']
            }

    Returns:
        pandas DataFrame with columns: region, facility_count
    """
    # Build WHERE clause with global filters
    # Exclude NULL regions as per specification
    # Execute query
    # Return results sorted DESC
```

---

### Function 2: get_insulin_by_sector_chart_data()

```python
@st.cache_data(ttl=600)
def get_insulin_by_sector_chart_data(_client, table_name, global_filters, local_regions):
    """
    Get insulin availability percentages by sector for bar chart.

    Args:
        _client: BigQuery client
        table_name: Table name
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown

    Returns:
        pandas DataFrame with columns:
            - sector (str)
            - sector_order (int)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)
    """
    # Build WHERE clause with global + local region filters
    # Calculate: (sum(insulin_available_num) / count(form_case__case_id)) * 100
    # Group by sector
    # Order by sector_order ASC
    # Execute query
    # Validate results
    # Return DataFrame
```

---

## UI Implementation Pattern

### Step 1: Sub-heading

```python
# After Insulin Availability - Overall component
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("#### Insulin availability - By sector")
```

---

### Step 2: Local Region Filter Dropdown with Checkbox Style and Excluded Count

```python
if st.session_state.selected_periods:
    # Build global filters dict
    global_filters = {
        'data_collection_period': st.session_state.selected_periods,
        'country': st.session_state.selected_countries if st.session_state.selected_countries else None,
        'region': st.session_state.selected_regions if st.session_state.selected_regions else None
    }

    # Single-column layout for Region filter
    st.markdown("**Region**")
    with st.spinner("Loading regions..."):
        region_df = get_insulin_by_sector_regions(client, TABLE_NAME, global_filters)

        if region_df is not None and not region_df.empty:
            # Build region options
            region_data = []
            for _, row in region_df.iterrows():
                region = row['region']
                count = row['facility_count']
                region_data.append((region, count))

            total_regions = len(region_data)

            # Initialize checkboxes in session state (first time only)
            for region, count in region_data:
                checkbox_key = f"insulin_by_sector_region_{region}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

            # Count CURRENT selected items from session state (before rendering)
            selected_count = sum(
                1 for region, _ in region_data
                if st.session_state.get(f"insulin_by_sector_region_{region}", True)
            )
            excluded_count = total_regions - selected_count

            # Create expander/dropdown with selection summary
            with st.expander(
                f"Select Regions ({selected_count}/{total_regions} selected)",
                expanded=False
            ):
                # Display excluded count inside expander
                if excluded_count > 0:
                    st.caption(f"🚫 {excluded_count} item{'s' if excluded_count != 1 else ''} excluded")

                # Create checkboxes for each region
                local_regions = []
                for region, count in region_data:
                    checkbox_key = f"insulin_by_sector_region_{region}"

                    # Display checkbox (uses Streamlit's automatic session state handling)
                    is_checked = st.checkbox(
                        f"{region} ({count:,})",
                        value=st.session_state.get(checkbox_key, True),
                        key=checkbox_key
                    )

                    # Add to selected list if checked
                    if is_checked:
                        local_regions.append(region)
        else:
            local_regions = []
            st.info("No region data available")
```

---

### Step 3: Plotly Bar Chart

```python
    # Fetch chart data
    chart_df = get_insulin_by_sector_chart_data(
        client,
        TABLE_NAME,
        global_filters,
        local_regions
    )

    if chart_df is not None and not chart_df.empty:
        # Ensure data types are correct (important for proper bar height display)
        chart_df['availability_percentage'] = pd.to_numeric(chart_df['availability_percentage'], errors='coerce')
        chart_df['total_facilities'] = pd.to_numeric(chart_df['total_facilities'], errors='coerce')
        chart_df['facilities_with_insulin'] = pd.to_numeric(chart_df['facilities_with_insulin'], errors='coerce')

        # Create bar chart using graph_objects for explicit control
        import plotly.graph_objects as go

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=chart_df['sector'].tolist(),
            y=chart_df['availability_percentage'].tolist(),
            text=[f'{val:.1f}%' for val in chart_df['availability_percentage'].tolist()],
            textposition='outside',
            marker_color='#1f77b4',
            hovertemplate='<b>%{x}</b><br>' +
                          'Availability: %{y:.1f}%<br>' +
                          'Facilities with Insulin: %{customdata[0]:,}<br>' +
                          'Total Facilities: %{customdata[1]:,}<extra></extra>',
            customdata=chart_df[['facilities_with_insulin', 'total_facilities']].values
        ))

        # Update layout for better appearance
        fig.update_layout(
            title='Facilities with Availability (%)',
            xaxis_title='Sector',
            yaxis_title='Availability (%)',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=450,
            yaxis=dict(
                range=[0, 110],  # Slightly higher to accommodate text labels above bars
                ticksuffix='%'
            ),
            xaxis_tickangle=-45 if len(chart_df) > 5 else 0,  # Rotate labels if many sectors
            showlegend=False,
            margin=dict(t=50, b=100, l=50, r=50)
        )

        # Display chart
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters")

else:
    st.markdown("""
        <div class="info-box">
            <strong>💡 Tip:</strong> Select one or more data collection periods above to view insulin availability by sector.
        </div>
    """, unsafe_allow_html=True)
```

**Implementation Notes:**
- **Why graph_objects instead of express:** Using `plotly.graph_objects.Bar` provides explicit control over data types and ensures bar heights correctly reflect numeric values
- **Data type conversion:** Essential to call `pd.to_numeric()` on percentage columns to ensure Plotly interprets them as numbers, not strings
- **Text labels:** Pre-formatted as strings (e.g., "60.0%") instead of using Plotly templates which can display literally
- **Y-axis range:** Extended to [0, 110] to accommodate text labels positioned outside/above bars
- **Custom data:** Manually set using `.values` to ensure correct indexing in hover tooltips

---

## Session State Management

### Initialize Local Filter State

```python
# Session state keys for this component use unique prefix to avoid conflicts
# Example: insulin_by_sector_region_Eastern, insulin_by_sector_region_Western
# These are automatically managed by Streamlit when using st.checkbox with key parameter
```

**Note:** Using Streamlit's `key` parameter in checkbox handles state automatically. Each checkbox key follows pattern: `insulin_by_sector_region_{region_name}`

---

## Error Handling & Edge Cases

### 1. No Data Collection Period Selected
```python
if not st.session_state.selected_periods:
    # Show tip message (already implemented above)
```

### 2. Division by Zero in Percentage Calculation
```python
# Handled in SQL query with CASE statement
CASE
    WHEN COUNT(DISTINCT form_case__case_id) > 0
    THEN calculation
    ELSE 0
END
```

### 3. NULL Values in insulin_available_num
```python
# Use COALESCE in SQL
SUM(COALESCE(insulin_available_num, 0))
```

### 4. Empty Region Dropdown
```python
if region_df is None or region_df.empty:
    st.info("No region data available")
    local_regions = []
```

### 5. No Data After Filtering (Empty Chart)
```python
if chart_df is None or chart_df.empty:
    st.info("No data available for the selected filters")
```

### 6. Missing sector_order Column
```python
# If sector_order column doesn't exist, fallback to alphabetical sort
# Add try/except in query function or check schema beforehand
```

### 7. NULL/Empty Sector Names
```python
# Filter in WHERE clause:
AND sector IS NOT NULL
AND TRIM(sector) != ''
```

---

## Performance Optimization

### Caching Strategy
- All BigQuery functions use `@st.cache_data(ttl=600)` for 10-minute cache
- Cache keys include filter parameters to ensure correct data per filter combination
- Plotly chart creation is fast, no caching needed for visualization

### Query Optimization
- Use single query for all chart metrics (availability %, total facilities, facilities with insulin)
- Apply filters at database level, not in Python
- Use `COUNT(DISTINCT)`, `SUM`, and aggregations efficiently
- Use `sector_order` for consistent sorting (indexed column if available)

---

## Styling & Responsive Design

### Plotly Chart Styling
- **Color scheme:** Use primary color `#1f77b4` from existing palette
- **Transparency:** Background transparent to match Streamlit theme
- **Font:** Plotly default fonts (readable, professional)
- **Hover effects:** Custom template with sector name, percentage, and facility counts

### Responsive Behavior
- Chart uses `use_container_width=True` for automatic width adjustment
- On mobile, chart scales down appropriately
- X-axis labels rotate at -45° when many sectors present
- Bar labels appear outside bars for clarity

### Consistency with Existing Components
- Use same section spacing (`<br><br>`)
- Use same markdown sub-heading style (`####`)
- Use same info-box class for messages
- Use same checkbox dropdown pattern from Plan 3

---

## Testing Requirements

### Unit Tests
```python
def test_get_insulin_by_sector_regions():
    """Test region dropdown data fetching"""
    # Test with various filter combinations
    # Verify NULL/empty region exclusion
    # Verify DESC sorting

def test_get_insulin_by_sector_chart_data():
    """Test bar chart data fetching"""
    # Test with local region filters
    # Verify percentage calculation: (sum / count) * 100
    # Verify sector_order ASC sorting
    # Verify NULL handling in insulin_available_num
    # Verify division by zero protection
```

### Integration Tests
1. Test filter cascade: Global → Local Region → Chart
2. Test chart updates when Region filter changes
3. Test with empty datasets (show "No data available")
4. Verify chart displays correct number of bars (one per sector)
5. Verify percentage values match database calculations
6. Test hover tooltips show correct information
7. Test with single region vs multiple regions selected

### Visual Validation
1. Verify bars display in correct order (sector_order ASC)
2. Verify percentage labels appear on top of bars
3. Verify y-axis range is 0-100%
4. Verify x-axis labels are readable (rotated if needed)
5. Verify chart height is appropriate (~450px)
6. Test responsive behavior on different screen sizes

---

## Implementation Checklist

### Backend Functions
- [x] Implement `get_insulin_by_sector_regions()` in bigquery_client.py
- [x] Implement `get_insulin_by_sector_chart_data()` in bigquery_client.py
- [x] Add imports to app.py (including plotly.graph_objects)
- [x] Add caching decorators with ttl=600
- [x] Verify `insulin_available_num` column exists in database
- [x] Verify `sector_order` column exists in database (STRING type, requires SAFE_CAST)

### UI Implementation
- [x] Add sub-heading "Insulin availability - By sector"
- [x] Implement Region dropdown with checkboxes
- [x] Add excluded count display inside dropdown
- [x] Implement Plotly bar chart with correct specifications (using go.Bar)
- [x] Configure chart title: "Facilities with Availability (%)"
- [x] Configure y-axis: Percentage format, 0-110 range (extended for labels)
- [x] Configure x-axis: Sector names, rotation if needed
- [x] Add data labels on bars (pre-formatted percentage values)
- [x] Configure hover tooltip with sector, %, and counts
- [x] Add "No data available" handling
- [x] Add tip message when no period selected
- [x] Set chart height to 450px

### Filter Integration
- [x] Global Data Collection Period filter applied
- [x] Global Country filter applied (if selected)
- [x] Global Region filter applied (if selected)
- [x] Local Region dropdown respects global filters
- [x] Local Region dropdown excludes NULL values
- [x] Chart respects all filters (global + local)

### Chart Styling
- [x] Use primary color `#1f77b4` for bars
- [x] Set transparent background
- [x] Add percentage symbol to y-axis ticks
- [x] Format percentage labels on bars (1 decimal place)
- [x] Configure hover template with custom formatting
- [x] Apply responsive width with `use_container_width=True`
- [x] Set appropriate margins

### Validation & Testing
- [x] Verify percentage formula: (sum(insulin_available_num) / count(form_case__case_id)) * 100
- [x] Test division by zero handling
- [x] Test NULL value handling in insulin_available_num
- [x] Test with various filter combinations
- [x] Verify chart values match database calculations (tested with real data)
- [x] Test bars are sorted by sector_order ASC
- [x] Verify excluded region logic works correctly
- [x] Test responsive design (chart uses use_container_width=True)
- [x] Verify hover tooltips display correctly

**Implementation Status:** ✅ **COMPLETED** - All items implemented and tested successfully

---

## Success Criteria

1. **Data Accuracy:** Bar chart percentages match database calculations exactly
2. **Filter Cascade:** Local Region dropdown properly respects global filters
3. **Performance:** Component loads within 2 seconds
4. **Responsiveness:** Chart updates immediately when Region filter changes
5. **Error Handling:** Graceful handling of empty data, NULL values, division by zero
6. **User Experience:** Clear messaging when no data available
7. **Visual Quality:** Chart is visually appealing, readable, and matches dashboard style
8. **Sorting:** Bars display in correct order (sector_order ASC)

---

## Notes & Assumptions

### Actual Column Schema (Verified During Implementation)
- `insulin_available_num`: Integer (1 = available, 0 = not available) ✅ Confirmed
- `sector_order`: **STRING type** (stored as text, requires SAFE_CAST to INT64 for sorting) ✅ Confirmed
- `sector`: String with full sector names (e.g., "Public sector: MINSA") ✅ Confirmed
- `form_case__case_id`: Unique facility identifier ✅ Confirmed
- `region`: String with region names (may contain NULL values to exclude) ✅ Confirmed

### Implementation Findings
- **sector_order Data Type Issue:** Initially assumed INTEGER, but database stores it as STRING. Solution: Use `SAFE_CAST(sector_order AS INT64)` in both SELECT and ORDER BY clauses
- **NULL Handling:** sector_order can be NULL for some sectors, handled with `NULLS LAST` in ORDER BY
- **Bar Height Display:** Required explicit data type conversion using `pd.to_numeric()` to ensure Plotly renders bar heights correctly
- **Plotly Library Choice:** `plotly.graph_objects` chosen over `plotly.express` for better control over data types and explicit value handling

### Plotly vs Altair
Plan specifies Plotly, so use `plotly.express` or `plotly.graph_objects`. Plotly provides:
- Better interactivity (hover tooltips)
- Easier customization
- More responsive layouts
- Already used elsewhere in the dashboard

### Session State Key Naming
Use unique prefix `insulin_by_sector_region_` to avoid conflicts with Plan 3's `insulin_region_` keys. This allows both components to coexist without interference.

---

## Next Steps After Plan 4 Completion

1. User acceptance testing with real data
2. Verify chart displays correctly for all sectors
3. Validate percentage calculations against manual checks
4. Test filter interactions with Plan 3 component (ensure independence)
5. Document any data quality issues (missing sector_order, NULL values, etc.)
6. Proceed to next insulin availability filter/visualization if any

---

## Implementation Notes

### Key Differences from Plan 3
1. **Single filter instead of two:** Only Region dropdown (no Sector dropdown)
2. **Visualization instead of scorecards:** Plotly bar chart instead of metric cards
3. **Grouping by sector:** Data grouped and displayed by sector
4. **Sorting requirement:** Must use sector_order ASC (Plan 3 had no sorting requirement)
5. **Different session state keys:** Use `insulin_by_sector_region_` prefix to avoid conflicts

### Reusable Patterns from Plan 3
1. ✅ Checkbox dropdown implementation with st.expander
2. ✅ Excluded count display
3. ✅ Session state management for checkboxes
4. ✅ Global filter integration
5. ✅ Error handling for empty data
6. ✅ Caching strategy with @st.cache_data(ttl=600)

### New Patterns Introduced
1. 🆕 Plotly bar chart with percentage data using `go.Bar`
2. 🆕 Custom hover templates with customdata
3. 🆕 Pre-formatted data labels on bars
4. 🆕 Conditional x-axis rotation based on data size
5. 🆕 Sorting by STRING order column with SAFE_CAST
6. 🆕 Explicit data type conversion with pd.to_numeric()

---

## Issues Encountered & Resolutions

### Issue 1: COALESCE Type Mismatch Error
**Error:** `No matching signature for function COALESCE Argument types: STRING, INT64`
**Cause:** sector_order column is stored as STRING in database, initial query used `COALESCE(sector_order, 999)` mixing STRING and INT64
**Resolution:** Changed to `SAFE_CAST(sector_order AS INT64)` in SELECT and `ORDER BY SAFE_CAST(sector_order AS INT64) ASC NULLS LAST, sector ASC`
**Location:** database/bigquery_client.py:868, 879

### Issue 2: Bar Chart Showing Template Strings Literally
**Error:** Bar labels displayed as "%{text:.1f}%" instead of actual percentages
**Cause:** Plotly Express with `texttemplate` parameter wasn't being interpreted correctly
**Resolution:** Switched to `plotly.graph_objects.Bar` with pre-formatted text labels: `text=[f'{val:.1f}%' for val in ...]`
**Location:** app.py:732-742

### Issue 3: Bar Heights Not Reflecting Percentages
**Error:** Bar heights remained near 0% despite correct percentage values (60%, 100%, etc.)
**Cause:** DataFrame columns weren't explicitly numeric, Plotly interpreted them as categorical/string values
**Resolution:** Added explicit type conversion: `chart_df['availability_percentage'] = pd.to_numeric(chart_df['availability_percentage'], errors='coerce')`
**Location:** app.py:732-734

### Issue 4: Hover Tooltip Custom Data Indexing
**Error:** Hover tooltip showed incorrect facility counts
**Cause:** When using px.bar with hover_data, customdata indices were different
**Resolution:** With go.Bar, manually set `customdata=chart_df[['facilities_with_insulin', 'total_facilities']].values` and reference as `customdata[0]` and `customdata[1]`
**Location:** app.py:749, 755-758

---

## Implementation Timeline

1. ✅ **Backend functions created** (database/bigquery_client.py lines 749-887)
2. ✅ **UI component added** (app.py lines 651-786)
3. ✅ **Imports updated** (app.py lines 20-21)
4. ✅ **SAFE_CAST fix applied** for sector_order STRING type
5. ✅ **Switched from px.bar to go.Bar** for better control
6. ✅ **Added pd.to_numeric()** for proper bar height rendering
7. ✅ **Pre-formatted text labels** instead of Plotly templates
8. ✅ **Extended y-axis to [0, 110]** to accommodate outside text labels

**Final Status:** ✅ All issues resolved, component fully functional