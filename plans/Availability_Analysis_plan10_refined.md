# Dashboard UI Revamp - Plan 10: Insulin Availability - By Presentation and Insulin Type Component

## Task Overview
Implement the "Insulin Availability - By presentation and insulin type" component with two local filter dropdowns (Region and Sector) and one Plotly clustered bar chart showing percentage availability for different insulin presentations, with each presentation broken down by insulin type. Only insulins with availability > 0% are displayed.

**Use Serena MCP:** Define todo items list and solve them one by one according to this detailed plan.

**Current Phase:** Backend Integration and UI Implementation with Single Plotly Clustered Visualization
**Prerequisites:** Previous insulin availability components completed

---

## Component Placement

**Location:** Add as new sub-section under "Insulin Availability" section in app.py (after Insulin - Top 10 brands components)

**Visual Hierarchy:**
```
[Previous Insulin Availability component]
    ↓
<br><br> spacing
    ↓
[Sub-heading: "Insulin availability - By presentation and insulin type"]
    ↓
[Two-column filter row: Region | Sector]
    ↓
[Single Clustered Bar Chart: Facilities with Availability (%)]
    ↓
[Note message: "NOTE: Only insulins found to be available are shown."]
```

---

## Component Structure

### 1. Sub-heading
```python
st.markdown("#### Insulin availability - By presentation and insulin type")
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

### 3. Single Clustered Bar Chart Visualization

**Chart Title:** "Facilities with Availability (%)"

**Chart Type:** Plotly Clustered Bar Chart (using **plotly.graph_objects.Bar** for explicit data type control)

**Chart Specifications:**
- **Y-axis:** Percentage values (0-100%)
  - Label: "Facilities with Availability (%)"
  - Format: Show percentage symbol
  - Grid lines: Enabled for readability
- **X-axis:** Insulin Presentation
  - Label: "Presentation"
  - Values: Three main categories: **Vial**, **Prefilled pen**, and **Cartridge**
  - Rotation: Angle labels (-45°) for readability if needed
- **Clustered Bars (Legend - Insulin Type):**
  Each presentation category contains up to seven specific insulin types, indicated by color:
  - **Intermediate-Acting Human** (Teal/Dark Blue: `#1f5c5c` or `#006666`)
  - **Short-Acting Human** (Light Blue/Cyan: `#5dade2` or `#00b8d4`)
  - **Mixed Human** (Purple: `#9b59b6` or `#8e44ad`)
  - **Long-Acting Analogue** (Light Pink/Lavender: `#dda0dd` or `#e1bee7`)
  - **Rapid-Acting Analogue** (Maroon/Dark Red: `#800000` or `#a52a2a`)
  - **Mixed Analogue** (Pink: `#ff69b4` or `#ff1493`)
  - **Intermediate-Acting Animal** (Dark Purple/Indigo: `#4b0082` or `#5c2d91`)
- **Bars:**
  - Width: Appropriate spacing between groups
  - Shaded area: Represents percentage value
  - Data labels: Show percentage value on top of each bar (e.g., "75.5%")
  - Hover info: Display Presentation, Insulin Type, percentage value, available facilities count, and total facilities count
- **Sorting:** Descending by availability percentage (highest to lowest) within each presentation group
- **Filtering:** ONLY show insulin type/presentation combinations with availability > 0% (exclude 0% availability)
- **Layout:**
  - Responsive: Use `use_container_width=True`
  - Background: Transparent (`plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'`)
  - Height: ~500px for optimal viewing
  - Legend: Show insulin type legend on right side

**Example Chart Data:**
| Presentation | Insulin Type | Availability (%) |
|-------------|--------------|------------------|
| Vial | Intermediate-Acting Human | 78.5 |
| Vial | Short-Acting Human | 72.3 |
| Vial | Mixed Human | 65.8 |
| Prefilled pen | Long-Acting Analogue | 58.2 |
| Prefilled pen | Rapid-Acting Analogue | 52.1 |
| Cartridge | Mixed Analogue | 45.3 |

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
Clustered Bar Chart → Display data filtered by global + local region + local sector filters, grouped by insulin_presentation and breakdown by insulin_type, ONLY showing combinations with availability > 0%
```

**Example:**
- User selects: Global Period = "Y1/P1", Global Country = "Peru", Local Region = "Arequipa", Local Sector = "Public"
- Component behavior:
  - Region dropdown: Shows all regions in Peru for Y1/P1
  - Sector dropdown: Shows all sectors in Peru for Y1/P1
  - Chart: Shows availability percentages by presentation and insulin type for facilities in "Arequipa", "Public" sector during "Y1/P1" in Peru
  - Chart ONLY shows insulin type/presentation combinations with availability > 0% (excludes 0% entries)

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

### Query 3: Clustered Bar Chart Data - Availability by Presentation and Insulin Type

**Purpose:** Calculate percentage of facilities with insulin availability for each presentation/insulin type combination, ONLY showing combinations with availability > 0%

**Source Table:** `adl_repeat_repivot`

**Column Assumptions:**
- `is_unavailable`: Integer column (0 = available, 1 = not available)
- `insulin_presentation`: String column with presentation types (Vial, Prefilled pen, Cartridge)
- `insulin_type`: String column with insulin types (Intermediate-Acting Human, Short-Acting Human, Mixed Human, Long-Acting Analogue, Rapid-Acting Analogue, Mixed Analogue, Intermediate-Acting Animal)
- `form_case__case_id`: Unique facility identifier

**SQL Pattern:**
```sql
SELECT
    insulin_presentation,
    insulin_type,
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
    AND insulin_presentation IS NOT NULL
    AND TRIM(insulin_presentation) != ''
    AND insulin_presentation != 'NULL'
    AND insulin_type IS NOT NULL
    AND TRIM(insulin_type) != ''
    AND insulin_type != 'NULL'
GROUP BY insulin_presentation, insulin_type
HAVING
    CASE
        WHEN COUNT(DISTINCT form_case__case_id) > 0
        THEN ROUND((COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
        ELSE 0
    END > 0
ORDER BY availability_percentage DESC
```

**Expected Output:** DataFrame with columns:
- `insulin_presentation` (string): Presentation type
- `insulin_type` (string): Insulin type
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
- **HAVING clause:** Filters out insulin type/presentation combinations with 0% availability AFTER aggregation
- This ensures only combinations with some availability are displayed in the chart

---

## Implementation Functions

### Function 1: get_insulin_by_presentation_regions()

```python
@st.cache_data(ttl=600)
def get_insulin_by_presentation_regions(_client, table_name, global_filters):
    """
    Get regions for local Region dropdown in Insulin Availability - By Presentation and Type component.

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

### Function 2: get_insulin_by_presentation_sectors()

```python
@st.cache_data(ttl=600)
def get_insulin_by_presentation_sectors(_client, table_name, global_filters):
    """
    Get sectors for local Sector dropdown in Insulin Availability - By Presentation and Type component.

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

### Function 3: get_insulin_by_presentation_chart_data()

```python
@st.cache_data(ttl=600)
def get_insulin_by_presentation_chart_data(_client, table_name, global_filters, local_regions, local_sectors):
    """
    Get insulin availability percentages by presentation and insulin type, ONLY showing combinations with availability > 0%.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        pandas DataFrame with columns:
            - insulin_presentation (str)
            - insulin_type (str)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)

        Only returns rows where availability_percentage > 0
    """
    # Build WHERE clause with global + local region + local sector filters
    # Filter: insulin_presentation IS NOT NULL AND insulin_type IS NOT NULL
    # Calculate: COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id) * 100
    # Group by insulin_presentation, insulin_type
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
# After previous insulin availability component
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("#### Insulin availability - By presentation and insulin type")
```

---

### Step 2: Two-Column Filter Layout with Checkbox Dropdowns

```python
# Note: Plan 10 uses adl_surveys for dropdowns, adl_repeat_repivot for chart
PLAN10_SURVEYS_TABLE = config.TABLES["surveys"]
PLAN10_REPIVOT_TABLE = config.TABLES["repeat_repivot"]

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
            region_df = get_insulin_by_presentation_regions(client, PLAN10_SURVEYS_TABLE, global_filters)

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
                    checkbox_key = f"insulin_by_presentation_region_{region}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items from session state
                selected_count = sum(
                    1 for region, _ in region_data
                    if st.session_state.get(f"insulin_by_presentation_region_{region}", True)
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
                        checkbox_key = f"insulin_by_presentation_region_{region}"

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
            sector_df = get_insulin_by_presentation_sectors(client, PLAN10_SURVEYS_TABLE, global_filters)

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
                    checkbox_key = f"insulin_by_presentation_sector_{sector}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items from session state
                selected_count = sum(
                    1 for sector, _ in sector_data
                    if st.session_state.get(f"insulin_by_presentation_sector_{sector}", True)
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
                        checkbox_key = f"insulin_by_presentation_sector_{sector}"

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

### Step 3: Single Plotly Clustered Bar Chart

```python
    # Fetch and display clustered bar chart
    st.markdown("<br>", unsafe_allow_html=True)

    with st.spinner("Loading insulin availability by presentation and type..."):
        chart_df = get_insulin_by_presentation_chart_data(
            client,
            PLAN10_REPIVOT_TABLE,
            global_filters,
            local_regions,
            local_sectors
        )

        if chart_df is not None and not chart_df.empty:
            # Ensure data types are correct
            chart_df['availability_percentage'] = pd.to_numeric(chart_df['availability_percentage'], errors='coerce')
            chart_df['total_facilities'] = pd.to_numeric(chart_df['total_facilities'], errors='coerce')
            chart_df['facilities_with_insulin'] = pd.to_numeric(chart_df['facilities_with_insulin'], errors='coerce')

            # Define color mapping for insulin types
            insulin_type_colors = {
                'Intermediate-Acting Human': '#1f5c5c',  # Teal/Dark Blue
                'Short-Acting Human': '#5dade2',  # Light Blue/Cyan
                'Mixed Human': '#9b59b6',  # Purple
                'Long-Acting Analogue': '#dda0dd',  # Light Pink/Lavender
                'Rapid-Acting Analogue': '#800000',  # Maroon/Dark Red
                'Mixed Analogue': '#ff69b4',  # Pink
                'Intermediate-Acting Animal': '#4b0082'  # Dark Purple/Indigo
            }

            # Create clustered bar chart using graph_objects
            fig = go.Figure()

            # Get unique insulin types for legend ordering
            unique_types = chart_df['insulin_type'].unique()

            # Add trace for each insulin type
            for insulin_type in unique_types:
                type_data = chart_df[chart_df['insulin_type'] == insulin_type]

                fig.add_trace(go.Bar(
                    x=type_data['insulin_presentation'].tolist(),
                    y=type_data['availability_percentage'].tolist(),
                    name=insulin_type,
                    text=[f'{val:.1f}%' for val in type_data['availability_percentage'].tolist()],
                    textposition='outside',
                    marker_color=insulin_type_colors.get(insulin_type, '#808080'),  # Default gray if type not in mapping
                    hovertemplate='<b>%{x}</b><br>' +
                                  f'<b>{insulin_type}</b><br>' +
                                  'Availability: %{y:.1f}%<br>' +
                                  'Available Facilities: %{customdata[0]:,}<br>' +
                                  'Total Facilities: %{customdata[1]:,}<extra></extra>',
                    customdata=type_data[['facilities_with_insulin', 'total_facilities']].values
                ))

            # Update layout
            fig.update_layout(
                title='Facilities with Availability (%)',
                xaxis_title='Presentation',
                yaxis_title='Facilities with Availability (%)',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=500,
                barmode='group',  # Clustered bars
                yaxis=dict(
                    range=[0, 110],
                    ticksuffix='%'
                ),
                xaxis_tickangle=-45,  # Angle labels for readability if needed
                showlegend=True,
                legend=dict(
                    title='Insulin Type',
                    orientation='v',
                    yanchor='top',
                    y=1,
                    xanchor='left',
                    x=1.02
                ),
                margin=dict(t=50, b=100, l=50, r=150)  # Extra right margin for legend
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
            <strong>💡 Tip:</strong> Select one or more data collection periods above to view insulin availability by presentation and type.
        </div>
    """, unsafe_allow_html=True)
```

**Implementation Notes:**
- **Clustered chart:** Uses `barmode='group'` to create clustered bars
- **Color mapping:** Explicit dictionary for each insulin type
- **Data type conversion:** Essential `pd.to_numeric()` on all numeric columns
- **Text labels:** Pre-formatted percentage strings
- **Y-axis range:** Extended to [0, 110] for text labels above bars
- **Custom data:** Manually set for hover tooltips
- **X-axis rotation:** -45° for better readability
- **X-axis title:** "Presentation" explicitly shown
- **Legend:** Right side vertical legend with insulin type colors
- **Sorting:** Bars automatically sorted DESC by availability percentage (from query)
- **Filtering:** ONLY shows combinations with availability > 0% (handled in query)
- **Note placement:** Immediately below the chart

---

## Session State Management

### Initialize Local Filter State

```python
# Session state keys for this component use unique prefix to avoid conflicts
# Region checkboxes: insulin_by_presentation_region_{region_name}
# Sector checkboxes: insulin_by_presentation_sector_{sector_name}
# These are automatically managed by Streamlit when using st.checkbox with key parameter
```

**Note:** Using Streamlit's `key` parameter in checkbox handles state automatically. Unique prefix `insulin_by_presentation_` prevents conflicts with other insulin availability components.

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

### 7. NULL/Empty insulin_presentation or insulin_type Values
```python
# Filter in WHERE clause:
AND insulin_presentation IS NOT NULL
AND TRIM(insulin_presentation) != ''
AND insulin_presentation != 'NULL'
AND insulin_type IS NOT NULL
AND TRIM(insulin_type) != ''
AND insulin_type != 'NULL'
```

### 8. All Insulin Combinations Have 0% Availability
```python
# HAVING clause filters out 0% availability combinations
# If all combinations have 0%, result is empty
# Display "No data available" message
```

### 9. No Regions or Sectors Selected
```python
# If user unchecks all regions/sectors, local_regions/local_sectors will be empty list
# Queries should handle empty list and return no data
# Display "No data available" message
```

### 10. Unknown Insulin Type (Not in Color Mapping)
```python
# Use default gray color (#808080) for any insulin type not in predefined mapping
marker_color=insulin_type_colors.get(insulin_type, '#808080')
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
- Filter by insulin_presentation AND insulin_type at database level
- Group by both dimensions for aggregation
- HAVING clause filters availability > 0% at database level (more efficient than Python filtering)

### Parallel Data Fetching
- Region and Sector dropdown queries are independent (can run in parallel)
- Chart query depends on dropdown selections
- Consider loading both dropdowns concurrently if performance becomes issue

---

## Styling & Responsive Design

### Plotly Chart Styling
- **Color scheme:** Seven distinct colors mapped to insulin types
- **Transparency:** Background transparent to match Streamlit theme
- **Font:** Plotly default fonts (readable, professional)
- **Hover effects:** Custom template with presentation, insulin type, percentage, and facility counts
- **Legend:** Right-side vertical legend showing insulin types

### Responsive Behavior
- Chart uses `use_container_width=True` for automatic width adjustment
- Two-column filter layout adapts to screen size
- On mobile, columns stack vertically
- X-axis labels rotate at -45° if needed for readability
- Bar labels appear outside bars for clarity
- Extra right margin (150px) for legend

### Consistency with Existing Components
- Use same section spacing (`<br><br>`)
- Use same markdown sub-heading style (`####`)
- Use same info-box class for messages
- Use same checkbox dropdown pattern from other plans
- Use same two-column filter layout pattern

---

## Testing Requirements

### Unit Tests
```python
def test_get_insulin_by_presentation_regions():
    """Test region dropdown data fetching"""
    # Test with various filter combinations
    # Verify NULL/empty region exclusion
    # Verify DESC sorting
    # Verify uses adl_surveys table

def test_get_insulin_by_presentation_sectors():
    """Test sector dropdown data fetching"""
    # Test with various filter combinations
    # Verify NULL/empty sector exclusion
    # Verify DESC sorting
    # Verify uses adl_surveys table

def test_get_insulin_by_presentation_chart_data():
    """Test chart data fetching"""
    # Test with local region + sector filters
    # Verify percentage calculation
    # Verify is_unavailable = 0 logic
    # Verify division by zero protection
    # Verify insulin_presentation and insulin_type NULL exclusion
    # Verify availability > 0% filter (HAVING clause)
    # Verify DESC sorting by availability_percentage
    # Verify uses adl_repeat_repivot table
    # Verify GROUP BY both presentation and type
```

### Integration Tests
1. Test filter cascade: Global → Local Region → Local Sector → Chart
2. Test chart updates when Region or Sector filter changes
3. Test with empty datasets (show "No data available")
4. Verify chart displays presentation/type availability percentages
5. Verify percentage values match database calculations
6. Verify only combinations with > 0% availability are displayed
7. Test hover tooltips show correct information
8. Test with single vs multiple regions/sectors selected
9. Test independence from other insulin availability components
10. Verify bars are clustered correctly by presentation
11. Verify legend shows all insulin types with correct colors
12. Test with unknown insulin types (should use default color)

### Visual Validation
1. Verify bars are clustered by presentation (Vial, Prefilled pen, Cartridge)
2. Verify each cluster contains bars for different insulin types
3. Verify percentage labels appear on top of bars
4. Verify y-axis range is 0-110%
5. Verify x-axis labels show presentation names
6. Verify x-axis title is "Presentation"
7. Verify chart height is appropriate (~500px)
8. Test responsive behavior on different screen sizes
9. Verify note message appears below chart
10. Verify note message styling matches existing info-box
11. Verify chart colors match insulin type color mapping
12. Verify legend displays correctly on right side
13. Verify bars within each cluster are sorted by availability

---

## Implementation Checklist

### Backend Functions
- [ ] Implement `get_insulin_by_presentation_regions()` in bigquery_client.py
- [ ] Implement `get_insulin_by_presentation_sectors()` in bigquery_client.py
- [ ] Implement `get_insulin_by_presentation_chart_data()` in bigquery_client.py
- [ ] Add imports to app.py (plotly.graph_objects already imported)
- [ ] Add caching decorators with ttl=600
- [ ] Verify `is_unavailable` column exists in adl_repeat_repivot table
- [ ] Verify `insulin_presentation` column exists in adl_repeat_repivot table
- [ ] Verify `insulin_type` column exists in adl_repeat_repivot table
- [ ] Verify `region` column exists in adl_surveys table
- [ ] Verify `sector` column exists in adl_surveys table

### UI Implementation
- [ ] Add sub-heading "Insulin availability - By presentation and insulin type"
- [ ] Create two-column layout for Region and Sector filters
- [ ] Implement Region dropdown with checkboxes
- [ ] Add excluded count display inside Region dropdown
- [ ] Implement Sector dropdown with checkboxes
- [ ] Add excluded count display inside Sector dropdown
- [ ] Implement clustered bar chart with Plotly go.Bar
- [ ] Configure chart title: "Facilities with Availability (%)"
- [ ] Configure y-axis: Percentage format, 0-110 range
- [ ] Configure x-axis: "Presentation" title, presentation names
- [ ] Add data labels on bars (pre-formatted percentage values)
- [ ] Configure hover tooltips with presentation and insulin type
- [ ] Add "No data available" handling for chart
- [ ] Add tip message when no period selected
- [ ] Set chart height to 500px
- [ ] Configure barmode='group' for clustering
- [ ] Add insulin type color mapping
- [ ] Configure legend on right side
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
- [ ] Chart groups by insulin_presentation AND insulin_type
- [ ] Chart filters availability > 0% (HAVING clause)
- [ ] Chart sorts DESC by availability_percentage

### Chart Styling
- [ ] Define color mapping for seven insulin types
- [ ] Use default color for unknown insulin types
- [ ] Set transparent background
- [ ] Add percentage symbol to y-axis ticks
- [ ] Format percentage labels on bars (1 decimal place)
- [ ] Configure hover template with custom formatting
- [ ] Apply responsive width with `use_container_width=True`
- [ ] Set appropriate margins (extra right margin for legend)
- [ ] Add x-axis title "Presentation"
- [ ] Angle x-axis labels at -45° if needed
- [ ] Configure legend with title "Insulin Type"
- [ ] Position legend on right side vertically

### Validation & Testing
- [ ] Verify percentage formula: (COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id)) * 100
- [ ] Test division by zero handling
- [ ] Test NULL value handling in is_unavailable
- [ ] Test with various filter combinations
- [ ] Verify chart values match database calculations
- [ ] Verify bars are clustered correctly
- [ ] Verify ONLY combinations with > 0% availability are shown
- [ ] Verify excluded region/sector logic works correctly
- [ ] Test responsive design (chart uses use_container_width=True)
- [ ] Verify hover tooltips display correctly
- [ ] Test independence from other components
- [ ] Verify note message appears below chart
- [ ] Verify legend displays all insulin types
- [ ] Verify color mapping works correctly

**Implementation Status:** ⏳ **PENDING** - Ready for implementation

---

## Success Criteria

1. **Data Accuracy:** Chart percentages match database calculations exactly
2. **Filter Cascade:** Local Region and Sector dropdowns properly respect global filters
3. **Filter Logic:** Chart respects all filters (global + local region + local sector)
4. **Availability Filter:** ONLY combinations with > 0% availability are displayed
5. **Clustering:** Bars are properly clustered by presentation with insulin types as sub-groups
6. **Performance:** Component loads within 2 seconds
7. **Responsiveness:** Chart updates immediately when Region or Sector filter changes
8. **Error Handling:** Graceful handling of empty data, NULL values, division by zero
9. **User Experience:** Clear messaging when no data available
10. **Visual Quality:** Chart is visually appealing, readable, and matches dashboard style
11. **Color Coding:** Each insulin type has distinct, consistent color
12. **Legend:** Legend clearly shows insulin type color mapping
13. **Independence:** Component works independently of other insulin availability components
14. **Table Usage:** Dropdowns use adl_surveys, chart uses adl_repeat_repivot
15. **Note Display:** Note message appears below chart with correct styling

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
- `insulin_presentation`: String with presentation types (Vial, Prefilled pen, Cartridge)
- `insulin_type`: String with insulin types (Intermediate-Acting Human, Short-Acting Human, Mixed Human, Long-Acting Analogue, Rapid-Acting Analogue, Mixed Analogue, Intermediate-Acting Animal)
- `form_case__case_id`: Unique facility identifier
- `data_collection_period`: Period identifier
- `country`: Country name (optional)
- `region`: Region name (may contain NULL values)
- `sector`: Sector name (may contain NULL values)

### Key Features of Plan 10

1. **Two filters:** Region AND Sector
2. **Clustered grouping:** By insulin_presentation (main) and insulin_type (sub-groups)
3. **X-axis:** Presentation names (Vial, Prefilled pen, Cartridge)
4. **Legend:** Insulin type with color coding
5. **Sorting:** DESC by availability percentage
6. **Additional filter:** ONLY show combinations with availability > 0% (HAVING clause)
7. **Different tables:** Uses adl_surveys for dropdowns, adl_repeat_repivot for chart
8. **Clustered chart:** Multiple bars per presentation (one per insulin type)
9. **Note message:** Added below chart to explain filtering logic
10. **Color mapping:** Seven distinct colors for seven insulin types

### Metric Calculation Logic
**Plan 10 (By Presentation and Type):**
```sql
COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) / COUNT(DISTINCT form_case__case_id) * 100
-- Where is_unavailable = 0 means available
-- Grouped by insulin_presentation AND insulin_type
-- HAVING availability_percentage > 0 (only show available combinations)
-- Sorted DESC by availability_percentage
```

### Insulin Presentations
Common presentation types:
- **Vial** (traditional glass bottle)
- **Prefilled pen** (ready-to-use pen device)
- **Cartridge** (refillable pen cartridge)

### Insulin Types (Seven Categories)
1. **Intermediate-Acting Human** - NPH insulin
2. **Short-Acting Human** - Regular insulin
3. **Mixed Human** - Combination of short and intermediate-acting human
4. **Long-Acting Analogue** - Glargine, Detemir, Degludec
5. **Rapid-Acting Analogue** - Lispro, Aspart, Glulisine
6. **Mixed Analogue** - Combination of rapid and intermediate-acting analogue
7. **Intermediate-Acting Animal** - Animal-sourced NPH (rare)

### Plotly Clustered Bar Implementation Pattern
Following proven pattern with enhancements:
- Use `plotly.graph_objects.Bar` for explicit control
- Explicit data type conversion with `pd.to_numeric()`
- Pre-formatted text labels as Python strings
- Y-axis range [0, 110] for outside text labels
- Manual customdata for hover tooltips
- X-axis title explicitly set to "Presentation"
- Legend on right side with insulin type names
- Multiple traces (one per insulin type) for clustering
- `barmode='group'` for clustered layout

### Session State Key Naming
Use unique prefix `insulin_by_presentation_` to avoid conflicts:
- Plan 3: `insulin_region_`, `insulin_sector_`
- Plan 4: `insulin_by_sector_region_`
- Plan 5: `insulin_by_type_region_`, `insulin_by_type_sector_`
- Plan 6: `insulin_by_region_sector_`
- Plan 7: `insulin_public_levelcare_region_`
- Plan 8: `insulin_by_inn_region_`, `insulin_by_inn_sector_`
- Plan 10: `insulin_by_presentation_region_`, `insulin_by_presentation_sector_`

This ensures all components coexist without state interference.

---

## Next Steps After Plan 10 Completion

1. User acceptance testing with real data from adl_repeat_repivot table
2. Verify chart displays correct presentation/type availability percentages
3. Validate percentage calculations against manual checks
4. Test filter interactions with other insulin availability components (ensure independence)
5. Verify two-column filter layout works on various screen sizes
6. Verify ONLY combinations with > 0% availability are shown
7. Verify bars are clustered correctly by presentation
8. Verify insulin type colors match specification
9. Verify legend displays correctly
10. Verify note message appears correctly below chart
11. Document any data quality issues (missing presentation/type, NULL values, etc.)
12. Proceed to next insulin availability filter/visualization if any

---

## Implementation Notes

### Key Similarities with Plan 8
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
14. ✅ HAVING clause for filtering > 0% availability
15. ✅ DESC sorting by availability percentage
16. ✅ Mixed table usage (adl_surveys for dropdowns, adl_repeat_repivot for chart)
17. ✅ Note message below chart

### New Patterns Introduced in Plan 10
1. 🆕 Clustered bar chart with multiple traces (one per insulin type)
2. 🆕 Two-dimensional grouping (presentation AND insulin type)
3. 🆕 Color mapping dictionary for seven insulin types
4. 🆕 `barmode='group'` for clustered layout
5. 🆕 Legend showing insulin type categories
6. 🆕 Loop through insulin types to create multiple traces
7. 🆕 X-axis shows presentation (not type or INN)
8. 🆕 Right-side vertical legend with extra margin
9. 🆕 Default color handling for unknown insulin types

### Potential Challenges
1. **Data quality:** Verify insulin_presentation and insulin_type columns have clean, consistent values
2. **Color mapping completeness:** Ensure all insulin types in data are covered by color mapping
3. **Table mismatch:** Dropdowns from adl_surveys, chart from adl_repeat_repivot (ensure consistency)
4. **Empty chart:** All combinations might have 0% availability (filtered out by HAVING clause)
5. **Clustering complexity:** Multiple insulin types per presentation may create crowded chart
6. **Legend readability:** Seven insulin types in legend may be long
7. **Performance:** GROUP BY two dimensions may be slower than single dimension

### Recommended Testing Sequence
1. First verify adl_surveys and adl_repeat_repivot table schemas
2. Test region dropdown function with adl_surveys table
3. Test sector dropdown function with adl_surveys table
4. Verify insulin_presentation and insulin_type values in adl_repeat_repivot
5. Check which insulin types are actually present in data
6. Test chart function with hardcoded filters
7. Verify HAVING clause correctly filters availability > 0%
8. Verify clustering works correctly (bars grouped by presentation)
9. Verify color mapping applies correctly to all insulin types
10. Integrate Region and Sector filters with chart
11. Test full filter cascade (global + local region + local sector)
12. Test responsive layout
13. Final visual validation with note message and legend

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
- `insulin_presentation`: Presentation type - **Used for X-axis grouping**
- `insulin_type`: Insulin type - **Used for clustering/legend**
- `is_unavailable`: Integer (0 = available, 1 = not available)

**Usage in this component:** Source for clustered bar chart data

**Data Quality Checks:**
- Check for NULL values in critical columns (insulin_presentation, insulin_type, region, sector, is_unavailable)
- Verify insulin_presentation has expected values (Vial, Prefilled pen, Cartridge)
- Verify insulin_type has expected values (seven categories listed above)
- Check distribution of is_unavailable values (0 vs 1)
- Verify availability > 0% filter works correctly

---

## UI Layout Visual Guide

```
┌─────────────────────────────────────────────────────────────────┐
│ #### Insulin availability - By presentation and insulin type    │
├─────────────────────────────────────────────────────────────────┤
│ Region ▼                      │ Sector ▼                        │
│ Select Regions (X/Y selected) │ Select Sectors (X/Y selected)   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐   │
│ │ Facilities with Availability (%)                          │   │
│ │                                                           │   │
│ │  [Clustered Bar Chart: By Presentation & Type]            │   │
│ │                                                           │   │
│ │  X-axis: Presentation (Vial, Prefilled pen, Cartridge)   │   │
│ │  Y-axis: Availability (%)                                 │   │
│ │  Clusters: Each presentation has bars for insulin types   │   │
│ │  Legend: Insulin Type (7 colors)                          │   │
│ │  Sorted: DESC by availability percentage                  │   │
│ │  Filtered: Only combinations with > 0% availability       │   │
│ │                                                           │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ 📝 Note: Only insulins found to be available are shown.        │
└─────────────────────────────────────────────────────────────────┘
```

---

**End of Plan 10 Refined Document**
