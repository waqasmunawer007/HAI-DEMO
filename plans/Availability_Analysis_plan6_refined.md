# Dashboard UI Revamp - Plan 6: Insulin Availability - By Region Component

## Task Overview
Implement the "Insulin Availability - By Region" component with a local Sector filter dropdown and two Plotly bar charts showing percentage availability for Human and Analogue insulin types, grouped by region.

**Use Serena MCP:** Define todo items list and solve them one by one according to this detailed plan.

**Current Phase:** Backend Integration and UI Implementation with Dual Plotly Visualizations
**Prerequisites:** Plan 5 completed (Insulin Availability - By Insulin Type component)

---

## Component Placement

**Location:** Add after "Insulin Availability - By Insulin Type" component in app.py (after Plan 5, before next component/tab)

**Visual Hierarchy:**
```
[Insulin Availability - By Insulin Type component]
    ↓
<br><br> spacing
    ↓
[Sub-heading: "Insulin availability - By region"]
    ↓
[Single-column filter row: Sector]
    ↓
[Two Bar Charts side-by-side: "Human" | "Analogue"]
```

---

## Component Structure

### 1. Sub-heading
```python
st.markdown("#### Insulin availability - By region")
```

### 2. Single-Column Sector Filter Layout

**Sector Dropdown**
- Expandable dropdown (st.expander) containing checkbox list
- Dropdown label shows: "Select Sectors (X/Y selected)" where X=selected, Y=total
- Default state: Collapsed (expanded=False)
- Inside dropdown: Individual checkboxes for each sector
- Each checkbox shows: "Sector Name (count)" format
- Displays excluded items count inside dropdown: "🚫 X items excluded"
- Filters data within this component only
- Independent from global Data Selectors
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
- **X-axis:** Region names
  - Label: Not shown (implicit - regions)
  - Values: Display region names (e.g., "Arequipa", "Ayacucho", "Cusco")
  - Rotation: Angle labels if needed for long names
- **Bars:**
  - Color: Use single color from existing palette (e.g., `#1f77b4` for Human, `#ff7f0e` for Analogue)
  - Width: Appropriate spacing between bars
  - Shaded area: Represents percentage value
  - Data labels: Show percentage value on top of each bar (e.g., "75.5%")
  - Hover info: Display region, percentage value, available facilities count, and total facilities count
- **Layout:**
  - Responsive: Use `use_container_width=True`
  - Background: Transparent (`plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'`)
  - Height: ~400-500px for optimal viewing

**Example Human Chart Data:**
| Region | Availability (%) |
|--------|------------------|
| Arequipa | 65.3 |
| Ayacucho | 72.8 |
| Cusco | 58.4 |

**Example Analogue Chart Data:**
| Region | Availability (%) |
|--------|------------------|
| Arequipa | 45.2 |
| Ayacucho | 38.9 |
| Cusco | 52.1 |

---

## Filter Behavior & Scope

### Global Filters (From Data Selectors)
These filters apply to ALL components including this one:
- ✅ Data Collection Period (REQUIRED)
- ✅ Country (optional)
- ✅ Region (optional) - **Note:** If global Region is selected, it restricts which regions appear in charts

### Local Filters (Component-Specific)
These filters ONLY affect this component's bar charts:
- ✅ Local Sector dropdown (filters within component)

### Filter Cascade Logic
```
Global Filters → Applied first to narrow dataset
    ↓
Local Sector dropdown → Shows only sectors within global filter constraints
    ↓
Both Bar Charts → Display data filtered by global + local sector filters, grouped by region
```

**Example:**
- User selects: Global Period = "Y1/P1", Global Country = "Peru", Local Sector = "Public sector: MINSA"
- Component behavior:
  - Local Sector dropdown: Shows all sectors in Peru for Y1/P1
  - Both Charts: Show availability percentages by region for facilities in "Public sector: MINSA" during "Y1/P1" in Peru

---

## Database Query Specifications

### Common Parameters
- **Applied Global Filters:**
  - `data_collection_period IN (selected_periods)` (REQUIRED)
  - `country IN (selected_countries)` (if selected)
  - `region IN (selected_regions)` (if selected from global Data Selectors)

### Query 1: Sector Dropdown Options

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
GROUP BY sector
ORDER BY sector DESC
```

**Expected Output:** DataFrame with columns: sector, facility_count

**Notes:**
- Uses `adl_surveys` table (different from chart data source)
- Filter excludes NULL/empty sectors
- Sorted DESC as per plan requirement

---

### Query 2: Human Chart Data - Availability by Region (Human Insulin)

**Purpose:** Calculate percentage of facilities with insulin availability for Human insulin types, grouped by region

**Source Table:** `adl_repeat_repivot`

**Column Assumptions:**
- `is_unavailable`: Integer column (0 = available, 1 = not available)
- `insulin_type`: String column with insulin type names
- `form_case__case_id`: Unique facility identifier
- `region`: Region name

**SQL Pattern:**
```sql
SELECT
    region,
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
    AND ({local_sector_filter})  -- if local sector selected in component
    AND region IS NOT NULL
    AND TRIM(region) != ''
    AND insulin_type IS NOT NULL
    AND insulin_type LIKE '%Human%'
GROUP BY region
ORDER BY region ASC
```

**Expected Output:** DataFrame with columns:
- `region` (string): Region name
- `total_facilities` (int): Total facilities surveyed
- `facilities_with_insulin` (int): Facilities with insulin available (is_unavailable = 0)
- `availability_percentage` (float): Percentage (0-100, 1 decimal place)

**Validation Rules:**
- If result is empty, show "No data available" message
- `availability_percentage` should be between 0 and 100
- `facilities_with_insulin` ≤ `total_facilities`
- Sorted by `region ASC` for consistent bar ordering

---

### Query 3: Analogue Chart Data - Availability by Region (Analogue Insulin)

**Purpose:** Calculate percentage of facilities with insulin availability for Analogue insulin types, grouped by region

**Source Table:** `adl_repeat_repivot`

**SQL Pattern:**
```sql
SELECT
    region,
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
    AND ({local_sector_filter})  -- if local sector selected in component
    AND region IS NOT NULL
    AND TRIM(region) != ''
    AND insulin_type IS NOT NULL
    AND insulin_type LIKE '%Analogue%'
GROUP BY region
ORDER BY region ASC
```

**Expected Output:** Same structure as Query 2, but filtered for Analogue insulin types

**Validation Rules:** Same as Query 2

---

## Implementation Functions

### Function 1: get_insulin_by_region_sectors()

```python
@st.cache_data(ttl=600)
def get_insulin_by_region_sectors(_client, table_name, global_filters):
    """
    Get sectors for local Sector dropdown in Insulin Availability - By Region component.

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
        pandas DataFrame with columns: sector, facility_count
    """
    # Build WHERE clause with global filters
    # Exclude NULL sectors
    # Execute query on adl_surveys table
    # Return results sorted DESC
```

---

### Function 2: get_insulin_by_region_human_chart_data()

```python
@st.cache_data(ttl=600)
def get_insulin_by_region_human_chart_data(_client, table_name, global_filters, local_sectors):
    """
    Get insulin availability percentages by region for Human insulin bar chart.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        pandas DataFrame with columns:
            - region (str)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)
    """
    # Build WHERE clause with global + local sector filter
    # Filter: insulin_type LIKE '%Human%'
    # Calculate: COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id) * 100
    # Group by region
    # Order by region ASC
    # Execute query on adl_repeat_repivot table
    # Validate results
    # Return DataFrame
```

---

### Function 3: get_insulin_by_region_analogue_chart_data()

```python
@st.cache_data(ttl=600)
def get_insulin_by_region_analogue_chart_data(_client, table_name, global_filters, local_sectors):
    """
    Get insulin availability percentages by region for Analogue insulin bar chart.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        pandas DataFrame with columns:
            - region (str)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)
    """
    # Build WHERE clause with global + local sector filter
    # Filter: insulin_type LIKE '%Analogue%'
    # Calculate: COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id) * 100
    # Group by region
    # Order by region ASC
    # Execute query on adl_repeat_repivot table
    # Validate results
    # Return DataFrame
```

---

## UI Implementation Pattern

### Step 1: Sub-heading

```python
# After Insulin Availability - By Insulin Type component
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("#### Insulin availability - By region")
```

---

### Step 2: Single-Column Sector Filter Layout with Checkbox Dropdown

```python
if st.session_state.selected_periods:
    # Build global filters dict
    global_filters = {
        'data_collection_period': st.session_state.selected_periods,
        'country': st.session_state.selected_countries if st.session_state.selected_countries else None,
        'region': st.session_state.selected_regions if st.session_state.selected_regions else None
    }

    # Sector Filter
    st.markdown("**Sector**")
    with st.spinner("Loading sectors..."):
        sector_df = get_insulin_by_region_sectors(client, 'adl_surveys', global_filters)

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
                checkbox_key = f"insulin_by_region_sector_{sector}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

            # Count selected items from session state
            selected_count = sum(
                1 for sector, _ in sector_data
                if st.session_state.get(f"insulin_by_region_sector_{sector}", True)
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
                    checkbox_key = f"insulin_by_region_sector_{sector}"

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

    # Chart 1: Human Insulin Types by Region
    with chart_col1:
        st.markdown("**Human**")

        # Fetch chart data
        human_df = get_insulin_by_region_human_chart_data(
            client,
            'adl_repeat_repivot',
            global_filters,
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
                x=human_df['region'].tolist(),
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

    # Chart 2: Analogue Insulin Types by Region
    with chart_col2:
        st.markdown("**Analogue**")

        # Fetch chart data
        analogue_df = get_insulin_by_region_analogue_chart_data(
            client,
            'adl_repeat_repivot',
            global_filters,
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
                x=analogue_df['region'].tolist(),
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
            <strong>💡 Tip:</strong> Select one or more data collection periods above to view insulin availability by region.
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
- **X-axis:** Regions sorted ASC for consistent ordering

---

## Session State Management

### Initialize Local Filter State

```python
# Session state keys for this component use unique prefix to avoid conflicts
# Sector checkboxes: insulin_by_region_sector_{sector_name}
# These are automatically managed by Streamlit when using st.checkbox with key parameter
```

**Note:** Using Streamlit's `key` parameter in checkbox handles state automatically. Unique prefix `insulin_by_region_` prevents conflicts with Plan 3, Plan 4, and Plan 5 components.

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

### 4. Empty Sector Dropdown
```python
if sector_df is None or sector_df.empty:
    st.info("No sector data available")
    local_sectors = []
```

### 5. No Data After Filtering (Empty Charts)
```python
if human_df is None or human_df.empty:
    st.info("No data available for Human insulin types")

if analogue_df is None or analogue_df.empty:
    st.info("No data available for Analogue insulin types")
```

### 6. NULL/Empty Region Names
```python
# Filter in WHERE clause:
AND region IS NOT NULL
AND TRIM(region) != ''
```

### 7. No Insulin Types Match Filter
```python
# Query returns empty result if no insulin_type contains "Human" or "Analogue"
# Handle with "No data available" message
```

### 8. Sector Filter from Different Table
```python
# Sector dropdown uses adl_surveys table
# Charts use adl_repeat_repivot table
# Ensure sector values are consistent across tables
# Handle case where sector exists in one table but not the other
```

### 9. No Sectors Selected
```python
# If user unchecks all sectors, local_sectors will be empty list
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
- Filter by insulin_type pattern (LIKE '%Human%' or '%Analogue%') at database level
- Group by region for aggregation

### Parallel Data Fetching
- Sector dropdown query is independent from chart queries
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
- **Hover effects:** Custom template with region, percentage, and facility counts

### Responsive Behavior
- Charts use `use_container_width=True` for automatic width adjustment
- Two-column layout adapts to screen size
- On mobile, columns stack vertically
- X-axis labels rotate at -45° when many regions present
- Bar labels appear outside bars for clarity

### Consistency with Existing Components
- Use same section spacing (`<br><br>`)
- Use same markdown sub-heading style (`####`)
- Use same info-box class for messages
- Use same checkbox dropdown pattern from Plan 3, 4, and 5
- Use same two-column layout pattern for charts

---

## Testing Requirements

### Unit Tests
```python
def test_get_insulin_by_region_sectors():
    """Test sector dropdown data fetching"""
    # Test with various filter combinations
    # Verify NULL/empty sector exclusion
    # Verify DESC sorting
    # Verify uses adl_surveys table

def test_get_insulin_by_region_human_chart_data():
    """Test Human chart data fetching"""
    # Test with local sector filter
    # Verify percentage calculation
    # Verify insulin_type filter (LIKE '%Human%')
    # Verify region ASC sorting
    # Verify is_unavailable = 0 logic
    # Verify division by zero protection
    # Verify uses adl_repeat_repivot table

def test_get_insulin_by_region_analogue_chart_data():
    """Test Analogue chart data fetching"""
    # Same tests as Human chart
    # Verify insulin_type filter (LIKE '%Analogue%')
```

### Integration Tests
1. Test filter cascade: Global → Local Sector → Both Charts
2. Test charts update when Sector filter changes
3. Test with empty datasets (show "No data available")
4. Verify Human chart displays Human insulin availability by region
5. Verify Analogue chart displays Analogue insulin availability by region
6. Verify percentage values match database calculations
7. Test hover tooltips show correct information
8. Test with single vs multiple sectors selected
9. Test independence from Plan 3, 4, and 5 components
10. Verify sector dropdown uses adl_surveys, charts use adl_repeat_repivot

### Visual Validation
1. Verify bars display in correct order (region ASC)
2. Verify percentage labels appear on top of bars
3. Verify y-axis range is 0-110%
4. Verify x-axis labels are readable (rotated if needed)
5. Verify chart height is appropriate (~450px)
6. Test responsive behavior on different screen sizes
7. Verify two charts display side-by-side on desktop
8. Verify charts stack vertically on mobile
9. Verify different colors for Human (blue) and Analogue (orange)
10. Verify single sector filter layout (not two-column like Plan 5)

---

## Implementation Checklist

### Backend Functions
- [ ] Implement `get_insulin_by_region_sectors()` in bigquery_client.py
- [ ] Implement `get_insulin_by_region_human_chart_data()` in bigquery_client.py
- [ ] Implement `get_insulin_by_region_analogue_chart_data()` in bigquery_client.py
- [ ] Add imports to app.py (including plotly.graph_objects if not already imported)
- [ ] Add caching decorators with ttl=600
- [ ] Verify `is_unavailable` column exists in adl_repeat_repivot table
- [ ] Verify `insulin_type` column contains "Human" and "Analogue" values
- [ ] Verify `sector` column exists in both adl_surveys and adl_repeat_repivot tables
- [ ] Verify `region` column exists in adl_repeat_repivot table

### UI Implementation
- [ ] Add sub-heading "Insulin availability - By region"
- [ ] Create single-column layout for Sector filter
- [ ] Implement Sector dropdown with checkboxes
- [ ] Add excluded count display inside Sector dropdown
- [ ] Create two-column layout for charts (Human | Analogue)
- [ ] Implement Human chart with Plotly go.Bar
- [ ] Implement Analogue chart with Plotly go.Bar
- [ ] Configure chart titles: "Human" and "Analogue"
- [ ] Configure y-axis: Percentage format, 0-110 range
- [ ] Configure x-axis: Region names, rotation if needed
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
- [ ] Local Sector dropdown respects global filters
- [ ] Local Sector dropdown excludes NULL values
- [ ] Local Sector dropdown uses adl_surveys table
- [ ] Both charts respect all filters (global + local sector)
- [ ] Both charts use adl_repeat_repivot table
- [ ] Human chart filters by insulin_type LIKE '%Human%'
- [ ] Analogue chart filters by insulin_type LIKE '%Analogue%'
- [ ] Both charts group by region

### Chart Styling
- [ ] Human chart uses color `#1f77b4` (blue)
- [ ] Analogue chart uses color `#ff7f0e` (orange)
- [ ] Set transparent background for both charts
- [ ] Add percentage symbol to y-axis ticks
- [ ] Format percentage labels on bars (1 decimal place)
- [ ] Configure hover template with custom formatting
- [ ] Apply responsive width with `use_container_width=True`
- [ ] Set appropriate margins
- [ ] Sort x-axis regions ASC

### Validation & Testing
- [ ] Verify percentage formula: (COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id)) * 100
- [ ] Test division by zero handling
- [ ] Test NULL value handling in is_unavailable
- [ ] Test with various filter combinations
- [ ] Verify chart values match database calculations
- [ ] Verify bars are sorted by region ASC
- [ ] Verify excluded sector logic works correctly
- [ ] Test responsive design (charts use use_container_width=True)
- [ ] Verify hover tooltips display correctly
- [ ] Verify Human chart shows Human insulin availability by region
- [ ] Verify Analogue chart shows Analogue insulin availability by region
- [ ] Test independence from other components (Plan 3, 4, 5)
- [ ] Verify sector dropdown data comes from adl_surveys
- [ ] Verify chart data comes from adl_repeat_repivot

**Implementation Status:** ⏳ **PENDING** - Ready for implementation

---

## Success Criteria

1. **Data Accuracy:** Both chart percentages match database calculations exactly
2. **Filter Cascade:** Local Sector dropdown properly respects global filters
3. **Filter Logic:** Human chart shows Human types, Analogue chart shows Analogue types, both grouped by region
4. **Performance:** Component loads within 2 seconds
5. **Responsiveness:** Charts update immediately when Sector filter changes
6. **Error Handling:** Graceful handling of empty data, NULL values, division by zero
7. **User Experience:** Clear messaging when no data available
8. **Visual Quality:** Charts are visually appealing, readable, and match dashboard style
9. **Sorting:** Bars display in correct order (region ASC)
10. **Independence:** Component works independently of Plan 3, 4, and 5 components
11. **Table Usage:** Sector dropdown uses adl_surveys, charts use adl_repeat_repivot

---

## Notes & Assumptions

### Assumed Column Schema

**Table: adl_surveys**
- `sector`: String with sector names (may contain NULL values to exclude)
- `form_case__case_id`: Unique facility identifier
- `data_collection_period`: Period identifier
- `country`: Country name (optional)
- `region`: Region name (optional)

**Table: adl_repeat_repivot**
- `is_unavailable`: Integer (0 = available, 1 = not available)
- `insulin_type`: String with insulin type names (contains "Human" or "Analogue")
- `form_case__case_id`: Unique facility identifier
- `region`: String with region names (may contain NULL values to exclude)
- `sector`: String with sector names (for filtering)
- `data_collection_period`: Period identifier
- `country`: Country name (optional)

### Key Differences from Plan 5
1. **Single filter:** Sector only (Plan 5 had Region AND Sector)
2. **Different grouping:** By region (Plan 5 grouped by insulin_type)
3. **Different table for dropdown:** adl_surveys for Sector dropdown (Plan 5 used adl_repeat_repivot for both)
4. **Same chart pattern:** Two charts (Human and Analogue) side-by-side
5. **Same availability logic:** is_unavailable = 0 means available
6. **Same data source for charts:** adl_repeat_repivot

### Metric Calculation Logic
**Plan 6 (By Region):**
```sql
COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) / COUNT(DISTINCT form_case__case_id) * 100
-- Where is_unavailable = 0 means available
-- Grouped by region
-- Filtered by insulin_type LIKE '%Human%' or '%Analogue%'
```

### Plotly Implementation Pattern
Following Plan 4 and Plan 5's proven pattern:
- Use `plotly.graph_objects.Bar` for explicit control
- Explicit data type conversion with `pd.to_numeric()`
- Pre-formatted text labels as Python strings
- Y-axis range [0, 110] for outside text labels
- Manual customdata for hover tooltips
- Different colors for visual distinction (Human vs Analogue)

### Session State Key Naming
Use unique prefix `insulin_by_region_` to avoid conflicts:
- Plan 3: `insulin_region_`, `insulin_sector_`
- Plan 4: `insulin_by_sector_region_`
- Plan 5: `insulin_by_type_region_`, `insulin_by_type_sector_`
- Plan 6: `insulin_by_region_sector_`

This ensures all components coexist without state interference.

---

## Next Steps After Plan 6 Completion

1. User acceptance testing with real data from adl_surveys and adl_repeat_repivot tables
2. Verify both charts display correct regional availability for Human vs Analogue
3. Validate percentage calculations against manual checks
4. Test filter interactions with Plan 3, 4, and 5 components (ensure independence)
5. Verify two-column chart layout works on various screen sizes
6. Verify sector dropdown uses adl_surveys, charts use adl_repeat_repivot
7. Document any data quality issues (missing regions, NULL values, etc.)
8. Proceed to next insulin availability filter/visualization if any

---

## Implementation Notes

### Key Similarities with Plan 5
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
11. ✅ Two bar charts side-by-side (Human and Analogue)
12. ✅ Same availability logic (is_unavailable = 0)

### New Patterns Introduced
1. 🆕 Single local filter (Sector only) instead of two filters
2. 🆕 Different grouping (by region instead of by insulin_type)
3. 🆕 Mixed table sources (adl_surveys for dropdown, adl_repeat_repivot for charts)
4. 🆕 X-axis shows regions instead of insulin types
5. 🆕 Three backend functions instead of four

### Potential Challenges
1. **Table mismatch:** Sector dropdown uses adl_surveys, charts use adl_repeat_repivot
   - Sectors must exist in both tables for meaningful filtering
   - If sector exists in adl_surveys but not in adl_repeat_repivot, charts may be empty
2. **Region availability:** Verify region column exists and is populated in adl_repeat_repivot
3. **Data consistency:** Verify sector values are consistent across both tables
4. **Filter interaction:** Single sector filter may result in small datasets if too restrictive
5. **Empty charts:** One chart may have data while the other doesn't (e.g., only Human types available in certain regions)
6. **Chart layout:** Side-by-side layout may need adjustment on smaller screens
7. **Many regions:** If too many regions, x-axis labels may overlap even with rotation

### Recommended Testing Sequence
1. First verify both tables (adl_surveys, adl_repeat_repivot) and column schemas
2. Test sector dropdown function (adl_surveys)
3. Verify sector values exist in both tables
4. Test Human chart function with hardcoded filters (adl_repeat_repivot)
5. Test Analogue chart function with hardcoded filters (adl_repeat_repivot)
6. Integrate Sector filter with both charts
7. Test full filter cascade (global + local)
8. Test responsive layout
9. Final visual validation
10. Test with various numbers of regions (few vs many)

---

## Database Table Information

### Table: adl_surveys

**Purpose:** Main survey responses table

**Expected Columns:**
- `form_case__case_id`: Unique facility identifier
- `data_collection_period`: Period identifier (e.g., "Y1/P1")
- `country`: Country name
- `region`: Region name (may contain NULL)
- `sector`: Sector name (used for Sector dropdown)

**Usage in this component:** Source for Sector dropdown options

---

### Table: adl_repeat_repivot

**Purpose:** Contains insulin availability data with repeat entries repivoted for analysis

**Expected Columns:**
- `form_case__case_id`: Unique facility identifier
- `data_collection_period`: Period identifier (e.g., "Y1/P1")
- `country`: Country name
- `region`: Region name (may contain NULL) - **Used for grouping in charts**
- `sector`: Sector name (used for filtering)
- `insulin_type`: Insulin type name (e.g., "Insulin type: Regular Human", "Insulin type: Lispro Analogue")
- `is_unavailable`: Integer (0 = available, 1 = not available)

**Usage in this component:** Source for both chart data (Human and Analogue)

**Data Quality Checks:**
- Check for NULL values in critical columns (region, insulin_type, is_unavailable)
- Verify insulin_type contains "Human" or "Analogue" for filtering
- Check distribution of is_unavailable values (0 vs 1)
- Verify sector values match between adl_surveys and adl_repeat_repivot
- Verify region column is properly populated

---

## UI Layout Visual Guide

```
┌─────────────────────────────────────────────────────────────────┐
│ #### Insulin availability - By region                           │
├─────────────────────────────────────────────────────────────────┤
│ Sector ▼                                                        │
│ Select Sectors (X/Y selected)                                   │
├─────────────────────────────────────────────────────────────────┤
│ Human                             │ Analogue                    │
│ ┌───────────────────────────────┐ │ ┌───────────────────────────┐│
│ │ Facilities with Availability  │ │ │ Facilities with Availability││
│ │ (%)                           │ │ │ (%)                       ││
│ │                               │ │ │                           ││
│ │  [Bar Chart: By Region]      │ │ │  [Bar Chart: By Region]  ││
│ │                               │ │ │                           ││
│ │  - Arequipa                   │ │ │  - Arequipa               ││
│ │  - Ayacucho                   │ │ │  - Ayacucho               ││
│ │  - Cusco                      │ │ │  - Cusco                  ││
│ │  - etc.                       │ │ │  - etc.                   ││
│ │                               │ │ │                           ││
│ └───────────────────────────────┘ │ └───────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

**End of Plan 6 Refined Document**
