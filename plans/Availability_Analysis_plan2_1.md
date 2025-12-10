```markdown
# Dashboard UI Revamp - Plan 2.1: Summary of Facilities Surveyed Component

## Task Overview
Implement backend database queries for the hierarchical facility summary tree component (renamed from "Summary Statistics Tree" to "Summary of facilities surveyed") to populate all nodes with real-time data from the database.
Use Serena mcP to implement this component, define todo items list and solve them one by one according to the given details plan.   
**Current Phase:** Backend Integration and Data Population
**Previous Phase:** UI Design and Structure (Plan 2)

---

## Component Title Update

**Old Name:** Summary Statistics Tree  
**New Name:** Summary of facilities surveyed

**Implementation:**
- Update main heading text in component
- Update any references in code/documentation
- Ensure heading style matches other section headings

---

## Database Query Specifications

### Common Query Parameters

**Source Table:** `adl_surveys`  
**Primary Metric:** `COUNT_DISTINCT(form_case__case_id)` (distinct survey count)  
**Applied Filters:** Based on user selections from Data Selectors (Country, Region, Data Collection Period)

---

## Node-Specific Query Configurations

### 1. Root Node: Total Facilities Surveyed

**Query Configuration:**
- **Table:** `adl_surveys`
- **Metric:** `COUNT_DISTINCT(form_case__case_id)`
- **Filters:** None (baseline query, respects global filters from Data Selectors)
- **Purpose:** Aggregate count of all facilities across all sectors

**SQL Pattern:**
```sql
SELECT COUNT(DISTINCT form_case__case_id) as total_facilities
FROM adl_surveys
WHERE [global_filters_from_data_selectors]
```

**Expected Output:** Integer value representing total unique facilities surveyed

---

### 2. Level 1 Node: Public Facilities

**Query Configuration:**
- **Table:** `adl_surveys`
- **Metric:** `COUNT_DISTINCT(form_case__case_id)`
- **Filter:** `INCLUDE Sector CONTAINS "Public"`
- **Purpose:** Count all public sector facilities

**SQL Pattern:**
```sql
SELECT COUNT(DISTINCT form_case__case_id) as public_facilities
FROM adl_surveys
WHERE Sector LIKE '%Public%'
  AND [global_filters_from_data_selectors]
```

**Expected Output:** Integer value for public facilities  
**Validation:** Value should be ≤ Total Facilities Surveyed

---

### 3. Level 2 Node: Primary Level of Care

**Query Configuration:**
- **Table:** `adl_surveys`
- **Metric:** `COUNT_DISTINCT(form_case__case_id)`
- **Filter:** 
  - `INCLUDE Sector CONTAINS "Public"` AND
  - `INCLUDE Level of Care EQUALS "Primary"`
- **Purpose:** Count primary care facilities within public sector

**SQL Pattern:**
```sql
SELECT COUNT(DISTINCT form_case__case_id) as primary_facilities
FROM adl_surveys
WHERE Sector LIKE '%Public%'
  AND "Level of Care" = 'Primary'
  AND [global_filters_from_data_selectors]
```

**Expected Output:** Integer value for primary level facilities  
**Validation:** Value should be ≤ Public Facilities

---

### 4. Level 2 Node: Secondary Level of Care

**Query Configuration:**
- **Table:** `adl_surveys`
- **Metric:** `COUNT_DISTINCT(form_case__case_id)`
- **Filter:**
  - `INCLUDE Sector CONTAINS "Public"` AND
  - `INCLUDE Level of Care EQUALS "Secondary"`
- **Purpose:** Count secondary care facilities within public sector

**SQL Pattern:**
```sql
SELECT COUNT(DISTINCT form_case__case_id) as secondary_facilities
FROM adl_surveys
WHERE Sector LIKE '%Public%'
  AND "Level of Care" = 'Secondary'
  AND [global_filters_from_data_selectors]
```

**Expected Output:** Integer value for secondary level facilities  
**Validation:** Value should be ≤ Public Facilities

---

### 5. Level 2 Node: Tertiary Level of Care

**Query Configuration:**
- **Table:** `adl_surveys`
- **Metric:** `COUNT_DISTINCT(form_case__case_id)`
- **Filter:**
  - `INCLUDE Sector CONTAINS "Public"` AND
  - `INCLUDE Level of Care EQUALS "Tertiary"`
- **Purpose:** Count tertiary care facilities within public sector

**SQL Pattern:**
```sql
SELECT COUNT(DISTINCT form_case__case_id) as tertiary_facilities
FROM adl_surveys
WHERE Sector LIKE '%Public%'
  AND "Level of Care" = 'Tertiary'
  AND [global_filters_from_data_selectors]
```

**Expected Output:** Integer value for tertiary level facilities  
**Validation:** Value should be ≤ Public Facilities

---

### 6. Level 1 Node: Private Pharmacies

**Query Configuration:**
- **Table:** `adl_surveys`
- **Metric:** `COUNT_DISTINCT(form_case__case_id)`
- **Filter:** `INCLUDE Sector CONTAINS "Private Pharmacy"`
- **Purpose:** Count private pharmacy facilities

**SQL Pattern:**
```sql
SELECT COUNT(DISTINCT form_case__case_id) as private_pharmacies
FROM adl_surveys
WHERE Sector LIKE '%Private Pharmacy%'
  AND [global_filters_from_data_selectors]
```

**Expected Output:** Integer value for private pharmacies  
**Validation:** Value should be ≤ Total Facilities Surveyed

---

### 7. Level 1 Node: NGO/Faith Based Facilities

**Query Configuration:**
- **Table:** `adl_surveys`
- **Metric:** `COUNT_DISTINCT(form_case__case_id)`
- **Filter:** `INCLUDE Sector CONTAINS "NGO"`
- **Purpose:** Count NGO and faith-based facilities

**SQL Pattern:**
```sql
SELECT COUNT(DISTINCT form_case__case_id) as ngo_facilities
FROM adl_surveys
WHERE Sector LIKE '%NGO%'
  AND [global_filters_from_data_selectors]
```

**Expected Output:** Integer value for NGO/faith-based facilities  
**Validation:** Value should be ≤ Total Facilities Surveyed

**Note:** Verify if "Faith" facilities are captured under "NGO" sector or if additional filter needed

---

### 8. Level 1 Node: Private Hospitals/Clinics

**Query Configuration:**
- **Table:** `adl_surveys`
- **Metric:** `COUNT_DISTINCT(form_case__case_id)`
- **Filter:** `INCLUDE Sector CONTAINS "Private Hospital or Clinic"`
- **Purpose:** Count private hospital and clinic facilities

**SQL Pattern:**
```sql
SELECT COUNT(DISTINCT form_case__case_id) as private_hospitals
FROM adl_surveys
WHERE Sector LIKE '%Private Hospital or Clinic%'
  AND [global_filters_from_data_selectors]
```

**Expected Output:** Integer value for private hospitals/clinics  
**Validation:** Value should be ≤ Total Facilities Surveyed

---

### 9. Level 1 Node: Other

**Query Configuration:**
- **Table:** `adl_surveys`
- **Metric:** `COUNT_DISTINCT(form_case__case_id)`
- **Filter:** `INCLUDE Sector CONTAINS "Other"`
- **Purpose:** Count facilities categorized as "Other" sector

**SQL Pattern:**
```sql
SELECT COUNT(DISTINCT form_case__case_id) as other_facilities
FROM adl_surveys
WHERE Sector LIKE '%Other%'
  AND [global_filters_from_data_selectors]
```

**Expected Output:** Integer value for other facilities  
**Validation:** Value should be ≤ Total Facilities Surveyed

---

## Global Filter Integration

### Data Selector Filters to Apply

All queries must respect the following filters from the Data Selectors section:

1. **Country Filter:**
   - Column: `country`
   - Operator: `IN` or `=`
   - Value: Selected country/countries from dropdown

2. **Region Filter:**
   - Column: `region`
   - Operator: `IN` or `=`
   - Value: Selected region(s) from dropdown

3. **Data Collection Period Filter:**
   - Column: `data_collection_period`
   - Operator: `IN` or `=`
   - Value: Selected period(s) from dropdown

### Global Filter SQL Template
```sql
WHERE 
  (country IN ({selected_countries}) OR {no_country_filter})
  AND (region IN ({selected_regions}) OR {no_region_filter})
  AND (data_collection_period IN ({selected_periods}) OR {no_period_filter})
```

---

## Query Execution Strategy

### Option 1: Individual Queries (Simple)
```python
def fetch_facility_stats():
    """Execute separate query for each node"""
    
    stats = {
        'total': execute_query(query_total_facilities),
        'public': execute_query(query_public_facilities),
        'primary': execute_query(query_primary_care),
        'secondary': execute_query(query_secondary_care),
        'tertiary': execute_query(query_tertiary_care),
        'private_pharmacies': execute_query(query_private_pharmacies),
        'ngo': execute_query(query_ngo_facilities),
        'private_hospitals': execute_query(query_private_hospitals),
        'other': execute_query(query_other_facilities)
    }
    
    return stats
```

**Pros:** Simple, easy to debug  
**Cons:** Multiple database round trips, slower performance

---

### Option 2: Single Aggregated Query (Optimized - Recommended)
```python
def fetch_facility_stats_optimized():
    """Execute single query with conditional aggregation"""
    
    query = """
    SELECT 
        COUNT(DISTINCT form_case__case_id) as total_facilities,
        COUNT(DISTINCT CASE WHEN Sector LIKE '%Public%' THEN form_case__case_id END) as public_facilities,
        COUNT(DISTINCT CASE WHEN Sector LIKE '%Public%' AND "Level of Care" = 'Primary' THEN form_case__case_id END) as primary_facilities,
        COUNT(DISTINCT CASE WHEN Sector LIKE '%Public%' AND "Level of Care" = 'Secondary' THEN form_case__case_id END) as secondary_facilities,
        COUNT(DISTINCT CASE WHEN Sector LIKE '%Public%' AND "Level of Care" = 'Tertiary' THEN form_case__case_id END) as tertiary_facilities,
        COUNT(DISTINCT CASE WHEN Sector LIKE '%Private Pharmacy%' THEN form_case__case_id END) as private_pharmacies,
        COUNT(DISTINCT CASE WHEN Sector LIKE '%NGO%' THEN form_case__case_id END) as ngo_facilities,
        COUNT(DISTINCT CASE WHEN Sector LIKE '%Private Hospital or Clinic%' THEN form_case__case_id END) as private_hospitals,
        COUNT(DISTINCT CASE WHEN Sector LIKE '%Other%' THEN form_case__case_id END) as other_facilities
    FROM adl_surveys
    WHERE [global_filters_from_data_selectors]
    """
    
    result = execute_query(query)
    return result
```

**Pros:** Single database round trip, faster performance  
**Cons:** More complex query, harder to modify individual metrics

**Recommendation:** Use Option 2 for production implementation

---

## Data Structure Output Format

### Return Format
```python
facility_statistics = {
    "total": 1247,
    "categories": {
        "public": {
            "total": 823,
            "subcategories": {
                "primary": 456,
                "secondary": 289,
                "tertiary": 78
            }
        },
        "private_pharmacies": 215,
        "ngo_faith": 103,
        "private_hospitals": 89,
        "other": 17
    }
}
```

### Validation Rules
```python
def validate_facility_stats(stats):
    """Validate data integrity"""
    
    # Rule 1: Sum of Level 1 categories should equal total
    level1_sum = (
        stats['categories']['public']['total'] +
        stats['categories']['private_pharmacies'] +
        stats['categories']['ngo_faith'] +
        stats['categories']['private_hospitals'] +
        stats['categories']['other']
    )
    
    assert level1_sum <= stats['total'], "Level 1 sum exceeds total"
    
    # Rule 2: Sum of Level 2 (public subcategories) should equal public total
    level2_sum = (
        stats['categories']['public']['subcategories']['primary'] +
        stats['categories']['public']['subcategories']['secondary'] +
        stats['categories']['public']['subcategories']['tertiary']
    )
    
    assert level2_sum <= stats['categories']['public']['total'], "Level 2 sum exceeds public total"
    
    # Rule 3: All values should be non-negative
    assert all(v >= 0 for v in flatten_dict(stats)), "Negative values detected"
    
    return True
```

---

## Implementation Functions

### Query Builder Function
```python
def build_facility_query(filters):
    """
    Build SQL query with dynamic filters
    
    Args:
        filters (dict): Filter selections from Data Selectors
            {
                'country': ['Tanzania', 'Kenya'],
                'region': ['Dar es Salaam'],
                'data_collection_period': ['Y3/P1']
            }
    
    Returns:
        str: Complete SQL query with filters
    """
    
    base_query = """
    SELECT 
        COUNT(DISTINCT form_case__case_id) as total_facilities,
        COUNT(DISTINCT CASE WHEN Sector LIKE '%Public%' THEN form_case__case_id END) as public_facilities,
        -- ... (all other CASE statements)
    FROM adl_surveys
    WHERE 1=1
    """
    
    # Add country filter
    if filters.get('country'):
        country_list = "','".join(filters['country'])
        base_query += f" AND country IN ('{country_list}')"
    
    # Add region filter
    if filters.get('region'):
        region_list = "','".join(filters['region'])
        base_query += f" AND region IN ('{region_list}')"
    
    # Add data collection period filter
    if filters.get('data_collection_period'):
        period_list = "','".join(filters['data_collection_period'])
        base_query += f" AND data_collection_period IN ('{period_list}')"
    
    return base_query
```

### Data Fetching Function
```python
def fetch_facility_statistics(filters):
    """
    Fetch facility statistics from database
    
    Args:
        filters (dict): Applied filters from Data Selectors
    
    Returns:
        dict: Formatted facility statistics
    """
    
    query = build_facility_query(filters)
    result = execute_database_query(query)
    
    # Transform to expected format
    stats = {
        "total": result['total_facilities'],
        "categories": {
            "public": {
                "total": result['public_facilities'],
                "subcategories": {
                    "primary": result['primary_facilities'],
                    "secondary": result['secondary_facilities'],
                    "tertiary": result['tertiary_facilities']
                }
            },
            "private_pharmacies": result['private_pharmacies'],
            "ngo_faith": result['ngo_facilities'],
            "private_hospitals": result['private_hospitals'],
            "other": result['other_facilities']
        }
    }
    
    # Validate before returning
    validate_facility_stats(stats)
    
    return stats
```

### Component Update Function
```python
def update_tree_component(filters):
    """
    Update tree component with fresh data
    
    Args:
        filters (dict): Current filter selections
    """
    
    # Fetch data
    stats = fetch_facility_statistics(filters)
    
    # Render tree with updated values
    render_statistics_tree(stats)
```

---

## Filter Change Event Handling

### Trigger Conditions
The tree component should refresh when any of these filters change:
1. Country selection changes
2. Region selection changes
3. Data Collection Period selection changes

### Implementation Pattern
```python
# In main Streamlit app

# Capture filter changes
selected_country = st.selectbox("Country", countries)
selected_region = st.selectbox("Region", regions)
selected_period = st.multiselect("Data Collection Period", periods)

# Build filter dict
filters = {
    'country': [selected_country] if selected_country else [],
    'region': [selected_region] if selected_region else [],
    'data_collection_period': selected_period
}

# Update tree when filters change
if filters['data_collection_period']:  # Only show if period selected
    update_tree_component(filters)
else:
    st.info("Select a Data Collection Period to view facility statistics")
```

---

## Loading and Error States

### Loading State
```python
def render_statistics_tree(stats):
    """Render tree with loading state"""
    
    with st.spinner("Loading facility statistics..."):
        try:
            # Fetch and render
            facility_stats = fetch_facility_statistics(filters)
            # ... render tree with stats
        except Exception as e:
            st.error(f"Error loading facility data: {str(e)}")
```

### Empty State
```python
if not filters.get('data_collection_period'):
    st.markdown("""
    <div style='text-align: center; padding: 40px; color: #757575;'>
        <p>No data to display. Please select a Data Collection Period above.</p>
    </div>
    """, unsafe_allow_html=True)
```

### Error State
```python
try:
    stats = fetch_facility_statistics(filters)
except DatabaseError as e:
    st.error("Unable to fetch facility data. Please try again later.")
    logger.error(f"Database error in facility stats: {e}")
except ValidationError as e:
    st.warning("Data validation failed. Some statistics may be inconsistent.")
    logger.warning(f"Validation error: {e}")
```

---

## Performance Optimization

### Caching Strategy
```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_facility_statistics(filters):
    """Cached version of data fetching"""
    # Implementation as above
    pass
```

### Query Optimization
1. **Indexes:** Ensure database has indexes on:
   - `form_case__case_id`
   - `Sector`
   - `Level of Care`
   - `country`
   - `region`
   - `data_collection_period`

2. **Query Execution Plan:** Analyze and optimize query execution plan for large datasets

---

## Testing Requirements

### Unit Tests
```python
def test_query_builder():
    """Test query builder with various filter combinations"""
    
    # Test with all filters
    filters = {
        'country': ['Tanzania'],
        'region': ['Dar es Salaam'],
        'data_collection_period': ['Y3/P1']
    }
    query = build_facility_query(filters)
    assert 'Tanzania' in query
    assert 'Dar es Salaam' in query
    
    # Test with no filters
    empty_filters = {}
    query = build_facility_query(empty_filters)
    assert 'WHERE 1=1' in query

def test_data_validation():
    """Test validation logic"""
    
    valid_stats = {
        'total': 100,
        'categories': {
            'public': {'total': 60, 'subcategories': {'primary': 30, 'secondary': 20, 'tertiary': 10}},
            'private_pharmacies': 20,
            'ngo_faith': 10,
            'private_hospitals': 8,
            'other': 2
        }
    }
    
    assert validate_facility_stats(valid_stats) == True
```

### Integration Tests
1. Test with production database connection
2. Verify query performance with large datasets
3. Test filter combinations
4. Verify data accuracy against known sample data

---

## Implementation Checklist

### Backend Integration
- [ ] Database connection configured
- [ ] Query builder function implemented
- [ ] Data fetching function created
- [ ] Data validation function implemented
- [ ] Error handling added
- [ ] Caching strategy implemented

### Query Implementation
- [ ] Total Facilities query tested
- [ ] Public Facilities query tested
- [ ] Primary Level query tested
- [ ] Secondary Level query tested
- [ ] Tertiary Level query tested
- [ ] Private Pharmacies query tested
- [ ] NGO/Faith query tested
- [ ] Private Hospitals query tested
- [ ] Other query tested

### Filter Integration
- [ ] Country filter applied correctly
- [ ] Region filter applied correctly
- [ ] Data Collection Period filter applied correctly
- [ ] Multiple filter combination tested
- [ ] Filter change triggers component update

### Data Display
- [ ] Component title updated to "Summary of facilities surveyed"
- [ ] Values populate in tree cards
- [ ] Numbers format correctly (with commas for large numbers)
- [ ] Zero values display properly
- [ ] Loading state shows during data fetch

### Validation & Testing
- [ ] Data validation rules implemented
- [ ] Unit tests written and passing
- [ ] Integration tests completed
- [ ] Performance benchmarked
- [ ] Error scenarios tested

---

## Success Criteria

1. **Data Accuracy:** All node values match database query results exactly
2. **Performance:** Component loads within 2 seconds with typical dataset
3. **Validation:** Sum of child nodes never exceeds parent node values
4. **Responsiveness:** Component updates immediately when filters change
5. **Error Handling:** Graceful degradation when queries fail
6. **User Experience:** Clear loading states and helpful error messages

---

## Next Steps After Plan 2.1 Completion

1. User acceptance testing with sample data
2. Performance optimization if needed
3. Proceed to Plan 3: Additional visualizations/components
4. Document database schema dependencies
5. Create data dictionary for `Sector` and `Level of Care` values
```