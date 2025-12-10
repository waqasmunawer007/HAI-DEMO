# Dashboard UI Revamp - Plan 9: Insulin - Top 10 Brands Component

## Task Overview
Implement the "Insulin - Top 10 brands" component with one local filter dropdown (Sector) and one Plotly pie chart showing percentage distribution of the top 10 insulin brands by stock count. Brands outside the top 10 are grouped into an "Other" category.

**Use Serena MCP:** Define todo items list and solve them one by one according to this detailed plan.

**Current Phase:** Backend Integration and UI Implementation with Single Plotly Pie Chart Visualization
**Prerequisites:** Plan 8 completed (Insulin Availability - By INN component)

---

## Component Placement

**Location:** Add after "Insulin availability - By INN" component in app.py (after Plan 8, before next component/tab)

**Visual Hierarchy:**
```
[Insulin Availability - By INN component]
    ↓
<br><br> spacing
    ↓
[Sub-heading: "Insulin - Top 10 brands"]
    ↓
[Single-column filter row: Sector]
    ↓
[Single Pie Chart: Top 10 Insulin Brands by % of all stock]
    ↓
[Note message: "NOTE: Pie chart shows the top 10 Insulin Brands by % of all stock. Other indicates brands outside of the top 10."]
```

---

## Component Structure

### 1. Sub-heading
```python
st.markdown("#### Insulin - Top 10 brands")
```

### 2. Single-Column Filter Layout

**Sector Dropdown**
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

### 3. Single Pie Chart Visualization

**Chart Title:** "Top 10 Insulin Brands by % of all stock"

**Chart Type:** Plotly Pie Chart (using **plotly.graph_objects.Pie** for donut-style visualization)

**Chart Specifications:**
- **Pie Slices:** Top 10 insulin brands + "Other" category
  - Each slice represents percentage of total stock count
  - Color: Auto-assigned from Plotly color palette
  - Data labels: Show percentage value on slice
  - Hover info: Display brand name, record count, and percentage
- **Legend:**
  - Position: Right side of pie chart
  - Shows brand names with color indicators
  - Default Plotly feature (automatically displayed)
- **Top 10 Logic:**
  - Query returns all brands sorted DESC by record count
  - Take top 10 brands by record count
  - Sum remaining brands into "Other" category
  - If < 10 brands total, show only available brands (no "Other")
- **Donut Style:**
  - Hole in center for modern donut pie chart appearance
  - `hole=0.4` parameter for donut effect
- **Layout:**
  - Responsive: Use `use_container_width=True`
  - Background: Transparent (`plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'`)
  - Height: ~500px for optimal viewing with legend

**Example Chart Data:**
| Brand Name     | Record Count | Percentage |
|----------------|--------------|------------|
| Humulin        | 1250         | 22.5%      |
| Novolin        | 1100         | 19.8%      |
| Lantus         | 890          | 16.0%      |
| NovoRapid      | 780          | 14.0%      |
| Humalog        | 650          | 11.7%      |
| Levemir        | 420          | 7.6%       |
| Tresiba        | 180          | 3.2%       |
| Apidra         | 140          | 2.5%       |
| Fiasp          | 90           | 1.6%       |
| Toujeo         | 50           | 0.9%       |
| Other          | 5            | 0.1%       |

### 4. Note Message

**Placement:** Below the pie chart

**Content:**
```python
st.markdown("""
    <div class="info-box">
        <strong>📝 Note:</strong> Pie chart shows the top 10 Insulin Brands by % of all stock. Other indicates brands outside of the top 10.
    </div>
""", unsafe_allow_html=True)
```

---

## Filter Behavior & Scope

### Global Filters (From Data Selectors)
These filters apply to ALL components including this one:
- ✅ Data Collection Period (REQUIRED)
- ✅ Country (optional)
- ✅ Region (optional)

### Local Filters (Component-Specific)
These filters ONLY affect this component's pie chart:
- ✅ Local Sector dropdown (filters within component)

### Filter Cascade Logic
```
Global Filters → Applied first to narrow dataset
    ↓
Local Sector dropdown → Shows only sectors within global filter constraints
    ↓
Pie Chart → Display top 10 brands by record count, grouped by insulin_brand, filtered by global + local sector filters
```

**Example:**
- User selects: Global Period = "Y1/P1", Global Country = "Peru", Local Sector = "Public"
- Component behavior:
  - Sector dropdown: Shows all sectors in Peru for Y1/P1
  - Chart: Shows top 10 insulin brands by stock percentage for "Public" sector facilities during "Y1/P1" in Peru
  - Chart groups all brands outside top 10 into "Other" category

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

### Query 2: Pie Chart Data - Top 10 Brands by Stock Count

**Purpose:** Get record count for all insulin brands, to be processed in Python to show top 10 + "Other"

**Source Table:** `adl_surveys_repeat`

**Column Assumptions:**
- `insulin_brand`: String column with brand names
- `form_case__case_id`: Facility identifier (not unique per brand; count records, not distinct facilities)
- Multiple records per facility (repeat data for different insulin products)

**SQL Pattern:**
```sql
SELECT
    insulin_brand,
    COUNT(*) as record_count
FROM `{GCP_PROJECT_ID}.{BQ_DATASET}.adl_surveys_repeat`
WHERE
    data_collection_period IN ({selected_periods})
    AND ({country_filter})  -- if global country selected
    AND ({global_region_filter})   -- if global region selected
    AND ({local_sector_filter})  -- if local sector selected in component
    AND insulin_brand IS NOT NULL
    AND TRIM(insulin_brand) != ''
    AND insulin_brand != 'NULL'
    AND insulin_brand != '---'  -- Exclude placeholder values
GROUP BY insulin_brand
ORDER BY record_count DESC
```

**Expected Output:** DataFrame with columns:
- `insulin_brand` (string): Brand name
- `record_count` (int): Total records for this brand

**Post-Query Processing (in Python):**
1. Take top 10 brands by `record_count`
2. Calculate total_count = SUM(all record_count)
3. For each top 10: percentage = (record_count / total_count) * 100
4. If more than 10 brands exist:
   - Sum remaining brands' record_count into "Other"
   - Calculate "Other" percentage = (other_count / total_count) * 100
   - Append "Other" row to data
5. Result: DataFrame with top 10 brands + "Other" (if applicable)

**Validation Rules:**
- If result is empty, show "No data available" message
- Sum of all percentages should equal 100%
- Sorted by `record_count DESC` for largest brands first
- Exclude "---" placeholder brand values

---

## Implementation Functions

### Function 1: get_insulin_top_brands_sectors()

```python
@st.cache_data(ttl=600)
def get_insulin_top_brands_sectors(_client, table_name, global_filters):
    """
    Get sectors for local Sector dropdown in Insulin - Top 10 brands component.

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
    # Exclude NULL/empty sectors
    # Execute query on adl_surveys table
    # Return results sorted DESC
```

---

### Function 2: get_insulin_top_brands_chart_data()

```python
@st.cache_data(ttl=600)
def get_insulin_top_brands_chart_data(_client, table_name, global_filters, local_sectors):
    """
    Get record counts for all insulin brands, to be processed for top 10 + "Other" display.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        global_filters (dict): Global filters from Data Selectors
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        pandas DataFrame with columns:
            - insulin_brand (str): Brand name
            - record_count (int): Total records for this brand
            - percentage (float): Percentage of total stock (calculated in Python)

        Returns top 10 brands + "Other" category (if more than 10 brands exist)
    """
    # Build WHERE clause with global + local sector filters
    # Filter: insulin_brand IS NOT NULL AND != '---'
    # Calculate: COUNT(*) as record_count
    # Group by insulin_brand
    # Order by record_count DESC
    # Execute query on adl_surveys_repeat table

    # Post-processing in Python:
    # 1. Take top 10 brands by record_count
    # 2. Calculate total_count = SUM(all record_count)
    # 3. Calculate percentage for each top 10 brand
    # 4. If > 10 brands, sum remaining into "Other" with percentage
    # 5. Return DataFrame with top 10 + "Other"
```

---

## UI Implementation Pattern

### Step 1: Sub-heading

```python
# After Insulin Availability - By INN component
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("#### Insulin - Top 10 brands")
```

---

### Step 2: Single-Column Filter Layout with Checkbox Dropdown

```python
# Note: Plan 9 uses adl_surveys for dropdown, adl_surveys_repeat for chart
PLAN9_SURVEYS_TABLE = config.TABLES["surveys"]
PLAN9_REPEAT_TABLE = config.TABLES["surveys_repeat"]

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
        sector_df = get_insulin_top_brands_sectors(client, PLAN9_SURVEYS_TABLE, global_filters)

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
                checkbox_key = f"insulin_top_brands_sector_{sector}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

            # Count selected items from session state
            selected_count = sum(
                1 for sector, _ in sector_data
                if st.session_state.get(f"insulin_top_brands_sector_{sector}", True)
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
                    checkbox_key = f"insulin_top_brands_sector_{sector}"

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

### Step 3: Single Plotly Pie Chart

```python
    # Fetch and display pie chart
    st.markdown("<br>", unsafe_allow_html=True)

    with st.spinner("Loading top 10 insulin brands..."):
        chart_df = get_insulin_top_brands_chart_data(
            client,
            PLAN9_REPEAT_TABLE,
            global_filters,
            local_sectors
        )

        if chart_df is not None and not chart_df.empty:
            # Ensure data types are correct
            chart_df['record_count'] = pd.to_numeric(chart_df['record_count'], errors='coerce')
            chart_df['percentage'] = pd.to_numeric(chart_df['percentage'], errors='coerce')

            # Create pie chart using graph_objects (donut style)
            fig = go.Figure()

            fig.add_trace(go.Pie(
                labels=chart_df['insulin_brand'].tolist(),
                values=chart_df['record_count'].tolist(),
                hole=0.4,  # Donut style
                textposition='auto',
                textinfo='percent',
                hovertemplate='<b>%{label}</b><br>' +
                              'Record Count: %{value:,}<br>' +
                              'Percentage: %{percent}<extra></extra>',
                marker=dict(
                    line=dict(color='white', width=2)
                )
            ))

            # Update layout
            fig.update_layout(
                title='Top 10 Insulin Brands by % of all stock',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=500,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05
                ),
                margin=dict(t=50, b=50, l=50, r=150)
            )

            # Display chart
            st.plotly_chart(fig, use_container_width=True)

            # Display note message below chart
            st.markdown("""
                <div class="info-box">
                    <strong>📝 Note:</strong> Pie chart shows the top 10 Insulin Brands by % of all stock. Other indicates brands outside of the top 10.
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No data available for the selected filters")

else:
    st.markdown("""
        <div class="info-box">
            <strong>💡 Tip:</strong> Select one or more data collection periods above to view top 10 insulin brands.
        </div>
    """, unsafe_allow_html=True)
```

**Implementation Notes:**
- **Donut pie chart:** Uses `hole=0.4` for modern donut appearance
- **Data type conversion:** Essential `pd.to_numeric()` on numeric columns
- **Text info:** Shows `percent` on slices
- **Legend:** Right side, vertical orientation at x=1.05
- **Custom hover:** Shows brand, record count, and percentage
- **Top 10 + Other:** Calculated in backend function
- **White borders:** Between slices for visual clarity
- **Note placement:** Immediately below the chart

---

## Session State Management

### Initialize Local Filter State

```python
# Session state keys for this component use unique prefix to avoid conflicts
# Sector checkboxes: insulin_top_brands_sector_{sector_name}
# These are automatically managed by Streamlit when using st.checkbox with key parameter
```

**Note:** Using Streamlit's `key` parameter in checkbox handles state automatically. Unique prefix `insulin_top_brands_` prevents conflicts with Plan 3, 4, 5, 6, 7, and 8 components.

---

## Error Handling & Edge Cases

### 1. No Data Collection Period Selected
```python
if not st.session_state.selected_periods:
    # Show tip message (already implemented above)
```

### 2. Division by Zero in Percentage Calculation
```python
# Handled in Python post-processing:
if total_count > 0:
    percentage = (record_count / total_count) * 100
else:
    percentage = 0
```

### 3. Fewer Than 10 Brands
```python
# If < 10 brands exist, show only available brands
# No "Other" category needed
if len(all_brands) <= 10:
    return all_brands  # No "Other" category
else:
    return top_10_brands + other_category
```

### 4. Empty Sector Dropdown
```python
if sector_df is None or sector_df.empty:
    st.info("No sector data available")
    local_sectors = []
```

### 5. No Data After Filtering (Empty Chart)
```python
if chart_df is None or chart_df.empty:
    st.info("No data available for the selected filters")
```

### 6. NULL/Empty insulin_brand Values
```python
# Filter in WHERE clause:
AND insulin_brand IS NOT NULL
AND TRIM(insulin_brand) != ''
AND insulin_brand != 'NULL'
AND insulin_brand != '---'
```

### 7. No Sectors Selected
```python
# If user unchecks all sectors, local_sectors will be empty list
# Query should handle empty list and return no data
# Display "No data available" message
```

---

## Performance Optimization

### Caching Strategy
- All BigQuery functions use `@st.cache_data(ttl=600)` for 10-minute cache
- Cache keys include filter parameters to ensure correct data per filter combination
- Two separate cached functions allow independent data fetching
- Top 10 + "Other" calculation done in Python (fast, no need to cache separately)

### Query Optimization
- Use single query to fetch all brands with record counts
- Apply filters at database level, not in Python
- Use `COUNT(*)` for record count (not COUNT DISTINCT)
- Group by insulin_brand for aggregation
- Python processes top 10 logic (more flexible than SQL LIMIT)

### Post-Processing Strategy
- Query returns all brands sorted DESC
- Python takes top 10 and sums remaining into "Other"
- More efficient than two queries (one for top 10, one for other)
- Allows dynamic "Other" category calculation

---

## Styling & Responsive Design

### Plotly Chart Styling
- **Color scheme:** Auto-assigned from Plotly color palette (consistent, visually distinct)
- **Donut style:** 40% hole for modern appearance
- **Transparency:** Background transparent to match Streamlit theme
- **Legend:** Right side with brand names and color indicators
- **White borders:** 2px white lines between slices for clarity

### Responsive Behavior
- Chart uses `use_container_width=True` for automatic width adjustment
- Legend positioned to right (x=1.05) to avoid overlap
- On mobile, legend may stack below chart
- Donut hole provides visual focus
- Text labels auto-positioned for readability

### Consistency with Existing Components
- Use same section spacing (`<br><br>`)
- Use same markdown sub-heading style (`####`)
- Use same info-box class for messages
- Use same checkbox dropdown pattern from Plan 3-8
- Use same single-column filter layout

---

## Testing Requirements

### Unit Tests
```python
def test_get_insulin_top_brands_sectors():
    """Test sector dropdown data fetching"""
    # Test with various filter combinations
    # Verify NULL/empty sector exclusion
    # Verify DESC sorting
    # Verify uses adl_surveys table

def test_get_insulin_top_brands_chart_data():
    """Test chart data fetching"""
    # Test with local sector filter
    # Verify record count calculation (COUNT(*))
    # Verify insulin_brand NULL exclusion
    # Verify "---" placeholder exclusion
    # Verify top 10 + "Other" logic
    # Verify percentage calculation
    # Verify sum of percentages = 100%
    # Verify DESC sorting by record_count
    # Verify uses adl_surveys_repeat table
    # Test edge case: < 10 brands (no "Other")
    # Test edge case: exactly 10 brands (no "Other")
    # Test edge case: > 10 brands ("Other" included)
```

### Integration Tests
1. Test filter cascade: Global → Local Sector → Chart
2. Test chart updates when Sector filter changes
3. Test with empty datasets (show "No data available")
4. Verify chart displays top 10 brands correctly
5. Verify "Other" category calculation when > 10 brands
6. Verify no "Other" category when ≤ 10 brands
7. Test hover tooltips show correct information
8. Test with single vs multiple sectors selected
9. Test independence from Plan 3-8 components
10. Verify percentages sum to 100%

### Visual Validation
1. Verify pie chart displays in donut style (hole in center)
2. Verify legend shows brand names with color indicators
3. Verify legend positioned on right side
4. Verify percentage labels appear on slices
5. Verify chart height is appropriate (~500px)
6. Verify white borders between slices
7. Test responsive behavior on different screen sizes
8. Verify note message appears below chart
9. Verify note message styling matches existing info-box
10. Verify top 10 + "Other" logic works correctly

---

## Implementation Checklist

### Backend Functions
- [ ] Implement `get_insulin_top_brands_sectors()` in bigquery_client.py
- [ ] Implement `get_insulin_top_brands_chart_data()` in bigquery_client.py
- [ ] Add imports to app.py (plotly.graph_objects already imported)
- [ ] Add caching decorators with ttl=600
- [ ] Verify `insulin_brand` column exists in adl_surveys_repeat table
- [ ] Verify `sector` column exists in adl_surveys table
- [ ] Implement top 10 + "Other" logic in Python

### UI Implementation
- [ ] Add sub-heading "Insulin - Top 10 brands"
- [ ] Implement Sector dropdown with checkboxes
- [ ] Add excluded count display inside Sector dropdown
- [ ] Implement single pie chart with Plotly go.Pie
- [ ] Configure donut style with hole=0.4
- [ ] Configure chart title: "Top 10 Insulin Brands by % of all stock"
- [ ] Configure legend: Right side, vertical orientation
- [ ] Configure text info: Show percent on slices
- [ ] Configure hover tooltips
- [ ] Add "No data available" handling for chart
- [ ] Add tip message when no period selected
- [ ] Set chart height to 500px
- [ ] Add note message below chart
- [ ] Add white borders between slices

### Filter Integration
- [ ] Global Data Collection Period filter applied
- [ ] Global Country filter applied (if selected)
- [ ] Global Region filter applied (if selected)
- [ ] Local Sector dropdown respects global filters
- [ ] Local Sector dropdown excludes NULL values
- [ ] Local Sector dropdown uses adl_surveys table
- [ ] Chart respects all filters (global + local sector)
- [ ] Chart uses adl_surveys_repeat table
- [ ] Chart groups by insulin_brand
- [ ] Chart excludes "---" placeholder values
- [ ] Chart calculates top 10 + "Other"

### Chart Styling
- [ ] Use donut style (hole=0.4)
- [ ] Set transparent background
- [ ] Configure legend position (right side, x=1.05)
- [ ] Format percentage labels on slices
- [ ] Configure hover template with custom formatting
- [ ] Apply responsive width with `use_container_width=True`
- [ ] Set appropriate margins (right margin=150 for legend)
- [ ] Add white borders between slices (2px)
- [ ] Auto-assign colors from Plotly palette

### Validation & Testing
- [ ] Verify record count formula: COUNT(*) per brand
- [ ] Test top 10 logic with various data sizes
- [ ] Test "Other" category calculation
- [ ] Test with < 10 brands (no "Other")
- [ ] Test with exactly 10 brands (no "Other")
- [ ] Test with > 10 brands ("Other" included)
- [ ] Verify percentages sum to 100%
- [ ] Test with various filter combinations
- [ ] Verify excluded sector logic works correctly
- [ ] Test responsive design (chart uses use_container_width=True)
- [ ] Verify hover tooltips display correctly
- [ ] Test independence from other components (Plan 3-8)
- [ ] Verify note message appears below chart

**Implementation Status:** ⏳ **PENDING** - Ready for implementation

---

## Success Criteria

1. **Data Accuracy:** Pie chart percentages sum to 100% exactly
2. **Top 10 Logic:** Correctly shows top 10 brands + "Other" when > 10 brands exist
3. **Filter Cascade:** Local Sector dropdown properly respects global filters
4. **Filter Logic:** Chart respects all filters (global + local sector)
5. **Performance:** Component loads within 2 seconds
6. **Responsiveness:** Chart updates immediately when Sector filter changes
7. **Error Handling:** Graceful handling of empty data, NULL values, < 10 brands
8. **User Experience:** Clear messaging when no data available
9. **Visual Quality:** Donut pie chart is visually appealing, readable, and matches dashboard style
10. **Legend Display:** Legend shows brand names with color indicators on right side
11. **Independence:** Component works independently of Plan 3-8 components
12. **Table Usage:** Dropdown uses adl_surveys, chart uses adl_surveys_repeat
13. **Note Display:** Note message appears below chart with correct styling

---

## Notes & Assumptions

### Assumed Column Schema

**Table: adl_surveys**
- `form_case__case_id`: Unique facility identifier
- `data_collection_period`: Period identifier
- `country`: Country name (optional)
- `region`: Region name (may contain NULL values)
- `sector`: Sector name (may contain NULL values to exclude)

**Table: adl_surveys_repeat**
- `insulin_brand`: String with brand names (Humulin, Novolin, Lantus, etc.)
- `form_case__case_id`: Facility identifier (NOT unique per brand; multiple records per facility)
- `data_collection_period`: Period identifier
- `country`: Country name (optional)
- `region`: Region name (may contain NULL values)
- `sector`: Sector name (may contain NULL values)

### Key Differences from Plan 8
1. **Pie chart instead of bar chart:** Visual change from bars to pie slices
2. **Single filter instead of two:** Only Sector (Plan 8 had Region AND Sector)
3. **Top 10 + "Other" logic:** New Python post-processing requirement
4. **Record count metric:** COUNT(*) instead of availability percentage
5. **Different table:** Uses adl_surveys_repeat instead of adl_repeat_repivot
6. **Donut style:** Hole=0.4 for modern appearance
7. **Legend display:** Right side with brand names and colors
8. **No availability logic:** Shows stock distribution, not availability
9. **Different grouping:** By insulin_brand instead of insulin_inn

### Metric Calculation Logic
**Plan 9 (Top 10 Brands):**
```sql
COUNT(*) as record_count
-- Count all records for each brand (not distinct facilities)
-- Group by insulin_brand
-- Sort DESC by record_count
```

**Python Post-Processing:**
```python
# Take top 10 brands by record_count
top_10 = df.head(10)

# Calculate total count
total_count = df['record_count'].sum()

# Calculate percentages for top 10
top_10['percentage'] = (top_10['record_count'] / total_count) * 100

# If more than 10 brands, sum remaining into "Other"
if len(df) > 10:
    other_count = df.iloc[10:]['record_count'].sum()
    other_percentage = (other_count / total_count) * 100
    other_row = pd.DataFrame([{
        'insulin_brand': 'Other',
        'record_count': other_count,
        'percentage': other_percentage
    }])
    result = pd.concat([top_10, other_row], ignore_index=True)
else:
    result = top_10

return result
```

### Plotly Pie Chart Pattern
New pattern for this component:
- Use `plotly.graph_objects.Pie` for pie chart
- Set `hole=0.4` for donut style
- Set `textinfo='percent'` to show percentages on slices
- Configure legend with `orientation="v"` and `x=1.05` for right side
- Add white borders with `marker=dict(line=dict(color='white', width=2))`
- Use auto-assigned colors from Plotly palette
- Custom hover template with brand, count, and percentage

### Session State Key Naming
Use unique prefix `insulin_top_brands_` to avoid conflicts:
- Plan 3: `insulin_region_`, `insulin_sector_`
- Plan 4: `insulin_by_sector_region_`
- Plan 5: `insulin_by_type_region_`, `insulin_by_type_sector_`
- Plan 6: `insulin_by_region_sector_`
- Plan 7: `insulin_public_levelcare_region_`
- Plan 8: `insulin_by_inn_region_`, `insulin_by_inn_sector_`
- Plan 9: `insulin_top_brands_sector_`

This ensures all components coexist without state interference.

---

## Next Steps After Plan 9 Completion

1. User acceptance testing with real data from adl_surveys_repeat table
2. Verify pie chart displays top 10 brands correctly
3. Validate "Other" category calculation accuracy
4. Test filter interactions with Plan 3-8 components (ensure independence)
5. Verify donut style appearance on various screen sizes
6. Verify legend displays correctly on right side
7. Verify percentages sum to 100%
8. Verify note message appears correctly below chart
9. Document any data quality issues (missing brands, "---" values, etc.)
10. Proceed to next insulin availability filter/visualization if any

---

## Implementation Notes

### Key Similarities with Previous Plans
1. ✅ Checkbox dropdown implementation pattern
2. ✅ Excluded count display
3. ✅ Session state management for checkboxes
4. ✅ Global filter integration
5. ✅ Error handling for empty data
6. ✅ Caching strategy with @st.cache_data(ttl=600)
7. ✅ Data type conversion with pd.to_numeric()
8. ✅ Custom hover tooltips
9. ✅ Single-column filter layout
10. ✅ Note message below chart

### New Patterns Introduced
1. 🆕 Pie chart visualization (first pie chart in dashboard)
2. 🆕 Donut style with hole=0.4
3. 🆕 Top 10 + "Other" logic in Python post-processing
4. 🆕 Legend on right side with brand names
5. 🆕 Record count metric (COUNT(*)) instead of availability
6. 🆕 Uses adl_surveys_repeat table
7. 🆕 White borders between pie slices
8. 🆕 Auto-assigned colors from Plotly palette
9. 🆕 Percentage display on slices (textinfo='percent')

### Potential Challenges
1. **Brand data quality:** Verify insulin_brand column has clean, consistent brand names
2. **"---" placeholder values:** Ensure these are properly excluded
3. **Top 10 + "Other" edge cases:** Test with < 10, exactly 10, and > 10 brands
4. **Percentage rounding:** Ensure percentages sum to exactly 100% (handle rounding)
5. **Legend overlap:** Ensure legend doesn't overlap pie chart on smaller screens
6. **Long brand names:** Some brands might have long names that affect legend display
7. **Table differences:** adl_surveys_repeat vs adl_repeat_repivot (ensure correct table)

### Recommended Testing Sequence
1. First verify adl_surveys and adl_surveys_repeat table schemas
2. Test sector dropdown function with adl_surveys table
3. Verify insulin_brand values in adl_surveys_repeat are as expected
4. Test chart function with hardcoded filters
5. Verify top 10 + "Other" logic with various data sizes
6. Verify percentages sum to 100%
7. Integrate Sector filter with chart
8. Test full filter cascade (global + local sector)
9. Test responsive layout and legend positioning
10. Final visual validation with note message

---

## Database Table Information

### Table: adl_surveys

**Purpose:** Contains main survey data for facilities

**Expected Columns:**
- `form_case__case_id`: Unique facility identifier
- `data_collection_period`: Period identifier (e.g., "Y1/P1")
- `country`: Country name
- `region`: Region name (may contain NULL)
- `sector`: Sector name (may contain NULL) - **Used for Sector dropdown**

**Usage in this component:** Source for Sector dropdown

### Table: adl_surveys_repeat

**Purpose:** Contains repeat insulin data for facilities (multiple records per facility for different insulin products)

**Expected Columns:**
- `form_case__case_id`: Facility identifier (NOT unique; multiple records per facility)
- `data_collection_period`: Period identifier (e.g., "Y1/P1")
- `country`: Country name
- `region`: Region name (may contain NULL)
- `sector`: Sector name (may contain NULL)
- `insulin_brand`: Brand name - **Used for grouping in chart**

**Usage in this component:** Source for pie chart data

**Data Quality Checks:**
- Check for NULL values in critical columns (insulin_brand, sector)
- Verify insulin_brand has recognizable brand names (Humulin, Novolin, Lantus, etc.)
- Check for "---" placeholder values and ensure they're excluded
- Verify multiple records per facility (repeat data structure)
- Test with various record count distributions

---

## UI Layout Visual Guide

```
┌─────────────────────────────────────────────────────────────────┐
│ #### Insulin - Top 10 brands                                    │
├─────────────────────────────────────────────────────────────────┤
│ Sector ▼                                                        │
│ Select Sectors (X/Y selected)                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌───────────────────────────────────────┬─────────────────────┐ │
│ │                                       │ Legend:             │ │
│ │        Top 10 Insulin Brands          │ ● Humulin           │ │
│ │        by % of all stock              │ ● Novolin           │ │
│ │                                       │ ● Lantus            │ │
│ │       ┌─────────────────┐             │ ● NovoRapid         │ │
│ │       │   Donut Pie     │             │ ● Humalog           │ │
│ │       │   Chart with    │             │ ● Levemir           │ │
│ │       │   Percentages   │             │ ● Tresiba           │ │
│ │       └─────────────────┘             │ ● Apidra            │ │
│ │                                       │ ● Fiasp             │ │
│ │  (Hole in center = donut style)       │ ● Toujeo            │ │
│ │                                       │ ● Other             │ │
│ └───────────────────────────────────────┴─────────────────────┘ │
│                                                                 │
│ 📝 Note: Pie chart shows the top 10 Insulin Brands by % of    │
│          all stock. Other indicates brands outside of the      │
│          top 10.                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

**End of Plan 9 Refined Document**