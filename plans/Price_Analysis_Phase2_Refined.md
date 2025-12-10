# Price Analysis Tab - Phase 2 Implementation Plan (Refined)

## Overview
This document provides a detailed implementation plan for Phase 2 of the Price Analysis tab. Phase 2 adds price visualization features including median price charts by insulin type and level of care. The implementation follows the existing architecture patterns established in Phase 1 and the Availability Analysis tab.

## Phase 2 Scope
Phase 2 focuses on building the first set of price visualizations:
- "Where patients were charged the full price" section header
- Informational paragraph about price standardization
- Region and Sector expandable checkbox filters (local to this section)
- Two clustered bar charts:
  1. Median price by insulin type
  2. Median price by insulin type and level of care (public sector only)
- Optional metrics toggle (Local currency / USD / Product count)

---

## 1. Section Structure

### 1.1 Section Header and Information

**Location:** `app.py` - Inside `with tab2:` block, after the default state message (after line ~2724)

**Condition:** Only display when at least one Data Collection Period is selected

**Implementation:**
```python
if st.session_state.selected_periods_price:
    # Section: Where patients were charged the full price
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>Where patients were charged the full price</h3></div>', unsafe_allow_html=True)

    # Information paragraph
    st.markdown("""
    Insulin price is standardised in all cases to 1000IU. Click on the optional metrics button
    to see the number of products that make up the median price.
    """)
```

**CSS:** Uses existing `.section-header` class (already defined in app.py)

---

## 2. Local Filter Controls (Region and Sector)

### 2.1 Two-Column Layout for Filters

**Location:** Immediately after information paragraph

**Implementation Pattern:**
```python
    # Local filters for price analysis
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
```

### 2.2 Region Checkbox Filter (Column 1)

**Database Query:**
- **Table:** `adl_surveys`
- **Function:** New function `get_price_regions()`
- **Metric:** `COUNT(DISTINCT form_case__case_id)`
- **Filter:** `WHERE region IS NOT NULL AND region != 'NULL'`
- **Group By:** `region`
- **Sort:** `ORDER BY region DESC`
- **Additional Filters:** Apply selected countries and periods from global filters

**UI Pattern:** Expandable checkbox list (st.expander)

**Implementation:**
```python
with col1:
    st.markdown("**Region**")
    with st.spinner("Loading regions..."):
        # Build global filters dict from session state
        global_filters_price = {
            'data_collection_period': st.session_state.selected_periods_price,
            'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None
        }

        region_df = get_price_regions(client, TABLE_NAME, global_filters_price)

        if region_df is not None and not region_df.empty:
            # Build region options with counts
            region_data = []
            for _, row in region_df.iterrows():
                region = row['region']
                count = row['facility_count']
                region_data.append((region, count))

            total_regions = len(region_data)

            # Initialize checkboxes in session state
            for region, count in region_data:
                checkbox_key = f"price_region_{region}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

            # Count selected items
            selected_count = sum(
                1 for region, _ in region_data
                if st.session_state.get(f"price_region_{region}", True)
            )
            excluded_count = total_regions - selected_count

            # Create expander with selection summary
            with st.expander(
                f"Select Regions ({selected_count}/{total_regions} selected)",
                expanded=False
            ):
                if excluded_count > 0:
                    st.caption(f"🚫 {excluded_count} item{'s' if excluded_count != 1 else ''} excluded")

                # Create checkboxes
                local_regions_price = []
                for region, count in region_data:
                    checkbox_key = f"price_region_{region}"
                    is_checked = st.checkbox(
                        f"{region} ({count:,})",
                        value=st.session_state.get(checkbox_key, True),
                        key=checkbox_key
                    )
                    if is_checked:
                        local_regions_price.append(region)
        else:
            local_regions_price = []
            st.info("No region data available")
```

**Session State Keys:** `price_region_{region_name}` (one per region, boolean)

### 2.3 Sector Checkbox Filter (Column 2)

**Database Query:**
- **Table:** `adl_surveys`
- **Function:** New function `get_price_sectors()`
- **Metric:** `COUNT(DISTINCT form_case__case_id)`
- **Filter:** Apply global filters + selected regions from local Region filter
- **Group By:** `sector`
- **Sort:** `ORDER BY sector DESC`

**UI Pattern:** Expandable checkbox list (st.expander)

**Implementation:**
```python
with col2:
    st.markdown("**Sector**")
    with st.spinner("Loading sectors..."):
        sector_df = get_price_sectors(client, TABLE_NAME, global_filters_price, local_regions_price)

        if sector_df is not None and not sector_df.empty:
            # Build sector options with counts
            sector_data = []
            for _, row in sector_df.iterrows():
                sector = row['sector']
                count = row['facility_count']
                sector_data.append((sector, count))

            total_sectors = len(sector_data)

            # Initialize checkboxes in session state
            for sector, count in sector_data:
                checkbox_key = f"price_sector_{sector}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

            # Count selected items
            selected_count = sum(
                1 for sector, _ in sector_data
                if st.session_state.get(f"price_sector_{sector}", True)
            )
            excluded_count = total_sectors - selected_count

            # Create expander with selection summary
            with st.expander(
                f"Select Sectors ({selected_count}/{total_sectors} selected)",
                expanded=False
            ):
                if excluded_count > 0:
                    st.caption(f"🚫 {excluded_count} item{'s' if excluded_count != 1 else ''} excluded")

                # Create checkboxes
                local_sectors_price = []
                for sector, count in sector_data:
                    checkbox_key = f"price_sector_{sector}"
                    is_checked = st.checkbox(
                        f"{sector} ({count:,})",
                        value=st.session_state.get(checkbox_key, True),
                        key=checkbox_key
                    )
                    if is_checked:
                        local_sectors_price.append(sector)
        else:
            local_sectors_price = []
            st.info("No sector data available")
```

**Session State Keys:** `price_sector_{sector_name}` (one per sector, boolean)

---

## 3. Chart 1: Median Price by Insulin Type

### 3.1 Section Header

**Location:** After the Region/Sector filters

**Implementation:**
```python
    # Chart 1: Median price by insulin type
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Median price - By insulin type")
```

### 3.2 Chart Specifications

**Chart Type:** Clustered Bar Chart (Plotly Graph Objects)

**Data Source:**
- **Table:** `adl_surveys_repeat`
- **Function:** New function `get_median_price_by_type()`

**Axes:**
- **X-axis:** Insulin Type (7 categories)
- **Y-axis:** Median Price - Local (range: 0 to 6000)

**Categories (7 insulin types):**
1. Short-Acting Human
2. Intermediate-Acting Human
3. Mixed Human
4. Long-Acting Analogue
5. Rapid-Acting Analogue
6. Mixed Analogue
7. Intermediate-Acting Animal

**Visual Properties:**
- **Bar Color:** Teal/Dark Blue (`#17becf` or `#1f77b4`)
- **Text on Bars:** Display median price value
- **X-axis Labels:** Rotated -45° if needed for readability
- **Legend:** "Median Price - Local" (shown by default)

**Optional Metrics:**
- Metric 1: Median Price - Local (default, shown)
- Metric 2: Median Price - USD (optional)
- Metric 3: Product Count (optional)

### 3.3 Implementation Pattern

```python
    with st.spinner("Loading median price data..."):
        # Prepare filters
        price_filters = {
            'data_collection_period': st.session_state.selected_periods_price,
            'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None,
            'region': local_regions_price if local_regions_price else None,
            'sector': local_sectors_price if local_sectors_price else None
        }

        chart_df = get_median_price_by_type(client, config.TABLES["surveys_repeat"], price_filters)

        if chart_df is not None and not chart_df.empty:
            # Create Plotly bar chart
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=chart_df['insulin_type'].tolist(),
                y=chart_df['median_price_local'].tolist(),
                name='Median Price - Local',
                marker_color='#17becf',
                text=[f'{val:,.0f}' for val in chart_df['median_price_local'].tolist()],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>' +
                              'Median Price: %{y:,.2f}<br>' +
                              'Products: %{customdata}<extra></extra>',
                customdata=chart_df['product_count'].tolist()
            ))

            # Update layout
            fig.update_layout(
                title='Median Price by Insulin Type',
                xaxis_title='Insulin Type',
                yaxis_title='Median Price - Local',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=500,
                yaxis=dict(
                    range=[0, 6000],
                    tickformat=',.0f'
                ),
                xaxis_tickangle=-45,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(t=80, b=120, l=60, r=40)
            )

            # Display chart
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No median price data available for the selected filters")
```

### 3.4 Database Query Specification

**Function Name:** `get_median_price_by_type(_client, table_name, filters)`

**Query Structure:**
```sql
SELECT
    insulin_type,
    insulin_type_order,
    PERCENTILE_CONT(insulin_standard_price_local, 0.5) OVER() as median_price_local,
    PERCENTILE_CONT(insulin_standard_price_usd, 0.5) OVER() as median_price_usd,
    COUNT(1) as product_count
FROM `{project}.{dataset}.{table_name}`
WHERE
    insulin_type IS NOT NULL
    AND insulin_type != '---'
    AND (
        insulin_out_of_pocket = 'Yes'
        OR insulin_out_of_pocket = 'Some people pay out of pocket'
    )
    AND data_collection_period IN (...)  -- from filters
    -- Additional filters for country, region, sector
GROUP BY insulin_type, insulin_type_order
ORDER BY insulin_type_order ASC
```

**Returns:** DataFrame with columns:
- `insulin_type` (str)
- `insulin_type_order` (int)
- `median_price_local` (float)
- `median_price_usd` (float)
- `product_count` (int)

---

## 4. Chart 2: Median Price by Type and Level of Care

### 4.1 Section Header

**Location:** After Chart 1

**Implementation:**
```python
    # Chart 2: Median price by insulin type and level of care
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Median price - By insulin type and level of care (public sector only)")
```

### 4.2 Chart Specifications

**Chart Type:** Grouped/Clustered Bar Chart (Plotly Graph Objects)

**Data Source:**
- **Table:** `adl_surveys_repeat`
- **Function:** New function `get_median_price_by_type_levelcare()`

**Axes:**
- **X-axis:** Insulin Type (same 7 categories)
- **Y-axis:** Median Price - Local (range: 0 to 6000)

**Grouping:** Level of Care
- **Secondary** (one bar per insulin type)
- **Tertiary** (one bar per insulin type)

**Visual Properties:**
- **Bar Colors:**
  - Secondary: `#1f77b4` (blue)
  - Tertiary: `#ff7f0e` (orange)
- **Text on Bars:** Display median price value
- **X-axis Labels:** Rotated -45°
- **Legend:** Show "Secondary" and "Tertiary" labels
- **Grouping Mode:** `group` (bars side-by-side)

**Filters Applied:**
- Public sector only (sector CONTAINS "Public")
- Exclude NULL and "---" level_of_care values
- Out-of-pocket payment (same as Chart 1)

### 4.3 Implementation Pattern

```python
    with st.spinner("Loading median price by level of care data..."):
        chart_df = get_median_price_by_type_levelcare(client, config.TABLES["surveys_repeat"], price_filters)

        if chart_df is not None and not chart_df.empty:
            # Separate data by level of care
            secondary_df = chart_df[chart_df['level_of_care'] == 'Secondary']
            tertiary_df = chart_df[chart_df['level_of_care'] == 'Tertiary']

            # Create Plotly grouped bar chart
            fig = go.Figure()

            # Add Secondary bar trace
            if not secondary_df.empty:
                fig.add_trace(go.Bar(
                    x=secondary_df['insulin_type'].tolist(),
                    y=secondary_df['median_price_local'].tolist(),
                    name='Secondary',
                    marker_color='#1f77b4',
                    text=[f'{val:,.0f}' for val in secondary_df['median_price_local'].tolist()],
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>' +
                                  'Level: Secondary<br>' +
                                  'Median Price: %{y:,.2f}<br>' +
                                  'Products: %{customdata}<extra></extra>',
                    customdata=secondary_df['product_count'].tolist()
                ))

            # Add Tertiary bar trace
            if not tertiary_df.empty:
                fig.add_trace(go.Bar(
                    x=tertiary_df['insulin_type'].tolist(),
                    y=tertiary_df['median_price_local'].tolist(),
                    name='Tertiary',
                    marker_color='#ff7f0e',
                    text=[f'{val:,.0f}' for val in tertiary_df['median_price_local'].tolist()],
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>' +
                                  'Level: Tertiary<br>' +
                                  'Median Price: %{y:,.2f}<br>' +
                                  'Products: %{customdata}<extra></extra>',
                    customdata=tertiary_df['product_count'].tolist()
                ))

            # Update layout
            fig.update_layout(
                title='Median Price by Insulin Type and Level of Care (Public Sector)',
                xaxis_title='Insulin Type',
                yaxis_title='Median Price - Local',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=500,
                yaxis=dict(
                    range=[0, 6000],
                    tickformat=',.0f'
                ),
                xaxis_tickangle=-45,
                barmode='group',  # Grouped bars side-by-side
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(t=80, b=120, l=60, r=40)
            )

            # Display chart
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No median price data available for public sector level of care")
```

### 4.4 Database Query Specification

**Function Name:** `get_median_price_by_type_levelcare(_client, table_name, filters)`

**Query Structure:**
```sql
SELECT
    insulin_type,
    insulin_type_order,
    level_of_care,
    PERCENTILE_CONT(insulin_standard_price_local, 0.5) OVER(PARTITION BY insulin_type, level_of_care) as median_price_local,
    PERCENTILE_CONT(insulin_standard_price_usd, 0.5) OVER(PARTITION BY insulin_type, level_of_care) as median_price_usd,
    COUNT(1) as product_count
FROM `{project}.{dataset}.{table_name}`
WHERE
    insulin_type IS NOT NULL
    AND insulin_type != '---'
    AND sector LIKE '%Public%'
    AND level_of_care IS NOT NULL
    AND level_of_care != 'NULL'
    AND level_of_care != '---'
    AND (
        insulin_out_of_pocket = 'Yes'
        OR insulin_out_of_pocket = 'Some people pay out of pocket'
    )
    AND data_collection_period IN (...)  -- from filters
    -- Additional filters for country, region
GROUP BY insulin_type, insulin_type_order, level_of_care
ORDER BY insulin_type_order ASC, level_of_care ASC
```

**Returns:** DataFrame with columns:
- `insulin_type` (str)
- `insulin_type_order` (int)
- `level_of_care` (str)
- `median_price_local` (float)
- `median_price_usd` (float)
- `product_count` (int)

---

## 5. Database Functions to Implement

### 5.1 Function Summary

Add to `database/bigquery_client.py`:

| Function Name | Purpose | Table | Returns |
|---------------|---------|-------|---------|
| `get_price_regions()` | Get regions for price filter | `adl_surveys` | region, facility_count |
| `get_price_sectors()` | Get sectors for price filter | `adl_surveys` | sector, facility_count |
| `get_median_price_by_type()` | Chart 1 data | `adl_surveys_repeat` | insulin_type, median_price_local, median_price_usd, product_count |
| `get_median_price_by_type_levelcare()` | Chart 2 data | `adl_surveys_repeat` | insulin_type, level_of_care, median_price_local, median_price_usd, product_count |

### 5.2 Function 1: get_price_regions()

```python
@st.cache_data(ttl=600)
def get_price_regions(_client, table_name, global_filters):
    """
    Get regions for price analysis filter with facility counts.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys)
        global_filters (dict): Global filters (data_collection_period, country)

    Returns:
        pandas DataFrame with columns: region, facility_count
    """
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause
    where_clauses = ["1=1"]

    # Add data collection period filter
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Exclude NULL regions
    where_clauses.append("region IS NOT NULL")
    where_clauses.append("region != 'NULL'")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        region,
        COUNT(DISTINCT form_case__case_id) as facility_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY region
    ORDER BY region DESC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting price regions: {str(e)}")
        return None
```

### 5.3 Function 2: get_price_sectors()

```python
@st.cache_data(ttl=600)
def get_price_sectors(_client, table_name, global_filters, local_regions):
    """
    Get sectors for price analysis filter with facility counts.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys)
        global_filters (dict): Global filters (data_collection_period, country)
        local_regions (list): Selected regions from local region filter

    Returns:
        pandas DataFrame with columns: sector, facility_count
    """
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause
    where_clauses = ["1=1"]

    # Add data collection period filter
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add local region filter (optional)
    if local_regions:
        regions_str = "', '".join(local_regions)
        where_clauses.append(f"region IN ('{regions_str}')")

    # Exclude NULL sectors
    where_clauses.append("sector IS NOT NULL")
    where_clauses.append("TRIM(sector) != ''")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        sector,
        COUNT(DISTINCT form_case__case_id) as facility_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY sector
    ORDER BY sector DESC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting price sectors: {str(e)}")
        return None
```

### 5.4 Function 3: get_median_price_by_type()

```python
@st.cache_data(ttl=600)
def get_median_price_by_type(_client, table_name, filters):
    """
    Get median insulin prices by insulin type for chart.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        filters (dict): Filters (data_collection_period, country, region, sector)

    Returns:
        pandas DataFrame with columns:
            - insulin_type (str)
            - insulin_type_order (int)
            - median_price_local (float)
            - median_price_usd (float)
            - product_count (int)
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

    # Insulin type filters
    where_clauses.append("insulin_type IS NOT NULL")
    where_clauses.append("insulin_type != '---'")

    # Out-of-pocket payment filter
    where_clauses.append("(insulin_out_of_pocket = 'Yes' OR insulin_out_of_pocket = 'Some people pay out of pocket')")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        insulin_type,
        insulin_type_order,
        APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(50)] as median_price_local,
        APPROX_QUANTILES(insulin_standard_price_usd, 100)[OFFSET(50)] as median_price_usd,
        COUNT(1) as product_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_type, insulin_type_order
    ORDER BY insulin_type_order ASC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting median price by type: {str(e)}")
        return None
```

### 5.5 Function 4: get_median_price_by_type_levelcare()

```python
@st.cache_data(ttl=600)
def get_median_price_by_type_levelcare(_client, table_name, filters):
    """
    Get median insulin prices by insulin type and level of care (public sector only).

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        filters (dict): Filters (data_collection_period, country, region)

    Returns:
        pandas DataFrame with columns:
            - insulin_type (str)
            - insulin_type_order (int)
            - level_of_care (str)
            - median_price_local (float)
            - median_price_usd (float)
            - product_count (int)
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

    # Public sector filter
    where_clauses.append("sector LIKE '%Public%'")

    # Insulin type filters
    where_clauses.append("insulin_type IS NOT NULL")
    where_clauses.append("insulin_type != '---'")

    # Level of care filters
    where_clauses.append("level_of_care IS NOT NULL")
    where_clauses.append("level_of_care != 'NULL'")
    where_clauses.append("level_of_care != '---'")

    # Out-of-pocket payment filter
    where_clauses.append("(insulin_out_of_pocket = 'Yes' OR insulin_out_of_pocket = 'Some people pay out of pocket')")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        insulin_type,
        insulin_type_order,
        level_of_care,
        APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(50)] as median_price_local,
        APPROX_QUANTILES(insulin_standard_price_usd, 100)[OFFSET(50)] as median_price_usd,
        COUNT(1) as product_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_type, insulin_type_order, level_of_care
    ORDER BY insulin_type_order ASC, level_of_care ASC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting median price by type and level of care: {str(e)}")
        return None
```

---

## 6. Code Organization

### 6.1 File Structure

```
/Users/waqas/HAI_demo/
├── app.py                          # Main application file
│   └── [Line ~2580-2724] Tab 2: Price Analysis
│       ├── Phase 1: Filters (existing)
│       └── Phase 2: Price visualizations (new)
│           ├── Section header
│           ├── Information paragraph
│           ├── Local Region/Sector filters
│           ├── Chart 1: Median price by type
│           └── Chart 2: Median price by type & level of care
├── database/
│   └── bigquery_client.py         # Add 4 new functions
│       ├── get_price_regions()
│       ├── get_price_sectors()
│       ├── get_median_price_by_type()
│       └── get_median_price_by_type_levelcare()
├── plans/
│   ├── Price_Analysis_plan2.md    # Original plan
│   └── Price_Analysis_Phase2_Refined.md  # This document
```

### 6.2 Import Updates

Add to `app.py` imports (around line 10-49):

```python
from database.bigquery_client import (
    # ... existing imports ...
    get_price_regions,
    get_price_sectors,
    get_median_price_by_type,
    get_median_price_by_type_levelcare
)
```

---

## 7. Implementation Steps

### Step 1: Add Database Functions (45 minutes)
- Add 4 new functions to `database/bigquery_client.py`
- Test each function independently with sample filters
- Verify query results in BigQuery console

### Step 2: Update Imports (5 minutes)
- Add new function imports to `app.py`
- Run syntax check

### Step 3: Add Section Header and Info (10 minutes)
- Add conditional wrapper for selected periods
- Add section header and information paragraph
- Test display when periods selected/unselected

### Step 4: Build Region/Sector Filters (30 minutes)
- Create two-column layout
- Implement Region checkbox expander
- Implement Sector checkbox expander
- Test filter interactions and session state

### Step 5: Build Chart 1 (30 minutes)
- Add section header
- Implement data fetching
- Create Plotly bar chart
- Add styling and formatting
- Test with various filter combinations

### Step 6: Build Chart 2 (30 minutes)
- Add section header
- Implement data fetching
- Create Plotly grouped bar chart
- Add styling for two level-of-care categories
- Test public sector filtering

### Step 7: Testing & Validation (30 minutes)
- Run syntax check
- Manual testing of all features
- Cross-filter testing (global + local filters)
- Edge case testing (no data, single category, etc.)

**Total Estimated Time:** ~3 hours

---

## 8. Testing Strategy

### 8.1 Manual Testing Checklist

**Section Display:**
- [ ] Section only shows when at least one period is selected
- [ ] Section hides when no periods selected
- [ ] Information paragraph displays correctly

**Filter Functionality:**
- [ ] Region checkboxes load with facility counts
- [ ] Sector checkboxes load with facility counts
- [ ] Region filter affects sector options
- [ ] Expander shows correct selection count (N/M selected)
- [ ] Excluded count displays when items unchecked
- [ ] Checkboxes persist state across reruns
- [ ] All regions selected by default on first load

**Chart 1 (Median Price by Type):**
- [ ] Chart displays with 7 insulin type categories
- [ ] Median prices shown on bars
- [ ] Y-axis range is 0-6000
- [ ] X-axis labels rotated -45°
- [ ] Teal/blue bar colors
- [ ] Legend shows "Median Price - Local"
- [ ] Hover tooltip shows price and product count
- [ ] Chart responds to filter changes

**Chart 2 (By Type & Level of Care):**
- [ ] Chart displays grouped bars (Secondary/Tertiary)
- [ ] Public sector filter applied correctly
- [ ] Two distinct bar colors (blue/orange)
- [ ] Both level-of-care categories shown in legend
- [ ] Bars grouped side-by-side correctly
- [ ] Y-axis range is 0-6000
- [ ] Chart responds to filter changes

**Data Integrity:**
- [ ] Queries execute without errors
- [ ] Median calculations are reasonable
- [ ] Product counts are positive integers
- [ ] No NULL insulin types displayed
- [ ] Out-of-pocket filter applied correctly
- [ ] Public sector filter applied in Chart 2 only

### 8.2 Test Execution Commands

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
3. Verify section appears
4. Test Region checkbox filter
5. Test Sector checkbox filter (depends on Region)
6. Verify Chart 1 displays
7. Verify Chart 2 displays
8. Change filters and verify charts update
9. Uncheck all regions - verify info message
10. Deselect all periods - verify section hides

### 8.3 Expected BigQuery Queries

**Region Filter Query:**
```sql
SELECT
    region,
    COUNT(DISTINCT form_case__case_id) as facility_count
FROM `hai-dev.facilities.adl_surveys`
WHERE
    data_collection_period IN (...)
    AND country IN (...)
    AND region IS NOT NULL
    AND region != 'NULL'
GROUP BY region
ORDER BY region DESC
```

**Chart 1 Query:**
```sql
SELECT
    insulin_type,
    insulin_type_order,
    APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(50)] as median_price_local,
    APPROX_QUANTILES(insulin_standard_price_usd, 100)[OFFSET(50)] as median_price_usd,
    COUNT(1) as product_count
FROM `hai-dev.facilities.adl_surveys_repeat`
WHERE
    insulin_type IS NOT NULL
    AND insulin_type != '---'
    AND (insulin_out_of_pocket = 'Yes' OR insulin_out_of_pocket = 'Some people pay out of pocket')
    AND data_collection_period IN (...)
    -- Additional filters
GROUP BY insulin_type, insulin_type_order
ORDER BY insulin_type_order ASC
```

**Chart 2 Query:**
```sql
SELECT
    insulin_type,
    insulin_type_order,
    level_of_care,
    APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(50)] as median_price_local,
    APPROX_QUANTILES(insulin_standard_price_usd, 100)[OFFSET(50)] as median_price_usd,
    COUNT(1) as product_count
FROM `hai-dev.facilities.adl_surveys_repeat`
WHERE
    insulin_type IS NOT NULL
    AND insulin_type != '---'
    AND sector LIKE '%Public%'
    AND level_of_care IS NOT NULL
    AND level_of_care != 'NULL'
    AND level_of_care != '---'
    AND (insulin_out_of_pocket = 'Yes' OR insulin_out_of_pocket = 'Some people pay out of pocket')
    AND data_collection_period IN (...)
    -- Additional filters
GROUP BY insulin_type, insulin_type_order, level_of_care
ORDER BY insulin_type_order ASC, level_of_care ASC
```

---

## 9. Key Design Decisions

### 9.1 Local vs Global Filters
**Decision:** Region and Sector filters are local to the price section (not shared with Phase 1 filters)

**Rationale:**
- Allows independent filtering for price analysis
- Matches pattern from Availability Analysis tab
- Prevents unintended filter interactions
- Users can set different criteria for price vs availability

### 9.2 Checkbox vs Multiselect
**Decision:** Use expandable checkbox lists (st.expander) for Region/Sector filters

**Rationale:**
- Consistent with Availability Analysis tab pattern
- Better UX for many options (collapsible)
- Shows selection summary in collapsed state
- Indicates excluded count
- All items selected by default (better initial UX)

### 9.3 Median vs Mean for Pricing
**Decision:** Use median (50th percentile) for price aggregation

**Rationale:**
- Less sensitive to outliers than mean
- Better represents "typical" price
- Matches requirement in original plan
- BigQuery `APPROX_QUANTILES()` is efficient for large datasets

### 9.4 Table Choice: adl_surveys_repeat
**Decision:** Use `adl_surveys_repeat` table for price data, not `adl_surveys`

**Rationale:**
- Contains repeat/insulin-specific data
- Has `insulin_standard_price_local` and `insulin_standard_price_usd` columns
- Has `insulin_type_order` for correct sorting
- Has `insulin_out_of_pocket` for filtering
- Matches requirement in original plan

### 9.5 Y-axis Fixed Range (0-6000)
**Decision:** Use fixed Y-axis range instead of auto-scaling

**Rationale:**
- Requirement from original plan
- Ensures consistency across filter changes
- Makes visual comparisons easier
- Prevents misleading scale distortions

### 9.6 Public Sector Only for Chart 2
**Decision:** Chart 2 only shows public sector data with level of care breakdown

**Rationale:**
- Requirement from original plan
- Level of care is most relevant in public sector
- Private sector may not have clear level-of-care distinctions
- Simplifies chart and focuses analysis

---

## 10. Potential Issues & Solutions

### Issue 1: No Data for Some Insulin Types
**Symptom:** Some of the 7 insulin types missing from chart
**Solution:**
- Display info message when data is sparse
- Consider showing "0" or hiding missing categories
- Add note in information paragraph

### Issue 2: Median Calculation Performance
**Symptom:** Slow query execution for median calculations
**Solution:**
- `APPROX_QUANTILES()` is already optimized for BigQuery
- Use caching (@st.cache_data with ttl=600)
- Consider pre-aggregated table if still slow

### Issue 3: Public Sector Filter Too Restrictive
**Symptom:** Chart 2 shows no data
**Solution:**
- Use `LIKE '%Public%'` to catch variations
- Verify sector naming conventions in data
- Add debugging to show applied filters

### Issue 4: Level of Care Labels Inconsistent
**Symptom:** Missing "Secondary" or "Tertiary" categories
**Solution:**
- Normalize level_of_care values in query (UPPER/TRIM)
- Check for alternative spellings
- Filter out NULL/'---' values

### Issue 5: Checkbox State Not Persisting
**Symptom:** Checkboxes reset on page refresh
**Solution:**
- Ensure unique session state keys (`price_region_{name}`)
- Initialize all checkboxes before rendering
- Use Streamlit's automatic key-based state management

---

## 11. Acceptance Criteria

Phase 2 implementation is complete when:

- [x] **AC1:** Section header "Where patients were charged the full price" displays
- [x] **AC2:** Information paragraph about price standardization displays
- [x] **AC3:** Section only shows when at least one period is selected
- [x] **AC4:** Region checkbox filter loads with facility counts
- [x] **AC5:** Sector checkbox filter loads with facility counts
- [x] **AC6:** Sector filter options update when Region filter changes
- [x] **AC7:** Expanders show selection count "N/M selected"
- [x] **AC8:** Expanders show excluded count when items unchecked
- [x] **AC9:** All checkboxes selected by default on first load
- [x] **AC10:** Chart 1 displays median price by insulin type (7 categories)
- [x] **AC11:** Chart 1 Y-axis range is 0-6000
- [x] **AC12:** Chart 1 bars are teal/dark blue color
- [x] **AC13:** Chart 1 shows median price values on bars
- [x] **AC14:** Chart 2 displays grouped bars by level of care (Secondary/Tertiary)
- [x] **AC15:** Chart 2 only shows public sector data
- [x] **AC16:** Chart 2 uses blue and orange colors for level-of-care groups
- [x] **AC17:** Both charts update when filters change
- [x] **AC18:** Hover tooltips show price and product count
- [x] **AC19:** No errors in console or BigQuery logs
- [x] **AC20:** Both files pass syntax check

---

## 12. Future Enhancements (Phase 3+)

### Optional Metrics Toggle
- Add button to switch between:
  - Median Price - Local (default)
  - Median Price - USD
  - Product Count
- Implementation: Use radio buttons or dropdown above charts
- Update chart data and Y-axis labels dynamically

### Additional Price Charts
- Median price by region (geographic map)
- Median price by sector (all sectors, not just public)
- Price distribution histograms
- Originator vs biosimilar price comparison
- Price by presentation type (vial/pen/cartridge)
- Price trends over time (if multiple periods selected)

### Export Functionality
- Download chart data as CSV
- Export charts as PNG images
- Generate price analysis reports

### Price Alert Thresholds
- Highlight unusually high prices
- Flag price outliers
- Compare against reference prices

---

## 13. Dependencies

### Required Packages (Already Installed)
- `streamlit` - UI framework
- `pandas` - Data manipulation
- `plotly` - Charts (plotly.graph_objects)
- `google-cloud-bigquery` - BigQuery client

### Required Files
- `app.py` - Main application (modify)
- `database/bigquery_client.py` - Database functions (add 4 new functions)
- `config.py` - Configuration settings (no changes)
- `.env` - Environment variables (no changes)

### BigQuery Requirements
- **Project:** `hai-dev`
- **Dataset:** `facilities`
- **Tables:**
  - `adl_surveys` (for Region/Sector filters)
  - `adl_surveys_repeat` (for price data)

**Columns needed in adl_surveys:**
- `form_case__case_id` (STRING)
- `data_collection_period` (STRING)
- `country` (STRING)
- `region` (STRING)
- `sector` (STRING)

**Columns needed in adl_surveys_repeat:**
- `data_collection_period` (STRING)
- `country` (STRING)
- `region` (STRING)
- `sector` (STRING)
- `insulin_type` (STRING)
- `insulin_type_order` (INT64)
- `insulin_standard_price_local` (FLOAT64)
- `insulin_standard_price_usd` (FLOAT64)
- `insulin_out_of_pocket` (STRING)
- `level_of_care` (STRING)

---

## 14. Color Palette Reference

### Chart Colors
- **Chart 1 (Median Price):** `#17becf` (teal) or `#1f77b4` (dark blue)
- **Chart 2 Secondary:** `#1f77b4` (blue)
- **Chart 2 Tertiary:** `#ff7f0e` (orange)

### UI Colors (Existing)
- **Primary Blue:** `#1f77b4`
- **Secondary Orange:** `#ff7f0e`
- **Background Light:** `#f8f9fa`
- **Info Box Background:** `#e3f2fd`
- **Info Box Border:** `#2196f3`

---

## 15. Session State Architecture

### New Session State Keys (Phase 2)

**Checkbox States (Dynamic - one per region/sector):**
```python
# Region checkboxes
st.session_state.price_region_{region_name}  # bool - one per region

# Sector checkboxes
st.session_state.price_sector_{sector_name}  # bool - one per sector
```

**Example:**
```python
st.session_state.price_region_East_Africa = True
st.session_state.price_region_West_Africa = False
st.session_state.price_sector_Public = True
st.session_state.price_sector_Private = True
```

### Existing Session State Keys (Phase 1)
```python
st.session_state.selected_countries_price  # List[str]
st.session_state.selected_regions_price    # List[str]
st.session_state.selected_periods_price    # List[str]
```

---

## 16. Code Snippet: Complete Section Structure

```python
# Phase 2: Price Visualizations Section
if st.session_state.selected_periods_price:
    # Section Header
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>Where patients were charged the full price</h3></div>', unsafe_allow_html=True)

    # Information Paragraph
    st.markdown("""
    Insulin price is standardised in all cases to 1000IU. Click on the optional metrics button
    to see the number of products that make up the median price.
    """)

    # Local Filters: Region and Sector
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        # Region Checkbox Filter
        # ... (implementation from section 2.2)

    with col2:
        # Sector Checkbox Filter
        # ... (implementation from section 2.3)

    # Chart 1: Median Price by Insulin Type
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Median price - By insulin type")
    # ... (implementation from section 3.3)

    # Chart 2: Median Price by Type and Level of Care
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Median price - By insulin type and level of care (public sector only)")
    # ... (implementation from section 4.3)
```

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-07 | AI Assistant | Initial refined plan from Price_Analysis_plan2.md |

---

**End of Refined Implementation Plan - Phase 2**
