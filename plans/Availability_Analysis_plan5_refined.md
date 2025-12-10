# Dashboard UI Revamp - Plan 5: Insulin Availability - By Insulin Type Component

## Task Overview
Implement the "Insulin Availability - By Insulin Type" component with local Region and Sector filter dropdowns and two Plotly bar charts showing percentage availability for Human and Analogue insulin types.

**Use Serena MCP:** Define todo items list and solve them one by one according to this detailed plan.

**Current Phase:** Backend Integration and UI Implementation with Dual Plotly Visualizations
**Prerequisites:** Plan 4 completed (Insulin Availability - By Sector component)

---

## Component Placement

**Location:** Add after "Insulin Availability - By Sector" component in app.py (after Plan 4, before next component/tab)

**Visual Hierarchy:**
```
[Insulin Availability - By Sector component]
    ↓
<br><br> spacing
    ↓
[Sub-heading: "Insulin availability - By insulin type"]
    ↓
[Two-column filter row: Region | Sector]
    ↓
[Two Bar Charts side-by-side: "Human" | "Analogue"]
```

---

## Component Structure

### 1. Sub-heading
```python
st.markdown("#### Insulin availability - By insulin type")
```

### 2. Two-Column Filter Layout

**Column 1: Region Dropdown**
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

**Column 2: Sector Dropdown**
- Same checkbox dropdown pattern as Region
- Dropdown label shows: "Select Sectors (X/Y selected)" where X=selected, Y=total
- Default state: Collapsed (expanded=False)
- Each checkbox shows: "Sector Name (count)" format
- Displays excluded items count inside dropdown: "🚫 X items excluded"
- Filters data within this component only
- Default: All sectors selected (all checkboxes checked)
- Unchecked items are excluded from analysis

### 3. Two Bar Chart Visualizations (Side-by-Side)

**Chart 1 Title:** "Human"
**Chart 2 Title:** "Analogue"

**Chart Type:** Plotly Bar Chart (using **plotly.graph_objects.Bar** for explicit data type control)

**Chart Specifications (Both Charts):**
- **Y-axis:** Percentage values (0-100%)
  - Label: "Facilities with Availability (%)"
  - Format: Show percentage symbol
  - Grid lines: Enabled for readability
- **X-axis:** Insulin type names
  - Label: Not shown (implicit - insulin types)
  - Values: Display insulin type names (e.g., "Insulin type: Regular Human", "Insulin type: NPH Human", "Insulin type: Lispro Analogue")
  - Rotation: Angle labels if needed for long names
- **Bars:**
  - Color: Use single color from existing palette (e.g., `#1f77b4` or gradient)
  - Width: Appropriate spacing between bars
  - Shaded area: Represents percentage value
  - Data labels: Show percentage value on top of each bar (e.g., "75.5%")
  - Hover info: Display insulin type, percentage value, available facilities count, and total facilities count
- **Layout:**
  - Responsive: Use `use_container_width=True`
  - Background: Transparent (`plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'`)
  - Height: ~400-500px for optimal viewing

**Example Human Chart Data:**
| Insulin Type | Availability (%) |
|--------------|------------------|
| Insulin type: Regular Human | 65.3 |
| Insulin type: NPH Human | 72.8 |

**Example Analogue Chart Data:**
| Insulin Type | Availability (%) |
|--------------|------------------|
| Insulin type: Lispro Analogue | 45.2 |
| Insulin type: Aspart Analogue | 38.9 |
| Insulin type: Glargine Analogue | 52.1 |

---

## Filter Behavior & Scope

### Global Filters (From Data Selectors)
These filters apply to ALL components including this one:
- ✅ Data Collection Period (REQUIRED)
- ✅ Country (optional)
- ✅ Region (optional) - **Note:** If global Region is selected, it restricts the local Region dropdown options

### Local Filters (Component-Specific)
These filters ONLY affect this component's bar charts:
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
Both Bar Charts → Display data filtered by global + local region + local sector filters, grouped by insulin_type
```

**Example:**
- User selects: Global Period = "Y1/P1", Global Country = "Tanzania", Local Region = "Eastern", Local Sector = "Public sector: MINSA"
- Component behavior:
  - Local Region dropdown: Shows all regions in Tanzania for Y1/P1
  - Local Sector dropdown: Shows all sectors in Tanzania for Y1/P1
  - Both Charts: Show availability percentages by insulin type for facilities in "Eastern" region, "Public sector: MINSA" during "Y1/P1"

---

## Database Query Specifications

### Common Parameters
- **Source Table:** `adl_repeat_repivot`
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
FROM `{GCP_PROJECT_ID}.{BQ_DATASET}.adl_repeat_repivot`
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

### Query 2: Sector Dropdown Options

**Purpose:** Populate local Sector dropdown with options

**SQL Pattern:**
```sql
SELECT
    sector,
    COUNT(DISTINCT form_case__case_id) as facility_count
FROM `{GCP_PROJECT_ID}.{BQ_DATASET}.adl_repeat_repivot`
WHERE
    data_collection_period IN ({selected_periods})
    AND ({country_filter})  -- if global country selected
    AND ({region_filter})   -- if global region selected
    AND sector IS NOT NULL
    AND TRIM(sector) != ''
GROUP BY sector
ORDER BY sector DESC
```

**Expected Output:** DataFrame with columns: sector, facility_count

**Notes:**
- Filter excludes NULL/empty sectors
- Sorted DESC as per plan requirement

---

### Query 3: Human Chart Data - Availability by Insulin Type (Human)

**Purpose:** Calculate percentage of facilities with insulin availability for Human insulin types

**Column Assumptions:**
- `is_unavailable`: Integer column (0 = available, 1 = not available)
- `insulin_type_order`: Integer column for sorting
- `insulin_type`: String column with insulin type names
- `form_case__case_id`: Unique facility identifier

**SQL Pattern:**
```sql
SELECT
    insulin_type,
    insulin_type_order,
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
    AND ({region_filter})   -- if global region selected
    AND ({local_region_filter})  -- if local region selected in component
    AND ({local_sector_filter})  -- if local sector selected in component
    AND insulin_type IS NOT NULL
    AND TRIM(insulin_type) != ''
    AND insulin_type LIKE '%Human%'
GROUP BY insulin_type, insulin_type_order
ORDER BY insulin_type_order ASC
```

**Expected Output:** DataFrame with columns:
- `insulin_type` (string): Insulin type name
- `insulin_type_order` (int): Order value for sorting
- `total_facilities` (int): Total facilities surveyed
- `facilities_with_insulin` (int): Facilities with insulin available (is_unavailable = 0)
- `availability_percentage` (float): Percentage (0-100, 1 decimal place)

**Validation Rules:**
- If result is empty, show "No data available" message
- `availability_percentage` should be between 0 and 100
- `facilities_with_insulin` ≤ `total_facilities`
- Sorted by `insulin_type_order ASC` for consistent bar ordering

---

### Query 4: Analogue Chart Data - Availability by Insulin Type (Analogue)

**Purpose:** Calculate percentage of facilities with insulin availability for Analogue insulin types

**SQL Pattern:**
```sql
SELECT
    insulin_type,
    insulin_type_order,
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
    AND ({region_filter})   -- if global region selected
    AND ({local_region_filter})  -- if local region selected in component
    AND ({local_sector_filter})  -- if local sector selected in component
    AND insulin_type IS NOT NULL
    AND TRIM(insulin_type) != ''
    AND insulin_type LIKE '%Analogue%'
GROUP BY insulin_type, insulin_type_order
ORDER BY insulin_type_order ASC
```

**Expected Output:** Same structure as Query 3, but filtered for Analogue insulin types

**Validation Rules:** Same as Query 3

---

## Implementation Functions

### Function 1: get_insulin_by_type_regions()

```python
@st.cache_data(ttl=600)
def get_insulin_by_type_regions(_client, table_name, global_filters):
    """
    Get regions for local Region dropdown in Insulin Availability - By Insulin Type component.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
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

### Function 2: get_insulin_by_type_sectors()

```python
@st.cache_data(ttl=600)
def get_insulin_by_type_sectors(_client, table_name, global_filters):
    """
    Get sectors for local Sector dropdown in Insulin Availability - By Insulin Type component.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors

    Returns:
        pandas DataFrame with columns: sector, facility_count
    """
    # Build WHERE clause with global filters
    # Exclude NULL sectors
    # Execute query
    # Return results sorted DESC
```

---

### Function 3: get_insulin_by_type_human_chart_data()

```python
@st.cache_data(ttl=600)
def get_insulin_by_type_human_chart_data(_client, table_name, global_filters, local_regions, local_sectors):
    """
    Get insulin availability percentages by insulin type for Human insulin bar chart.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        pandas DataFrame with columns:
            - insulin_type (str)
            - insulin_type_order (int)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)
    """
    # Build WHERE clause with global + local filters
    # Filter: insulin_type LIKE '%Human%'
    # Calculate: COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id) * 100
    # Group by insulin_type
    # Order by insulin_type_order ASC
    # Execute query
    # Validate results
    # Return DataFrame
```

---

### Function 4: get_insulin_by_type_analogue_chart_data()

```python
@st.cache_data(ttl=600)
def get_insulin_by_type_analogue_chart_data(_client, table_name, global_filters, local_regions, local_sectors):
    """
    Get insulin availability percentages by insulin type for Analogue insulin bar chart.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        pandas DataFrame with columns:
            - insulin_type (str)
            - insulin_type_order (int)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)
    """
    # Build WHERE clause with global + local filters
    # Filter: insulin_type LIKE '%Analogue%'
    # Calculate: COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id) * 100
    # Group by insulin_type
    # Order by insulin_type_order ASC
    # Execute query
    # Validate results
    # Return DataFrame
```

---

## UI Implementation Pattern

### Step 1: Sub-heading

```python
# After Insulin Availability - By Sector component
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("#### Insulin availability - By insulin type")
```

---

### Step 2: Two-Column Filter Layout with Checkbox Dropdowns

```python
if st.session_state.selected_periods:
    # Build global filters dict
    global_filters = {
        'data_collection_period': st.session_state.selected_periods,
        'country': st.session_state.selected_countries if st.session_state.selected_countries else None,
        'region': st.session_state.selected_regions if st.session_state.selected_regions else None
    }

    # Create two columns for filters
    col1, col2 = st.columns(2)

    # Column 1: Region Filter
    with col1:
        st.markdown("**Region**")
        with st.spinner("Loading regions..."):
            region_df = get_insulin_by_type_regions(client, TABLE_NAME, global_filters)

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
                    checkbox_key = f"insulin_by_type_region_{region}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items from session state
                selected_count = sum(
                    1 for region, _ in region_data
                    if st.session_state.get(f"insulin_by_type_region_{region}", True)
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
                        checkbox_key = f"insulin_by_type_region_{region}"

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
            sector_df = get_insulin_by_type_sectors(client, TABLE_NAME, global_filters)

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
                    checkbox_key = f"insulin_by_type_sector_{sector}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items from session state
                selected_count = sum(
                    1 for sector, _ in sector_data
                    if st.session_state.get(f"insulin_by_type_sector_{sector}", True)
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
                        checkbox_key = f"insulin_by_type_sector_{sector}"

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

### Step 3: Two Plotly Bar Charts (Side-by-Side)

```python
    # Create two columns for charts
    chart_col1, chart_col2 = st.columns(2)

    # Chart 1: Human Insulin Types
    with chart_col1:
        st.markdown("**Human**")

        # Fetch chart data
        human_df = get_insulin_by_type_human_chart_data(
            client,
            TABLE_NAME,
            global_filters,
            local_regions,
            local_sectors
        )

        if human_df is not None and not human_df.empty:
            # Ensure data types are correct
            human_df['availability_percentage'] = pd.to_numeric(human_df['availability_percentage'], errors='coerce')
            human_df['total_facilities'] = pd.to_numeric(human_df['total_facilities'], errors='coerce')
            human_df['facilities_with_insulin'] = pd.to_numeric(human_df['facilities_with_insulin'], errors='coerce')

            # Create bar chart using graph_objects
            import plotly.graph_objects as go

            fig_human = go.Figure()

            fig_human.add_trace(go.Bar(
                x=human_df['insulin_type'].tolist(),
                y=human_df['availability_percentage'].tolist(),
                text=[f'{val:.1f}%' for val in human_df['availability_percentage'].tolist()],
                textposition='outside',
                marker_color='#1f77b4',
                hovertemplate='<b>%{x}</b><br>' +
                              'Availability: %{y:.1f}%<br>' +
                              'Available Facilities: %{customdata[0]:,}<br>' +
                              'Total Facilities: %{customdata[1]:,}<extra></extra>',
                customdata=human_df[['facilities_with_insulin', 'total_facilities']].values
            ))

            # Update layout
            fig_human.update_layout(
                title='Facilities with Availability (%)',
                xaxis_title=None,
                yaxis_title='Facilities with Availability (%)',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=450,
                yaxis=dict(
                    range=[0, 110],
                    ticksuffix='%'
                ),
                xaxis_tickangle=-45 if len(human_df) > 3 else 0,
                showlegend=False,
                margin=dict(t=50, b=100, l=50, r=50)
            )

            # Display chart
            st.plotly_chart(fig_human, use_container_width=True)
        else:
            st.info("No data available for Human insulin types")

    # Chart 2: Analogue Insulin Types
    with chart_col2:
        st.markdown("**Analogue**")

        # Fetch chart data
        analogue_df = get_insulin_by_type_analogue_chart_data(
            client,
            TABLE_NAME,
            global_filters,
            local_regions,
            local_sectors
        )

        if analogue_df is not None and not analogue_df.empty:
            # Ensure data types are correct
            analogue_df['availability_percentage'] = pd.to_numeric(analogue_df['availability_percentage'], errors='coerce')
            analogue_df['total_facilities'] = pd.to_numeric(analogue_df['total_facilities'], errors='coerce')
            analogue_df['facilities_with_insulin'] = pd.to_numeric(analogue_df['facilities_with_insulin'], errors='coerce')

            # Create bar chart using graph_objects
            fig_analogue = go.Figure()

            fig_analogue.add_trace(go.Bar(
                x=analogue_df['insulin_type'].tolist(),
                y=analogue_df['availability_percentage'].tolist(),
                text=[f'{val:.1f}%' for val in analogue_df['availability_percentage'].tolist()],
                textposition='outside',
                marker_color='#ff7f0e',  # Different color for Analogue
                hovertemplate='<b>%{x}</b><br>' +
                              'Availability: %{y:.1f}%<br>' +
                              'Available Facilities: %{customdata[0]:,}<br>' +
                              'Total Facilities: %{customdata[1]:,}<extra></extra>',
                customdata=analogue_df[['facilities_with_insulin', 'total_facilities']].values
            ))

            # Update layout
            fig_analogue.update_layout(
                title='Facilities with Availability (%)',
                xaxis_title=None,
                yaxis_title='Facilities with Availability (%)',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=450,
                yaxis=dict(
                    range=[0, 110],
                    ticksuffix='%'
                ),
                xaxis_tickangle=-45 if len(analogue_df) > 3 else 0,
                showlegend=False,
                margin=dict(t=50, b=100, l=50, r=50)
            )

            # Display chart
            st.plotly_chart(fig_analogue, use_container_width=True)
        else:
            st.info("No data available for Analogue insulin types")

else:
    st.markdown("""
        <div class="info-box">
            <strong>💡 Tip:</strong> Select one or more data collection periods above to view insulin availability by insulin type.
        </div>
    """, unsafe_allow_html=True)
```

**Implementation Notes:**
- **Two charts:** Human uses `#1f77b4` (blue), Analogue uses `#ff7f0e` (orange) for visual distinction
- **Data type conversion:** Essential `pd.to_numeric()` on all numeric columns
- **Text labels:** Pre-formatted percentage strings
- **Y-axis range:** Extended to [0, 110] for text labels above bars
- **Custom data:** Manually set for hover tooltips
- **Column layout:** `st.columns(2)` for side-by-side display

---

## Session State Management

### Initialize Local Filter State

```python
# Session state keys for this component use unique prefix to avoid conflicts
# Region checkboxes: insulin_by_type_region_{region_name}
# Sector checkboxes: insulin_by_type_sector_{sector_name}
# These are automatically managed by Streamlit when using st.checkbox with key parameter
```

**Note:** Using Streamlit's `key` parameter in checkbox handles state automatically. Different prefixes prevent conflicts with Plan 3 and Plan 4 components.

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

### 6. No Data After Filtering (Empty Charts)
```python
if human_df is None or human_df.empty:
    st.info("No data available for Human insulin types")

if analogue_df is None or analogue_df.empty:
    st.info("No data available for Analogue insulin types")
```

### 7. Missing insulin_type_order Column
```python
# If insulin_type_order column doesn't exist, fallback to alphabetical sort
# Add try/except in query function or check schema beforehand
```

### 8. NULL/Empty Insulin Type Names
```python
# Filter in WHERE clause:
AND insulin_type IS NOT NULL
AND TRIM(insulin_type) != ''
```

### 9. No Insulin Types Match Filter
```python
# Query returns empty result if no insulin_type contains "Human" or "Analogue"
# Handle with "No data available" message
```

---

## Performance Optimization

### Caching Strategy
- All BigQuery functions use `@st.cache_data(ttl=600)` for 10-minute cache
- Cache keys include filter parameters to ensure correct data per filter combination
- Four separate cached functions allow independent data fetching
- Plotly chart creation is fast, no caching needed for visualization

### Query Optimization
- Use single query for all chart metrics (availability %, total facilities, available facilities)
- Apply filters at database level, not in Python
- Use `COUNT(DISTINCT)` and CASE WHEN efficiently
- Use `insulin_type_order` for consistent sorting
- Filter by insulin_type pattern (LIKE '%Human%' or '%Analogue%') at database level

### Parallel Data Fetching
- Region and Sector dropdowns can be fetched in parallel (independent queries)
- Human and Analogue chart data fetched separately (required for different filters)
- Consider loading both charts concurrently if performance becomes issue

---

## Styling & Responsive Design

### Plotly Chart Styling
- **Color scheme:**
  - Human chart: `#1f77b4` (blue) from existing palette
  - Analogue chart: `#ff7f0e` (orange) for visual distinction
- **Transparency:** Background transparent to match Streamlit theme
- **Font:** Plotly default fonts (readable, professional)
- **Hover effects:** Custom template with insulin type, percentage, and facility counts

### Responsive Behavior
- Charts use `use_container_width=True` for automatic width adjustment
- Two-column layout adapts to screen size
- On mobile, columns stack vertically
- X-axis labels rotate at -45° when many insulin types present
- Bar labels appear outside bars for clarity

### Consistency with Existing Components
- Use same section spacing (`<br><br>`)
- Use same markdown sub-heading style (`####`)
- Use same info-box class for messages
- Use same checkbox dropdown pattern from Plan 3 and Plan 4
- Use same two-column layout pattern

---

## Testing Requirements

### Unit Tests
```python
def test_get_insulin_by_type_regions():
    """Test region dropdown data fetching"""
    # Test with various filter combinations
    # Verify NULL/empty region exclusion
    # Verify DESC sorting

def test_get_insulin_by_type_sectors():
    """Test sector dropdown data fetching"""
    # Test with various filter combinations
    # Verify NULL/empty sector exclusion
    # Verify DESC sorting

def test_get_insulin_by_type_human_chart_data():
    """Test Human chart data fetching"""
    # Test with local region and sector filters
    # Verify percentage calculation
    # Verify insulin_type filter (LIKE '%Human%')
    # Verify insulin_type_order ASC sorting
    # Verify is_unavailable = 0 logic
    # Verify division by zero protection

def test_get_insulin_by_type_analogue_chart_data():
    """Test Analogue chart data fetching"""
    # Same tests as Human chart
    # Verify insulin_type filter (LIKE '%Analogue%')
```

### Integration Tests
1. Test filter cascade: Global → Local Region → Local Sector → Both Charts
2. Test charts update when Region or Sector filters change
3. Test with empty datasets (show "No data available")
4. Verify Human chart displays only Human insulin types
5. Verify Analogue chart displays only Analogue insulin types
6. Verify percentage values match database calculations
7. Test hover tooltips show correct information
8. Test with single vs multiple regions/sectors selected
9. Test independence from Plan 3 and Plan 4 components

### Visual Validation
1. Verify bars display in correct order (insulin_type_order ASC)
2. Verify percentage labels appear on top of bars
3. Verify y-axis range is 0-110%
4. Verify x-axis labels are readable (rotated if needed)
5. Verify chart height is appropriate (~450px)
6. Test responsive behavior on different screen sizes
7. Verify two charts display side-by-side on desktop
8. Verify charts stack vertically on mobile
9. Verify different colors for Human (blue) and Analogue (orange)

---

## Implementation Checklist

### Backend Functions
- [ ] Implement `get_insulin_by_type_regions()` in bigquery_client.py
- [ ] Implement `get_insulin_by_type_sectors()` in bigquery_client.py
- [ ] Implement `get_insulin_by_type_human_chart_data()` in bigquery_client.py
- [ ] Implement `get_insulin_by_type_analogue_chart_data()` in bigquery_client.py
- [ ] Add imports to app.py (including plotly.graph_objects if not already imported)
- [ ] Add caching decorators with ttl=600
- [ ] Verify `is_unavailable` column exists in adl_repeat_repivot table
- [ ] Verify `insulin_type_order` column exists in adl_repeat_repivot table
- [ ] Verify `insulin_type` column contains "Human" and "Analogue" values

### UI Implementation
- [ ] Add sub-heading "Insulin availability - By insulin type"
- [ ] Create two-column layout for filters (Region | Sector)
- [ ] Implement Region dropdown with checkboxes
- [ ] Implement Sector dropdown with checkboxes
- [ ] Add excluded count display inside both dropdowns
- [ ] Create two-column layout for charts (Human | Analogue)
- [ ] Implement Human chart with Plotly go.Bar
- [ ] Implement Analogue chart with Plotly go.Bar
- [ ] Configure chart titles: "Human" and "Analogue"
- [ ] Configure y-axis: Percentage format, 0-110 range
- [ ] Configure x-axis: Insulin type names, rotation if needed
- [ ] Add data labels on bars (pre-formatted percentage values)
- [ ] Configure hover tooltips for both charts
- [ ] Add "No data available" handling for both charts
- [ ] Add tip message when no period selected
- [ ] Set chart height to 450px for both charts
- [ ] Use different colors: Human (#1f77b4), Analogue (#ff7f0e)

### Filter Integration
- [ ] Global Data Collection Period filter applied
- [ ] Global Country filter applied (if selected)
- [ ] Global Region filter applied (if selected)
- [ ] Local Region dropdown respects global filters
- [ ] Local Sector dropdown respects global filters
- [ ] Local Region dropdown excludes NULL values
- [ ] Local Sector dropdown excludes NULL values
- [ ] Both charts respect all filters (global + local region + local sector)
- [ ] Human chart filters by insulin_type LIKE '%Human%'
- [ ] Analogue chart filters by insulin_type LIKE '%Analogue%'

### Chart Styling
- [ ] Human chart uses color `#1f77b4` (blue)
- [ ] Analogue chart uses color `#ff7f0e` (orange)
- [ ] Set transparent background for both charts
- [ ] Add percentage symbol to y-axis ticks
- [ ] Format percentage labels on bars (1 decimal place)
- [ ] Configure hover template with custom formatting
- [ ] Apply responsive width with `use_container_width=True`
- [ ] Set appropriate margins

### Validation & Testing
- [ ] Verify percentage formula: (COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id)) * 100
- [ ] Test division by zero handling
- [ ] Test NULL value handling in is_unavailable
- [ ] Test with various filter combinations
- [ ] Verify chart values match database calculations
- [ ] Test bars are sorted by insulin_type_order ASC
- [ ] Verify excluded region/sector logic works correctly
- [ ] Test responsive design (charts use use_container_width=True)
- [ ] Verify hover tooltips display correctly
- [ ] Verify Human chart only shows Human insulin types
- [ ] Verify Analogue chart only shows Analogue insulin types
- [ ] Test independence from other components (Plan 3, Plan 4)

**Implementation Status:** ⏳ **PENDING** - Ready for implementation

---

## Success Criteria

1. **Data Accuracy:** Both chart percentages match database calculations exactly
2. **Filter Cascade:** Local Region and Sector dropdowns properly respect global filters
3. **Filter Logic:** Human chart shows only Human types, Analogue chart shows only Analogue types
4. **Performance:** Component loads within 2 seconds
5. **Responsiveness:** Charts update immediately when Region or Sector filters change
6. **Error Handling:** Graceful handling of empty data, NULL values, division by zero
7. **User Experience:** Clear messaging when no data available
8. **Visual Quality:** Charts are visually appealing, readable, and match dashboard style
9. **Sorting:** Bars display in correct order (insulin_type_order ASC)
10. **Independence:** Component works independently of Plan 3 and Plan 4 components

---

## Notes & Assumptions

### Assumed Column Schema
- `is_unavailable`: Integer (0 = available, 1 = not available) - **Different from Plan 4's insulin_available_num**
- `insulin_type_order`: Integer for sorting
- `insulin_type`: String with insulin type names (contains "Human" or "Analogue")
- `form_case__case_id`: Unique facility identifier
- `region`: String with region names (may contain NULL values to exclude)
- `sector`: String with sector names (may contain NULL values to exclude)

### Key Differences from Plan 4
1. **Different table:** adl_repeat_repivot instead of adl_surveys
2. **Different availability column:** is_unavailable (0 = available) instead of insulin_available_num (1 = available)
3. **Different metric calculation:** COUNT(DISTINCT CASE WHEN is_unavailable = 0...) instead of SUM(insulin_available_num)
4. **Two filters:** Region AND Sector instead of just Region
5. **Two charts:** Human and Analogue instead of single chart
6. **Different grouping:** By insulin_type instead of sector
7. **Different filtering:** insulin_type LIKE '%Human%' or '%Analogue%'

### Metric Calculation Logic
**Plan 4 (By Sector):**
```sql
SUM(COALESCE(insulin_available_num, 0)) / COUNT(DISTINCT form_case__case_id) * 100
-- Where insulin_available_num = 1 means available
```

**Plan 5 (By Insulin Type):**
```sql
COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) / COUNT(DISTINCT form_case__case_id) * 100
-- Where is_unavailable = 0 means available
```

### Plotly Implementation Pattern
Following Plan 4's proven pattern:
- Use `plotly.graph_objects.Bar` for explicit control
- Explicit data type conversion with `pd.to_numeric()`
- Pre-formatted text labels as Python strings
- Y-axis range [0, 110] for outside text labels
- Manual customdata for hover tooltips
- Different colors for visual distinction (Human vs Analogue)

### Session State Key Naming
Use unique prefix `insulin_by_type_` to avoid conflicts:
- Plan 3: `insulin_region_`, `insulin_sector_`
- Plan 4: `insulin_by_sector_region_`
- Plan 5: `insulin_by_type_region_`, `insulin_by_type_sector_`

This ensures all components coexist without state interference.

---

## Next Steps After Plan 5 Completion

1. User acceptance testing with real data from adl_repeat_repivot table
2. Verify both charts display correct insulin types (Human vs Analogue)
3. Validate percentage calculations against manual checks
4. Test filter interactions with Plan 3 and Plan 4 components (ensure independence)
5. Verify two-column layout works on various screen sizes
6. Document any data quality issues (missing insulin_type_order, NULL values, etc.)
7. Proceed to next insulin availability filter/visualization if any

---

## Implementation Notes

### Key Similarities with Plan 4
1. ✅ Checkbox dropdown implementation pattern
2. ✅ Excluded count display
3. ✅ Session state management for checkboxes
4. ✅ Global filter integration
5. ✅ Error handling for empty data
6. ✅ Caching strategy with @st.cache_data(ttl=600)
7. ✅ Plotly go.Bar chart pattern
8. ✅ Data type conversion with pd.to_numeric()
9. ✅ Pre-formatted text labels
10. ✅ Custom hover tooltips

### New Patterns Introduced
1. 🆕 Two local filters (Region AND Sector) instead of one
2. 🆕 Two bar charts side-by-side instead of single chart
3. 🆕 Different color scheme for visual distinction (blue vs orange)
4. 🆕 Different data source (adl_repeat_repivot)
5. 🆕 Different availability logic (is_unavailable = 0 instead of insulin_available_num = 1)
6. 🆕 Filtering by substring pattern (LIKE '%Human%' or '%Analogue%')
7. 🆕 Four backend functions instead of two

### Potential Challenges
1. **Table availability:** Verify adl_repeat_repivot table exists in BigQuery
2. **Column existence:** Verify is_unavailable, insulin_type, insulin_type_order columns exist
3. **Data patterns:** Verify insulin_type column contains "Human" and "Analogue" substrings
4. **Filter interaction:** Two filters (Region + Sector) may result in very small datasets if too restrictive
5. **Empty charts:** One chart may have data while the other doesn't (e.g., only Human types available)
6. **Chart layout:** Side-by-side layout may need adjustment on smaller screens

### Recommended Testing Sequence
1. First verify table and column schema
2. Test each backend function independently
3. Test Region dropdown first
4. Test Sector dropdown second
5. Test Human chart with hardcoded filters
6. Test Analogue chart with hardcoded filters
7. Integrate filters with charts
8. Test full filter cascade
9. Test responsive layout
10. Final visual validation

---

## Database Table Information

### Table: adl_repeat_repivot

**Purpose:** Contains insulin availability data with repeat entries repivoted for analysis

**Expected Columns:**
- `form_case__case_id`: Unique facility identifier (PRIMARY KEY)
- `data_collection_period`: Period identifier (e.g., "Y1/P1")
- `country`: Country name
- `region`: Region name (may contain NULL)
- `sector`: Sector name (may contain NULL)
- `insulin_type`: Insulin type name (e.g., "Insulin type: Regular Human", "Insulin type: Lispro Analogue")
- `insulin_type_order`: Integer for sorting insulin types
- `is_unavailable`: Integer (0 = available, 1 = not available)

**Data Quality Checks:**
- Check for NULL values in critical columns
- Verify insulin_type contains "Human" or "Analogue" for filtering
- Verify insulin_type_order is properly populated for sorting
- Check distribution of is_unavailable values (0 vs 1)

---

## UI Layout Visual Guide

```
┌─────────────────────────────────────────────────────────────────┐
│ #### Insulin availability - By insulin type                     │
├─────────────────────────────────────────────────────────────────┤
│ Region ▼                          │ Sector ▼                    │
│ Select Regions (X/Y selected)     │ Select Sectors (X/Y selected)│
├───────────────────────────────────┴─────────────────────────────┤
│ Human                             │ Analogue                    │
│ ┌───────────────────────────────┐ │ ┌───────────────────────────┐│
│ │ Facilities with Availability  │ │ │ Facilities with Availability││
│ │ (%)                           │ │ │ (%)                       ││
│ │                               │ │ │                           ││
│ │  [Bar Chart: Human Types]    │ │ │  [Bar Chart: Analogue]   ││
│ │                               │ │ │                           ││
│ │  - Regular Human              │ │ │  - Lispro Analogue        ││
│ │  - NPH Human                  │ │ │  - Aspart Analogue        ││
│ │  - etc.                       │ │ │  - Glargine Analogue      ││
│ │                               │ │ │  - etc.                   ││
│ └───────────────────────────────┘ │ └───────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

**End of Plan 5 Refined Document**
