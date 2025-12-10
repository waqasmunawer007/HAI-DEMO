# Dashboard UI Revamp - Plan 12: Insulin Availability - Availability of Comparator Medicines Component

## Task Overview
Implement the "Insulin availability - Availability of comparator medicine" component with two local filter dropdowns (Region and Sector) and a paginated table showing availability percentages for comparator NCD medicines (Metformin, Glibenclamide, Statins, Antihypertensives) by name and strength.

**Use Serena MCP:** Define todo items list and solve them one by one according to this detailed plan.

**Current Phase:** Backend Integration and UI Implementation with Paginated Table
**Prerequisites:** Plan 11 completed (Insulin Availability - By originator brands VS biosimilars component)

---

## Component Placement

**Location:** Add after "Insulin Availability - By originator brands VS biosimilars" component in app.py (after Plan 11)

**Visual Hierarchy:**
```
[Insulin Availability - By originator brands VS biosimilars component]
    ↓
<br><br> spacing
    ↓
[Sub-heading: "Insulin availability - Availability of comparator medicine"]
    ↓
[Two-column filter row: Region | Sector]
    ↓
[Paginated Table: Name | Strength (mg) | Facilities with Availability (%)]
    ↓
[Pagination controls: Previous | Page X of Y | Next]
```

---

## Component Structure

### 1. Sub-heading
```python
st.markdown("#### Insulin availability - Availability of comparator medicine")
```

### 2. Two-Column Filter Layout

**Region Dropdown (Column 1)**
- Expandable dropdown (st.expander) containing checkbox list
- Dropdown label shows: "Region (X/Y selected)" where X=selected, Y=total
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
- Dropdown label shows: "Sector (X/Y selected)" where X=selected, Y=total
- Default state: Collapsed (expanded=False)
- Inside dropdown: Individual checkboxes for each sector
- Each checkbox shows: "Sector Name (count)" format
- Displays excluded items count inside dropdown: "🚫 X items excluded"
- Source table: `adl_surveys`
- Filters data within this component only
- Independent from global Data Selectors
- Default: All sectors selected (all checkboxes checked)

### 3. Paginated Table

**Table Columns:**
1. **Name** - Medicine name (e.g., "Atorvastatin", "Metformin")
2. **Strength (mg)** - Medicine strength in milligrams (e.g., "20", "500")
3. **Facilities with Availability (%)** - Percentage of facilities where medicine is available

**Table Features:**
- Pagination: 10 rows per page
- Page navigation: Previous/Next buttons with page indicator "Page X of Y"
- Sorting: By Name column (default: DESC/reverse alphabetical)
- Responsive design: Full width
- Source table: `adl_comparators`

**Table Specifications:**
- Use Streamlit's native `st.dataframe()` with interactive features
- Column configuration for proper display
- Percentage column formatted with 1 decimal place
- Empty state message when no data available

---

## Filter Behavior & Scope

### Global Filters (From Data Selectors)
These filters apply to ALL components including this one:
- ✅ Data Collection Period (REQUIRED)
- ✅ Country (optional)
- ✅ Region (optional) - **Note:** If global Region is selected, it restricts which regions appear in local dropdown

### Local Filters (Component-Specific)
These filters ONLY affect this component's table:
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
Table Data → Display comparator medicines filtered by global + local region + local sector filters, grouped by name and strength
```

**Example:**
- User selects: Global Period = "Y1/P1", Global Country = "Peru", Local Region = "Arequipa", Local Sector = "Public"
- Component behavior:
  - Region dropdown: Shows all regions in Peru for Y1/P1
  - Sector dropdown: Shows all sectors in Peru for Y1/P1
  - Table: Shows availability percentages for comparator medicines (grouped by name + strength) for facilities in "Arequipa", "Public" sector during "Y1/P1" in Peru

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

### Query 3: Comparator Medicine Table Data

**Purpose:** Get table data with medicine name, strength, and availability percentage

**Source Table:** `adl_comparators`

**Column Assumptions:**
- `available_num`: String column ("0" = not available, "1" = available) - needs CAST to INT64
- `survey_id`: Unique survey identifier
- `name`: Medicine name (e.g., "Atorvastatin", "Metformin")
- `strength`: Medicine strength as string (e.g., "20", "500")

**SQL Pattern:**
```sql
SELECT
    name,
    strength,
    COUNT(DISTINCT survey_id) as total_surveys,
    SUM(CAST(available_num AS INT64)) as surveys_with_medicine,
    CASE
        WHEN COUNT(DISTINCT survey_id) > 0
        THEN ROUND((SUM(CAST(available_num AS INT64)) * 100.0) / COUNT(DISTINCT survey_id), 1)
        ELSE 0
    END as availability_percentage
FROM `{GCP_PROJECT_ID}.{BQ_DATASET}.adl_comparators`
WHERE
    data_collection_period IN ({selected_periods})
    AND ({country_filter})  -- if global country selected
    AND ({global_region_filter})   -- if global region selected
    AND ({local_region_filter})  -- if local region selected in component
    AND ({local_sector_filter})  -- if local sector selected in component
    AND name IS NOT NULL
    AND TRIM(name) != ''
    AND strength IS NOT NULL
    AND TRIM(strength) != ''
GROUP BY name, strength
ORDER BY name DESC
```

**Expected Output:** DataFrame with columns:
- `name` (string): Medicine name
- `strength` (string): Medicine strength
- `total_surveys` (int): Total surveys for this medicine
- `surveys_with_medicine` (int): Surveys where medicine was available (available_num = "1")
- `availability_percentage` (float): Percentage (0-100, 1 decimal place)

**Validation Rules:**
- If result is empty, show empty table message
- `availability_percentage` should be between 0 and 100
- `surveys_with_medicine` ≤ `total_surveys`
- NULL names and strengths are excluded

**Pagination Logic:**
- Performed in Python after query execution
- Page size: 10 rows
- Page number stored in session state

---

## Implementation Functions

### Function 1: get_comparator_medicine_regions()

```python
@st.cache_data(ttl=600)
def get_comparator_medicine_regions(_client, table_name, global_filters):
    """
    Get regions for local Region dropdown in Comparator Medicine Availability component.

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

### Function 2: get_comparator_medicine_sectors()

```python
@st.cache_data(ttl=600)
def get_comparator_medicine_sectors(_client, table_name, global_filters):
    """
    Get sectors for local Sector dropdown in Comparator Medicine Availability component.

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

### Function 3: get_comparator_medicine_table_data()

```python
@st.cache_data(ttl=600)
def get_comparator_medicine_table_data(_client, table_name, global_filters, local_regions, local_sectors):
    """
    Get comparator medicine availability data for table display.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_comparators)
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        pandas DataFrame with columns: name, strength, availability_percentage
        (total_surveys and surveys_with_medicine are also returned for debugging but not displayed)
    """
    # Build WHERE clause with global + local filters
    # Filter out NULL/empty names and strengths
    # Calculate: SUM(CAST(available_num AS INT64)) / COUNT(DISTINCT survey_id) * 100
    # Group by name, strength
    # Sort by name DESC
    # Execute query on adl_comparators table
    # Return DataFrame
```

---

## UI Implementation Pattern

### Step 1: Sub-heading

```python
# After Insulin Availability - By originator brands VS biosimilars component
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("#### Insulin availability - Availability of comparator medicine")
```

---

### Step 2: Two-Column Filter Layout with Checkbox Dropdowns

```python
# Note: Plan 12 uses adl_surveys for dropdowns, adl_comparators for table data
PLAN12_SURVEYS_TABLE = config.TABLES["surveys"]
PLAN12_COMPARATORS_TABLE = config.TABLES["comparators"]

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
            region_df = get_comparator_medicine_regions(client, PLAN12_SURVEYS_TABLE, global_filters)

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
                    checkbox_key = f"comparator_medicine_region_{region}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items from session state
                selected_count = sum(
                    1 for region, _ in region_data
                    if st.session_state.get(f"comparator_medicine_region_{region}", True)
                )
                excluded_count = total_regions - selected_count

                # Create expander/dropdown with selection summary
                with st.expander(
                    f"Region ({selected_count}/{total_regions} selected)",
                    expanded=False
                ):
                    # Display excluded count inside expander
                    if excluded_count > 0:
                        st.caption(f"🚫 {excluded_count} item{'s' if excluded_count != 1 else ''} excluded")

                    # Create checkboxes for each region
                    local_regions = []
                    for region, count in region_data:
                        checkbox_key = f"comparator_medicine_region_{region}"

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
            sector_df = get_comparator_medicine_sectors(client, PLAN12_SURVEYS_TABLE, global_filters)

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
                    checkbox_key = f"comparator_medicine_sector_{sector}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items from session state
                selected_count = sum(
                    1 for sector, _ in sector_data
                    if st.session_state.get(f"comparator_medicine_sector_{sector}", True)
                )
                excluded_count = total_sectors - selected_count

                # Create expander/dropdown with selection summary
                with st.expander(
                    f"Sector ({selected_count}/{total_sectors} selected)",
                    expanded=False
                ):
                    # Display excluded count inside expander
                    if excluded_count > 0:
                        st.caption(f"🚫 {excluded_count} item{'s' if excluded_count != 1 else ''} excluded")

                    # Create checkboxes for each sector
                    local_sectors = []
                    for sector, count in sector_data:
                        checkbox_key = f"comparator_medicine_sector_{sector}"

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

### Step 3: Paginated Table

```python
    # Fetch table data
    st.markdown("<br>", unsafe_allow_html=True)

    with st.spinner("Loading comparator medicine data..."):
        table_df = get_comparator_medicine_table_data(
            client,
            PLAN12_COMPARATORS_TABLE,
            global_filters,
            local_regions,
            local_sectors
        )

        if table_df is not None and not table_df.empty:
            # Prepare display dataframe (only show name, strength, availability_percentage)
            display_df = table_df[['name', 'strength', 'availability_percentage']].copy()

            # Rename columns for display
            display_df.columns = ['Name', 'Strength (mg)', 'Facilities with Availability (%)']

            # Format percentage column
            display_df['Facilities with Availability (%)'] = display_df['Facilities with Availability (%)'].apply(
                lambda x: f"{x:.1f}"
            )

            # Pagination logic
            ROWS_PER_PAGE = 10
            total_rows = len(display_df)
            total_pages = (total_rows + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE  # Ceiling division

            # Initialize page number in session state
            if 'comparator_medicine_page' not in st.session_state:
                st.session_state.comparator_medicine_page = 1

            # Ensure page number is within bounds
            if st.session_state.comparator_medicine_page > total_pages:
                st.session_state.comparator_medicine_page = total_pages if total_pages > 0 else 1

            # Calculate pagination range
            start_idx = (st.session_state.comparator_medicine_page - 1) * ROWS_PER_PAGE
            end_idx = min(start_idx + ROWS_PER_PAGE, total_rows)

            # Display paginated data
            paginated_df = display_df.iloc[start_idx:end_idx]

            # Display table
            st.dataframe(
                paginated_df,
                use_container_width=True,
                hide_index=True
            )

            # Pagination controls
            if total_pages > 1:
                col1, col2, col3 = st.columns([1, 2, 1])

                with col1:
                    if st.button("◀ Previous", disabled=(st.session_state.comparator_medicine_page == 1)):
                        st.session_state.comparator_medicine_page -= 1
                        st.rerun()

                with col2:
                    st.markdown(
                        f"<div style='text-align: center; padding-top: 0.3rem;'>Page {st.session_state.comparator_medicine_page} of {total_pages}</div>",
                        unsafe_allow_html=True
                    )

                with col3:
                    if st.button("Next ▶", disabled=(st.session_state.comparator_medicine_page == total_pages)):
                        st.session_state.comparator_medicine_page += 1
                        st.rerun()

            # Display summary
            st.caption(f"Showing {start_idx + 1}-{end_idx} of {total_rows} medicine(s)")

        else:
            st.info("No comparator medicine data available for the selected filters")

else:
    st.markdown("""
        <div class="info-box">
            <strong>💡 Tip:</strong> Select one or more data collection periods above to view comparator medicine availability.
        </div>
    """, unsafe_allow_html=True)
```

**Implementation Notes:**
- **Pagination:** Uses session state (`comparator_medicine_page`) to track current page
- **Page controls:** Previous/Next buttons with disabled state at boundaries
- **Page indicator:** "Page X of Y" displayed centrally
- **Rows per page:** Fixed at 10 rows
- **Table display:** Uses `st.dataframe()` with `use_container_width=True`
- **Column formatting:** Percentage formatted to 1 decimal place as string
- **Empty state:** Shows info message when no data available

---

## Session State Management

### Initialize Local Filter State and Pagination

```python
# Session state keys for this component use unique prefix to avoid conflicts
# Region checkboxes: comparator_medicine_region_{region_name}
# Sector checkboxes: comparator_medicine_sector_{sector_name}
# Page number: comparator_medicine_page
# These are automatically managed by Streamlit when using st.checkbox with key parameter
```

**Note:** Using Streamlit's `key` parameter in checkbox handles state automatically. Unique prefix `comparator_medicine_` prevents conflicts with other components.

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
    WHEN COUNT(DISTINCT survey_id) > 0
    THEN calculation
    ELSE 0
END
```

### 3. NULL Values in available_num Column
```python
# Use CAST to convert string to INT64 in SQL
SUM(CAST(available_num AS INT64))
# NULL values are treated as 0 by SUM
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

### 6. No Data After Filtering (Empty Table)
```python
if table_df is None or table_df.empty:
    st.info("No comparator medicine data available for the selected filters")
```

### 7. NULL/Empty Medicine Names or Strengths
```python
# Filter in SQL query:
AND name IS NOT NULL
AND TRIM(name) != ''
AND strength IS NOT NULL
AND TRIM(strength) != ''
# NULL values automatically excluded
```

### 8. No Regions or Sectors Selected
```python
# If user unchecks all regions/sectors, local_regions/local_sectors will be empty list
# Query should handle empty list and return empty DataFrame
# Display "No data available" message
```

### 9. Page Number Out of Bounds
```python
# Check and reset page number when filters change
if st.session_state.comparator_medicine_page > total_pages:
    st.session_state.comparator_medicine_page = total_pages if total_pages > 0 else 1
```

### 10. Single Page of Data
```python
# Only show pagination controls if total_pages > 1
if total_pages > 1:
    # Display Previous/Next buttons and page indicator
```

---

## Performance Optimization

### Caching Strategy
- All BigQuery functions use `@st.cache_data(ttl=600)` for 10-minute cache
- Cache keys include filter parameters to ensure correct data per filter combination
- Three separate cached functions allow independent data fetching
- Table rendering is fast, no additional caching needed for pagination

### Query Optimization
- Use single query for table data (count and percentage in one query)
- Apply filters at database level, not in Python
- Use `COUNT(DISTINCT)` and `SUM(CAST(...))` efficiently
- Filter out NULL/empty names and strengths at database level
- GROUP BY name, strength for aggregation
- Pagination performed in Python (not SQL) for simplicity

### Data Loading Strategy
- Region and Sector dropdown queries are independent (can run in parallel)
- Table query depends on dropdown selections
- Total rows fetched from database (no server-side pagination to reduce query complexity)
- Client-side pagination using Python slicing

---

## Styling & Responsive Design

### Table Styling
- **Layout:** Full container width
- **Columns:**
  - Name: Left-aligned text
  - Strength (mg): Center-aligned numeric
  - Facilities with Availability (%): Right-aligned percentage
- **Formatting:** Percentage with 1 decimal place (e.g., "75.3")
- **Empty state:** Info message with icon

### Pagination Control Styling
- **Layout:** Three columns (Previous | Page indicator | Next)
- **Buttons:** Disabled state when at boundaries
- **Page indicator:** Centered text with padding
- **Summary:** Caption showing range (e.g., "Showing 1-10 of 47 medicine(s)")

### Responsive Behavior
- Two-column filter layout adapts to screen size
- On mobile, columns stack vertically
- Table expands to container width
- Pagination controls remain accessible on mobile
- Consistent spacing with `<br>` tags

### Consistency with Existing Components
- Use same section spacing (`<br><br>`)
- Use same markdown sub-heading style (`####`)
- Use same info-box class for messages
- Use same checkbox dropdown pattern from other plans
- Use same two-column filter layout pattern
- Use Streamlit's native table component

---

## Testing Requirements

### Unit Tests
```python
def test_get_comparator_medicine_regions():
    """Test region dropdown data fetching"""
    # Test with various filter combinations
    # Verify NULL/empty region exclusion
    # Verify DESC sorting
    # Verify uses adl_surveys table

def test_get_comparator_medicine_sectors():
    """Test sector dropdown data fetching"""
    # Test with various filter combinations
    # Verify NULL/empty sector exclusion
    # Verify DESC sorting
    # Verify uses adl_surveys table

def test_get_comparator_medicine_table_data():
    """Test table data fetching and calculation"""
    # Test with local region + sector filters
    # Verify percentage calculation: SUM(CAST(available_num AS INT64)) / COUNT(DISTINCT survey_id) * 100
    # Verify GROUP BY name, strength
    # Verify NULL/empty name and strength exclusion
    # Verify DESC sorting by name
    # Verify division by zero protection
    # Verify uses adl_comparators table
    # Verify returns DataFrame with correct columns
```

### Integration Tests
1. Test filter cascade: Global → Local Region → Local Sector → Table Data
2. Test table updates when Region or Sector filter changes
3. Test with empty datasets (show "No data available" message)
4. Verify table displays correct data
5. Verify percentage values match database calculations
6. Test with single vs multiple regions/sectors selected
7. Test independence from other components
8. Verify pagination works correctly
9. Test pagination boundary conditions (first page, last page)
10. Verify page number resets when filters change

### Visual Validation
1. Verify two-column filter layout
2. Verify table displays with correct columns
3. Verify percentage values display with 1 decimal place
4. Verify pagination controls appear when >10 rows
5. Verify "Page X of Y" indicator displays correctly
6. Verify Previous button disabled on first page
7. Verify Next button disabled on last page
8. Verify summary text shows correct row range
9. Test responsive behavior on different screen sizes
10. Verify table matches existing app.py styling

---

## Implementation Checklist

### Backend Functions
- [ ] Implement `get_comparator_medicine_regions()` in bigquery_client.py
- [ ] Implement `get_comparator_medicine_sectors()` in bigquery_client.py
- [ ] Implement `get_comparator_medicine_table_data()` in bigquery_client.py
- [ ] Add caching decorators with ttl=600
- [ ] Verify `available_num` column exists in adl_comparators table (as string)
- [ ] Verify `name` column exists in adl_comparators table
- [ ] Verify `strength` column exists in adl_comparators table
- [ ] Verify `survey_id` column exists in adl_comparators table
- [ ] Verify `region` column exists in adl_surveys table
- [ ] Verify `sector` column exists in adl_surveys table

### UI Implementation
- [ ] Add sub-heading "Insulin availability - Availability of comparator medicine"
- [ ] Create two-column layout for Region and Sector filters
- [ ] Implement Region dropdown with checkboxes
- [ ] Add excluded count display inside Region dropdown
- [ ] Implement Sector dropdown with checkboxes
- [ ] Add excluded count display inside Sector dropdown
- [ ] Fetch table data with filters applied
- [ ] Create display DataFrame with renamed columns
- [ ] Format percentage column to 1 decimal place
- [ ] Implement pagination logic (10 rows per page)
- [ ] Initialize page number in session state
- [ ] Calculate pagination range (start_idx, end_idx)
- [ ] Display paginated table with st.dataframe()
- [ ] Add Previous button with disabled state logic
- [ ] Add page indicator "Page X of Y"
- [ ] Add Next button with disabled state logic
- [ ] Add row count summary
- [ ] Add tip message when no period selected
- [ ] Handle empty table state

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
- [ ] Table data respects all filters (global + local region + local sector)
- [ ] Table data uses adl_comparators table
- [ ] Table data groups by name and strength
- [ ] Table data sorts by name DESC
- [ ] Table data excludes NULL names and strengths

### Pagination Implementation
- [ ] Session state key: comparator_medicine_page
- [ ] Page number initialized to 1
- [ ] Page number bounded (1 to total_pages)
- [ ] Rows per page set to 10
- [ ] Total pages calculated correctly
- [ ] Start/end indices calculated correctly
- [ ] Pagination controls only show when >1 page
- [ ] Previous button disabled on page 1
- [ ] Next button disabled on last page
- [ ] Page indicator displays current/total pages
- [ ] st.rerun() called on page change

### Validation & Testing
- [ ] Verify percentage formula: SUM(CAST(available_num AS INT64)) / COUNT(DISTINCT survey_id) * 100
- [ ] Test division by zero handling
- [ ] Test NULL value handling in available_num
- [ ] Test with various filter combinations
- [ ] Verify table values match database calculations
- [ ] Verify excluded region/sector logic works correctly
- [ ] Test responsive design (table adapts to container width)
- [ ] Test independence from other components
- [ ] Verify pagination boundary conditions
- [ ] Test page number reset when filters change
- [ ] Verify empty state messages display correctly

**Implementation Status:** ⏳ **PENDING** - Ready for implementation

---

## Success Criteria

1. **Data Accuracy:** Table percentages match database calculations exactly
2. **Filter Cascade:** Local Region and Sector dropdowns properly respect global filters
3. **Filter Logic:** Table data respects all filters (global + local region + local sector)
4. **Grouping:** Data correctly grouped by medicine name and strength
5. **Sorting:** Table sorted by name in DESC order
6. **Pagination:** 10 rows per page, navigation works correctly
7. **Performance:** Component loads within 2 seconds
8. **Responsiveness:** Table updates immediately when Region or Sector filter changes
9. **Error Handling:** Graceful handling of empty data, NULL values, division by zero
10. **User Experience:** Clear messaging when no data available, pagination controls intuitive
11. **Visual Quality:** Table is readable, well-formatted, and matches dashboard style
12. **Independence:** Component works independently of other insulin availability components
13. **Table Usage:** Dropdowns use adl_surveys, table data uses adl_comparators

---

## Notes & Assumptions

### Assumed Column Schema

**Table: adl_surveys**
- `form_case__case_id`: Unique facility identifier
- `data_collection_period`: Period identifier
- `country`: Country name (optional)
- `region`: Region name (may contain NULL values to exclude)
- `sector`: Sector name (may contain NULL values to exclude)

**Table: adl_comparators**
- `survey_id`: Unique survey identifier
- `data_collection_period`: Period identifier
- `country`: Country name (optional)
- `region`: Region name (may contain NULL values)
- `sector`: Sector name (may contain NULL values)
- `name`: Medicine name (e.g., "Atorvastatin", "Metformin")
- `strength`: Medicine strength as string (e.g., "20", "500")
- `available_num`: String ("0" or "1") indicating availability - **Needs CAST to INT64**
- `comparator`: Medicine type (e.g., "statin", "metformin", "glibenclamide", "antihypertensive")

### Key Features of Plan 12

1. **Two filters:** Region AND Sector
2. **Table visualization:** Paginated data table (not scorecards or charts)
3. **Three columns:** Name, Strength (mg), Facilities with Availability (%)
4. **Pagination:** 10 rows per page with Previous/Next navigation
5. **Different tables:** Uses adl_surveys for dropdowns, adl_comparators for table data
6. **New data source:** adl_comparators table (comparator NCD medicines)
7. **Aggregation:** Group by name + strength, calculate availability percentage
8. **Sorting:** By name DESC (reverse alphabetical)

### Metric Calculation Logic
**Plan 12 (Comparator Medicines):**
```sql
SUM(CAST(available_num AS INT64)) / COUNT(DISTINCT survey_id) * 100
-- Where available_num is "1" for available, "0" for not available
-- Grouped by name, strength
-- Sorted by name DESC
```

### Comparator Medicines

**What are Comparator NCD Medicines?**
These are non-insulin medications used as comparators in the study to assess healthcare access beyond diabetes-specific treatments:

1. **Metformin** - Oral diabetes medication (first-line treatment for type 2 diabetes)
2. **Glibenclamide** - Oral diabetes medication (sulfonylurea)
3. **Statins** - Cholesterol-lowering medications (e.g., Atorvastatin, Simvastatin)
4. **Antihypertensives** - Blood pressure medications (sometimes labeled as "Aspirin" in data)

These medications are important indicators of overall NCD (Non-Communicable Disease) medicine availability at healthcare facilities.

### Table Implementation Pattern
Following Streamlit best practices:
- Use `st.dataframe()` for interactive table display
- Column configuration for proper formatting
- Hide index for cleaner display
- Full container width for responsiveness
- Session state for pagination
- Python-based pagination (slice DataFrame)

### Session State Key Naming
Use unique prefix `comparator_medicine_` to avoid conflicts:
- Plan 3: `insulin_region_`, `insulin_sector_`
- Plan 4: `insulin_by_sector_region_`
- Plan 5: `insulin_by_type_region_`, `insulin_by_type_sector_`
- Plan 6: `insulin_by_region_sector_`
- Plan 7: `insulin_public_levelcare_region_`
- Plan 8: `insulin_by_inn_region_`, `insulin_by_inn_sector_`
- Plan 10: `insulin_by_presentation_region_`, `insulin_by_presentation_sector_`
- Plan 11: `insulin_originator_biosimilar_region_`, `insulin_originator_biosimilar_sector_`
- Plan 12: `comparator_medicine_region_`, `comparator_medicine_sector_`, `comparator_medicine_page`

This ensures all components coexist without state interference.

---

## Next Steps After Plan 12 Completion

1. User acceptance testing with real data from adl_comparators table
2. Verify table displays correct medicine names and strengths
3. Validate percentage calculations against manual checks
4. Test filter interactions with other components (ensure independence)
5. Verify two-column filter layout works on various screen sizes
6. Verify table layout works on various screen sizes
7. Test pagination with different data sizes (<10 rows, exactly 10, >10, >100 rows)
8. Verify sorting by name column works correctly
9. Document any data quality issues (missing names/strengths, NULL values, etc.)
10. Proceed to next component if any

---

## Implementation Notes

### Key Similarities with Plan 11
1. ✅ Two-filter design (Region and Sector)
2. ✅ Checkbox dropdown implementation pattern
3. ✅ Excluded count display
4. ✅ Session state management for checkboxes
5. ✅ Global filter integration
6. ✅ Error handling for empty data
7. ✅ Caching strategy with @st.cache_data(ttl=600)
8. ✅ Two-column layout for filters
9. ✅ Mixed table usage (adl_surveys for dropdowns, adl_comparators for data)

### New Patterns Introduced in Plan 12
1. 🆕 Paginated table visualization (not scorecards or charts)
2. 🆕 Session state for page number tracking
3. 🆕 Previous/Next button navigation
4. 🆕 Page indicator display
5. 🆕 Client-side pagination with Python slicing
6. 🆕 Three-column table layout
7. 🆕 Different data source: adl_comparators table
8. 🆕 String-to-INT64 casting for available_num
9. 🆕 Group by multiple columns (name, strength)
10. 🆕 Comparator medicines instead of insulin products

### Potential Challenges
1. **Data quality:** Verify available_num is consistently "0" or "1" (string format)
2. **Table mismatch:** Dropdowns from adl_surveys, data from adl_comparators (ensure consistency)
3. **Empty table:** Handle case where no medicines match filters
4. **Pagination reset:** Ensure page number resets to 1 when filters change
5. **Strength format:** Medicine strength may vary in format (handle as string)
6. **Large datasets:** If >100 rows, consider adding jump-to-page functionality
7. **Column widths:** Ensure columns display properly on various screen sizes

### Recommended Testing Sequence
1. First verify adl_surveys and adl_comparators table schemas
2. Check available_num column format (should be "0" or "1" as string)
3. Check name and strength column values and formats
4. Test region dropdown function with adl_surveys table
5. Test sector dropdown function with adl_surveys table
6. Test table data function with hardcoded filters
7. Verify percentage calculations are correct
8. Integrate Region and Sector filters with table
9. Test full filter cascade (global + local region + local sector)
10. Test pagination with different data sizes
11. Final visual validation with complete component

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

### Table: adl_comparators

**Purpose:** Contains comparator NCD medicine availability and pricing data

**Expected Columns:**
- `survey_id`: Unique survey identifier
- `data_collection_period`: Period identifier (e.g., "Y1/P1")
- `country`: Country name
- `region`: Region name (may contain NULL)
- `sector`: Sector name (may contain NULL)
- `name`: Medicine name (e.g., "Atorvastatin", "Metformin")
- `strength`: Medicine strength as string (e.g., "20", "500")
- `available_num`: String ("0" or "1") - **0 = not available, 1 = available**
- `comparator`: Medicine type (e.g., "statin", "metformin")
- `available`: String ("Yes" or "No") - Human-readable availability
- `price_local`: Local currency price (may be NULL)
- `price_usd`: USD price (may be NULL)
- `form_case__case_id`: Facility identifier

**Usage in this component:** Source for table data

**Data Quality Checks:**
- Check for NULL values in critical columns (name, strength, available_num, survey_id)
- Verify available_num has expected values ("0", "1")
- Verify name and strength are not empty strings
- Check distribution of comparator types
- Verify data exists for various medicines (Metformin, Glibenclamide, Statins, etc.)

---

## UI Layout Visual Guide

```
┌─────────────────────────────────────────────────────────────────┐
│ #### Insulin availability - Availability of comparator medicine │
├─────────────────────────────────────────────────────────────────┤
│ Region ▼                      │ Sector ▼                        │
│ Region (X/Y selected)         │ Sector (X/Y selected)           │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Name          │ Strength (mg) │ Facilities with Avail. (%) │ │
│ ├───────────────┼───────────────┼────────────────────────────┤ │
│ │ Simvastatin   │ 20            │ 75.3                       │ │
│ │ Simvastatin   │ 40            │ 68.2                       │ │
│ │ Metformin     │ 500           │ 82.1                       │ │
│ │ Metformin     │ 850           │ 65.4                       │ │
│ │ Glibenclamide │ 5             │ 55.7                       │ │
│ │ Atorvastatin  │ 10            │ 71.8                       │ │
│ │ Atorvastatin  │ 20            │ 78.9                       │ │
│ │ Atorvastatin  │ 40            │ 62.3                       │ │
│ │ Aspirin       │ 100           │ 88.5                       │ │
│ │ Aspirin       │ 81            │ 76.2                       │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ ◀ Previous      │    Page 1 of 5    │          Next ▶         │
├─────────────────────────────────────────────────────────────────┤
│ Showing 1-10 of 47 medicine(s)                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Corrections from Initial Plan 12

### Issues Found and Fixed:

1. **❌ INCORRECT FILTER in Initial Plan:**
   ```
   Filter: INCLUDE "insulin_originator_biosimilar" EQUALS "Originator Brand"
           AND INCLUDE insulin_type CONTAINS "Human"
   ```
   - **Problem:** These columns don't exist in adl_comparators table
   - **Root Cause:** Copy-paste error from Plan 11
   - **✅ CORRECTION:** Removed these filters - they don't apply to comparator medicines

2. **Clarified Component Purpose:**
   - Component is for **comparator NCD medicines** (Metformin, Glibenclamide, Statins, Antihypertensives)
   - NOT for insulin products
   - Data source is adl_comparators table, not adl_repeat_repivot

3. **Metric Calculation Clarified:**
   - Formula: `SUM(CAST(available_num AS INT64)) / COUNT(DISTINCT survey_id) * 100`
   - available_num is a string column ("0" or "1") that needs casting
   - Groups by name + strength to show each medicine variant

4. **Additional Specifications Added:**
   - Pagination implementation details
   - Session state management for page number
   - Boundary condition handling
   - Empty state handling
   - Column formatting specifications

---

**End of Plan 12 Refined Document**
