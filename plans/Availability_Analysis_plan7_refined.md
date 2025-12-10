# Dashboard UI Revamp - Plan 7: Insulin Availability - Public Sector - By Level of Care Component

## Task Overview
Implement the "Insulin Availability - Public sector - By level of care" component with a local Region filter dropdown and two Plotly bar charts showing percentage availability for Human and Analogue insulin types, grouped by level of care (Primary, Secondary, Tertiary) for PUBLIC SECTOR facilities only.

**Use Serena MCP:** Define todo items list and solve them one by one according to this detailed plan.

**Current Phase:** Backend Integration and UI Implementation with Dual Plotly Visualizations
**Prerequisites:** Plan 6 completed (Insulin Availability - By Region component)

---

## Component Placement

**Location:** Add after "Insulin Availability - By Region" component in app.py (after Plan 6, before next component/tab)

**Visual Hierarchy:**
```
[Insulin Availability - By Region component]
    ↓
<br><br> spacing
    ↓
[Sub-heading: "Insulin availability - Public sector - By level of care"]
    ↓
[Single-column filter row: Region]
    ↓
[Two Bar Charts side-by-side: "Human" | "Analogue"]
```

---

## Component Structure

### 1. Sub-heading
```python
st.markdown("#### Insulin availability - Public sector - By level of care")
```

### 2. Single-Column Region Filter Layout

**Region Dropdown**
- Expandable dropdown (st.expander) containing checkbox list
- Dropdown label shows: "Select Regions (X/Y selected)" where X=selected, Y=total
- Default state: Collapsed (expanded=False)
- Inside dropdown: Individual checkboxes for each region
- Each checkbox shows: "Region Name (count)" format
- Displays excluded items count inside dropdown: "🚫 X items excluded"
- Filters data within this component only
- Independent from global Data Selectors
- Default: All regions selected (all checkboxes checked)
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
- **X-axis:** Level of Care categories
  - Label: "Level of Care"
  - Values: Display level of care names (Primary, Secondary, Tertiary)
  - Rotation: Angle labels if needed
- **Bars:**
  - Color: Use single color from existing palette (e.g., `#1f77b4` for Human, `#ff7f0e` for Analogue)
  - Width: Appropriate spacing between bars
  - Shaded area: Represents percentage value
  - Data labels: Show percentage value on top of each bar (e.g., "75.5%")
  - Hover info: Display level of care, percentage value, available facilities count, and total facilities count
- **Layout:**
  - Responsive: Use `use_container_width=True`
  - Background: Transparent (`plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'`)
  - Height: ~450px for optimal viewing

**Example Human Chart Data:**
| Level of Care | Availability (%) |
|---------------|------------------|
| Primary       | 65.3             |
| Secondary     | 72.8             |
| Tertiary      | 58.4             |

**Example Analogue Chart Data:**
| Level of Care | Availability (%) |
|---------------|------------------|
| Primary       | 45.2             |
| Secondary     | 38.9             |
| Tertiary      | 52.1             |

---

## Filter Behavior & Scope

### Global Filters (From Data Selectors)
These filters apply to ALL components including this one:
- ✅ Data Collection Period (REQUIRED)
- ✅ Country (optional)
- ✅ Region (optional) - **Note:** If global Region is selected, it restricts which regions appear in local dropdown

### Implicit Filters (Hardcoded)
This component ALWAYS filters for:
- ✅ Public Sector only (`sector LIKE '%Public%'`)

### Local Filters (Component-Specific)
These filters ONLY affect this component's bar charts:
- ✅ Local Region dropdown (filters within component)

### Filter Cascade Logic
```
Global Filters → Applied first to narrow dataset
    ↓
Implicit Public Sector Filter → Restricts to public facilities only
    ↓
Local Region dropdown → Shows only regions within global filter + public sector constraints
    ↓
Both Bar Charts → Display data filtered by global + implicit public sector + local region filters, grouped by level of care
```

**Example:**
- User selects: Global Period = "Y1/P1", Global Country = "Peru", Local Region = "Arequipa"
- Component behavior:
  - Implicit filter: Only Public sector facilities
  - Local Region dropdown: Shows all regions in Peru for Y1/P1 (Public sector only)
  - Both Charts: Show availability percentages by level of care for Public sector facilities in "Arequipa" during "Y1/P1" in Peru

---

## Database Query Specifications

### Common Parameters
- **Applied Global Filters:**
  - `data_collection_period IN (selected_periods)` (REQUIRED)
  - `country IN (selected_countries)` (if selected)
  - `region IN (selected_regions)` (if selected from global Data Selectors)
- **Applied Implicit Filters:**
  - `sector LIKE '%Public%'` (ALWAYS APPLIED)

### Query 1: Region Dropdown Options

**Purpose:** Populate local Region dropdown with options (Public sector facilities only)

**Source Table:** `adl_repeat_repivot`

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
    AND sector LIKE '%Public%'  -- PUBLIC SECTOR ONLY (implicit filter)
    AND region IS NOT NULL
    AND TRIM(region) != ''
    AND region != 'NULL'
GROUP BY region
ORDER BY region ASC
```

**Expected Output:** DataFrame with columns: region, facility_count

**Notes:**
- Uses `adl_repeat_repivot` table (same as chart data source)
- Filter excludes NULL/empty regions
- Filter ALWAYS includes Public sector only
- Sorted ASC for consistent ordering

---

### Query 2: Human Chart Data - Availability by Level of Care (Human Insulin)

**Purpose:** Calculate percentage of facilities with insulin availability for Human insulin types in PUBLIC SECTOR, grouped by level of care

**Source Table:** `adl_repeat_repivot`

**Column Assumptions:**
- `is_unavailable`: Integer column (0 = available, 1 = not available)
- `insulin_type`: String column with insulin type names
- `form_case__case_id`: Unique facility identifier
- `level_of_care`: Level of care category (Primary, Secondary, Tertiary)
- `sector`: Sector name (will filter for Public)

**SQL Pattern:**
```sql
SELECT
    level_of_care,
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
    AND sector LIKE '%Public%'  -- PUBLIC SECTOR ONLY (implicit filter)
    AND insulin_type LIKE '%Human%'
    AND level_of_care IS NOT NULL
    AND TRIM(level_of_care) != ''
    AND level_of_care NOT IN ('NULL', '---')
GROUP BY level_of_care
ORDER BY level_of_care ASC
```

**Expected Output:** DataFrame with columns:
- `level_of_care` (string): Level of care category
- `total_facilities` (int): Total facilities surveyed
- `facilities_with_insulin` (int): Facilities with insulin available (is_unavailable = 0)
- `availability_percentage` (float): Percentage (0-100, 1 decimal place)

**Validation Rules:**
- If result is empty, show "No data available" message
- `availability_percentage` should be between 0 and 100
- `facilities_with_insulin` ≤ `total_facilities`
- Sorted by `level_of_care ASC` for consistent bar ordering

---

### Query 3: Analogue Chart Data - Availability by Level of Care (Analogue Insulin)

**Purpose:** Calculate percentage of facilities with insulin availability for Analogue insulin types in PUBLIC SECTOR, grouped by level of care

**Source Table:** `adl_repeat_repivot`

**SQL Pattern:**
```sql
SELECT
    level_of_care,
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
    AND ({country_filter})
    AND ({global_region_filter})
    AND ({local_region_filter})
    AND sector LIKE '%Public%'  -- PUBLIC SECTOR ONLY (implicit filter)
    AND insulin_type LIKE '%Analogue%'
    AND level_of_care IS NOT NULL
    AND TRIM(level_of_care) != ''
    AND level_of_care NOT IN ('NULL', '---')
GROUP BY level_of_care
ORDER BY level_of_care ASC
```

**Expected Output:** Same structure as Query 2, but filtered for Analogue insulin types

**Validation Rules:** Same as Query 2

---

## Implementation Functions

### Function 1: get_insulin_public_levelcare_regions()

```python
@st.cache_data(ttl=600)
def get_insulin_public_levelcare_regions(_client, table_name, global_filters):
    """
    Get regions for local Region dropdown in Insulin Availability - Public Sector - By Level of Care component.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
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
    # Add implicit Public sector filter: sector LIKE '%Public%'
    # Exclude NULL/empty regions
    # Execute query on adl_repeat_repivot table
    # Return results sorted ASC
```

---

### Function 2: get_insulin_public_levelcare_human_chart_data()

```python
@st.cache_data(ttl=600)
def get_insulin_public_levelcare_human_chart_data(_client, table_name, global_filters, local_regions):
    """
    Get insulin availability percentages by level of care for Human insulin in Public sector.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown

    Returns:
        pandas DataFrame with columns:
            - level_of_care (str)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)
    """
    # Build WHERE clause with global + local region filter
    # Add implicit Public sector filter: sector LIKE '%Public%'
    # Filter: insulin_type LIKE '%Human%'
    # Exclude level_of_care: NULL, '---'
    # Calculate: COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id) * 100
    # Group by level_of_care
    # Order by level_of_care ASC
    # Execute query on adl_repeat_repivot table
    # Validate results
    # Return DataFrame
```

---

### Function 3: get_insulin_public_levelcare_analogue_chart_data()

```python
@st.cache_data(ttl=600)
def get_insulin_public_levelcare_analogue_chart_data(_client, table_name, global_filters, local_regions):
    """
    Get insulin availability percentages by level of care for Analogue insulin in Public sector.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown

    Returns:
        pandas DataFrame with columns:
            - level_of_care (str)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)
    """
    # Build WHERE clause with global + local region filter
    # Add implicit Public sector filter: sector LIKE '%Public%'
    # Filter: insulin_type LIKE '%Analogue%'
    # Exclude level_of_care: NULL, '---'
    # Calculate: COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id) * 100
    # Group by level_of_care
    # Order by level_of_care ASC
    # Execute query on adl_repeat_repivot table
    # Validate results
    # Return DataFrame
```

---

## UI Implementation Pattern

### Step 1: Sub-heading

```python
# After Insulin Availability - By Region component
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("#### Insulin availability - Public sector - By level of care")
```

---

### Step 2: Single-Column Region Filter Layout with Checkbox Dropdown

```python
# Note: Plan 7 uses adl_repeat_repivot for dropdown
PLAN7_TABLE_NAME = config.TABLES["repeat_repivot"]

if st.session_state.selected_periods:
    # Build global filters dict
    global_filters = {
        'data_collection_period': st.session_state.selected_periods,
        'country': st.session_state.selected_countries if st.session_state.selected_countries else None,
        'region': st.session_state.selected_regions if st.session_state.selected_regions else None
    }

    # Region Filter
    st.markdown("**Region**")
    with st.spinner("Loading regions..."):
        region_df = get_insulin_public_levelcare_regions(client, PLAN7_TABLE_NAME, global_filters)

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
                checkbox_key = f"insulin_public_levelcare_region_{region}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

            # Count selected items from session state
            selected_count = sum(
                1 for region, _ in region_data
                if st.session_state.get(f"insulin_public_levelcare_region_{region}", True)
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
                    checkbox_key = f"insulin_public_levelcare_region_{region}"

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
```

---

### Step 3: Two Plotly Bar Charts (Side-by-Side)

```python
    # Create two columns for charts
    st.markdown("<br>", unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns(2)

    # Chart 1: Human Insulin by Level of Care (Public Sector)
    with chart_col1:
        st.markdown("**Human**")

        with st.spinner("Loading Human insulin data by level of care..."):
            # Fetch chart data
            human_df = get_insulin_public_levelcare_human_chart_data(
                client,
                PLAN7_TABLE_NAME,
                global_filters,
                local_regions
            )

            if human_df is not None and not human_df.empty:
                # Ensure data types are correct
                human_df['availability_percentage'] = pd.to_numeric(human_df['availability_percentage'], errors='coerce')
                human_df['total_facilities'] = pd.to_numeric(human_df['total_facilities'], errors='coerce')
                human_df['facilities_with_insulin'] = pd.to_numeric(human_df['facilities_with_insulin'], errors='coerce')

                # Create bar chart using graph_objects
                fig_human = go.Figure()

                fig_human.add_trace(go.Bar(
                    x=human_df['level_of_care'].tolist(),
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
                    xaxis_title='Level of Care',
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

    # Chart 2: Analogue Insulin by Level of Care (Public Sector)
    with chart_col2:
        st.markdown("**Analogue**")

        with st.spinner("Loading Analogue insulin data by level of care..."):
            # Fetch chart data
            analogue_df = get_insulin_public_levelcare_analogue_chart_data(
                client,
                PLAN7_TABLE_NAME,
                global_filters,
                local_regions
            )

            if analogue_df is not None and not analogue_df.empty:
                # Ensure data types are correct
                analogue_df['availability_percentage'] = pd.to_numeric(analogue_df['availability_percentage'], errors='coerce')
                analogue_df['total_facilities'] = pd.to_numeric(analogue_df['total_facilities'], errors='coerce')
                analogue_df['facilities_with_insulin'] = pd.to_numeric(analogue_df['facilities_with_insulin'], errors='coerce')

                # Create bar chart using graph_objects
                fig_analogue = go.Figure()

                fig_analogue.add_trace(go.Bar(
                    x=analogue_df['level_of_care'].tolist(),
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
                    xaxis_title='Level of Care',
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
            <strong>💡 Tip:</strong> Select one or more data collection periods above to view insulin availability in the Public sector by level of care.
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
- **X-axis:** Level of care categories sorted ASC for consistent ordering
- **X-axis title:** "Level of Care" explicitly shown

---

## Session State Management

### Initialize Local Filter State

```python
# Session state keys for this component use unique prefix to avoid conflicts
# Region checkboxes: insulin_public_levelcare_region_{region_name}
# These are automatically managed by Streamlit when using st.checkbox with key parameter
```

**Note:** Using Streamlit's `key` parameter in checkbox handles state automatically. Unique prefix `insulin_public_levelcare_` prevents conflicts with Plan 3, Plan 4, Plan 5, and Plan 6 components.

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

### 5. No Data After Filtering (Empty Charts)
```python
if human_df is None or human_df.empty:
    st.info("No data available for Human insulin types")

if analogue_df is None or analogue_df.empty:
    st.info("No data available for Analogue insulin types")
```

### 6. NULL/Empty Level of Care Values
```python
# Filter in WHERE clause:
AND level_of_care IS NOT NULL
AND TRIM(level_of_care) != ''
AND level_of_care NOT IN ('NULL', '---')
```

### 7. No Insulin Types Match Filter
```python
# Query returns empty result if no insulin_type contains "Human" or "Analogue"
# Handle with "No data available" message
```

### 8. No Public Sector Facilities
```python
# If sector LIKE '%Public%' returns no results
# Region dropdown will be empty
# Display "No region data available" message
```

### 9. No Regions Selected
```python
# If user unchecks all regions, local_regions will be empty list
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
- Filter by sector (LIKE '%Public%'), insulin_type pattern (LIKE '%Human%' or '%Analogue%'), and level_of_care at database level
- Group by level_of_care for aggregation

### Parallel Data Fetching
- Region dropdown query is independent from chart queries
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
- **Hover effects:** Custom template with level of care, percentage, and facility counts

### Responsive Behavior
- Charts use `use_container_width=True` for automatic width adjustment
- Two-column layout adapts to screen size
- On mobile, columns stack vertically
- X-axis labels rotate at -45° when many categories present
- Bar labels appear outside bars for clarity

### Consistency with Existing Components
- Use same section spacing (`<br><br>`)
- Use same markdown sub-heading style (`####`)
- Use same info-box class for messages
- Use same checkbox dropdown pattern from Plan 3, 4, 5, and 6
- Use same two-column layout pattern for charts

---

## Testing Requirements

### Unit Tests
```python
def test_get_insulin_public_levelcare_regions():
    """Test region dropdown data fetching"""
    # Test with various filter combinations
    # Verify Public sector filter applied
    # Verify NULL/empty region exclusion
    # Verify ASC sorting
    # Verify uses adl_repeat_repivot table

def test_get_insulin_public_levelcare_human_chart_data():
    """Test Human chart data fetching"""
    # Test with local region filter
    # Verify percentage calculation
    # Verify Public sector filter applied
    # Verify insulin_type filter (LIKE '%Human%')
    # Verify level_of_care ASC sorting
    # Verify is_unavailable = 0 logic
    # Verify division by zero protection
    # Verify level_of_care NULL/'---' exclusion
    # Verify uses adl_repeat_repivot table

def test_get_insulin_public_levelcare_analogue_chart_data():
    """Test Analogue chart data fetching"""
    # Same tests as Human chart
    # Verify insulin_type filter (LIKE '%Analogue%')
```

### Integration Tests
1. Test filter cascade: Global → Implicit Public Sector → Local Region → Both Charts
2. Test charts update when Region filter changes
3. Test with empty datasets (show "No data available")
4. Verify Human chart displays Human insulin availability by level of care (Public sector)
5. Verify Analogue chart displays Analogue insulin availability by level of care (Public sector)
6. Verify percentage values match database calculations
7. Test hover tooltips show correct information
8. Test with single vs multiple regions selected
9. Test independence from Plan 3, 4, 5, and 6 components
10. Verify only Public sector data appears in all queries

### Visual Validation
1. Verify bars display in correct order (Primary, Secondary, Tertiary)
2. Verify percentage labels appear on top of bars
3. Verify y-axis range is 0-110%
4. Verify x-axis labels show "Primary", "Secondary", "Tertiary"
5. Verify x-axis title is "Level of Care"
6. Verify chart height is appropriate (~450px)
7. Test responsive behavior on different screen sizes
8. Verify two charts display side-by-side on desktop
9. Verify charts stack vertically on mobile
10. Verify different colors for Human (blue) and Analogue (orange)

---

## Implementation Checklist

### Backend Functions
- [ ] Implement `get_insulin_public_levelcare_regions()` in bigquery_client.py
- [ ] Implement `get_insulin_public_levelcare_human_chart_data()` in bigquery_client.py
- [ ] Implement `get_insulin_public_levelcare_analogue_chart_data()` in bigquery_client.py
- [ ] Add imports to app.py (plotly.graph_objects already imported)
- [ ] Add caching decorators with ttl=600
- [ ] Verify `is_unavailable` column exists in adl_repeat_repivot table
- [ ] Verify `insulin_type` column contains "Human" and "Analogue" values
- [ ] Verify `sector` column exists in adl_repeat_repivot table
- [ ] Verify `level_of_care` column exists in adl_repeat_repivot table
- [ ] Verify `region` column exists in adl_repeat_repivot table

### UI Implementation
- [ ] Add sub-heading "Insulin availability - Public sector - By level of care"
- [ ] Create single-column layout for Region filter
- [ ] Implement Region dropdown with checkboxes
- [ ] Add excluded count display inside Region dropdown
- [ ] Create two-column layout for charts (Human | Analogue)
- [ ] Implement Human chart with Plotly go.Bar
- [ ] Implement Analogue chart with Plotly go.Bar
- [ ] Configure chart titles: "Human" and "Analogue"
- [ ] Configure y-axis: Percentage format, 0-110 range
- [ ] Configure x-axis: "Level of Care" title, level categories
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
- [ ] Implicit Public sector filter applied to ALL queries
- [ ] Local Region dropdown respects global filters + public sector filter
- [ ] Local Region dropdown excludes NULL values
- [ ] Local Region dropdown uses adl_repeat_repivot table
- [ ] Both charts respect all filters (global + implicit public + local region)
- [ ] Both charts use adl_repeat_repivot table
- [ ] Human chart filters by insulin_type LIKE '%Human%'
- [ ] Analogue chart filters by insulin_type LIKE '%Analogue%'
- [ ] Both charts group by level_of_care
- [ ] Both charts exclude level_of_care NULL/'---'

### Chart Styling
- [ ] Human chart uses color `#1f77b4` (blue)
- [ ] Analogue chart uses color `#ff7f0e` (orange)
- [ ] Set transparent background for both charts
- [ ] Add percentage symbol to y-axis ticks
- [ ] Format percentage labels on bars (1 decimal place)
- [ ] Configure hover template with custom formatting
- [ ] Apply responsive width with `use_container_width=True`
- [ ] Set appropriate margins
- [ ] Sort x-axis level_of_care ASC
- [ ] Add x-axis title "Level of Care"

### Validation & Testing
- [ ] Verify percentage formula: (COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id)) * 100
- [ ] Test division by zero handling
- [ ] Test NULL value handling in is_unavailable
- [ ] Test with various filter combinations
- [ ] Verify chart values match database calculations
- [ ] Verify bars are sorted by level_of_care ASC
- [ ] Verify excluded region logic works correctly
- [ ] Test responsive design (charts use use_container_width=True)
- [ ] Verify hover tooltips display correctly
- [ ] Verify Human chart shows Human insulin availability by level of care
- [ ] Verify Analogue chart shows Analogue insulin availability by level of care
- [ ] Test independence from other components (Plan 3, 4, 5, 6)
- [ ] Verify only Public sector data appears (test with non-public data)

**Implementation Status:** ⏳ **PENDING** - Ready for implementation

---

## Success Criteria

1. **Data Accuracy:** Both chart percentages match database calculations exactly
2. **Public Sector Filter:** ONLY Public sector facilities included in all queries
3. **Filter Cascade:** Local Region dropdown properly respects global filters + public sector filter
4. **Filter Logic:** Human chart shows Human types, Analogue chart shows Analogue types, both grouped by level of care
5. **Performance:** Component loads within 2 seconds
6. **Responsiveness:** Charts update immediately when Region filter changes
7. **Error Handling:** Graceful handling of empty data, NULL values, division by zero
8. **User Experience:** Clear messaging when no data available
9. **Visual Quality:** Charts are visually appealing, readable, and match dashboard style
10. **Sorting:** Bars display in correct order (Primary, Secondary, Tertiary)
11. **Independence:** Component works independently of Plan 3, 4, 5, and 6 components
12. **Table Usage:** All queries use adl_repeat_repivot table

---

## Notes & Assumptions

### Assumed Column Schema

**Table: adl_repeat_repivot**
- `is_unavailable`: Integer (0 = available, 1 = not available)
- `insulin_type`: String with insulin type names (contains "Human" or "Analogue")
- `form_case__case_id`: Unique facility identifier
- `level_of_care`: String with level of care categories (Primary, Secondary, Tertiary, may contain NULL/'---' to exclude)
- `sector`: String with sector names (will filter for Public)
- `region`: String with region names (may contain NULL values to exclude)
- `data_collection_period`: Period identifier
- `country`: Country name (optional)

### Key Differences from Plan 6
1. **Implicit sector filter:** Always filters for Public sector (no Sector dropdown)
2. **Different grouping:** By level_of_care instead of by region
3. **Different X-axis:** Level of Care (Primary, Secondary, Tertiary)
4. **Single local filter:** Region only (Plan 6 had Sector only)
5. **Same table for all:** Uses `adl_repeat_repivot` for both dropdown and charts
6. **Additional filters:** Excludes level_of_care = 'NULL' and '---'
7. **Explicit X-axis title:** Shows "Level of Care" label

### Metric Calculation Logic
**Plan 7 (Public Sector by Level of Care):**
```sql
COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) / COUNT(DISTINCT form_case__case_id) * 100
-- Where is_unavailable = 0 means available
-- Grouped by level_of_care
-- Filtered by sector LIKE '%Public%' (ALWAYS)
-- Filtered by insulin_type LIKE '%Human%' or '%Analogue%'
-- Excluded: level_of_care NULL/'---'
```

### Plotly Implementation Pattern
Following Plan 4, 5, and 6's proven pattern:
- Use `plotly.graph_objects.Bar` for explicit control
- Explicit data type conversion with `pd.to_numeric()`
- Pre-formatted text labels as Python strings
- Y-axis range [0, 110] for outside text labels
- Manual customdata for hover tooltips
- Different colors for visual distinction (Human vs Analogue)
- X-axis title explicitly set to "Level of Care"

### Session State Key Naming
Use unique prefix `insulin_public_levelcare_` to avoid conflicts:
- Plan 3: `insulin_region_`, `insulin_sector_`
- Plan 4: `insulin_by_sector_region_`
- Plan 5: `insulin_by_type_region_`, `insulin_by_type_sector_`
- Plan 6: `insulin_by_region_sector_`
- Plan 7: `insulin_public_levelcare_region_`

This ensures all components coexist without state interference.

---

## Next Steps After Plan 7 Completion

1. User acceptance testing with real data from adl_repeat_repivot table
2. Verify both charts display correct level of care availability for Human vs Analogue (Public sector only)
3. Validate percentage calculations against manual checks
4. Test filter interactions with Plan 3, 4, 5, and 6 components (ensure independence)
5. Verify two-column chart layout works on various screen sizes
6. Verify implicit Public sector filter is properly applied to all queries
7. Verify level_of_care categories are properly sorted (Primary, Secondary, Tertiary)
8. Document any data quality issues (missing level_of_care, NULL values, etc.)
9. Proceed to next insulin availability filter/visualization if any

---

## Implementation Notes

### Key Similarities with Plan 6
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
13. ✅ Single local filter (Region instead of Sector)

### New Patterns Introduced
1. 🆕 Implicit sector filter (Public only) instead of dropdown
2. 🆕 Different grouping (by level_of_care instead of by region)
3. 🆕 Same table for all queries (adl_repeat_repivot)
4. 🆕 X-axis shows level of care instead of regions
5. 🆕 Explicit X-axis title "Level of Care"
6. 🆕 Additional filter for level_of_care (exclude NULL and '---')

### Potential Challenges
1. **Public sector definition:** Verify sector column contains "Public" string consistently
2. **Level of care values:** Verify level_of_care has exactly Primary, Secondary, Tertiary (or handle other values)
3. **Data availability:** Public sector may have fewer data points than all sectors combined
4. **Empty charts:** One chart may have data while the other doesn't (e.g., only Human types available)
5. **Chart layout:** Side-by-side layout may need adjustment on smaller screens
6. **Sorting:** Ensure Primary, Secondary, Tertiary appear in this order (ASC alphabetically may not work correctly if values differ)

### Recommended Testing Sequence
1. First verify adl_repeat_repivot table and column schemas
2. Test region dropdown function with Public sector filter
3. Verify level_of_care values are as expected (Primary, Secondary, Tertiary)
4. Test Human chart function with hardcoded filters
5. Test Analogue chart function with hardcoded filters
6. Integrate Region filter with both charts
7. Test full filter cascade (global + implicit public + local region)
8. Test responsive layout
9. Final visual validation
10. Test with various level_of_care categories

---

## Database Table Information

### Table: adl_repeat_repivot

**Purpose:** Contains insulin availability data with repeat entries repivoted for analysis

**Expected Columns:**
- `form_case__case_id`: Unique facility identifier
- `data_collection_period`: Period identifier (e.g., "Y1/P1")
- `country`: Country name
- `region`: Region name (may contain NULL) - **Used for filtering**
- `sector`: Sector name (will filter for Public) - **Used for implicit filtering**
- `level_of_care`: Level of care category - **Used for grouping in charts**
- `insulin_type`: Insulin type name (e.g., "Insulin type: Regular Human", "Insulin type: Lispro Analogue")
- `is_unavailable`: Integer (0 = available, 1 = not available)

**Usage in this component:** Source for region dropdown AND both chart data (Human and Analogue)

**Data Quality Checks:**
- Check for NULL values in critical columns (level_of_care, region, sector, insulin_type, is_unavailable)
- Verify insulin_type contains "Human" or "Analogue" for filtering
- Verify sector contains "Public" for filtering
- Verify level_of_care has expected values (Primary, Secondary, Tertiary)
- Check distribution of is_unavailable values (0 vs 1)
- Verify level_of_care NULL/'---' handling

---

## UI Layout Visual Guide

```
┌─────────────────────────────────────────────────────────────────┐
│ #### Insulin availability - Public sector - By level of care    │
├─────────────────────────────────────────────────────────────────┤
│ Region ▼                                                        │
│ Select Regions (X/Y selected)                                   │
├─────────────────────────────────────────────────────────────────┤
│ Human                             │ Analogue                    │
│ ┌───────────────────────────────┐ │ ┌───────────────────────────┐│
│ │ Facilities with Availability  │ │ │ Facilities with Availability││
│ │ (%)                           │ │ │ (%)                       ││
│ │                               │ │ │                           ││
│ │  [Bar Chart: By Level of Care]│ │ │  [Bar Chart: By Level of Care]││
│ │                               │ │ │                           ││
│ │  - Primary                    │ │ │  - Primary                ││
│ │  - Secondary                  │ │ │  - Secondary              ││
│ │  - Tertiary                   │ │ │  - Tertiary               ││
│ │                               │ │ │                           ││
│ │  X-axis: Level of Care        │ │ │  X-axis: Level of Care    ││
│ └───────────────────────────────┘ │ └───────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

**End of Plan 7 Refined Document**