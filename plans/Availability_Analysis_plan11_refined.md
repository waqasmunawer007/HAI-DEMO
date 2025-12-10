# Dashboard UI Revamp - Plan 11: Insulin Availability - By Originator Brands VS Biosimilars Component

## Task Overview
Implement the "Insulin Availability - By originator brands VS biosimilars" component with two local filter dropdowns (Region and Sector) and four scorecards showing percentage availability for Originator Brands and Biosimilars, broken down by insulin type (Human vs Analogue).

**Use Serena MCP:** Define todo items list and solve them one by one according to this detailed plan.

**Current Phase:** Backend Integration and UI Implementation with Scorecard Metrics
**Prerequisites:** Plan 10 completed (Insulin Availability - By presentation and insulin type component)

---

## Component Placement

**Location:** Add after "Insulin Availability - By presentation and insulin type" component in app.py (after Plan 10)

**Visual Hierarchy:**
```
[Insulin Availability - By presentation and insulin type component]
    ↓
<br><br> spacing
    ↓
[Sub-heading: "Insulin availability - By originator brands VS biosimilars"]
    ↓
[Two-column filter row: Region | Sector]
    ↓
[Two-column scorecard layout: Human | Analogue]
    ↓
[Each column has 2 scorecards stacked vertically:
 - Facilities with Originator Brands (%)
 - Facilities with Biosimilars (%)]
```

---

## Component Structure

### 1. Sub-heading
```python
st.markdown("#### Insulin availability - By originator brands VS biosimilars")
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

### 3. Two-Column Scorecard Layout

**Column 1: Insulin Type - Human**
- **Scorecard 1 (Top):**
  - Label: "Facilities with Originator Brands (%)"
  - Display: Percentage value (e.g., "75.3%")
  - Style: Custom HTML metric card
- **Scorecard 2 (Bottom):**
  - Label: "Facilities with Biosimilars (%)"
  - Display: Percentage value (e.g., "45.8%")
  - Style: Custom HTML metric card

**Column 2: Insulin Type - Analogue**
- **Scorecard 3 (Top):**
  - Label: "Facilities with Originator Brands (%)"
  - Display: Percentage value (e.g., "68.2%")
  - Style: Custom HTML metric card
- **Scorecard 4 (Bottom):**
  - Label: "Facilities with Biosimilars (%)"
  - Display: Percentage value (e.g., "52.1%")
  - Style: Custom HTML metric card

**Scorecard Specifications:**
- Use existing app.py metric card HTML pattern
- White background with colored left border
- Large percentage value displayed prominently
- Label displayed above or below percentage
- Hover effect (slight lift)
- Responsive width

---

## Filter Behavior & Scope

### Global Filters (From Data Selectors)
These filters apply to ALL components including this one:
- ✅ Data Collection Period (REQUIRED)
- ✅ Country (optional)
- ✅ Region (optional) - **Note:** If global Region is selected, it restricts which regions appear in local dropdown

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
Four Scorecards → Display data filtered by global + local region + local sector filters, broken down by insulin type and originator/biosimilar
```

**Example:**
- User selects: Global Period = "Y1/P1", Global Country = "Peru", Local Region = "Arequipa", Local Sector = "Public"
- Component behavior:
  - Region dropdown: Shows all regions in Peru for Y1/P1
  - Sector dropdown: Shows all sectors in Peru for Y1/P1
  - Scorecards: Show availability percentages for originator brands and biosimilars, split by Human/Analogue insulin types, for facilities in "Arequipa", "Public" sector during "Y1/P1" in Peru

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

### Query 3: Human - Originator Brands Metric

**Purpose:** Calculate percentage of facilities with Human insulin Originator Brands available

**Source Table:** `adl_repeat_repivot`

**Column Assumptions:**
- `is_unavailable`: Integer column (0 = available, 1 = not available)
- `insulin_originator_biosimilar`: String column with values "Originator Brand" or "Biosimilar"
- `insulin_type`: String column containing insulin type (e.g., "Human", "Analogue")
- `form_case__case_id`: Unique facility identifier

**SQL Pattern:**
```sql
SELECT
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
    AND insulin_originator_biosimilar = 'Originator Brand'
    AND insulin_type LIKE '%Human%'
```

**Expected Output:** Single row DataFrame with columns:
- `total_facilities` (int): Total facilities surveyed
- `facilities_with_insulin` (int): Facilities with insulin available (is_unavailable = 0)
- `availability_percentage` (float): Percentage (0-100, 1 decimal place)

**Validation Rules:**
- If result is empty, default to 0%
- `availability_percentage` should be between 0 and 100
- `facilities_with_insulin` ≤ `total_facilities`

---

### Query 4: Analogue - Originator Brands Metric

**Purpose:** Calculate percentage of facilities with Analogue insulin Originator Brands available

**Source Table:** `adl_repeat_repivot`

**SQL Pattern:**
```sql
SELECT
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
    AND ({local_sector_filter})
    AND insulin_originator_biosimilar = 'Originator Brand'
    AND insulin_type LIKE '%Analogue%'
```

**Expected Output:** Same structure as Query 3

**Validation Rules:** Same as Query 3

---

### Query 5: Human - Biosimilars Metric

**Purpose:** Calculate percentage of facilities with Human insulin Biosimilars available

**Source Table:** `adl_repeat_repivot`

**SQL Pattern:**
```sql
SELECT
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
    AND ({local_sector_filter})
    AND insulin_originator_biosimilar = 'Biosimilar'
    AND insulin_type LIKE '%Human%'
```

**Expected Output:** Same structure as Query 3

**Validation Rules:** Same as Query 3

---

### Query 6: Analogue - Biosimilars Metric

**Purpose:** Calculate percentage of facilities with Analogue insulin Biosimilars available

**Source Table:** `adl_repeat_repivot`

**SQL Pattern:**
```sql
SELECT
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
    AND ({local_sector_filter})
    AND insulin_originator_biosimilar = 'Biosimilar'
    AND insulin_type LIKE '%Analogue%'
```

**Expected Output:** Same structure as Query 3

**Validation Rules:** Same as Query 3

---

## Implementation Functions

### Function 1: get_insulin_originator_biosimilar_regions()

```python
@st.cache_data(ttl=600)
def get_insulin_originator_biosimilar_regions(_client, table_name, global_filters):
    """
    Get regions for local Region dropdown in Insulin Availability - Originator VS Biosimilar component.

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

### Function 2: get_insulin_originator_biosimilar_sectors()

```python
@st.cache_data(ttl=600)
def get_insulin_originator_biosimilar_sectors(_client, table_name, global_filters):
    """
    Get sectors for local Sector dropdown in Insulin Availability - Originator VS Biosimilar component.

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

### Function 3: get_insulin_human_originator_metric()

```python
@st.cache_data(ttl=600)
def get_insulin_human_originator_metric(_client, table_name, global_filters, local_regions, local_sectors):
    """
    Get availability percentage for Human insulin Originator Brands.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        float: Availability percentage (0-100, 1 decimal place)
    """
    # Build WHERE clause with global + local filters
    # Filter: insulin_originator_biosimilar = 'Originator Brand'
    # Filter: insulin_type LIKE '%Human%'
    # Calculate: COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id) * 100
    # Execute query on adl_repeat_repivot table
    # Return percentage value (default 0.0 if empty)
```

---

### Function 4: get_insulin_analogue_originator_metric()

```python
@st.cache_data(ttl=600)
def get_insulin_analogue_originator_metric(_client, table_name, global_filters, local_regions, local_sectors):
    """
    Get availability percentage for Analogue insulin Originator Brands.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        float: Availability percentage (0-100, 1 decimal place)
    """
    # Build WHERE clause with global + local filters
    # Filter: insulin_originator_biosimilar = 'Originator Brand'
    # Filter: insulin_type LIKE '%Analogue%'
    # Calculate: COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id) * 100
    # Execute query on adl_repeat_repivot table
    # Return percentage value (default 0.0 if empty)
```

---

### Function 5: get_insulin_human_biosimilar_metric()

```python
@st.cache_data(ttl=600)
def get_insulin_human_biosimilar_metric(_client, table_name, global_filters, local_regions, local_sectors):
    """
    Get availability percentage for Human insulin Biosimilars.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        float: Availability percentage (0-100, 1 decimal place)
    """
    # Build WHERE clause with global + local filters
    # Filter: insulin_originator_biosimilar = 'Biosimilar'
    # Filter: insulin_type LIKE '%Human%'
    # Calculate: COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id) * 100
    # Execute query on adl_repeat_repivot table
    # Return percentage value (default 0.0 if empty)
```

---

### Function 6: get_insulin_analogue_biosimilar_metric()

```python
@st.cache_data(ttl=600)
def get_insulin_analogue_biosimilar_metric(_client, table_name, global_filters, local_regions, local_sectors):
    """
    Get availability percentage for Analogue insulin Biosimilars.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        float: Availability percentage (0-100, 1 decimal place)
    """
    # Build WHERE clause with global + local filters
    # Filter: insulin_originator_biosimilar = 'Biosimilar'
    # Filter: insulin_type LIKE '%Analogue%'
    # Calculate: COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id) * 100
    # Execute query on adl_repeat_repivot table
    # Return percentage value (default 0.0 if empty)
```

---

## UI Implementation Pattern

### Step 1: Sub-heading

```python
# After Insulin Availability - By presentation and insulin type component
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("#### Insulin availability - By originator brands VS biosimilars")
```

---

### Step 2: Two-Column Filter Layout with Checkbox Dropdowns

```python
# Note: Plan 11 uses adl_surveys for dropdowns, adl_repeat_repivot for metrics
PLAN11_SURVEYS_TABLE = config.TABLES["surveys"]
PLAN11_REPIVOT_TABLE = config.TABLES["repeat_repivot"]

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
            region_df = get_insulin_originator_biosimilar_regions(client, PLAN11_SURVEYS_TABLE, global_filters)

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
                    checkbox_key = f"insulin_originator_biosimilar_region_{region}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items from session state
                selected_count = sum(
                    1 for region, _ in region_data
                    if st.session_state.get(f"insulin_originator_biosimilar_region_{region}", True)
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
                        checkbox_key = f"insulin_originator_biosimilar_region_{region}"

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
            sector_df = get_insulin_originator_biosimilar_sectors(client, PLAN11_SURVEYS_TABLE, global_filters)

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
                    checkbox_key = f"insulin_originator_biosimilar_sector_{sector}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items from session state
                selected_count = sum(
                    1 for sector, _ in sector_data
                    if st.session_state.get(f"insulin_originator_biosimilar_sector_{sector}", True)
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
                        checkbox_key = f"insulin_originator_biosimilar_sector_{sector}"

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

### Step 3: Two-Column Scorecard Layout

```python
    # Create two columns for scorecards
    st.markdown("<br>", unsafe_allow_html=True)
    scorecard_col1, scorecard_col2 = st.columns(2)

    # Column 1: Insulin Type - Human
    with scorecard_col1:
        st.markdown("**Insulin type - Human**")

        # Scorecard 1: Originator Brands
        with st.spinner("Loading Human Originator Brands metric..."):
            human_originator_pct = get_insulin_human_originator_metric(
                client,
                PLAN11_REPIVOT_TABLE,
                global_filters,
                local_regions,
                local_sectors
            )

            st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin: 0; font-size: 14px; color: #666;">Facilities with Originator Brands (%)</h4>
                    <p style="margin: 10px 0 0 0; font-size: 36px; font-weight: bold; color: #1f77b4;">{human_originator_pct:.1f}%</p>
                </div>
            """, unsafe_allow_html=True)

        # Scorecard 2: Biosimilars
        st.markdown("<br>", unsafe_allow_html=True)
        with st.spinner("Loading Human Biosimilars metric..."):
            human_biosimilar_pct = get_insulin_human_biosimilar_metric(
                client,
                PLAN11_REPIVOT_TABLE,
                global_filters,
                local_regions,
                local_sectors
            )

            st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin: 0; font-size: 14px; color: #666;">Facilities with Biosimilars (%)</h4>
                    <p style="margin: 10px 0 0 0; font-size: 36px; font-weight: bold; color: #1f77b4;">{human_biosimilar_pct:.1f}%</p>
                </div>
            """, unsafe_allow_html=True)

    # Column 2: Insulin Type - Analogue
    with scorecard_col2:
        st.markdown("**Insulin type - Analogue**")

        # Scorecard 3: Originator Brands
        with st.spinner("Loading Analogue Originator Brands metric..."):
            analogue_originator_pct = get_insulin_analogue_originator_metric(
                client,
                PLAN11_REPIVOT_TABLE,
                global_filters,
                local_regions,
                local_sectors
            )

            st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin: 0; font-size: 14px; color: #666;">Facilities with Originator Brands (%)</h4>
                    <p style="margin: 10px 0 0 0; font-size: 36px; font-weight: bold; color: #ff7f0e;">{analogue_originator_pct:.1f}%</p>
                </div>
            """, unsafe_allow_html=True)

        # Scorecard 4: Biosimilars
        st.markdown("<br>", unsafe_allow_html=True)
        with st.spinner("Loading Analogue Biosimilars metric..."):
            analogue_biosimilar_pct = get_insulin_analogue_biosimilar_metric(
                client,
                PLAN11_REPIVOT_TABLE,
                global_filters,
                local_regions,
                local_sectors
            )

            st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin: 0; font-size: 14px; color: #666;">Facilities with Biosimilars (%)</h4>
                    <p style="margin: 10px 0 0 0; font-size: 36px; font-weight: bold; color: #ff7f0e;">{analogue_biosimilar_pct:.1f}%</p>
                </div>
            """, unsafe_allow_html=True)

else:
    st.markdown("""
        <div class="info-box">
            <strong>💡 Tip:</strong> Select one or more data collection periods above to view insulin availability by originator brands and biosimilars.
        </div>
    """, unsafe_allow_html=True)
```

**Implementation Notes:**
- **Two columns:** Human uses `#1f77b4` (blue), Analogue uses `#ff7f0e` (orange) for visual distinction
- **Metric cards:** Use existing `.metric-card` CSS class from app.py
- **Stacked layout:** Two scorecards per column, vertical spacing with `<br>`
- **Column headers:** Bold text identifying insulin type above each column
- **Percentage formatting:** Display with 1 decimal place (e.g., "75.3%")
- **Default values:** Functions return 0.0 if no data available
- **Responsive:** Two-column layout adapts to screen size

---

## Session State Management

### Initialize Local Filter State

```python
# Session state keys for this component use unique prefix to avoid conflicts
# Region checkboxes: insulin_originator_biosimilar_region_{region_name}
# Sector checkboxes: insulin_originator_biosimilar_sector_{sector_name}
# These are automatically managed by Streamlit when using st.checkbox with key parameter
```

**Note:** Using Streamlit's `key` parameter in checkbox handles state automatically. Unique prefix `insulin_originator_biosimilar_` prevents conflicts with other insulin availability components.

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

### 6. No Data After Filtering (Metrics Return 0)
```python
# Functions return 0.0 if no data matches filters
# Display "0.0%" in scorecard
# This is acceptable behavior - indicates no availability
```

### 7. NULL/Empty insulin_originator_biosimilar Values
```python
# Filter with exact match:
AND insulin_originator_biosimilar = 'Originator Brand'
# or
AND insulin_originator_biosimilar = 'Biosimilar'
# NULL values automatically excluded
```

### 8. No Regions or Sectors Selected
```python
# If user unchecks all regions/sectors, local_regions/local_sectors will be empty list
# Queries should handle empty list and return 0.0
# Display "0.0%" in all scorecards
```

### 9. Inconsistent Column Values
```python
# If insulin_originator_biosimilar has unexpected values (not "Originator Brand" or "Biosimilar")
# Queries use exact match, so unexpected values are excluded
# This is desired behavior for data quality
```

---

## Performance Optimization

### Caching Strategy
- All BigQuery functions use `@st.cache_data(ttl=600)` for 10-minute cache
- Cache keys include filter parameters to ensure correct data per filter combination
- Six separate cached functions allow independent data fetching
- Scorecard rendering is fast, no caching needed for HTML generation

### Query Optimization
- Use single query for each metric (count and percentage in one query)
- Apply filters at database level, not in Python
- Use `COUNT(DISTINCT)` and CASE WHEN efficiently
- Filter by insulin_originator_biosimilar (exact match) and insulin_type (LIKE pattern) at database level
- No GROUP BY needed (single aggregate result per query)

### Parallel Data Fetching
- Region and Sector dropdown queries are independent (can run in parallel)
- Four metric queries depend on dropdown selections
- Consider fetching all four metrics concurrently if performance becomes issue

---

## Styling & Responsive Design

### Metric Card Styling
- **Color scheme:**
  - Human scorecards: `#1f77b4` (blue) from existing palette
  - Analogue scorecards: `#ff7f0e` (orange) for visual distinction
- **Card design:**
  - Use existing `.metric-card` CSS class
  - White background with colored left border
  - Label at top (14px, gray)
  - Percentage value large and bold (36px)
  - Slight shadow and hover lift effect
- **Layout:** Two columns with two cards each, vertically stacked

### Responsive Behavior
- Two-column layout adapts to screen size
- On mobile, columns stack vertically
- Metric cards expand to container width
- Consistent spacing between cards with `<br>` tags

### Consistency with Existing Components
- Use same section spacing (`<br><br>`)
- Use same markdown sub-heading style (`####`)
- Use same info-box class for messages
- Use same checkbox dropdown pattern from other plans
- Use same two-column filter layout pattern
- Use same metric-card pattern from existing app.py

---

## Testing Requirements

### Unit Tests
```python
def test_get_insulin_originator_biosimilar_regions():
    """Test region dropdown data fetching"""
    # Test with various filter combinations
    # Verify NULL/empty region exclusion
    # Verify DESC sorting
    # Verify uses adl_surveys table

def test_get_insulin_originator_biosimilar_sectors():
    """Test sector dropdown data fetching"""
    # Test with various filter combinations
    # Verify NULL/empty sector exclusion
    # Verify DESC sorting
    # Verify uses adl_surveys table

def test_get_insulin_human_originator_metric():
    """Test Human Originator Brands metric"""
    # Test with local region + sector filters
    # Verify percentage calculation
    # Verify insulin_originator_biosimilar filter (= 'Originator Brand')
    # Verify insulin_type filter (LIKE '%Human%')
    # Verify is_unavailable = 0 logic
    # Verify division by zero protection
    # Verify uses adl_repeat_repivot table
    # Verify returns float (0.0 if empty)

def test_get_insulin_analogue_originator_metric():
    """Test Analogue Originator Brands metric"""
    # Same tests as Human Originator
    # Verify insulin_type filter (LIKE '%Analogue%')

def test_get_insulin_human_biosimilar_metric():
    """Test Human Biosimilars metric"""
    # Same tests as Human Originator
    # Verify insulin_originator_biosimilar filter (= 'Biosimilar')

def test_get_insulin_analogue_biosimilar_metric():
    """Test Analogue Biosimilars metric"""
    # Same tests as Human Biosimilar
    # Verify insulin_type filter (LIKE '%Analogue%')
```

### Integration Tests
1. Test filter cascade: Global → Local Region → Local Sector → Four Metrics
2. Test metrics update when Region or Sector filter changes
3. Test with empty datasets (show "0.0%" in scorecards)
4. Verify all four scorecards display correct percentages
5. Verify percentage values match database calculations
6. Test with single vs multiple regions/sectors selected
7. Test independence from other insulin availability components
8. Verify Human column shows Human insulin metrics
9. Verify Analogue column shows Analogue insulin metrics
10. Verify Originator Brands vs Biosimilars distinction is correct

### Visual Validation
1. Verify two-column layout with Human and Analogue headers
2. Verify two scorecards per column, stacked vertically
3. Verify percentage values display with 1 decimal place
4. Verify label text is clear and correct
5. Verify Human scorecards use blue color (#1f77b4)
6. Verify Analogue scorecards use orange color (#ff7f0e)
7. Test responsive behavior on different screen sizes
8. Verify metric cards match existing app.py styling
9. Verify proper spacing between cards
10. Verify cards have hover effect

---

## Implementation Checklist

### Backend Functions
- [ ] Implement `get_insulin_originator_biosimilar_regions()` in bigquery_client.py
- [ ] Implement `get_insulin_originator_biosimilar_sectors()` in bigquery_client.py
- [ ] Implement `get_insulin_human_originator_metric()` in bigquery_client.py
- [ ] Implement `get_insulin_analogue_originator_metric()` in bigquery_client.py
- [ ] Implement `get_insulin_human_biosimilar_metric()` in bigquery_client.py
- [ ] Implement `get_insulin_analogue_biosimilar_metric()` in bigquery_client.py
- [ ] Add caching decorators with ttl=600
- [ ] Verify `is_unavailable` column exists in adl_repeat_repivot table
- [ ] Verify `insulin_originator_biosimilar` column exists in adl_repeat_repivot table
- [ ] Verify `insulin_type` column exists in adl_repeat_repivot table
- [ ] Verify `region` column exists in adl_surveys table
- [ ] Verify `sector` column exists in adl_surveys table

### UI Implementation
- [ ] Add sub-heading "Insulin availability - By originator brands VS biosimilars"
- [ ] Create two-column layout for Region and Sector filters
- [ ] Implement Region dropdown with checkboxes
- [ ] Add excluded count display inside Region dropdown
- [ ] Implement Sector dropdown with checkboxes
- [ ] Add excluded count display inside Sector dropdown
- [ ] Create two-column layout for scorecards (Human | Analogue)
- [ ] Add column headers: "Insulin type - Human" and "Insulin type - Analogue"
- [ ] Implement Human - Originator Brands scorecard
- [ ] Implement Human - Biosimilars scorecard
- [ ] Implement Analogue - Originator Brands scorecard
- [ ] Implement Analogue - Biosimilars scorecard
- [ ] Add vertical spacing between scorecards in each column
- [ ] Add tip message when no period selected
- [ ] Use metric-card CSS class for all scorecards

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
- [ ] All four metrics respect all filters (global + local region + local sector)
- [ ] All four metrics use adl_repeat_repivot table
- [ ] Human metrics filter by insulin_type LIKE '%Human%'
- [ ] Analogue metrics filter by insulin_type LIKE '%Analogue%'
- [ ] Originator metrics filter by insulin_originator_biosimilar = 'Originator Brand'
- [ ] Biosimilar metrics filter by insulin_originator_biosimilar = 'Biosimilar'

### Scorecard Styling
- [ ] Human scorecards use color `#1f77b4` (blue)
- [ ] Analogue scorecards use color `#ff7f0e` (orange)
- [ ] Use metric-card CSS class (white background, left border)
- [ ] Label font size: 14px, color: #666
- [ ] Percentage font size: 36px, bold
- [ ] Format percentage with 1 decimal place
- [ ] Add vertical spacing between cards with `<br>`
- [ ] Ensure responsive width

### Validation & Testing
- [ ] Verify percentage formula: (COUNT(DISTINCT CASE WHEN is_unavailable = 0...) / COUNT(DISTINCT form_case__case_id)) * 100
- [ ] Test division by zero handling
- [ ] Test NULL value handling in is_unavailable
- [ ] Test with various filter combinations
- [ ] Verify metric values match database calculations
- [ ] Verify excluded region/sector logic works correctly
- [ ] Test responsive design (cards adapt to container width)
- [ ] Verify Human column shows Human insulin metrics
- [ ] Verify Analogue column shows Analogue insulin metrics
- [ ] Test independence from other components
- [ ] Verify Originator Brands metrics are distinct from Biosimilars metrics
- [ ] Verify correct color coding (blue for Human, orange for Analogue)

**Implementation Status:** ⏳ **PENDING** - Ready for implementation

---

## Success Criteria

1. **Data Accuracy:** All four metric percentages match database calculations exactly
2. **Filter Cascade:** Local Region and Sector dropdowns properly respect global filters
3. **Filter Logic:** All four metrics respect all filters (global + local region + local sector)
4. **Originator/Biosimilar Distinction:** Metrics correctly distinguish between Originator Brands and Biosimilars
5. **Insulin Type Distinction:** Human and Analogue metrics are correctly separated
6. **Performance:** Component loads within 2 seconds
7. **Responsiveness:** Metrics update immediately when Region or Sector filter changes
8. **Error Handling:** Graceful handling of empty data, NULL values, division by zero (default to 0.0%)
9. **User Experience:** Clear messaging when no data available
10. **Visual Quality:** Scorecards are visually appealing, readable, and match dashboard style
11. **Color Coding:** Human cards use blue, Analogue cards use orange
12. **Independence:** Component works independently of other insulin availability components
13. **Table Usage:** Dropdowns use adl_surveys, metrics use adl_repeat_repivot

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
- `insulin_originator_biosimilar`: String with values "Originator Brand" or "Biosimilar" - **Used for filtering**
- `insulin_type`: String with insulin types (contains "Human" or "Analogue") - **Used for filtering**
- `form_case__case_id`: Unique facility identifier
- `data_collection_period`: Period identifier
- `country`: Country name (optional)
- `region`: Region name (may contain NULL values)
- `sector`: Sector name (may contain NULL values)

### Key Features of Plan 11

1. **Two filters:** Region AND Sector
2. **Scorecard visualization:** Not charts, but metric cards showing percentages
3. **Two dimensions:** Insulin Type (Human/Analogue) × Originator/Biosimilar
4. **Four metrics total:** 2×2 grid layout
5. **Different tables:** Uses adl_surveys for dropdowns, adl_repeat_repivot for metrics
6. **New filter column:** `insulin_originator_biosimilar` (not used in previous plans)
7. **Simple aggregation:** Single percentage value per metric (no grouping)
8. **Color coding:** Blue for Human, Orange for Analogue

### Metric Calculation Logic
**Plan 11 (Originator vs Biosimilar):**
```sql
COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) / COUNT(DISTINCT form_case__case_id) * 100
-- Where is_unavailable = 0 means available
-- Filtered by insulin_originator_biosimilar = 'Originator Brand' OR 'Biosimilar'
-- Filtered by insulin_type LIKE '%Human%' OR '%Analogue%'
-- No GROUP BY (single aggregate result)
```

### Originator Brands vs Biosimilars

**Originator Brands:**
- Original patented insulin products
- Typically more expensive
- Established brand recognition
- Examples: Humalog (Lilly), NovoLog (Novo Nordisk), Lantus (Sanofi)

**Biosimilars:**
- Similar biological products to originator brands
- Approved after patent expiration
- Typically lower cost
- Same clinical efficacy and safety profile
- Examples: Insulin glargine biosimilars, Insulin lispro biosimilars

### Scorecard Implementation Pattern
Following existing app.py metric card pattern:
- Use HTML with `unsafe_allow_html=True`
- Use `.metric-card` CSS class (already defined in app.py)
- Large percentage value (36px, bold)
- Small label text (14px, gray)
- Colored left border or colored text for visual distinction
- Two columns with st.columns(2)
- Vertical stacking within each column

### Session State Key Naming
Use unique prefix `insulin_originator_biosimilar_` to avoid conflicts:
- Plan 3: `insulin_region_`, `insulin_sector_`
- Plan 4: `insulin_by_sector_region_`
- Plan 5: `insulin_by_type_region_`, `insulin_by_type_sector_`
- Plan 6: `insulin_by_region_sector_`
- Plan 7: `insulin_public_levelcare_region_`
- Plan 8: `insulin_by_inn_region_`, `insulin_by_inn_sector_`
- Plan 10: `insulin_by_presentation_region_`, `insulin_by_presentation_sector_`
- Plan 11: `insulin_originator_biosimilar_region_`, `insulin_originator_biosimilar_sector_`

This ensures all components coexist without state interference.

---

## Next Steps After Plan 11 Completion

1. User acceptance testing with real data from adl_repeat_repivot table
2. Verify all four scorecards display correct percentages
3. Validate percentage calculations against manual checks
4. Test filter interactions with other insulin availability components (ensure independence)
5. Verify two-column filter layout works on various screen sizes
6. Verify two-column scorecard layout works on various screen sizes
7. Verify Originator Brands vs Biosimilars distinction is accurate
8. Verify Human vs Analogue insulin type distinction is accurate
9. Verify color coding (blue for Human, orange for Analogue)
10. Document any data quality issues (missing originator/biosimilar classification, NULL values, etc.)
11. Proceed to next insulin availability filter/visualization if any

---

## Implementation Notes

### Key Similarities with Plan 10
1. ✅ Two-filter design (Region and Sector)
2. ✅ Checkbox dropdown implementation pattern
3. ✅ Excluded count display
4. ✅ Session state management for checkboxes
5. ✅ Global filter integration
6. ✅ Error handling for empty data
7. ✅ Caching strategy with @st.cache_data(ttl=600)
8. ✅ Same availability logic (is_unavailable = 0)
9. ✅ Two-column layout
10. ✅ Mixed table usage (adl_surveys for dropdowns, adl_repeat_repivot for data)

### New Patterns Introduced in Plan 11
1. 🆕 Scorecard visualization instead of charts
2. 🆕 Metric card HTML pattern (from existing app.py)
3. 🆕 Four separate metric queries (no single combined query)
4. 🆕 Filter by `insulin_originator_biosimilar` column (new dimension)
5. 🆕 Simple aggregation (no GROUP BY, single result per query)
6. 🆕 2×2 grid layout (Insulin Type × Originator/Biosimilar)
7. 🆕 Column headers for insulin types
8. 🆕 Vertical stacking of cards within columns
9. 🆕 Return float directly from metric functions (not DataFrame)

### Potential Challenges
1. **Data quality:** Verify insulin_originator_biosimilar column has clean "Originator Brand" and "Biosimilar" values
2. **Table mismatch:** Dropdowns from adl_surveys, metrics from adl_repeat_repivot (ensure consistency)
3. **Empty metrics:** All four metrics might return 0.0% (acceptable behavior)
4. **Column value consistency:** insulin_originator_biosimilar might have unexpected values
5. **Scorecard styling:** Ensure metric-card CSS class exists in app.py
6. **Color differentiation:** Ensure blue and orange colors are distinct enough
7. **Layout balance:** Four cards in 2×2 grid should be visually balanced

### Recommended Testing Sequence
1. First verify adl_surveys and adl_repeat_repivot table schemas
2. Check insulin_originator_biosimilar column values (should be "Originator Brand" or "Biosimilar")
3. Check insulin_type column values (should contain "Human" or "Analogue")
4. Test region dropdown function with adl_surveys table
5. Test sector dropdown function with adl_surveys table
6. Test each metric function individually with hardcoded filters
7. Verify percentage calculations are correct
8. Integrate Region and Sector filters with metrics
9. Test full filter cascade (global + local region + local sector)
10. Test responsive layout (two-column filter and scorecard layouts)
11. Final visual validation with all four scorecards

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
- `insulin_originator_biosimilar`: Classification - **Used for filtering (Originator Brand/Biosimilar)**
- `insulin_type`: Insulin type - **Used for filtering (Human/Analogue)**
- `is_unavailable`: Integer (0 = available, 1 = not available)

**Usage in this component:** Source for all four metric calculations

**Data Quality Checks:**
- Check for NULL values in critical columns (insulin_originator_biosimilar, insulin_type, region, sector, is_unavailable)
- Verify insulin_originator_biosimilar has expected values ("Originator Brand", "Biosimilar")
- Verify insulin_type contains "Human" or "Analogue" for filtering
- Check distribution of is_unavailable values (0 vs 1)
- Verify data exists for all four combinations (Human×Originator, Human×Biosimilar, Analogue×Originator, Analogue×Biosimilar)

---

## UI Layout Visual Guide

```
┌─────────────────────────────────────────────────────────────────┐
│ #### Insulin availability - By originator brands VS biosimilars │
├─────────────────────────────────────────────────────────────────┤
│ Region ▼                      │ Sector ▼                        │
│ Region (X/Y selected)         │ Sector (X/Y selected)           │
├─────────────────────────────────────────────────────────────────┤
│ Insulin type - Human          │ Insulin type - Analogue         │
│ ┌───────────────────────────┐ │ ┌───────────────────────────┐   │
│ │ Facilities with           │ │ │ Facilities with           │   │
│ │ Originator Brands (%)     │ │ │ Originator Brands (%)     │   │
│ │                           │ │ │                           │   │
│ │      75.3%                │ │ │      68.2%                │   │
│ └───────────────────────────┘ │ └───────────────────────────┘   │
│                               │                               │
│ ┌───────────────────────────┐ │ ┌───────────────────────────┐   │
│ │ Facilities with           │ │ │ Facilities with           │   │
│ │ Biosimilars (%)           │ │ │ Biosimilars (%)           │   │
│ │                           │ │ │                           │   │
│ │      45.8%                │ │ │      52.1%                │   │
│ └───────────────────────────┘ │ └───────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

**End of Plan 11 Refined Document**
