# Price Analysis Tab - Phase 4 Implementation Plan (Refined)

## Overview
This document provides a detailed implementation plan for Phase 4 of the Price Analysis tab. Phase 4 adds a new "Price - By Brand" visualization section that displays paginated tables showing price statistics (min, median, max) for different insulin brands, split into Human and Analogue categories. The implementation follows the existing architecture patterns established in Phase 1, Phase 2, and Phase 3.

## Phase 4 Scope
Phase 4 focuses on building brand-based price tables with pagination:
- "Price - By Brand" section header
- Region and Sector expandable checkbox filters (local to this section)
- Two side-by-side tables: Human Insulin Brands and Analogue Insulin Brands
- Each table shows: Brand Name, Facility Count, Min/Median/Max Price-Local
- Pagination controls for both tables (10 rows per page)
- Responsive to local Region/Sector filters

---

## 1. Section Structure

### 1.1 Section Header

**Location:** `app.py` - Inside `with tab2:` block, after Phase 3 ("Price - By INN" section)

**Condition:** Only display when at least one Data Collection Period is selected

**Implementation:**
```python
if st.session_state.selected_periods_price:
    # Phase 4: Price - By Brand Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>Price - By Brand</h3></div>', unsafe_allow_html=True)
```

**CSS:** Uses existing `.section-header` class (already defined in app.py)

---

## 2. Local Filter Controls (Region and Sector)

### 2.1 Two-Column Layout for Filters

**Location:** Immediately after section header

**Implementation Pattern:**
```python
    # Local filters for Brand price analysis
    st.markdown("<br>", unsafe_allow_html=True)
    col1_brand, col2_brand = st.columns(2)
```

### 2.2 Region Checkbox Filter (Column 1)

**Database Query:**
- **Table:** `adl_surveys_repeat`
- **Function:** Reuse existing `get_price_regions()`
- **Metric:** `COUNT(DISTINCT form_case__case_id)`
- **Filter:** `WHERE region IS NOT NULL AND region != 'NULL'`
- **Group By:** `region`
- **Sort:** `ORDER BY region DESC` (as specified in plan)
- **Additional Filters:** Apply selected countries and periods from global filters

**UI Pattern:** Expandable checkbox list (st.expander)

**Implementation:**
```python
with col1_brand:
    st.markdown("**Region**")
    with st.spinner("Loading regions..."):
        # Build global filters dict from session state
        global_filters_brand = {
            'data_collection_period': st.session_state.selected_periods_price,
            'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None
        }

        region_df_brand = get_price_regions(client, config.TABLES["surveys_repeat"], global_filters_brand)

        if region_df_brand is not None and not region_df_brand.empty:
            # Build region options with counts
            region_data_brand = []
            for _, row in region_df_brand.iterrows():
                region = row['region']
                count = row['facility_count']
                region_data_brand.append((region, count))

            total_regions_brand = len(region_data_brand)

            # Initialize checkboxes in session state
            for region, count in region_data_brand:
                checkbox_key = f"price_brand_region_{region}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

            # Count selected items
            selected_count_brand = sum(
                1 for region, _ in region_data_brand
                if st.session_state.get(f"price_brand_region_{region}", True)
            )
            excluded_count_brand = total_regions_brand - selected_count_brand

            # Create expander with selection summary
            with st.expander(
                f"Select Regions ({selected_count_brand}/{total_regions_brand} selected)",
                expanded=False
            ):
                if excluded_count_brand > 0:
                    st.caption(f"🚫 {excluded_count_brand} item{'s' if excluded_count_brand != 1 else ''} excluded")

                # Create checkboxes
                local_regions_brand = []
                for region, count in region_data_brand:
                    checkbox_key = f"price_brand_region_{region}"
                    is_checked = st.checkbox(
                        f"{region} ({count:,})",
                        value=st.session_state.get(checkbox_key, True),
                        key=checkbox_key
                    )
                    if is_checked:
                        local_regions_brand.append(region)
        else:
            local_regions_brand = []
            st.info("No region data available")
```

**Session State Keys:** `price_brand_region_{region_name}` (one per region, boolean)

### 2.3 Sector Checkbox Filter (Column 2)

**Database Query:**
- **Table:** `adl_surveys_repeat`
- **Function:** Reuse existing `get_price_sectors()`
- **Metric:** `COUNT(DISTINCT form_case__case_id)`
- **Filter:** Apply global filters + selected regions from local Region filter
- **Group By:** `sector`
- **Sort:** `ORDER BY sector DESC` (as specified in plan)

**UI Pattern:** Expandable checkbox list (st.expander)

**Implementation:**
```python
with col2_brand:
    st.markdown("**Sector**")
    with st.spinner("Loading sectors..."):
        sector_df_brand = get_price_sectors(client, config.TABLES["surveys_repeat"], global_filters_brand, local_regions_brand)

        if sector_df_brand is not None and not sector_df_brand.empty:
            # Build sector options with counts
            sector_data_brand = []
            for _, row in sector_df_brand.iterrows():
                sector = row['sector']
                count = row['facility_count']
                sector_data_brand.append((sector, count))

            total_sectors_brand = len(sector_data_brand)

            # Initialize checkboxes in session state
            for sector, count in sector_data_brand:
                checkbox_key = f"price_brand_sector_{sector}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

            # Count selected items
            selected_count_brand_sec = sum(
                1 for sector, _ in sector_data_brand
                if st.session_state.get(f"price_brand_sector_{sector}", True)
            )
            excluded_count_brand_sec = total_sectors_brand - selected_count_brand_sec

            # Create expander with selection summary
            with st.expander(
                f"Select Sectors ({selected_count_brand_sec}/{total_sectors_brand} selected)",
                expanded=False
            ):
                if excluded_count_brand_sec > 0:
                    st.caption(f"🚫 {excluded_count_brand_sec} item{'s' if excluded_count_brand_sec != 1 else ''} excluded")

                # Create checkboxes
                local_sectors_brand = []
                for sector, count in sector_data_brand:
                    checkbox_key = f"price_brand_sector_{sector}"
                    is_checked = st.checkbox(
                        f"{sector} ({count:,})",
                        value=st.session_state.get(checkbox_key, True),
                        key=checkbox_key
                    )
                    if is_checked:
                        local_sectors_brand.append(sector)
        else:
            local_sectors_brand = []
            st.info("No sector data available")
```

**Session State Keys:** `price_brand_sector_{sector_name}` (one per sector, boolean)

---

## 3. Tables: Human and Analogue Insulin Brands

### 3.1 Two-Column Layout for Tables

**Location:** After the Region/Sector filters

**Implementation:**
```python
    # Tables: Human and Analogue side by side
    st.markdown("<br>", unsafe_allow_html=True)
    col_human, col_analogue = st.columns(2)
```

### 3.2 Human Insulin Brands Table (Left Column)

**Table Specifications:**
- **Title:** "Human Insulin Brands"
- **Columns:**
  1. Insulin Brand (string)
  2. Facilities with Availability (n) (integer with comma formatting)
  3. Min Price-Local (float with 2 decimals, comma formatting)
  4. Median Price-Local (float with 2 decimals, comma formatting)
  5. Max Price-Local (float with 2 decimals, comma formatting)

**Data Source:**
- **Table:** `adl_surveys_repeat`
- **Function:** New function `get_price_by_brand_human()`
- **Sort:** ORDER BY facility_count DESC (most facilities first)
- **Pagination:** 10 rows per page

**Implementation:**
```python
with col_human:
    st.markdown("#### Human Insulin Brands")

    with st.spinner("Loading human insulin brands..."):
        # Prepare filters
        brand_filters_human = {
            'data_collection_period': st.session_state.selected_periods_price,
            'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None,
            'region': local_regions_brand if local_regions_brand else None,
            'sector': local_sectors_brand if local_sectors_brand else None
        }

        human_brands_df = get_price_by_brand_human(client, config.TABLES["surveys_repeat"], brand_filters_human)

        if human_brands_df is not None and not human_brands_df.empty:
            # Pagination setup
            ROWS_PER_PAGE = 10
            total_rows_human = len(human_brands_df)
            total_pages_human = (total_rows_human + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE

            # Initialize page number in session state
            if 'price_brand_human_page' not in st.session_state:
                st.session_state.price_brand_human_page = 1

            # Pagination controls
            col_prev_h, col_info_h, col_next_h = st.columns([1, 2, 1])

            with col_prev_h:
                if st.button("← Previous", key="human_prev", disabled=(st.session_state.price_brand_human_page == 1)):
                    st.session_state.price_brand_human_page -= 1
                    st.rerun()

            with col_info_h:
                st.markdown(f"<div style='text-align: center;'>Page {st.session_state.price_brand_human_page} of {total_pages_human}</div>", unsafe_allow_html=True)

            with col_next_h:
                if st.button("Next →", key="human_next", disabled=(st.session_state.price_brand_human_page == total_pages_human)):
                    st.session_state.price_brand_human_page += 1
                    st.rerun()

            # Calculate pagination slice
            start_idx = (st.session_state.price_brand_human_page - 1) * ROWS_PER_PAGE
            end_idx = min(start_idx + ROWS_PER_PAGE, total_rows_human)
            paginated_human_df = human_brands_df.iloc[start_idx:end_idx]

            # Format display dataframe
            display_human_df = paginated_human_df.copy()
            display_human_df.columns = ['Insulin Brand', 'Facilities (n)', 'Min Price-Local', 'Median Price-Local', 'Max Price-Local']

            # Format numeric columns
            display_human_df['Facilities (n)'] = display_human_df['Facilities (n)'].apply(lambda x: f"{int(x):,}")
            display_human_df['Min Price-Local'] = display_human_df['Min Price-Local'].apply(lambda x: f"{x:,.2f}")
            display_human_df['Median Price-Local'] = display_human_df['Median Price-Local'].apply(lambda x: f"{x:,.2f}")
            display_human_df['Max Price-Local'] = display_human_df['Max Price-Local'].apply(lambda x: f"{x:,.2f}")

            # Display table
            st.dataframe(
                display_human_df,
                use_container_width=True,
                hide_index=True
            )

            # Show total count
            st.caption(f"Showing {start_idx + 1}-{end_idx} of {total_rows_human} brands")
        else:
            st.info("No human insulin brand data available for the selected filters")
```

### 3.3 Analogue Insulin Brands Table (Right Column)

**Table Specifications:**
- **Title:** "Analogue Insulin Brands"
- **Columns:** Same as Human table
- **Data Source:**
  - **Table:** `adl_surveys_repeat`
  - **Function:** New function `get_price_by_brand_analogue()`
  - **Sort:** ORDER BY facility_count DESC
  - **Pagination:** 10 rows per page

**Implementation:**
```python
with col_analogue:
    st.markdown("#### Analogue Insulin Brands")

    with st.spinner("Loading analogue insulin brands..."):
        # Prepare filters
        brand_filters_analogue = {
            'data_collection_period': st.session_state.selected_periods_price,
            'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None,
            'region': local_regions_brand if local_regions_brand else None,
            'sector': local_sectors_brand if local_sectors_brand else None
        }

        analogue_brands_df = get_price_by_brand_analogue(client, config.TABLES["surveys_repeat"], brand_filters_analogue)

        if analogue_brands_df is not None and not analogue_brands_df.empty:
            # Pagination setup
            ROWS_PER_PAGE = 10
            total_rows_analogue = len(analogue_brands_df)
            total_pages_analogue = (total_rows_analogue + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE

            # Initialize page number in session state
            if 'price_brand_analogue_page' not in st.session_state:
                st.session_state.price_brand_analogue_page = 1

            # Pagination controls
            col_prev_a, col_info_a, col_next_a = st.columns([1, 2, 1])

            with col_prev_a:
                if st.button("← Previous", key="analogue_prev", disabled=(st.session_state.price_brand_analogue_page == 1)):
                    st.session_state.price_brand_analogue_page -= 1
                    st.rerun()

            with col_info_a:
                st.markdown(f"<div style='text-align: center;'>Page {st.session_state.price_brand_analogue_page} of {total_pages_analogue}</div>", unsafe_allow_html=True)

            with col_next_a:
                if st.button("Next →", key="analogue_next", disabled=(st.session_state.price_brand_analogue_page == total_pages_analogue)):
                    st.session_state.price_brand_analogue_page += 1
                    st.rerun()

            # Calculate pagination slice
            start_idx = (st.session_state.price_brand_analogue_page - 1) * ROWS_PER_PAGE
            end_idx = min(start_idx + ROWS_PER_PAGE, total_rows_analogue)
            paginated_analogue_df = analogue_brands_df.iloc[start_idx:end_idx]

            # Format display dataframe
            display_analogue_df = paginated_analogue_df.copy()
            display_analogue_df.columns = ['Insulin Brand', 'Facilities (n)', 'Min Price-Local', 'Median Price-Local', 'Max Price-Local']

            # Format numeric columns
            display_analogue_df['Facilities (n)'] = display_analogue_df['Facilities (n)'].apply(lambda x: f"{int(x):,}")
            display_analogue_df['Min Price-Local'] = display_analogue_df['Min Price-Local'].apply(lambda x: f"{x:,.2f}")
            display_analogue_df['Median Price-Local'] = display_analogue_df['Median Price-Local'].apply(lambda x: f"{x:,.2f}")
            display_analogue_df['Max Price-Local'] = display_analogue_df['Max Price-Local'].apply(lambda x: f"{x:,.2f}")

            # Display table
            st.dataframe(
                display_analogue_df,
                use_container_width=True,
                hide_index=True
            )

            # Show total count
            st.caption(f"Showing {start_idx + 1}-{end_idx} of {total_rows_analogue} brands")
        else:
            st.info("No analogue insulin brand data available for the selected filters")
```

---

## 4. Database Functions to Implement

### 4.1 Function Summary

Add to `database/bigquery_client.py`:

| Function Name | Purpose | Table | Returns |
|---------------|---------|-------|---------|
| `get_price_by_brand_human()` | Get price stats for human insulin brands | `adl_surveys_repeat` | brand, facility_count, min/median/max price-local |
| `get_price_by_brand_analogue()` | Get price stats for analogue insulin brands | `adl_surveys_repeat` | brand, facility_count, min/median/max price-local |

### 4.2 Function: get_price_by_brand_human()

```python
@st.cache_data(ttl=600)
def get_price_by_brand_human(_client, table_name, filters):
    """
    Get price statistics for human insulin brands.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        filters (dict): Filters (data_collection_period, country, region, sector)

    Returns:
        pandas DataFrame with columns:
            - insulin_brand (str)
            - facility_count (int)
            - min_price_local (float)
            - median_price_local (float)
            - max_price_local (float)
    """
    if not filters.get('data_collection_period'):
        return None

    # Build WHERE clause
    where_clauses = ["1=1"]

    # Add data collection period filter
    periods = filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if filters.get('country'):
        countries_str = "', '".join(filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add region filter (optional)
    if filters.get('region'):
        regions_str = "', '".join(filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add sector filter (optional)
    if filters.get('sector'):
        sectors_str = "', '".join(filters['sector'])
        where_clauses.append(f"sector IN ('{sectors_str}')")

    # Human insulin type filter
    where_clauses.append("insulin_type LIKE '%Human%'")

    # Insulin brand filters
    where_clauses.append("insulin_standard_price_local IS NOT NULL")
    where_clauses.append("insulin_brand IS NOT NULL")
    where_clauses.append("insulin_brand != '0'")
    where_clauses.append("insulin_brand != '---'")

    # Out-of-pocket payment filter
    where_clauses.append("(insulin_out_of_pocket = 'Yes' OR insulin_out_of_pocket = 'Some people pay out of pocket')")

    where_clause = " AND ".join(where_clauses)

    # Use the complex median calculation from the plan
    query = f"""
    SELECT
      insulin_brand,
      COUNT(DISTINCT form_case__case_id) as facility_count,
      MIN(insulin_standard_price_local) as min_price_local,
      CASE
        WHEN MOD(COUNT(insulin_price_local), 2) = 1 THEN APPROX_QUANTILES(insulin_price_local, 2)[OFFSET(1)]
        WHEN MOD(COUNT(insulin_price_local), 2) = 0 AND COUNT(insulin_price_local) >= 100 THEN APPROX_QUANTILES(insulin_price_local, 2)[OFFSET(1)]
        ELSE (APPROX_QUANTILES(insulin_price_local, 100)[OFFSET(49)] + APPROX_QUANTILES(insulin_price_local, 100)[OFFSET(51)]) / 2
      END as median_price_local,
      MAX(insulin_standard_price_local) as max_price_local
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_brand
    ORDER BY facility_count DESC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting price by brand (human): {str(e)}")
        return None
```

### 4.3 Function: get_price_by_brand_analogue()

```python
@st.cache_data(ttl=600)
def get_price_by_brand_analogue(_client, table_name, filters):
    """
    Get price statistics for analogue insulin brands.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        filters (dict): Filters (data_collection_period, country, region, sector)

    Returns:
        pandas DataFrame with columns:
            - insulin_brand (str)
            - facility_count (int)
            - min_price_local (float)
            - median_price_local (float)
            - max_price_local (float)
    """
    if not filters.get('data_collection_period'):
        return None

    # Build WHERE clause
    where_clauses = ["1=1"]

    # Add data collection period filter
    periods = filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if filters.get('country'):
        countries_str = "', '".join(filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add region filter (optional)
    if filters.get('region'):
        regions_str = "', '".join(filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add sector filter (optional)
    if filters.get('sector'):
        sectors_str = "', '".join(filters['sector'])
        where_clauses.append(f"sector IN ('{sectors_str}')")

    # Analogue insulin type filter
    where_clauses.append("insulin_type LIKE '%Analogue%'")

    # Insulin brand filters
    where_clauses.append("insulin_standard_price_local IS NOT NULL")
    where_clauses.append("insulin_brand IS NOT NULL")
    where_clauses.append("insulin_brand != '0'")
    where_clauses.append("insulin_brand != '---'")

    # Out-of-pocket payment filter
    where_clauses.append("(insulin_out_of_pocket = 'Yes' OR insulin_out_of_pocket = 'Some people pay out of pocket')")

    where_clause = " AND ".join(where_clauses)

    # Use the complex median calculation from the plan
    query = f"""
    SELECT
      insulin_brand,
      COUNT(DISTINCT form_case__case_id) as facility_count,
      MIN(insulin_standard_price_local) as min_price_local,
      CASE
        WHEN MOD(COUNT(insulin_price_local), 2) = 1 THEN APPROX_QUANTILES(insulin_price_local, 2)[OFFSET(1)]
        WHEN MOD(COUNT(insulin_price_local), 2) = 0 AND COUNT(insulin_price_local) >= 100 THEN APPROX_QUANTILES(insulin_price_local, 2)[OFFSET(1)]
        ELSE (APPROX_QUANTILES(insulin_price_local, 100)[OFFSET(49)] + APPROX_QUANTILES(insulin_price_local, 100)[OFFSET(51)]) / 2
      END as median_price_local,
      MAX(insulin_standard_price_local) as max_price_local
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_brand
    ORDER BY facility_count DESC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting price by brand (analogue): {str(e)}")
        return None
```

---

## 5. Code Organization

### 5.1 File Structure

```
/Users/waqas/HAI_demo/
├── app.py                          # Main application file
│   └── [After Phase 3] Tab 2: Price Analysis
│       ├── Phase 1: Global filters (existing)
│       ├── Phase 2: Median price charts (existing)
│       ├── Phase 3: Price by INN (existing)
│       └── Phase 4: Price by Brand (new)
│           ├── Section header
│           ├── Local Region/Sector filters
│           ├── Two tables (Human and Analogue)
│           └── Pagination controls for each table
├── database/
│   └── bigquery_client.py         # Add 2 new functions
│       ├── get_price_by_brand_human()
│       └── get_price_by_brand_analogue()
├── plans/
│   ├── Price_Analysis_plan4.md    # Original plan
│   └── Price_Analysis_plan4_refined.md  # This document
```

### 5.2 Import Updates

Add to `app.py` imports (around line 10-54):

```python
from database.bigquery_client import (
    # ... existing imports ...
    get_price_by_brand_human,
    get_price_by_brand_analogue
)
```

---

## 6. Implementation Steps

### Step 1: Add Database Functions (30 minutes)
- Add `get_price_by_brand_human()` function to `database/bigquery_client.py`
- Add `get_price_by_brand_analogue()` function to `database/bigquery_client.py`
- Test queries with sample filters in BigQuery console
- Verify brand filtering and median calculation
- Ensure proper sorting by facility count

### Step 2: Update Imports (5 minutes)
- Add new function imports to `app.py`
- Run syntax check

### Step 3: Add Section Header (5 minutes)
- Add conditional wrapper for selected periods
- Add section header after Phase 3 (Price By INN)
- Test display when periods selected/unselected

### Step 4: Build Region/Sector Filters (25 minutes)
- Create two-column layout with unique variable names (`col1_brand`, `col2_brand`)
- Implement Region checkbox expander (reuse Phase 3 pattern)
- Implement Sector checkbox expander (reuse Phase 3 pattern)
- Use unique session state keys (`price_brand_region_*`, `price_brand_sector_*`)
- Test filter interactions and session state

### Step 5: Build Human Brands Table (40 minutes)
- Create left column layout
- Implement data fetching with filters
- Build pagination controls with session state
- Format table columns with proper number formatting
- Add pagination controls (Previous/Next buttons)
- Display page info (Page X of Y)
- Add total count caption
- Test pagination and filter interactions

### Step 6: Build Analogue Brands Table (40 minutes)
- Create right column layout
- Implement data fetching with filters (separate from Human)
- Build independent pagination controls
- Format table columns identically to Human table
- Add pagination controls (Previous/Next buttons with unique keys)
- Display page info
- Add total count caption
- Test pagination independently

### Step 7: Testing & Validation (30 minutes)
- Run syntax check
- Manual testing of all features
- Cross-filter testing (global + local filters)
- Pagination testing (both tables independently)
- Edge case testing (no data, single page, empty filters)
- Verify brand filtering (Human vs Analogue)

**Total Estimated Time:** ~3 hours

---

## 7. Testing Strategy

### 7.1 Manual Testing Checklist

**Section Display:**
- [ ] Section only shows when at least one period is selected
- [ ] Section hides when no periods selected
- [ ] Section header displays correctly
- [ ] Section appears after Phase 3 (Price By INN)

**Filter Functionality:**
- [ ] Region checkboxes load with facility counts
- [ ] Sector checkboxes load with facility counts
- [ ] Region filter affects sector options
- [ ] Expander shows correct selection count (N/M selected)
- [ ] Excluded count displays when items unchecked
- [ ] Checkboxes persist state across reruns
- [ ] All regions/sectors selected by default on first load
- [ ] Filters are independent from Phase 2 and Phase 3 filters

**Human Brands Table:**
- [ ] Table displays with 5 columns
- [ ] Brands are sorted by facility count (descending)
- [ ] Only human insulin brands shown
- [ ] Facility counts formatted with commas
- [ ] Price values formatted with 2 decimals and commas
- [ ] Pagination controls display when > 10 brands
- [ ] Previous button disabled on page 1
- [ ] Next button disabled on last page
- [ ] Page info shows current/total pages
- [ ] Caption shows row range (X-Y of Z)
- [ ] Table responds to filter changes
- [ ] Pagination resets when filters change

**Analogue Brands Table:**
- [ ] Table displays with 5 columns
- [ ] Brands are sorted by facility count (descending)
- [ ] Only analogue insulin brands shown
- [ ] Facility counts formatted with commas
- [ ] Price values formatted with 2 decimals and commas
- [ ] Pagination works independently from Human table
- [ ] Previous button disabled on page 1
- [ ] Next button disabled on last page
- [ ] Page info shows current/total pages
- [ ] Caption shows row range (X-Y of Z)
- [ ] Table responds to filter changes
- [ ] Pagination resets when filters change

**Data Integrity:**
- [ ] Human table only shows brands with insulin_type LIKE '%Human%'
- [ ] Analogue table only shows brands with insulin_type LIKE '%Analogue%'
- [ ] No NULL or "0" or "---" brand names displayed
- [ ] Facility counts are positive integers
- [ ] Min <= Median <= Max for each brand
- [ ] Out-of-pocket filter applied correctly
- [ ] Price values are non-negative

**Pagination:**
- [ ] Both tables paginate independently
- [ ] Page state persists when switching between other tabs
- [ ] Pagination resets to page 1 when filters change
- [ ] Buttons have unique keys (no conflicts)
- [ ] Page numbers update correctly

### 7.2 Test Execution Commands

**Syntax Check:**
```bash
python3 -m py_compile app.py
python3 -m py_compile database/bigquery_client.py
```

**Run Application:**
```bash
streamlit run app.py
```

**Test Sequence:**
1. Navigate to Price Analysis tab
2. Select at least one Data Collection Period
3. Scroll to "Price - By Brand" section
4. Verify section appears after "Price - By INN"
5. Test Region checkbox filter
6. Test Sector checkbox filter (depends on Region)
7. Verify both tables display side by side
8. Verify Human table shows only human insulin brands
9. Verify Analogue table shows only analogue insulin brands
10. Test pagination on Human table (if > 10 brands)
11. Test pagination on Analogue table (if > 10 brands)
12. Verify both paginations work independently
13. Change filters and verify tables update
14. Verify pagination resets to page 1 on filter change
15. Uncheck all regions - verify info messages
16. Deselect all periods - verify section hides

---

## 8. Key Design Decisions

### 8.1 Two Separate Functions vs Single Function
**Decision:** Create two separate functions (`get_price_by_brand_human()` and `get_price_by_brand_analogue()`)

**Rationale:**
- Clear separation of concerns
- Easier to maintain and debug
- Follows existing pattern in codebase
- Allows independent caching
- More flexible for future enhancements

### 8.2 Median Calculation Approach
**Decision:** Use the complex CASE-based median calculation from the original plan

**Rationale:**
- Specified in original plan requirements
- Handles different data sizes appropriately
- Odd vs even count logic
- Uses APPROX_QUANTILES for large datasets
- More accurate for edge cases

### 8.3 Pagination Implementation
**Decision:** Client-side pagination with session state

**Rationale:**
- Fetches all data once (cached for 10 minutes)
- Fast page switching without database queries
- Simple implementation using DataFrame slicing
- Consistent with Streamlit best practices
- Independent pagination state for each table

### 8.4 Table Display Format
**Decision:** Use `st.dataframe()` with formatted strings

**Rationale:**
- Native Streamlit component
- Responsive design
- Supports scrolling within container
- Easy to format with comma separators and decimals
- Clean professional appearance

### 8.5 Sort Order
**Decision:** Sort by facility count descending (most facilities first)

**Rationale:**
- Shows most widely available brands first
- Aligns with business priority
- Consistent with availability analysis patterns
- More relevant for policy decisions

### 8.6 Filter Independence
**Decision:** Brand section has its own Region/Sector filters

**Rationale:**
- Allows independent analysis
- Follows pattern from Phase 2 and Phase 3
- Prevents unintended filter interactions
- Better user experience for focused brand analysis

### 8.7 Column Names
**Decision:** Use "Facilities (n)" instead of "Facility with Availability (n)"

**Rationale:**
- More concise
- Clear meaning
- Fits better in column header
- (n) indicates count notation

---

## 9. Session State Architecture

### 9.1 New Session State Keys (Phase 4)

**Checkbox States (Dynamic - one per region/sector):**
```python
# Region checkboxes (Brand section)
st.session_state.price_brand_region_{region_name}  # bool - one per region

# Sector checkboxes (Brand section)
st.session_state.price_brand_sector_{sector_name}  # bool - one per sector
```

**Pagination States:**
```python
st.session_state.price_brand_human_page    # int - current page for Human table (default: 1)
st.session_state.price_brand_analogue_page # int - current page for Analogue table (default: 1)
```

**Example:**
```python
st.session_state.price_brand_region_East_Africa = True
st.session_state.price_brand_sector_Public = True
st.session_state.price_brand_human_page = 2
st.session_state.price_brand_analogue_page = 1
```

### 9.2 Existing Session State Keys (Not Modified)
```python
# Phase 1 - Global filters
st.session_state.selected_countries_price  # List[str]
st.session_state.selected_periods_price    # List[str]

# Phase 2 - Local filters
st.session_state.price_region_{region_name}
st.session_state.price_sector_{sector_name}

# Phase 3 - INN local filters
st.session_state.price_inn_region_{region_name}
st.session_state.price_inn_sector_{sector_name}
```

---

## 10. Potential Issues & Solutions

### Issue 1: Large Number of Brands
**Symptom:** Hundreds of brands causing many pages
**Solution:**
- 10 rows per page is appropriate
- Consider adding search/filter by brand name in future
- Show total count to set expectations
- Ensure pagination is performant

### Issue 2: Missing Brands in One Category
**Symptom:** Human or Analogue table has no data
**Solution:**
- Display info message when no data available
- Filter combinations may exclude all brands
- This is expected behavior
- User can adjust filters

### Issue 3: Pagination State Persistence
**Symptom:** Page number persists even when filter changes show different data
**Solution:**
- Consider resetting pagination to page 1 when filters change
- Add logic to check if current page > new total pages
- Use `st.rerun()` to refresh display

### Issue 4: Query Performance
**Symptom:** Slow query execution with complex median calculation
**Solution:**
- Use caching (@st.cache_data with ttl=600)
- Median calculation is complex but necessary per spec
- BigQuery optimized for this type of aggregation
- Monitor query execution time in logs

### Issue 5: Table Formatting Issues
**Symptom:** Numbers not aligned or formatted inconsistently
**Solution:**
- Use `.apply()` with lambda for consistent formatting
- Test with various data ranges (small/large numbers)
- Ensure comma separators work for thousands
- Verify decimal places (2 for prices, 0 for counts)

---

## 11. Acceptance Criteria

Phase 4 implementation is complete when:

- [ ] **AC1:** Section header "Price - By Brand" displays after "Price - By INN"
- [ ] **AC2:** Section only shows when at least one period is selected
- [ ] **AC3:** Region checkbox filter loads with facility counts (independent from other phases)
- [ ] **AC4:** Sector checkbox filter loads with facility counts (independent from other phases)
- [ ] **AC5:** Sector filter options update when Region filter changes
- [ ] **AC6:** Expanders show selection count "N/M selected"
- [ ] **AC7:** Expanders show excluded count when items unchecked
- [ ] **AC8:** All checkboxes selected by default on first load
- [ ] **AC9:** Two tables display side by side
- [ ] **AC10:** Human table shows only human insulin brands
- [ ] **AC11:** Analogue table shows only analogue insulin brands
- [ ] **AC12:** Both tables have 5 columns with correct headers
- [ ] **AC13:** Brands sorted by facility count (descending)
- [ ] **AC14:** Facility counts formatted with commas
- [ ] **AC15:** Price values formatted with 2 decimals and commas
- [ ] **AC16:** Pagination controls display when more than 10 brands
- [ ] **AC17:** Previous button disabled on first page
- [ ] **AC18:** Next button disabled on last page
- [ ] **AC19:** Page info displays "Page X of Y"
- [ ] **AC20:** Row count caption shows "Showing X-Y of Z brands"
- [ ] **AC21:** Both tables paginate independently
- [ ] **AC22:** Tables respond to filter changes
- [ ] **AC23:** Info message displays when no data available
- [ ] **AC24:** No errors in console or BigQuery logs
- [ ] **AC25:** Both files pass syntax check

---

## 12. Color Palette Reference

### UI Colors (Existing)
- **Primary Blue:** `#1f77b4`
- **Secondary Orange:** `#ff7f0e`
- **Background Light:** `#f8f9fa`
- **Info Box Background:** `#e3f2fd`
- **Info Box Border:** `#2196f3`

---

## 13. Dependencies

### Required Packages (Already Installed)
- `streamlit` - UI framework
- `pandas` - Data manipulation
- `google-cloud-bigquery` - BigQuery client

### Required Files
- `app.py` - Main application (modify)
- `database/bigquery_client.py` - Database functions (add 2 new functions)
- `config.py` - Configuration settings (no changes)
- `.env` - Environment variables (no changes)

### BigQuery Requirements
- **Project:** `hai-dev`
- **Dataset:** `facilities`
- **Tables:**
  - `adl_surveys_repeat` (for brand price data and filters)

**Columns needed in adl_surveys_repeat:**
- `form_case__case_id` (STRING)
- `data_collection_period` (STRING)
- `country` (STRING)
- `region` (STRING)
- `sector` (STRING)
- `insulin_type` (STRING) - Contains "Human" or "Analogue"
- `insulin_brand` (STRING) - Brand name
- `insulin_standard_price_local` (FLOAT64) - Price in local currency
- `insulin_price_local` (FLOAT64) - For median calculation
- `insulin_out_of_pocket` (STRING) - Out-of-pocket payment indicator

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-09 | AI Assistant | Initial refined plan from Price_Analysis_plan4.md |

---

**End of Refined Implementation Plan - Phase 4**
