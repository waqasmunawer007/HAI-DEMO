# Dashboard UI Revamp - Plan 8: Insulin Availability - By INN Component

## Task Overview
Implement the "Insulin Availability - By INN" component with two local filter dropdowns (Region and Sector) and one Plotly bar chart showing percentage availability for different insulin INNs (International Nonproprietary Names). Only insulins with availability > 0% are displayed.

**Use Serena MCP:** Define todo items list and solve them one by one according to this detailed plan.

**Current Phase:** Backend Integration and UI Implementation with Single Plotly Visualization
**Prerequisites:** Plan 7 completed (Insulin Availability - Public Sector - By Level of Care component)

---

## Component Placement

**Location:** Add after "Insulin Availability - Public sector - By level of care" component in app.py (after Plan 7, before next component/tab)

**Visual Hierarchy:**
```
[Insulin Availability - Public sector - By level of care component]
    ↓
<br><br> spacing
    ↓
[Sub-heading: "Insulin availability - By INN"]
    ↓
[Two-column filter row: Region | Sector]
    ↓
[Single Bar Chart: Facilities with Availability (%)]
    ↓
[Note message: "NOTE: Only insulins found to be available are shown."]
```

---

## Component Structure

### 1. Sub-heading
```python
st.markdown("#### Insulin availability - By INN")
```

### 2. Two-Column Filter Layout

**Region Dropdown (Column 1)**
- Expandable dropdown (st.expander) containing checkbox list
- Dropdown label shows: "Select Regions (X/Y selected)" where X=selected, Y=total
- Default state: Collapsed (expanded=False)
- Inside dropdown: Individual checkboxes for each region
- Each checkbox shows: "Region Name (count)" format
- Displays excluded items count inside dropdown: "🚫 X items excluded"
- Source table: `adl_surveys`
- Filters data within this component only
- Independent from global Data Selectors
- Default: All regions selected (all checkboxes checked)

**Sector Dropdown (Column 2)**
- Expandable dropdown (st.expander) containing checkbox list
- Dropdown label shows: "Select Sectors (X/Y selected)" where X=selected, Y=total
- Default state: Collapsed (expanded=False)
- Inside dropdown: Individual checkboxes for each sector
- Each checkbox shows: "Sector Name (count)" format
- Displays excluded items count inside dropdown: "🚫 X items excluded"
- Source table: `adl_surveys`
- Filters data within this component only
- Independent from global Data Selectors
- Default: All sectors selected (all checkboxes checked)

### 3. Single Bar Chart Visualization

**Chart Title:** "Facilities with Availability (%)"

**Chart Type:** Plotly Bar Chart (using **plotly.graph_objects.Bar** for explicit data type control)

**Chart Specifications:**
- **Y-axis:** Percentage values (0-100%)
  - Label: "Facilities with Availability (%)"
  - Format: Show percentage symbol
  - Grid lines: Enabled for readability
- **X-axis:** Insulin INN names
  - Label: "Insulin INN"
  - Values: Display insulin INN names (Regular, NPH, Lispro, Aspart, Glargine, etc.)
  - Rotation: Angle labels (-45°) for readability
- **Bars:**
  - Color: Use single color from existing palette (e.g., `#1f77b4`)
  - Width: Appropriate spacing between bars
  - Shaded area: Represents percentage value
  - Data labels: Show percentage value on top of each bar (e.g., "75.5%")
  - Hover info: Display INN name, percentage value, available facilities count, and total facilities count
- **Sorting:** Descending by availability percentage (highest to lowest)
- **Filtering:** ONLY show insulins with availability > 0% (exclude insulins with 0% availability)
- **Layout:**
  - Responsive: Use `use_container_width=True`
  - Background: Transparent (`plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'`)
  - Height: ~450px for optimal viewing

**Example Chart Data:**
| Insulin INN | Availability (%) |
|-------------|------------------|
| Regular     | 78.5             |
| NPH         | 72.3             |
| Lispro      | 65.8             |
| Aspart      | 58.2             |
| Glargine    | 52.1             |
| Detemir     | 45.3             |

### 4. Note Message

**Placement:** Below the bar chart

**Content:**
```python
st.markdown("""
    <div class="info-box">
        <strong>📝 Note:</strong> Only insulins found to be available are shown.
    </div>
""", unsafe_allow_html=True)
```

---

## Filter Behavior & Scope

### Global Filters (From Data Selectors)
These filters apply to ALL components including this one:
- ✅ Data Collection Period (REQUIRED)
- ✅ Country (optional)
- ✅ Region (optional) - **Note:** If global Region is selected, it restricts which regions appear in local dropdown

### Local Filters (Component-Specific)
These filters ONLY affect this component's bar chart:
- ✅ Local Region dropdown (filters within component)
- ✅ Local Sector dropdown (filters within component)

### Filter Cascade Logic
```
Global Filters → Applied first to narrow dataset
    ↓
Local Region dropdown → Shows only regions within global filter constraints
    ↓
Local Sector dropdown → Shows only sectors within global filter constraints
    ↓
Bar Chart → Display data filtered by global + local region + local sector filters, grouped by insulin_inn, ONLY showing insulins with availability > 0%
```

**Example:**
- User selects: Global Period = "Y1/P1", Global Country = "Peru", Local Region = "Arequipa", Local Sector = "Public"
- Component behavior:
  - Region dropdown: Shows all regions in Peru for Y1/P1
  - Sector dropdown: Shows all sectors in Peru for Y1/P1
  - Chart: Shows availability percentages by insulin INN for facilities in "Arequipa", "Public" sector during "Y1/P1" in Peru
  - Chart ONLY shows insulins with availability > 0% (excludes 0% entries)

---

## Database Query Specifications

### Common Parameters
- **Applied Global Filters:**
  - `data_collection_period IN (selected_periods)` (REQUIRED)
  - `country IN (selected_countries)` (if selected)
  - `region IN (selected_regions)` (if selected from global Data Selectors)

### Query 1: Region Dropdown Options

**Purpose:** Populate local Region dropdown with options

**Source Table:** `adl_surveys`

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
- Uses `adl_surveys` table
- Filter excludes NULL/empty regions
- Sorted DESC for reverse alphabetical ordering

---

### Query 2: Sector Dropdown Options

**Purpose:** Populate local Sector dropdown with options

**Source Table:** `adl_surveys`

**SQL Pattern:**
```sql
SELECT
    sector,
    COUNT(DISTINCT form_case__case_id) as facility_count
FROM `{GCP_PROJECT_ID}.{BQ_DATASET}.adl_surveys`
WHERE
    data_collection_period IN ({selected_periods})
    AND ({country_filter})  -- if global country selected
    AND ({region_filter})   -- if global region selected
    AND sector IS NOT NULL
    AND TRIM(sector) != ''
    AND sector != 'NULL'
GROUP BY sector
ORDER BY sector DESC
```

**Expected Output:** DataFrame with columns: sector, facility_count

**Notes:**
- Uses `adl_surveys` table
- Filter excludes NULL/empty sectors
- Sorted DESC for reverse alphabetical ordering

---

### Query 3: Bar Chart Data - Availability by Insulin INN

**Purpose:** Calculate percentage of facilities with insulin availability for each insulin INN, ONLY showing insulins with availability > 0%

**Source Table:** `adl_repeat_repivot`

**Column Assumptions:**
- `is_unavailable`: Integer column (0 = available, 1 = not available)
- `insulin_inn`: String column with INN names (Regular, NPH, Lispro, Aspart, Glargine, etc.)
- `form_case__case_id`: Unique facility identifier

**SQL Pattern:**
```sql
SELECT
    insulin_inn,
    COUNT(DISTINCT form_case__case_id) as total_facilities,
    COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) as facilities_with_insulin,
    CASE
        WHEN COUNT(DISTINCT form_case__case_id) > 0
        THEN ROUND((COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
        ELSE 0
    END as availability_percentage
FROM `{GCP_PROJECT_ID}.{BQ_DATASET}.adl_repeat_repivot`
WHERE
    data_collection_period IN ({selected_periods})
    AND ({country_filter})  -- if global country selected
    AND ({global_region_filter})   -- if global region selected
    AND ({local_region_filter})  -- if local region selected in component
    AND ({local_sector_filter})  -- if local sector selected in component
    AND insulin_inn IS NOT NULL
    AND TRIM(insulin_inn) != ''
    AND insulin_inn != 'NULL'
GROUP BY insulin_inn
HAVING
    CASE
        WHEN COUNT(DISTINCT form_case__case_id) > 0
        THEN ROUND((COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
        ELSE 0
    END > 0
ORDER BY availability_percentage DESC
```

**Expected Output:** DataFrame with columns:
- `insulin_inn` (string): Insulin INN name
- `total_facilities` (int): Total facilities surveyed
- `facilities_with_insulin` (int): Facilities with insulin available (is_unavailable = 0)
- `availability_percentage` (float): Percentage (0-100, 1 decimal place)

**Validation Rules:**
- If result is empty, show "No data available" message
- `availability_percentage` should be between 0 and 100
- `facilities_with_insulin` ≤ `total_facilities`
- Sorted by `availability_percentage DESC` for highest to lowest ordering
- ONLY includes rows where `availability_percentage > 0`

**Important Filter Logic:**
- **HAVING clause:** Filters out insulins with 0% availability AFTER aggregation
- This ensures only insulins with some availability are displayed in the chart

---

## Implementation Functions

### Function 1: get_insulin_by_inn_regions()

```python
@st.cache_data(ttl=600)
def get_insulin_by_inn_regions(_client, table_name, global_filters):
    """
    Get regions for local Region dropdown in Insulin Availability - By INN component.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys)
        global_filters (dict): Global filters from Data Selectors
            {
                'data_collection_period': ['Y1/P1'],
                'country': ['Peru'],
                'region': ['Arequipa']
            }

    Returns:
        pandas DataFrame with columns: region, facility_count
    """
    # Build WHERE clause with global filters
    # Exclude NULL/empty regions
    # Execute query on adl_surveys table
    # Return results sorted DESC
```

---

### Function 2: get_insulin_by_inn_sectors()

```python
@st.cache_data(ttl=600)
def get_insulin_by_inn_sectors(_client, table_name, global_filters):
    """
    Get sectors for local Sector dropdown in Insulin Availability - By INN component.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys)
        global_filters (dict): Global filters from Data Selectors

    Returns:
        pandas DataFrame with columns: sector, facility_count
    """
    # Build WHERE clause with global filters
    # Exclude NULL/empty sectors
    # Execute query on adl_surveys table
    # Return results sorted DESC
```

---

### Function 3: get_insulin_by_inn_chart_data()

```python
@st.cache_data(ttl=600)
def get_insulin_by_inn_chart_data(_client, table_name, global_filters, local_regions, local_sectors):
    """
    Get insulin availability percentages by insulin INN, ONLY showing insulins with availability > 0%.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        pandas DataFrame with columns:
            - insulin_inn (str)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)

        Only returns rows where availability_percentage > 0
    """
    # Build WHERE clause with global + local region + local sector filters
    # Filter: insulin_inn IS NOT NULL
    # Calculate: COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id) * 100
    # Group by insulin_inn
    # HAVING availability_percentage > 0 (exclude 0% availability)
    # Order by availability_percentage DESC
    # Execute query on adl_repeat_repivot table
    # Validate results
    # Return DataFrame
```

---

## UI Implementation Pattern

### Step 1: Sub-heading

```python
# After Insulin Availability - Public sector - By level of care component
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("#### Insulin availability - By INN")
```

---

### Step 2: Two-Column Filter Layout with Checkbox Dropdowns

```python
# Note: Plan 8 uses adl_surveys for dropdowns, adl_repeat_repivot for chart
PLAN8_SURVEYS_TABLE = config.TABLES["surveys"]
PLAN8_REPIVOT_TABLE = config.TABLES["repeat_repivot"]

if st.session_state.selected_periods:
    # Build global filters dict
    global_filters = {
        'data_collection_period': st.session_state.selected_periods,
        'country': st.session_state.selected_countries if st.session_state.selected_countries else None,
        'region': st.session_state.selected_regions if st.session_state.selected_regions else None
    }

    # Two-column layout for filters
    col1, col2 = st.columns(2)

    # Column 1: Region Filter
    with col1:
        st.markdown("**Region**")
        with st.spinner("Loading regions..."):
            region_df = get_insulin_by_inn_regions(client, PLAN8_SURVEYS_TABLE, global_filters)

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
                    checkbox_key = f"insulin_by_inn_region_{region}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items from session state
                selected_count = sum(
                    1 for region, _ in region_data
                    if st.session_state.get(f"insulin_by_inn_region_{region}", True)
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
                        checkbox_key = f"insulin_by_inn_region_{region}"

                        # Display checkbox
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

    # Column 2: Sector Filter
    with col2:
        st.markdown("**Sector**")
        with st.spinner("Loading sectors..."):
            sector_df = get_insulin_by_inn_sectors(client, PLAN8_SURVEYS_TABLE, global_filters)

            if sector_df is not None and not sector_df.empty:
                # Build sector options
                sector_data = []
                for _, row in sector_df.iterrows():
                    sector = row['sector']
                    count = row['facility_count']
                    sector_data.append((sector, count))

                total_sectors = len(sector_data)

                # Initialize checkboxes in session state (first time only)
                for sector, count in sector_data:
                    checkbox_key = f"insulin_by_inn_sector_{sector}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items from session state
                selected_count = sum(
                    1 for sector, _ in sector_data
                    if st.session_state.get(f"insulin_by_inn_sector_{sector}", True)
                )
                excluded_count = total_sectors - selected_count

                # Create expander/dropdown with selection summary
                with st.expander(
                    f"Select Sectors ({selected_count}/{total_sectors} selected)",
                    expanded=False
                ):
                    # Display excluded count inside expander
                    if excluded_count > 0:
                        st.caption(f"🚫 {excluded_count} item{'s' if excluded_count != 1 else ''} excluded")

                    # Create checkboxes for each sector
                    local_sectors = []
                    for sector, count in sector_data:
                        checkbox_key = f"insulin_by_inn_sector_{sector}"

                        # Display checkbox
                        is_checked = st.checkbox(
                            f"{sector} ({count:,})",
                            value=st.session_state.get(checkbox_key, True),
                            key=checkbox_key
                        )

                        # Add to selected list if checked
                        if is_checked:
                            local_sectors.append(sector)
            else:
                local_sectors = []
                st.info("No sector data available")
```

---

### Step 3: Single Plotly Bar Chart

```python
    # Fetch and display bar chart
    st.markdown("<br>", unsafe_allow_html=True)

    with st.spinner("Loading insulin availability by INN..."):
        chart_df = get_insulin_by_inn_chart_data(
            client,
            PLAN8_REPIVOT_TABLE,
            global_filters,
            local_regions,
            local_sectors
        )

        if chart_df is not None and not chart_df.empty:
            # Ensure data types are correct
            chart_df['availability_percentage'] = pd.to_numeric(chart_df['availability_percentage'], errors='coerce')
            chart_df['total_facilities'] = pd.to_numeric(chart_df['total_facilities'], errors='coerce')
            chart_df['facilities_with_insulin'] = pd.to_numeric(chart_df['facilities_with_insulin'], errors='coerce')

            # Create bar chart using graph_objects
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=chart_df['insulin_inn'].tolist(),
                y=chart_df['availability_percentage'].tolist(),
                text=[f'{val:.1f}%' for val in chart_df['availability_percentage'].tolist()],
                textposition='outside',
                marker_color='#1f77b4',
                hovertemplate='<b>%{x}</b><br>' +
                              'Availability: %{y:.1f}%<br>' +
                              'Available Facilities: %{customdata[0]:,}<br>' +
                              'Total Facilities: %{customdata[1]:,}<extra></extra>',
                customdata=chart_df[['facilities_with_insulin', 'total_facilities']].values
            ))

            # Update layout
            fig.update_layout(
                title='Facilities with Availability (%)',
                xaxis_title='Insulin INN',
                yaxis_title='Facilities with Availability (%)',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=450,
                yaxis=dict(
                    range=[0, 110],
                    ticksuffix='%'
                ),
                xaxis_tickangle=-45,  # Always angle labels for readability
                showlegend=False,
                margin=dict(t=50, b=100, l=50, r=50)
            )

            # Display chart
            st.plotly_chart(fig, use_container_width=True)

            # Display note message below chart
            st.markdown("""
                <div class="info-box">
                    <strong>📝 Note:</strong> Only insulins found to be available are shown.
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No data available for the selected filters")

else:
    st.markdown("""
        <div class="info-box">
            <strong>💡 Tip:</strong> Select one or more data collection periods above to view insulin availability by INN.
        </div>
    """, unsafe_allow_html=True)
```

**Implementation Notes:**
- **Single chart:** Uses `#1f77b4` (blue) color
- **Data type conversion:** Essential `pd.to_numeric()` on all numeric columns
- **Text labels:** Pre-formatted percentage strings
- **Y-axis range:** Extended to [0, 110] for text labels above bars
- **Custom data:** Manually set for hover tooltips
- **X-axis rotation:** Always -45° for better INN name readability
- **X-axis title:** "Insulin INN" explicitly shown
- **Sorting:** Bars automatically sorted DESC by availability percentage (from query)
- **Filtering:** ONLY shows insulins with availability > 0% (handled in query)
- **Note placement:** Immediately below the chart

---

## Session State Management

### Initialize Local Filter State

```python
# Session state keys for this component use unique prefix to avoid conflicts
# Region checkboxes: insulin_by_inn_region_{region_name}
# Sector checkboxes: insulin_by_inn_sector_{sector_name}
# These are automatically managed by Streamlit when using st.checkbox with key parameter
```

**Note:** Using Streamlit's `key` parameter in checkbox handles state automatically. Unique prefix `insulin_by_inn_` prevents conflicts with Plan 3, 4, 5, 6, and 7 components.

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

### 3. NULL Values in is_unavailable Column
```python
# Use CASE WHEN in SQL to only count non-null available facilities
COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END)
```

### 4. Empty Region Dropdown
```python
if region_df is None or region_df.empty:
    st.info("No region data available")
    local_regions = []
```

### 5. Empty Sector Dropdown
```python
if sector_df is None or sector_df.empty:
    st.info("No sector data available")
    local_sectors = []
```

### 6. No Data After Filtering (Empty Chart)
```python
if chart_df is None or chart_df.empty:
    st.info("No data available for the selected filters")
```

### 7. NULL/Empty insulin_inn Values
```python
# Filter in WHERE clause:
AND insulin_inn IS NOT NULL
AND TRIM(insulin_inn) != ''
AND insulin_inn != 'NULL'
```

### 8. All Insulins Have 0% Availability
```python
# HAVING clause filters out 0% availability insulins
# If all insulins have 0%, result is empty
# Display "No data available" message
```

### 9. No Regions or Sectors Selected
```python
# If user unchecks all regions/sectors, local_regions/local_sectors will be empty list
# Queries should handle empty list and return no data
# Display "No data available" message
```

---

## Performance Optimization

### Caching Strategy
- All BigQuery functions use `@st.cache_data(ttl=600)` for 10-minute cache
- Cache keys include filter parameters to ensure correct data per filter combination
- Three separate cached functions allow independent data fetching
- Plotly chart creation is fast, no caching needed for visualization

### Query Optimization
- Use single query for all chart metrics (availability %, total facilities, available facilities)
- Apply filters at database level, not in Python
- Use `COUNT(DISTINCT)` and CASE WHEN efficiently
- Filter by insulin_inn at database level
- Group by insulin_inn for aggregation
- HAVING clause filters availability > 0% at database level (more efficient than Python filtering)

### Parallel Data Fetching
- Region and Sector dropdown queries are independent (can run in parallel)
- Chart query depends on dropdown selections
- Consider loading both dropdowns concurrently if performance becomes issue

---

## Styling & Responsive Design

### Plotly Chart Styling
- **Color scheme:** `#1f77b4` (blue) from existing palette
- **Transparency:** Background transparent to match Streamlit theme
- **Font:** Plotly default fonts (readable, professional)
- **Hover effects:** Custom template with INN name, percentage, and facility counts

### Responsive Behavior
- Chart uses `use_container_width=True` for automatic width adjustment
- Two-column filter layout adapts to screen size
- On mobile, columns stack vertically
- X-axis labels always rotate at -45° for INN name readability
- Bar labels appear outside bars for clarity

### Consistency with Existing Components
- Use same section spacing (`<br><br>`)
- Use same markdown sub-heading style (`####`)
- Use same info-box class for messages
- Use same checkbox dropdown pattern from Plan 3-7
- Use same two-column filter layout pattern

---

## Testing Requirements

### Unit Tests
```python
def test_get_insulin_by_inn_regions():
    """Test region dropdown data fetching"""
    # Test with various filter combinations
    # Verify NULL/empty region exclusion
    # Verify DESC sorting
    # Verify uses adl_surveys table

def test_get_insulin_by_inn_sectors():
    """Test sector dropdown data fetching"""
    # Test with various filter combinations
    # Verify NULL/empty sector exclusion
    # Verify DESC sorting
    # Verify uses adl_surveys table

def test_get_insulin_by_inn_chart_data():
    """Test chart data fetching"""
    # Test with local region + sector filters
    # Verify percentage calculation
    # Verify is_unavailable = 0 logic
    # Verify division by zero protection
    # Verify insulin_inn NULL exclusion
    # Verify availability > 0% filter (HAVING clause)
    # Verify DESC sorting by availability_percentage
    # Verify uses adl_repeat_repivot table
```

### Integration Tests
1. Test filter cascade: Global → Local Region → Local Sector → Chart
2. Test chart updates when Region or Sector filter changes
3. Test with empty datasets (show "No data available")
4. Verify chart displays INN availability percentages
5. Verify percentage values match database calculations
6. Verify only insulins with > 0% availability are displayed
7. Test hover tooltips show correct information
8. Test with single vs multiple regions/sectors selected
9. Test independence from Plan 3, 4, 5, 6, and 7 components
10. Verify bars are sorted DESC by availability

### Visual Validation
1. Verify bars display in correct order (highest to lowest availability)
2. Verify percentage labels appear on top of bars
3. Verify y-axis range is 0-110%
4. Verify x-axis labels show INN names at -45° angle
5. Verify x-axis title is "Insulin INN"
6. Verify chart height is appropriate (~450px)
7. Test responsive behavior on different screen sizes
8. Verify note message appears below chart
9. Verify note message styling matches existing info-box
10. Verify chart color is consistent (#1f77b4)

---

## Implementation Checklist

### Backend Functions
- [ ] Implement `get_insulin_by_inn_regions()` in bigquery_client.py
- [ ] Implement `get_insulin_by_inn_sectors()` in bigquery_client.py
- [ ] Implement `get_insulin_by_inn_chart_data()` in bigquery_client.py
- [ ] Add imports to app.py (plotly.graph_objects already imported)
- [ ] Add caching decorators with ttl=600
- [ ] Verify `is_unavailable` column exists in adl_repeat_repivot table
- [ ] Verify `insulin_inn` column exists in adl_repeat_repivot table
- [ ] Verify `region` column exists in adl_surveys table
- [ ] Verify `sector` column exists in adl_surveys table

### UI Implementation
- [ ] Add sub-heading "Insulin availability - By INN"
- [ ] Create two-column layout for Region and Sector filters
- [ ] Implement Region dropdown with checkboxes
- [ ] Add excluded count display inside Region dropdown
- [ ] Implement Sector dropdown with checkboxes
- [ ] Add excluded count display inside Sector dropdown
- [ ] Implement single bar chart with Plotly go.Bar
- [ ] Configure chart title: "Facilities with Availability (%)"
- [ ] Configure y-axis: Percentage format, 0-110 range
- [ ] Configure x-axis: "Insulin INN" title, INN names at -45°
- [ ] Add data labels on bars (pre-formatted percentage values)
- [ ] Configure hover tooltips
- [ ] Add "No data available" handling for chart
- [ ] Add tip message when no period selected
- [ ] Set chart height to 450px
- [ ] Add note message below chart: "Only insulins found to be available are shown"

### Filter Integration
- [ ] Global Data Collection Period filter applied
- [ ] Global Country filter applied (if selected)
- [ ] Global Region filter applied (if selected)
- [ ] Local Region dropdown respects global filters
- [ ] Local Region dropdown excludes NULL values
- [ ] Local Region dropdown uses adl_surveys table
- [ ] Local Sector dropdown respects global filters
- [ ] Local Sector dropdown excludes NULL values
- [ ] Local Sector dropdown uses adl_surveys table
- [ ] Chart respects all filters (global + local region + local sector)
- [ ] Chart uses adl_repeat_repivot table
- [ ] Chart groups by insulin_inn
- [ ] Chart filters availability > 0% (HAVING clause)
- [ ] Chart sorts DESC by availability_percentage

### Chart Styling
- [ ] Use color `#1f77b4` (blue)
- [ ] Set transparent background
- [ ] Add percentage symbol to y-axis ticks
- [ ] Format percentage labels on bars (1 decimal place)
- [ ] Configure hover template with custom formatting
- [ ] Apply responsive width with `use_container_width=True`
- [ ] Set appropriate margins
- [ ] Sort x-axis DESC by availability
- [ ] Add x-axis title "Insulin INN"
- [ ] Angle x-axis labels at -45°

### Validation & Testing
- [ ] Verify percentage formula: (COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id)) * 100
- [ ] Test division by zero handling
- [ ] Test NULL value handling in is_unavailable
- [ ] Test with various filter combinations
- [ ] Verify chart values match database calculations
- [ ] Verify bars are sorted DESC by availability
- [ ] Verify ONLY insulins with > 0% availability are shown
- [ ] Verify excluded region/sector logic works correctly
- [ ] Test responsive design (chart uses use_container_width=True)
- [ ] Verify hover tooltips display correctly
- [ ] Test independence from other components (Plan 3-7)
- [ ] Verify note message appears below chart

**Implementation Status:** ⏳ **PENDING** - Ready for implementation

---

## Success Criteria

1. **Data Accuracy:** Chart percentages match database calculations exactly
2. **Filter Cascade:** Local Region and Sector dropdowns properly respect global filters
3. **Filter Logic:** Chart respects all filters (global + local region + local sector)
4. **Availability Filter:** ONLY insulins with > 0% availability are displayed
5. **Performance:** Component loads within 2 seconds
6. **Responsiveness:** Chart updates immediately when Region or Sector filter changes
7. **Error Handling:** Graceful handling of empty data, NULL values, division by zero
8. **User Experience:** Clear messaging when no data available
9. **Visual Quality:** Chart is visually appealing, readable, and matches dashboard style
10. **Sorting:** Bars display in correct order (highest to lowest availability)
11. **Independence:** Component works independently of Plan 3-7 components
12. **Table Usage:** Dropdowns use adl_surveys, chart uses adl_repeat_repivot
13. **Note Display:** Note message appears below chart with correct styling

---

## Notes & Assumptions

### Assumed Column Schema

**Table: adl_surveys**
- `form_case__case_id`: Unique facility identifier
- `data_collection_period`: Period identifier
- `country`: Country name (optional)
- `region`: Region name (may contain NULL values to exclude)
- `sector`: Sector name (may contain NULL values to exclude)

**Table: adl_repeat_repivot**
- `is_unavailable`: Integer (0 = available, 1 = not available)
- `insulin_inn`: String with INN names (Regular, NPH, Lispro, Aspart, Glargine, etc.)
- `form_case__case_id`: Unique facility identifier
- `data_collection_period`: Period identifier
- `country`: Country name (optional)
- `region`: Region name (may contain NULL values)
- `sector`: Sector name (may contain NULL values)

### Key Differences from Plan 7
1. **Two filters instead of one:** Region AND Sector (Plan 7 had only Region)
2. **Different grouping:** By insulin_inn instead of by level_of_care
3. **Different X-axis:** Insulin INN names instead of level of care
4. **Different sorting:** DESC by availability percentage (Plan 7 was ASC by level_of_care)
5. **Additional filter:** ONLY show insulins with availability > 0% (HAVING clause)
6. **Different tables:** Uses adl_surveys for dropdowns (Plan 7 used adl_repeat_repivot)
7. **No implicit filter:** All sectors included (Plan 7 filtered for Public only)
8. **Single chart:** One chart instead of two (Human/Analogue)
9. **Note message:** Added below chart to explain filtering logic

### Metric Calculation Logic
**Plan 8 (By INN):**
```sql
COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) / COUNT(DISTINCT form_case__case_id) * 100
-- Where is_unavailable = 0 means available
-- Grouped by insulin_inn
-- HAVING availability_percentage > 0 (only show available insulins)
-- Sorted DESC by availability_percentage
```

### INN (International Nonproprietary Name)
INN is the generic name for a pharmaceutical substance. For insulin, common INNs include:
- **Regular** (short-acting human insulin)
- **NPH** (intermediate-acting human insulin)
- **Lispro** (rapid-acting analogue)
- **Aspart** (rapid-acting analogue)
- **Glargine** (long-acting analogue)
- **Detemir** (long-acting analogue)
- **Degludec** (ultra-long-acting analogue)

### Plotly Implementation Pattern
Following Plan 4, 5, 6, and 7's proven pattern:
- Use `plotly.graph_objects.Bar` for explicit control
- Explicit data type conversion with `pd.to_numeric()`
- Pre-formatted text labels as Python strings
- Y-axis range [0, 110] for outside text labels
- Manual customdata for hover tooltips
- X-axis title explicitly set to "Insulin INN"
- X-axis labels angled at -45° for readability

### Session State Key Naming
Use unique prefix `insulin_by_inn_` to avoid conflicts:
- Plan 3: `insulin_region_`, `insulin_sector_`
- Plan 4: `insulin_by_sector_region_`
- Plan 5: `insulin_by_type_region_`, `insulin_by_type_sector_`
- Plan 6: `insulin_by_region_sector_`
- Plan 7: `insulin_public_levelcare_region_`
- Plan 8: `insulin_by_inn_region_`, `insulin_by_inn_sector_`

This ensures all components coexist without state interference.

---

## Next Steps After Plan 8 Completion

1. User acceptance testing with real data from adl_repeat_repivot table
2. Verify chart displays correct INN availability percentages
3. Validate percentage calculations against manual checks
4. Test filter interactions with Plan 3-7 components (ensure independence)
5. Verify two-column filter layout works on various screen sizes
6. Verify ONLY insulins with > 0% availability are shown
7. Verify bars are sorted DESC by availability percentage
8. Verify note message appears correctly below chart
9. Document any data quality issues (missing INN, NULL values, etc.)
10. Proceed to next insulin availability filter/visualization if any

---

## Implementation Notes

### Key Similarities with Plan 5
1. ✅ Two-filter design (Region and Sector)
2. ✅ Checkbox dropdown implementation pattern
3. ✅ Excluded count display
4. ✅ Session state management for checkboxes
5. ✅ Global filter integration
6. ✅ Error handling for empty data
7. ✅ Caching strategy with @st.cache_data(ttl=600)
8. ✅ Plotly go.Bar chart pattern
9. ✅ Data type conversion with pd.to_numeric()
10. ✅ Pre-formatted text labels
11. ✅ Custom hover tooltips
12. ✅ Same availability logic (is_unavailable = 0)
13. ✅ Two-column filter layout

### New Patterns Introduced
1. 🆕 HAVING clause to filter availability > 0% at database level
2. 🆕 DESC sorting by availability percentage (highest to lowest)
3. 🆕 Grouping by insulin_inn instead of insulin_type or level_of_care
4. 🆕 Mixed table usage (adl_surveys for dropdowns, adl_repeat_repivot for chart)
5. 🆕 Note message below chart to explain filtering logic
6. 🆕 X-axis title "Insulin INN" instead of "Insulin Type" or "Level of Care"
7. 🆕 Always angle x-axis labels at -45° (not conditional)

### Potential Challenges
1. **INN data quality:** Verify insulin_inn column has clean, consistent INN names
2. **HAVING clause performance:** Ensure HAVING clause doesn't slow query significantly
3. **Table mismatch:** Dropdowns from adl_surveys, chart from adl_repeat_repivot (ensure consistency)
4. **Empty chart:** All insulins might have 0% availability (filtered out by HAVING clause)
5. **Long INN names:** Some INNs might have long names that overlap even at -45° angle
6. **Sorting consistency:** DESC sorting should always show highest availability first

### Recommended Testing Sequence
1. First verify adl_surveys and adl_repeat_repivot table schemas
2. Test region dropdown function with adl_surveys table
3. Test sector dropdown function with adl_surveys table
4. Verify insulin_inn values in adl_repeat_repivot are as expected
5. Test chart function with hardcoded filters
6. Verify HAVING clause correctly filters availability > 0%
7. Integrate Region and Sector filters with chart
8. Test full filter cascade (global + local region + local sector)
9. Test responsive layout
10. Final visual validation with note message

---

## Database Table Information

### Table: adl_surveys

**Purpose:** Contains main survey data for facilities

**Expected Columns:**
- `form_case__case_id`: Unique facility identifier
- `data_collection_period`: Period identifier (e.g., "Y1/P1")
- `country`: Country name
- `region`: Region name (may contain NULL) - **Used for Region dropdown**
- `sector`: Sector name (may contain NULL) - **Used for Sector dropdown**

**Usage in this component:** Source for Region and Sector dropdowns

### Table: adl_repeat_repivot

**Purpose:** Contains insulin availability data with repeat entries repivoted for analysis

**Expected Columns:**
- `form_case__case_id`: Unique facility identifier
- `data_collection_period`: Period identifier (e.g., "Y1/P1")
- `country`: Country name
- `region`: Region name (may contain NULL)
- `sector`: Sector name (may contain NULL)
- `insulin_inn`: INN name - **Used for grouping in chart**
- `is_unavailable`: Integer (0 = available, 1 = not available)

**Usage in this component:** Source for bar chart data

**Data Quality Checks:**
- Check for NULL values in critical columns (insulin_inn, region, sector, is_unavailable)
- Verify insulin_inn has recognizable INN names (Regular, NPH, Lispro, etc.)
- Check distribution of is_unavailable values (0 vs 1)
- Verify availability > 0% filter works correctly

---

## UI Layout Visual Guide

```
┌─────────────────────────────────────────────────────────────────┐
│ #### Insulin availability - By INN                              │
├─────────────────────────────────────────────────────────────────┤
│ Region ▼                      │ Sector ▼                        │
│ Select Regions (X/Y selected) │ Select Sectors (X/Y selected)   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐   │
│ │ Facilities with Availability (%)                          │   │
│ │                                                           │   │
│ │  [Bar Chart: By Insulin INN]                              │   │
│ │                                                           │   │
│ │  X-axis: Insulin INN (Regular, NPH, Lispro, Aspart...)   │   │
│ │  Y-axis: Availability (%)                                 │   │
│ │  Sorted: DESC by availability percentage                  │   │
│ │  Filtered: Only insulins with > 0% availability           │   │
│ │                                                           │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ 📝 Note: Only insulins found to be available are shown.        │
└─────────────────────────────────────────────────────────────────┘
```

---

**End of Plan 8 Refined Document**