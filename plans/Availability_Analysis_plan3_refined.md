# Dashboard UI Revamp - Plan 3: Insulin Availability - Overall Component

## Task Overview
Implement the "Insulin Availability - Overall" component with local Region and Sector filter dropdowns and two scorecard metrics.

**Use Serena MCP:** Define todo items list and solve them one by one according to this detailed plan.

**Current Phase:** Backend Integration and UI Implementation
**Prerequisites:** Plan 2.1 completed (Summary of facilities surveyed component)

---

## Component Placement

**Location:** Add after "Summary of facilities surveyed" component in app.py (after line ~307, before Tab 2: Price Analysis)

**Visual Hierarchy:**
```
[Summary of facilities surveyed component]
    ↓
<br><br> spacing
    ↓
[Section Header: "Insulin availability"]
    ↓
[Sub-heading: "Insulin availability - Overall"]
    ↓
[Two-column filter row: Region | Sector]
    ↓
[Two-column scorecard row: Availability (n) | Unavailability (%)]
```

---

## Component Structure

### 1. Section Header
```python
st.markdown('<div class="section-header"><h3>Insulin availability</h3></div>', unsafe_allow_html=True)
```

### 2. Sub-heading
```python
st.markdown("#### Insulin availability - Overall")
```

### 3. Two-Column Filter Layout

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
- Expandable dropdown (st.expander) containing checkbox list
- Dropdown label shows: "Select Sectors (X/Y selected)" where X=selected, Y=total
- Default state: Collapsed (expanded=False)
- Inside dropdown: Individual checkboxes for each sector
- Each checkbox shows: "Sector Name (count)" format
- Displays excluded items count inside dropdown: "🚫 X items excluded"
- Filters data within this component only
- Independent from global Data Selectors filters
- Default: All sectors selected (all checkboxes checked)
- Unchecked items are excluded from analysis

### 4. Two-Column Scorecard Layout

**Scorecard 1: Facilities with Availability (n)**
- Displays the number of facilities with insulin available
- Uses metric card styling from existing CSS

**Scorecard 2: Facilities with Unavailability (%)**
- Displays percentage of facilities WITHOUT insulin available
- Formatted as percentage with 1 decimal place

---

## Filter Behavior & Scope

### Global Filters (From Data Selectors)
These filters apply to ALL components including this one:
- ✅ Data Collection Period (REQUIRED)
- ✅ Country (optional)
- ✅ Region (optional) - **Note:** If global Region is selected, it restricts the local Region dropdown options

### Local Filters (Component-Specific)
These filters ONLY affect this component's scorecards:
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
Scorecards → Calculated from filtered dataset
```

**Example:**
- User selects: Global Period = "Y1/P1", Global Region = "Eastern"
- Component behavior:
  - Local Region dropdown: Shows only "Eastern" (or could be hidden since only 1 option)
  - Local Sector dropdown: Shows all sectors within "Eastern" region in "Y1/P1"
  - Scorecards: Calculate based on Global Period + Global Region + Local Sector selections

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
GROUP BY region
ORDER BY region ASC
```

**Expected Output:** DataFrame with columns: region, facility_count

---

### Query 2: Sector Dropdown Options

**Purpose:** Populate local Sector dropdown with options

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
    AND ({local_region_filter})  -- if local region selected in component
    AND sector IS NOT NULL
    AND TRIM(sector) != ''
GROUP BY sector
ORDER BY sector ASC
```

**Expected Output:** DataFrame with columns: sector, facility_count

---

### Query 3: Scorecard Metrics

**Purpose:** Calculate both scorecard values in single optimized query

**Column Assumptions:**
- `insulin_available_num`: Integer column (1 = available, 0 = not available)

**SQL Pattern:**
```sql
SELECT
    SUM(COALESCE(insulin_available_num, 0)) as facilities_with_availability,
    COUNT(DISTINCT form_case__case_id) as total_facilities,
    CASE
        WHEN COUNT(DISTINCT form_case__case_id) > 0
        THEN ROUND(100 - ((SUM(COALESCE(insulin_available_num, 0)) * 100.0) / COUNT(DISTINCT form_case__case_id)), 1)
        ELSE 0
    END as unavailability_percentage
FROM `{GCP_PROJECT_ID}.{BQ_DATASET}.adl_surveys`
WHERE
    data_collection_period IN ({selected_periods})
    AND ({country_filter})  -- if global country selected
    AND ({region_filter})   -- if global region selected
    AND ({local_region_filter})  -- if local region selected in component
    AND ({local_sector_filter})  -- if local sector selected in component
```

**Expected Output:** Single row with columns:
- `facilities_with_availability` (int)
- `total_facilities` (int)
- `unavailability_percentage` (float)

**Validation Rules:**
- If `total_facilities` = 0, show "No data available" message
- `unavailability_percentage` should be between 0 and 100
- `facilities_with_availability` ≤ `total_facilities`

---

## Implementation Functions

### Function 1: get_insulin_regions()

```python
@st.cache_data(ttl=600)
def get_insulin_regions(_client, table_name, global_filters):
    """
    Get regions for local Region dropdown in Insulin Availability component.

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
    # Execute query
    # Return results
```

---

### Function 2: get_insulin_sectors()

```python
@st.cache_data(ttl=600)
def get_insulin_sectors(_client, table_name, global_filters, local_regions):
    """
    Get sectors for local Sector dropdown in Insulin Availability component.

    Args:
        _client: BigQuery client
        table_name: Table name
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown

    Returns:
        pandas DataFrame with columns: sector, facility_count
    """
    # Build WHERE clause with global + local region filters
    # Execute query
    # Return results
```

---

### Function 3: get_insulin_availability_metrics()

```python
@st.cache_data(ttl=600)
def get_insulin_availability_metrics(_client, table_name, global_filters, local_regions, local_sectors):
    """
    Get insulin availability metrics for scorecards.

    Args:
        _client: BigQuery client
        table_name: Table name
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local dropdown
        local_sectors (list): Selected sectors from local dropdown

    Returns:
        dict: {
            'facilities_with_availability': int,
            'total_facilities': int,
            'unavailability_percentage': float
        }
    """
    # Build WHERE clause with all filters
    # Execute query
    # Validate results
    # Return metrics dict
```

---

## UI Implementation Pattern

### Step 1: Section Header & Sub-heading

```python
# After Summary of facilities surveyed component
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div class="section-header"><h3>Insulin availability</h3></div>', unsafe_allow_html=True)
st.markdown("#### Insulin availability - Overall")
```

---

### Step 2: Local Filter Dropdowns with Checkbox Style and Excluded Count

```python
if st.session_state.selected_periods:
    # Build global filters dict
    global_filters = {
        'data_collection_period': st.session_state.selected_periods,
        'country': st.session_state.selected_countries if st.session_state.selected_countries else None,
        'region': st.session_state.selected_regions if st.session_state.selected_regions else None
    }

    # Two-column layout for filters
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Region**")
        with st.spinner("Loading regions..."):
            region_df = get_insulin_regions(client, TABLE_NAME, global_filters)

            if region_df is not None and not region_df.empty:
                # Create a container for checkbox list
                with st.container():
                    # Initialize session state for region checkboxes if not exists
                    if 'insulin_region_checkboxes' not in st.session_state:
                        st.session_state.insulin_region_checkboxes = {}

                    # Build region options
                    region_data = []
                    for _, row in region_df.iterrows():
                        region = row['region']
                        count = row['facility_count']
                        region_data.append((region, count))

                    total_regions = len(region_data)

                    # Create checkboxes for each region
                    local_regions = []
                    for region, count in region_data:
                        # Initialize checkbox state to True (checked) if not set
                        checkbox_key = f"insulin_region_{region}"
                        if checkbox_key not in st.session_state.insulin_region_checkboxes:
                            st.session_state.insulin_region_checkboxes[checkbox_key] = True

                        # Display checkbox
                        is_checked = st.checkbox(
                            f"{region} ({count:,})",
                            value=st.session_state.insulin_region_checkboxes[checkbox_key],
                            key=checkbox_key
                        )

                        # Update session state
                        st.session_state.insulin_region_checkboxes[checkbox_key] = is_checked

                        # Add to selected list if checked
                        if is_checked:
                            local_regions.append(region)

                    # Display excluded count
                    excluded_count = total_regions - len(local_regions)
                    if excluded_count > 0:
                        st.caption(f"🚫 {excluded_count} item{'s' if excluded_count != 1 else ''} excluded")
            else:
                local_regions = []
                st.info("No region data available")

    with col2:
        st.markdown("**Sector**")
        with st.spinner("Loading sectors..."):
            sector_df = get_insulin_sectors(client, TABLE_NAME, global_filters, local_regions)

            if sector_df is not None and not sector_df.empty:
                # Create a container for checkbox list
                with st.container():
                    # Initialize session state for sector checkboxes if not exists
                    if 'insulin_sector_checkboxes' not in st.session_state:
                        st.session_state.insulin_sector_checkboxes = {}

                    # Build sector options
                    sector_data = []
                    for _, row in sector_df.iterrows():
                        sector = row['sector']
                        count = row['facility_count']
                        sector_data.append((sector, count))

                    total_sectors = len(sector_data)

                    # Create checkboxes for each sector
                    local_sectors = []
                    for sector, count in sector_data:
                        # Initialize checkbox state to True (checked) if not set
                        checkbox_key = f"insulin_sector_{sector}"
                        if checkbox_key not in st.session_state.insulin_sector_checkboxes:
                            st.session_state.insulin_sector_checkboxes[checkbox_key] = True

                        # Display checkbox
                        is_checked = st.checkbox(
                            f"{sector} ({count:,})",
                            value=st.session_state.insulin_sector_checkboxes[checkbox_key],
                            key=checkbox_key
                        )

                        # Update session state
                        st.session_state.insulin_sector_checkboxes[checkbox_key] = is_checked

                        # Add to selected list if checked
                        if is_checked:
                            local_sectors.append(sector)

                    # Display excluded count
                    excluded_count = total_sectors - len(local_sectors)
                    if excluded_count > 0:
                        st.caption(f"🚫 {excluded_count} item{'s' if excluded_count != 1 else ''} excluded")
            else:
                local_sectors = []
                st.info("No sector data available")
```

---

### Step 3: Scorecard Display

```python
    # Fetch metrics
    metrics = get_insulin_availability_metrics(
        client,
        TABLE_NAME,
        global_filters,
        local_regions,
        local_sectors
    )

    if metrics and metrics['total_facilities'] > 0:
        # Two-column layout for scorecards
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                label="Facilities with Availability (n)",
                value=f"{metrics['facilities_with_availability']:,}",
                help="Number of facilities with insulin available"
            )

        with col2:
            st.metric(
                label="Facilities with Unavailability (%)",
                value=f"{metrics['unavailability_percentage']:.1f}%",
                help="Percentage of facilities without insulin available"
            )
    else:
        st.info("No data available for the selected filters")

else:
    st.markdown("""
        <div class="info-box">
            <strong>💡 Tip:</strong> Select one or more data collection periods above to view insulin availability metrics.
        </div>
    """, unsafe_allow_html=True)
```

---

## Session State Management

### Initialize Local Filter State

```python
# Add to session state initialization section (around line 170)
if 'insulin_local_regions' not in st.session_state:
    st.session_state.insulin_local_regions = []
if 'insulin_local_sectors' not in st.session_state:
    st.session_state.insulin_local_sectors = []
```

**Note:** Using Streamlit's `key` parameter in multiselect handles state automatically

---

## Error Handling & Edge Cases

### 1. No Data Collection Period Selected
```python
if not st.session_state.selected_periods:
    # Show tip message (already implemented above)
```

### 2. Division by Zero
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

### 4. Empty Dropdown Options
```python
if region_df is None or region_df.empty:
    st.info("No region data available")
    local_regions = []
```

### 5. No Data After Filtering
```python
if metrics and metrics['total_facilities'] > 0:
    # Show scorecards
else:
    st.info("No data available for the selected filters")
```

---

## Performance Optimization

### Caching Strategy
- All BigQuery functions use `@st.cache_data(ttl=600)` for 10-minute cache
- Cache keys include filter parameters to ensure correct data per filter combination

### Query Optimization
- Use single query for scorecard metrics instead of separate queries
- Apply filters at database level, not in Python
- Use `COUNT(DISTINCT)` and `SUM` aggregations efficiently

---

## Styling & Responsive Design

### Use Existing CSS Classes
- `.section-header` for main heading
- `.info-box` for tip messages
- Streamlit's built-in `st.metric()` for scorecards

### Responsive Behavior
- Two-column layout uses `st.columns(2)`
- On mobile, columns stack automatically
- Metric cards are responsive by default

---

## Testing Requirements

### Unit Tests
```python
def test_get_insulin_regions():
    """Test region dropdown data fetching"""
    # Test with various filter combinations
    # Verify NULL handling

def test_get_insulin_sectors():
    """Test sector dropdown data fetching"""
    # Test with local region filters
    # Verify cascading behavior

def test_get_insulin_availability_metrics():
    """Test scorecard metric calculations"""
    # Verify division by zero handling
    # Verify percentage calculation
    # Verify unavailability formula: 100 - (available/total * 100)
```

### Integration Tests
1. Test filter cascade: Global → Local Region → Local Sector
2. Test scorecard updates when filters change
3. Test with empty datasets
4. Verify metric card formatting

---

## Implementation Checklist

### Backend Functions
- [ ] Implement `get_insulin_regions()` in bigquery_client.py
- [ ] Implement `get_insulin_sectors()` in bigquery_client.py
- [ ] Implement `get_insulin_availability_metrics()` in bigquery_client.py
- [ ] Add imports to app.py
- [ ] Add caching decorators

### UI Implementation
- [ ] Add section header "Insulin availability"
- [ ] Add sub-heading "Insulin availability - Overall"
- [ ] Implement two-column filter layout
- [ ] Implement Region dropdown with counts
- [ ] Implement Sector dropdown with counts
- [ ] Implement two-column scorecard layout
- [ ] Add Availability (n) metric card
- [ ] Add Unavailability (%) metric card
- [ ] Add "No data available" handling
- [ ] Add tip message when no period selected

### Filter Integration
- [ ] Global Data Collection Period filter applied
- [ ] Global Country filter applied (if selected)
- [ ] Global Region filter applied (if selected)
- [ ] Local Region dropdown respects global filters
- [ ] Local Sector dropdown respects global + local region filters
- [ ] Scorecards respect all filters (global + local)

### Validation & Testing
- [ ] Verify unavailability % formula: 100 - (available/total * 100)
- [ ] Test division by zero handling
- [ ] Test NULL value handling in insulin_available_num
- [ ] Test with various filter combinations
- [ ] Verify metric values are accurate
- [ ] Test responsive design on mobile

---

## Success Criteria

1. **Data Accuracy:** Scorecard metrics match database calculations exactly
2. **Filter Cascade:** Local dropdowns properly respect global filters
3. **Performance:** Component loads within 2 seconds
4. **Responsiveness:** Filters update scorecards immediately
5. **Error Handling:** Graceful handling of empty data, NULL values, division by zero
6. **User Experience:** Clear messaging when no data available

---

## Notes & Assumptions

### Assumed Column Schema
- `insulin_available_num`: Integer (1 = available, 0 = not available)
- If actual column is boolean or different format, queries need adjustment

### Alternative Column Names to Check
- `insulin_available` (boolean)
- `has_insulin` (boolean)
- `insulin_in_stock` (integer)

**Action Required:** Verify actual column name and data type in database before implementation

---

## Next Steps After Plan 3 Completion

1. User acceptance testing
2. Verify metrics accuracy against manual calculations
3. Document any data quality issues discovered
4. Proceed to Plan 4: Additional insulin availability filters/visualizations
