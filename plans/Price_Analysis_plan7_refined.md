# Price Analysis Tab - Phase 7 Implementation Plan (Refined)

## Overview
This document provides a detailed implementation plan for Phase 7 of the Price Analysis tab. Phase 7 adds a new "Where insulin is free" section that displays information about facilities providing free insulin and facilities not charging full price. The implementation follows the existing architecture patterns established in Phase 1-6.

## Phase 7 Scope
Phase 7 focuses on building visualizations for free and subsidized insulin:
- "Where insulin is free" section header
- Region and Sector expandable checkbox filters (local to this section)
- Row 1: Two visualizations side by side:
  - Left: Scorecard "Facilities providing for free"
  - Right: Pie chart "Reasons insulin provided for free"
- Row 2: Two visualizations side by side:
  - Left: Scorecard "Facilities not charging full price"
  - Right: Pie chart "Reasons for not charging full price"
- Informational note at bottom
- Professional styling with Plotly pie charts
- Multi-color pie chart legends

---

## 1. Section Structure

### 1.1 Section Header

**Location:** `app.py` - Inside `with tab2:` block, after Phase 6 ("Median price - By originator brands and biosimilars" section)

**Condition:** Only display when at least one Data Collection Period is selected

**Implementation:**
```python
if st.session_state.selected_periods_price:
    # Phase 7: Where insulin is free Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>Where insulin is free</h3></div>', unsafe_allow_html=True)
```

**CSS:** Uses existing `.section-header` class (already defined in app.py)

---

## 2. Local Filter Controls (Region and Sector)

### 2.1 Two-Column Layout for Filters

**Location:** Immediately after section header

**Implementation Pattern:**
```python
    # Local filters for free insulin analysis
    st.markdown("<br>", unsafe_allow_html=True)
    col1_free, col2_free = st.columns(2)
```

### 2.2 Region Checkbox Filter (Column 1)

**Database Query:**
- **Table:** `adl_surveys`
- **Function:** New function `get_free_insulin_regions()`
- **Metric:** `COUNT(DISTINCT form_case__case_id)`
- **Filter:** `WHERE region IS NOT NULL AND region != 'NULL'`
- **Group By:** `region`
- **Sort:** `ORDER BY region DESC` (as specified in plan)
- **Additional Filters:** Apply selected countries and periods from global filters

**UI Pattern:** Expandable checkbox list (st.expander)

**Implementation:**
```python
with col1_free:
    st.markdown("**Region**")
    with st.spinner("Loading regions..."):
        # Build global filters dict from session state
        global_filters_free = {
            'data_collection_period': st.session_state.selected_periods_price,
            'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None
        }

        region_df_free = get_free_insulin_regions(client, config.TABLES["surveys"], global_filters_free)

        if region_df_free is not None and not region_df_free.empty:
            # Build region options with counts
            region_data_free = []
            for _, row in region_df_free.iterrows():
                region = row['region']
                count = row['facility_count']
                region_data_free.append((region, count))

            total_regions_free = len(region_data_free)

            # Initialize checkboxes in session state
            for region, count in region_data_free:
                checkbox_key = f"price_free_region_{region}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

            # Count selected items
            selected_count_free = sum(
                1 for region, _ in region_data_free
                if st.session_state.get(f"price_free_region_{region}", True)
            )
            excluded_count_free = total_regions_free - selected_count_free

            # Create expander with selection summary
            with st.expander(
                f"Select Regions ({selected_count_free}/{total_regions_free} selected)",
                expanded=False
            ):
                if excluded_count_free > 0:
                    st.caption(f"🚫 {excluded_count_free} item{'s' if excluded_count_free != 1 else ''} excluded")

                # Create checkboxes
                local_regions_free = []
                for region, count in region_data_free:
                    checkbox_key = f"price_free_region_{region}"
                    is_checked = st.checkbox(
                        f"{region} ({count:,})",
                        value=st.session_state.get(checkbox_key, True),
                        key=checkbox_key
                    )
                    if is_checked:
                        local_regions_free.append(region)
        else:
            local_regions_free = []
            st.info("No region data available")
```

**Session State Keys:** `price_free_region_{region_name}` (one per region, boolean)

### 2.3 Sector Checkbox Filter (Column 2)

**Database Query:**
- **Table:** `adl_surveys`
- **Function:** New function `get_free_insulin_sectors()`
- **Metric:** `COUNT(DISTINCT form_case__case_id)`
- **Filter:** Apply global filters + selected regions from local Region filter
- **Group By:** `sector`
- **Sort:** `ORDER BY sector DESC` (as specified in plan)

**UI Pattern:** Expandable checkbox list (st.expander)

**Implementation:**
```python
with col2_free:
    st.markdown("**Sector**")
    with st.spinner("Loading sectors..."):
        sector_df_free = get_free_insulin_sectors(client, config.TABLES["surveys"], global_filters_free, local_regions_free)

        if sector_df_free is not None and not sector_df_free.empty:
            # Build sector options with counts
            sector_data_free = []
            for _, row in sector_df_free.iterrows():
                sector = row['sector']
                count = row['facility_count']
                sector_data_free.append((sector, count))

            total_sectors_free = len(sector_data_free)

            # Initialize checkboxes in session state
            for sector, count in sector_data_free:
                checkbox_key = f"price_free_sector_{sector}"
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = True

            # Count selected items
            selected_count_free_sec = sum(
                1 for sector, _ in sector_data_free
                if st.session_state.get(f"price_free_sector_{sector}", True)
            )
            excluded_count_free_sec = total_sectors_free - selected_count_free_sec

            # Create expander with selection summary
            with st.expander(
                f"Select Sectors ({selected_count_free_sec}/{total_sectors_free} selected)",
                expanded=False
            ):
                if excluded_count_free_sec > 0:
                    st.caption(f"🚫 {excluded_count_free_sec} item{'s' if excluded_count_free_sec != 1 else ''} excluded")

                # Create checkboxes
                local_sectors_free = []
                for sector, count in sector_data_free:
                    checkbox_key = f"price_free_sector_{sector}"
                    is_checked = st.checkbox(
                        f"{sector} ({count:,})",
                        value=st.session_state.get(checkbox_key, True),
                        key=checkbox_key
                    )
                    if is_checked:
                        local_sectors_free.append(sector)
        else:
            local_sectors_free = []
            st.info("No sector data available")
```

**Session State Keys:** `price_free_sector_{sector_name}` (one per sector, boolean)

---

## 3. Row 1: Facilities Providing for Free

### 3.1 Two-Column Layout for Row 1

**Location:** After the Region/Sector filters

**Implementation:**
```python
    # Row 1: Facilities providing for free
    st.markdown("<br>", unsafe_allow_html=True)
    col_scorecard1, col_pie1 = st.columns(2)
```

### 3.2 Scorecard 1: Facilities Providing for Free (Left Column)

**Scorecard Specifications:**
- **Heading:** "Facilities providing for free"
- **Label:** "Facilities(n)"
- **Value:** Count of distinct facilities
- **Styling:** Custom HTML with metric-card class

**Data Source:**
- **Table:** `adl_surveys_repeat`
- **Function:** New function `get_facilities_providing_free()`
- **Metric:** `COUNT(DISTINCT form_case__case_id)`
- **Filter:** `insulin_out_of_pocket IN ('No', 'Both')`

**Implementation:**
```python
with col_scorecard1:
    st.markdown("#### Facilities providing for free")

    with st.spinner("Loading facilities providing free data..."):
        # Prepare filters
        free_filters = {
            'data_collection_period': st.session_state.selected_periods_price,
            'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None,
            'region': local_regions_free if local_regions_free else None,
            'sector': local_sectors_free if local_sectors_free else None
        }

        facilities_free_count = get_facilities_providing_free(client, config.TABLES["surveys_repeat"], free_filters)

        if facilities_free_count is not None:
            # Display scorecard using custom HTML
            scorecard_html = f"""
            <div class="metric-card" style="padding: 20px; background: white; border-radius: 8px;
                 border-left: 4px solid #667eea; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="color: #666; font-size: 14px; margin-bottom: 8px;">Facilities(n)</div>
                <div style="color: #1f77b4; font-size: 32px; font-weight: bold;">{facilities_free_count:,}</div>
            </div>
            """
            st.markdown(scorecard_html, unsafe_allow_html=True)
        else:
            st.info("No data available for facilities providing free")
```

### 3.3 Pie Chart 1: Reasons Insulin Provided for Free (Right Column)

**Chart Specifications:**
- **Title:** "Reasons insulin provided for free"
- **Guidance Text:** "Hover over a slice to see the Reported Products(n) making up the percentage"
- **Chart Type:** Pie Chart (Plotly Express)
- **Data:** Percentage of each reason
- **Colors:** Different colors for each reason (Plotly default palette)
- **Legend:** Display in different colors
- **Hover:** Show "Reported Products(n)" count

**Data Source:**
- **Table:** `adl_surveys_repeat`
- **Function:** New function `get_reasons_insulin_free()`
- **Metric:** `COUNT(DISTINCT form_case__case_id)` (Reported Products)
- **Filter:** `insulin_out_of_pocket IN ('No', 'Both')`
- **Group By:** `insulin_free_reason`
- **Sort:** `ORDER BY COUNT(DISTINCT form_case__case_id) DESC`

**Implementation:**
```python
with col_pie1:
    st.markdown("#### Reasons insulin provided for free")
    st.markdown('<p style="font-size: 12px; color: #666;">Hover over a slice to see the Reported Products(n) making up the percentage</p>',
                unsafe_allow_html=True)

    with st.spinner("Loading reasons for free insulin..."):
        reasons_free_df = get_reasons_insulin_free(client, config.TABLES["surveys_repeat"], free_filters)

        if reasons_free_df is not None and not reasons_free_df.empty:
            # Calculate percentages
            total_products = reasons_free_df['product_count'].sum()
            reasons_free_df['percentage'] = (reasons_free_df['product_count'] / total_products * 100).round(2)

            # Create pie chart
            fig_reasons_free = px.pie(
                reasons_free_df,
                values='percentage',
                names='insulin_free_reason',
                title='',
                color_discrete_sequence=px.colors.qualitative.Set3
            )

            # Update traces for better hover info
            fig_reasons_free.update_traces(
                textposition='inside',
                textinfo='percent',
                hovertemplate='<b>%{label}</b><br>' +
                              'Percentage: %{value:.1f}%<br>' +
                              'Reported Products(n): %{customdata[0]:,}<br>' +
                              '<extra></extra>',
                customdata=reasons_free_df[['product_count']].values
            )

            # Update layout
            fig_reasons_free.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05
                ),
                height=400,
                margin=dict(t=20, b=20, l=20, r=120)
            )

            st.plotly_chart(fig_reasons_free, use_container_width=True)
        else:
            st.info("No data available for reasons insulin provided for free")
```

---

## 4. Row 2: Facilities Not Charging Full Price

### 4.1 Two-Column Layout for Row 2

**Location:** After Row 1

**Implementation:**
```python
    # Row 2: Facilities not charging full price
    st.markdown("<br>", unsafe_allow_html=True)
    col_scorecard2, col_pie2 = st.columns(2)
```

### 4.2 Scorecard 2: Facilities Not Charging Full Price (Left Column)

**Scorecard Specifications:**
- **Heading:** "Facilities not charging full price"
- **Label:** "Facilities(n)"
- **Value:** Count of distinct facilities
- **Styling:** Custom HTML with metric-card class

**Data Source:**
- **Table:** `adl_surveys_repeat`
- **Function:** New function `get_facilities_not_full_price()`
- **Metric:** `COUNT(DISTINCT form_case__case_id)`
- **Filter:**
  - `EXCLUDE insulin_subsidised_reason = '---'`
  - `EXCLUDE insulin_subsidised_reason = 'NULL'`
  - `insulin_subsidised_reason IS NOT NULL`

**Implementation:**
```python
with col_scorecard2:
    st.markdown("#### Facilities not charging full price")

    with st.spinner("Loading facilities not charging full price data..."):
        facilities_subsidised_count = get_facilities_not_full_price(client, config.TABLES["surveys_repeat"], free_filters)

        if facilities_subsidised_count is not None:
            # Display scorecard using custom HTML
            scorecard_html = f"""
            <div class="metric-card" style="padding: 20px; background: white; border-radius: 8px;
                 border-left: 4px solid #667eea; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="color: #666; font-size: 14px; margin-bottom: 8px;">Facilities(n)</div>
                <div style="color: #1f77b4; font-size: 32px; font-weight: bold;">{facilities_subsidised_count:,}</div>
            </div>
            """
            st.markdown(scorecard_html, unsafe_allow_html=True)
        else:
            st.info("No data available for facilities not charging full price")
```

### 4.3 Pie Chart 2: Reasons for Not Charging Full Price (Right Column)

**Chart Specifications:**
- **Title:** "Reasons for not charging full price"
- **Guidance Text:** "Hover over a slice to see the Reported Products(n) making up the percentage"
- **Chart Type:** Pie Chart (Plotly Express)
- **Data:** Percentage of each reason
- **Colors:** Different colors for each reason (Plotly default palette)
- **Legend:** Display in different colors
- **Hover:** Show "Reported Products(n)" count

**Data Source:**
- **Table:** `adl_surveys_repeat`
- **Function:** New function `get_reasons_not_full_price()`
- **Metric:** `COUNT(DISTINCT form_case__case_id)` (Reported Products)
- **Filter:**
  - `EXCLUDE insulin_subsidised_reason = '---'`
  - `EXCLUDE insulin_subsidised_reason = 'NULL'`
  - `insulin_subsidised_reason IS NOT NULL`
- **Group By:** `insulin_subsidised_reason`
- **Sort:** `ORDER BY COUNT(DISTINCT form_case__case_id) DESC`

**Implementation:**
```python
with col_pie2:
    st.markdown("#### Reasons for not charging full price")
    st.markdown('<p style="font-size: 12px; color: #666;">Hover over a slice to see the Reported Products(n) making up the percentage</p>',
                unsafe_allow_html=True)

    with st.spinner("Loading reasons for not charging full price..."):
        reasons_subsidised_df = get_reasons_not_full_price(client, config.TABLES["surveys_repeat"], free_filters)

        if reasons_subsidised_df is not None and not reasons_subsidised_df.empty:
            # Calculate percentages
            total_products = reasons_subsidised_df['product_count'].sum()
            reasons_subsidised_df['percentage'] = (reasons_subsidised_df['product_count'] / total_products * 100).round(2)

            # Create pie chart
            fig_reasons_subsidised = px.pie(
                reasons_subsidised_df,
                values='percentage',
                names='insulin_subsidised_reason',
                title='',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )

            # Update traces for better hover info
            fig_reasons_subsidised.update_traces(
                textposition='inside',
                textinfo='percent',
                hovertemplate='<b>%{label}</b><br>' +
                              'Percentage: %{value:.1f}%<br>' +
                              'Reported Products(n): %{customdata[0]:,}<br>' +
                              '<extra></extra>',
                customdata=reasons_subsidised_df[['product_count']].values
            )

            # Update layout
            fig_reasons_subsidised.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05
                ),
                height=400,
                margin=dict(t=20, b=20, l=20, r=120)
            )

            st.plotly_chart(fig_reasons_subsidised, use_container_width=True)
        else:
            st.info("No data available for reasons not charging full price")
```

---

## 5. Note Message

### 5.1 Informational Note

**Location:** After Row 2 (scorecard 2 and pie chart 2)

**Implementation:**
```python
    # Note message
    st.markdown("<br>", unsafe_allow_html=True)
    note_html = """
    <div class="info-box" style="padding: 15px; background: #e3f2fd; border-left: 4px solid #2196f3;
         border-radius: 4px; margin-top: 15px;">
        <p style="margin: 0; color: #1565c0; font-size: 14px;">
            <strong>Note:</strong> This includes facilities that report providing insulin for free at least
            some people, depending on the national policies, for example insurance or donation schemes.
        </p>
    </div>
    """
    st.markdown(note_html, unsafe_allow_html=True)
```

---

## 6. Database Functions to Implement

### 6.1 Function Summary

Add to `database/bigquery_client.py`:

| Function Name | Purpose | Table | Returns |
|---------------|---------|-------|---------|
| `get_free_insulin_regions()` | Get regions for free insulin filter | `adl_surveys` | region, facility_count |
| `get_free_insulin_sectors()` | Get sectors for free insulin filter | `adl_surveys` | sector, facility_count |
| `get_facilities_providing_free()` | Count facilities providing free insulin | `adl_surveys_repeat` | integer count |
| `get_reasons_insulin_free()` | Get reasons insulin provided for free | `adl_surveys_repeat` | insulin_free_reason, product_count |
| `get_facilities_not_full_price()` | Count facilities not charging full price | `adl_surveys_repeat` | integer count |
| `get_reasons_not_full_price()` | Get reasons for not charging full price | `adl_surveys_repeat` | insulin_subsidised_reason, product_count |

### 6.2 Function: get_free_insulin_regions()

```python
@st.cache_data(ttl=600)
def get_free_insulin_regions(_client, table_name, global_filters):
    """
    Get regions for free insulin analysis filter with facility counts.

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
        st.error(f"Error getting free insulin regions: {str(e)}")
        return None
```

### 6.3 Function: get_free_insulin_sectors()

```python
@st.cache_data(ttl=600)
def get_free_insulin_sectors(_client, table_name, global_filters, selected_regions):
    """
    Get sectors for free insulin analysis filter with facility counts.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys)
        global_filters (dict): Global filters (data_collection_period, country)
        selected_regions (list): Selected regions from local Region filter

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

    # Add region filter from local selection
    if selected_regions:
        regions_str = "', '".join(selected_regions)
        where_clauses.append(f"region IN ('{regions_str}')")

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
        st.error(f"Error getting free insulin sectors: {str(e)}")
        return None
```

### 6.4 Function: get_facilities_providing_free()

```python
@st.cache_data(ttl=600)
def get_facilities_providing_free(_client, table_name, filters):
    """
    Get count of facilities providing insulin for free.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        filters (dict): Filters (data_collection_period, country, region, sector)

    Returns:
        int: Count of distinct facilities
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

    # Free insulin filter
    where_clauses.append("insulin_out_of_pocket IN ('No', 'Both')")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        COUNT(DISTINCT form_case__case_id) as facility_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    """

    try:
        result = _client.query(query).to_dataframe()
        if not result.empty:
            return int(result.iloc[0]['facility_count'])
        return 0
    except Exception as e:
        st.error(f"Error getting facilities providing free: {str(e)}")
        return None
```

### 6.5 Function: get_reasons_insulin_free()

```python
@st.cache_data(ttl=600)
def get_reasons_insulin_free(_client, table_name, filters):
    """
    Get reasons why insulin is provided for free with product counts.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        filters (dict): Filters (data_collection_period, country, region, sector)

    Returns:
        pandas DataFrame with columns: insulin_free_reason, product_count
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

    # Free insulin filter
    where_clauses.append("insulin_out_of_pocket IN ('No', 'Both')")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        insulin_free_reason,
        COUNT(DISTINCT form_case__case_id) as product_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_free_reason
    ORDER BY product_count DESC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting reasons insulin free: {str(e)}")
        return None
```

### 6.6 Function: get_facilities_not_full_price()

```python
@st.cache_data(ttl=600)
def get_facilities_not_full_price(_client, table_name, filters):
    """
    Get count of facilities not charging full price for insulin.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        filters (dict): Filters (data_collection_period, country, region, sector)

    Returns:
        int: Count of distinct facilities
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

    # Subsidised insulin filters
    where_clauses.append("insulin_subsidised_reason IS NOT NULL")
    where_clauses.append("insulin_subsidised_reason != '---'")
    where_clauses.append("insulin_subsidised_reason != 'NULL'")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        COUNT(DISTINCT form_case__case_id) as facility_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    """

    try:
        result = _client.query(query).to_dataframe()
        if not result.empty:
            return int(result.iloc[0]['facility_count'])
        return 0
    except Exception as e:
        st.error(f"Error getting facilities not charging full price: {str(e)}")
        return None
```

### 6.7 Function: get_reasons_not_full_price()

```python
@st.cache_data(ttl=600)
def get_reasons_not_full_price(_client, table_name, filters):
    """
    Get reasons why facilities are not charging full price with product counts.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        filters (dict): Filters (data_collection_period, country, region, sector)

    Returns:
        pandas DataFrame with columns: insulin_subsidised_reason, product_count
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

    # Subsidised insulin filters
    where_clauses.append("insulin_subsidised_reason IS NOT NULL")
    where_clauses.append("insulin_subsidised_reason != '---'")
    where_clauses.append("insulin_subsidised_reason != 'NULL'")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        insulin_subsidised_reason,
        COUNT(DISTINCT form_case__case_id) as product_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_subsidised_reason
    ORDER BY product_count DESC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting reasons not full price: {str(e)}")
        return None
```

---

## 7. Code Organization

### 7.1 File Structure

```
/Users/waqas/HAI_demo/
├── app.py                          # Main application file
│   └── [After Phase 6] Tab 2: Price Analysis
│       ├── Phase 1: Global filters (existing)
│       ├── Phase 2: Median price charts (existing)
│       ├── Phase 3: Price by INN (existing)
│       ├── Phase 4: Price by Brand (existing)
│       ├── Phase 5: Median price by Presentation (existing)
│       ├── Phase 6: Median price by Originator/Biosimilar (existing)
│       └── Phase 7: Where insulin is free (new)
│           ├── Section header
│           ├── Local Region/Sector filters
│           ├── Row 1: Scorecard + Pie (Providing for free)
│           ├── Row 2: Scorecard + Pie (Not full price)
│           └── Note message
├── database/
│   └── bigquery_client.py         # Add 6 new functions
│       ├── get_free_insulin_regions()
│       ├── get_free_insulin_sectors()
│       ├── get_facilities_providing_free()
│       ├── get_reasons_insulin_free()
│       ├── get_facilities_not_full_price()
│       └── get_reasons_not_full_price()
├── plans/
│   ├── Price_Analysis_plan7.md    # Original plan
│   └── Price_Analysis_plan7_refined.md  # This document
```

### 7.2 Import Updates

Add to `app.py` imports (around line 10-57):

```python
from database.bigquery_client import (
    # ... existing imports ...
    get_free_insulin_regions,
    get_free_insulin_sectors,
    get_facilities_providing_free,
    get_reasons_insulin_free,
    get_facilities_not_full_price,
    get_reasons_not_full_price
)
```

---

## 8. Implementation Steps

### Step 1: Add Database Functions (45 minutes)
- Add `get_free_insulin_regions()` function to `database/bigquery_client.py`
- Add `get_free_insulin_sectors()` function to `database/bigquery_client.py`
- Add `get_facilities_providing_free()` function to `database/bigquery_client.py`
- Add `get_reasons_insulin_free()` function to `database/bigquery_client.py`
- Add `get_facilities_not_full_price()` function to `database/bigquery_client.py`
- Add `get_reasons_not_full_price()` function to `database/bigquery_client.py`
- Test queries with sample filters in BigQuery console
- Verify filters work correctly

### Step 2: Update Imports (5 minutes)
- Add 6 new function imports to `app.py`
- Run syntax check

### Step 3: Add Section Header (5 minutes)
- Add conditional wrapper for selected periods
- Add section header "Where insulin is free" after Phase 6
- Test display when periods selected/unselected

### Step 4: Build Region/Sector Filters (25 minutes)
- Create two-column layout with unique variable names (`col1_free`, `col2_free`)
- Implement Region checkbox expander (reuse existing pattern)
- Implement Sector checkbox expander (reuse existing pattern)
- Use unique session state keys (`price_free_region_*`, `price_free_sector_*`)
- Test filter interactions and session state

### Step 5: Build Row 1 - Free Insulin Visualizations (35 minutes)
- Create two-column layout (`col_scorecard1`, `col_pie1`)
- Implement scorecard 1 with custom HTML styling
- Implement pie chart 1 with Plotly Express
- Add guidance text for pie chart
- Configure hover tooltips with product counts
- Test with various filter combinations

### Step 6: Build Row 2 - Not Full Price Visualizations (35 minutes)
- Create two-column layout (`col_scorecard2`, `col_pie2`)
- Implement scorecard 2 with custom HTML styling
- Implement pie chart 2 with Plotly Express
- Add guidance text for pie chart
- Configure hover tooltips with product counts
- Test with various filter combinations

### Step 7: Add Note Message (5 minutes)
- Add informational note with custom HTML
- Style with info-box class
- Test display

### Step 8: Testing & Validation (25 minutes)
- Run syntax check
- Manual testing of all features
- Cross-filter testing (global + local filters)
- Edge case testing (no data, single reason, etc.)
- Verify scorecards display correctly
- Verify pie charts display with correct percentages

**Total Estimated Time:** ~3 hours

---

## 9. Testing Strategy

### 9.1 Manual Testing Checklist

**Section Display:**
- [ ] Section only shows when at least one period is selected
- [ ] Section hides when no periods selected
- [ ] Section header "Where insulin is free" displays correctly
- [ ] Section appears after Phase 6 (Median price - By originator brands and biosimilars)

**Filter Functionality:**
- [ ] Region checkboxes load with facility counts
- [ ] Sector checkboxes load with facility counts
- [ ] Region filter affects sector options
- [ ] Expander shows correct selection count (N/M selected)
- [ ] Excluded count displays when items unchecked
- [ ] Checkboxes persist state across reruns
- [ ] All regions/sectors selected by default on first load
- [ ] Filters are independent from Phase 2-6 filters

**Row 1 - Scorecard 1:**
- [ ] Heading: "Facilities providing for free"
- [ ] Label: "Facilities(n)"
- [ ] Value displays as formatted number with comma separators
- [ ] Scorecard has proper styling (white background, left border)
- [ ] Value changes when filters are adjusted

**Row 1 - Pie Chart 1:**
- [ ] Title: "Reasons insulin provided for free"
- [ ] Guidance text displays below title
- [ ] Pie chart shows percentages on slices
- [ ] Different colors for each reason (legend visible)
- [ ] Hover shows reason, percentage, and "Reported Products(n)"
- [ ] Chart responds to filter changes
- [ ] Legend displays on the right side

**Row 2 - Scorecard 2:**
- [ ] Heading: "Facilities not charging full price"
- [ ] Label: "Facilities(n)"
- [ ] Value displays as formatted number with comma separators
- [ ] Scorecard has proper styling (white background, left border)
- [ ] Value changes when filters are adjusted

**Row 2 - Pie Chart 2:**
- [ ] Title: "Reasons for not charging full price"
- [ ] Guidance text displays below title
- [ ] Pie chart shows percentages on slices
- [ ] Different colors for each reason (legend visible)
- [ ] Hover shows reason, percentage, and "Reported Products(n)"
- [ ] Chart responds to filter changes
- [ ] Legend displays on the right side

**Note Message:**
- [ ] Note displays after Row 2
- [ ] Note has proper styling (light blue background, left border)
- [ ] Note text is correct and readable

**Data Integrity:**
- [ ] Scorecard 1 uses `insulin_out_of_pocket IN ('No', 'Both')` filter
- [ ] Pie chart 1 uses same filter as scorecard 1
- [ ] Pie chart 1 groups by `insulin_free_reason`
- [ ] Scorecard 2 excludes "---" and "NULL" in `insulin_subsidised_reason`
- [ ] Pie chart 2 uses same filter as scorecard 2
- [ ] Pie chart 2 groups by `insulin_subsidised_reason`
- [ ] Percentages in pie charts add up to 100%
- [ ] Product counts are positive integers

### 9.2 Test Execution Commands

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
3. Scroll to "Where insulin is free" section
4. Verify section appears after "Median price - By originator brands and biosimilars"
5. Test Region checkbox filter
6. Test Sector checkbox filter (depends on Region)
7. Verify Row 1 displays (scorecard + pie chart)
8. Verify scorecard 1 shows facility count
9. Verify pie chart 1 shows reasons with percentages
10. Hover over pie chart 1 slices to verify tooltips
11. Verify Row 2 displays (scorecard + pie chart)
12. Verify scorecard 2 shows facility count
13. Verify pie chart 2 shows reasons with percentages
14. Hover over pie chart 2 slices to verify tooltips
15. Verify note message displays
16. Change filters and verify all visualizations update
17. Uncheck all regions - verify info messages
18. Deselect all periods - verify section hides

---

## 10. Key Design Decisions

### 10.1 Scorecard vs Metric Card
**Decision:** Use custom HTML scorecards instead of st.metric()

**Rationale:**
- More control over styling
- Consistent with existing phases
- Better visual appearance
- Can customize colors and layout
- Professional dashboard look

### 10.2 Pie Chart for Reasons
**Decision:** Use pie charts to display reason percentages

**Rationale:**
- Ideal for showing percentage distributions
- Easy to compare relative proportions
- Visual and intuitive
- Supports hover tooltips with detailed info
- Legends provide clear color coding
- Common visualization for categorical percentages

### 10.3 Two Rows of Visualizations
**Decision:** Separate free insulin and subsidized insulin into two rows

**Rationale:**
- Clear visual separation of concepts
- Prevents confusion between "free" and "not full price"
- Easier to understand and compare
- Follows logical grouping
- Better user experience

### 10.4 Filter Independence
**Decision:** Phase 7 has its own Region/Sector filters

**Rationale:**
- Allows independent analysis
- Follows pattern from Phase 2-6
- Prevents unintended filter interactions
- Better user experience for focused analysis
- Users can analyze free insulin separately

### 10.5 Color Scheme for Pie Charts
**Decision:** Use different Plotly color schemes for each pie chart

**Rationale:**
- Pie chart 1: Set3 (pastel colors)
- Pie chart 2: Pastel (different pastel palette)
- Visual distinction between the two charts
- Both palettes have good color variety
- Professional appearance
- Good contrast for readability

### 10.6 Hover Tooltip Content
**Decision:** Show "Reported Products(n)" count in hover tooltip

**Rationale:**
- Provides additional context
- Users can see actual counts, not just percentages
- More informative
- Follows plan specification
- Better data transparency

### 10.7 Note Placement
**Decision:** Place note after both rows of visualizations

**Rationale:**
- Users see visualizations first, then context
- Logical flow of information
- Note applies to entire section
- Follows plan specification
- Better UX pattern

---

## 11. Session State Architecture

### 11.1 New Session State Keys (Phase 7)

**Checkbox States (Dynamic - one per region/sector):**
```python
# Region checkboxes (Free insulin section)
st.session_state.price_free_region_{region_name}  # bool - one per region

# Sector checkboxes (Free insulin section)
st.session_state.price_free_sector_{sector_name}  # bool - one per sector
```

**Example:**
```python
st.session_state.price_free_region_East_Africa = True
st.session_state.price_free_region_West_Africa = False
st.session_state.price_free_sector_Public = True
st.session_state.price_free_sector_Private = True
```

### 11.2 Existing Session State Keys (Not Modified)
```python
# Phase 1 - Global filters
st.session_state.selected_countries_price  # List[str]
st.session_state.selected_periods_price    # List[str]

# Phase 2-6 - Local filters (not reused)
st.session_state.price_region_{region_name}
st.session_state.price_sector_{sector_name}
st.session_state.price_inn_region_{region_name}
st.session_state.price_inn_sector_{sector_name}
st.session_state.price_brand_region_{region_name}
st.session_state.price_brand_sector_{sector_name}
st.session_state.price_pres_region_{region_name}
st.session_state.price_pres_sector_{sector_name}
st.session_state.price_orig_region_{region_name}
st.session_state.price_orig_sector_{sector_name}
```

---

## 12. Potential Issues & Solutions

### Issue 1: No Free Insulin Data
**Symptom:** Some filters return no facilities providing free insulin
**Solution:**
- Display info message when no data available
- This is expected behavior
- User can adjust filters
- Clear messaging prevents confusion

### Issue 2: Single Reason in Pie Chart
**Symptom:** Only one reason available, pie chart looks like full circle
**Solution:**
- Pie chart still displays correctly
- Single slice shown with 100%
- This is expected behavior
- Legend still shows the reason

### Issue 3: Missing Reason Data
**Symptom:** `insulin_free_reason` or `insulin_subsidised_reason` is NULL
**Solution:**
- Query filters handle NULL values
- Empty results show info message
- This is expected behavior
- User can check data quality

### Issue 4: Query Performance
**Symptom:** Slow query execution with multiple filters
**Solution:**
- Use caching (@st.cache_data with ttl=600)
- BigQuery optimized for aggregations
- Monitor query execution time
- Queries are relatively simple (count + group by)

### Issue 5: Percentage Calculation
**Symptom:** Percentages don't add to exactly 100% due to rounding
**Solution:**
- Use .round(2) for 2 decimal places
- Minor rounding differences acceptable
- Pie chart handles this gracefully
- Visual representation is primary goal

### Issue 6: Long Reason Names
**Symptom:** Reason text too long for pie chart labels
**Solution:**
- Use legends instead of on-slice text for labels
- Hover tooltips show full reason text
- Pie slices show only percentages
- This is already in the design

---

## 13. Acceptance Criteria

Phase 7 implementation is complete when:

- [ ] **AC1:** Section header "Where insulin is free" displays
- [ ] **AC2:** Section appears after Phase 6 section
- [ ] **AC3:** Section only shows when at least one period is selected
- [ ] **AC4:** Region checkbox filter loads with facility counts (independent from other phases)
- [ ] **AC5:** Sector checkbox filter loads with facility counts (independent from other phases)
- [ ] **AC6:** Sector filter options update when Region filter changes
- [ ] **AC7:** Expanders show selection count "N/M selected"
- [ ] **AC8:** Expanders show excluded count when items unchecked
- [ ] **AC9:** All checkboxes selected by default on first load
- [ ] **AC10:** Row 1 displays scorecard and pie chart side by side
- [ ] **AC11:** Scorecard 1 heading is "Facilities providing for free"
- [ ] **AC12:** Scorecard 1 label is "Facilities(n)"
- [ ] **AC13:** Scorecard 1 value is formatted with comma separators
- [ ] **AC14:** Pie chart 1 title is "Reasons insulin provided for free"
- [ ] **AC15:** Pie chart 1 has guidance text below title
- [ ] **AC16:** Pie chart 1 shows percentages on slices
- [ ] **AC17:** Pie chart 1 has multi-color legend
- [ ] **AC18:** Pie chart 1 hover shows reason, percentage, and "Reported Products(n)"
- [ ] **AC19:** Row 2 displays scorecard and pie chart side by side
- [ ] **AC20:** Scorecard 2 heading is "Facilities not charging full price"
- [ ] **AC21:** Scorecard 2 label is "Facilities(n)"
- [ ] **AC22:** Scorecard 2 value is formatted with comma separators
- [ ] **AC23:** Pie chart 2 title is "Reasons for not charging full price"
- [ ] **AC24:** Pie chart 2 has guidance text below title
- [ ] **AC25:** Pie chart 2 shows percentages on slices
- [ ] **AC26:** Pie chart 2 has multi-color legend
- [ ] **AC27:** Pie chart 2 hover shows reason, percentage, and "Reported Products(n)"
- [ ] **AC28:** Note message displays after Row 2
- [ ] **AC29:** Note has correct text about national policies
- [ ] **AC30:** Note has proper styling (blue background, left border)
- [ ] **AC31:** All visualizations respond to filter changes
- [ ] **AC32:** Info messages display when no data available
- [ ] **AC33:** No errors in console or BigQuery logs
- [ ] **AC34:** Both files pass syntax check
- [ ] **AC35:** Scorecard 1 uses correct filter: `insulin_out_of_pocket IN ('No', 'Both')`
- [ ] **AC36:** Pie chart 1 groups by `insulin_free_reason`
- [ ] **AC37:** Scorecard 2 excludes "---" and "NULL" in `insulin_subsidised_reason`
- [ ] **AC38:** Pie chart 2 groups by `insulin_subsidised_reason`

---

## 14. Color Palette Reference

### Scorecard Colors
- **Background:** `white` or `#ffffff`
- **Left Border:** `#667eea` (purple accent)
- **Label Color:** `#666` (gray)
- **Value Color:** `#1f77b4` (blue)

### Pie Chart Colors
- **Chart 1 (Reasons Free):** Plotly Set3 palette (pastel colors)
- **Chart 2 (Reasons Subsidised):** Plotly Pastel palette

### Info Box Colors (Note)
- **Background:** `#e3f2fd` (light blue)
- **Border:** `#2196f3` (blue)
- **Text Color:** `#1565c0` (dark blue)

### UI Colors (Existing)
- **Primary Blue:** `#1f77b4`
- **Secondary Orange:** `#ff7f0e`
- **Background Light:** `#f8f9fa`

---

## 15. Dependencies

### Required Packages (Already Installed)
- `streamlit` - UI framework
- `pandas` - Data manipulation
- `plotly` - Charts (plotly.express)
- `google-cloud-bigquery` - BigQuery client

### Required Files
- `app.py` - Main application (modify)
- `database/bigquery_client.py` - Database functions (add 6 new functions)
- `config.py` - Configuration settings (no changes)
- `.env` - Environment variables (no changes)

### BigQuery Requirements
- **Project:** `hai-dev`
- **Dataset:** `facilities`
- **Tables:**
  - `adl_surveys` (for Region and Sector filters)
  - `adl_surveys_repeat` (for all metrics and pie chart data)

**Columns needed in adl_surveys:**
- `form_case__case_id` (STRING)
- `data_collection_period` (STRING)
- `country` (STRING)
- `region` (STRING)
- `sector` (STRING)

**Columns needed in adl_surveys_repeat:**
- `form_case__case_id` (STRING)
- `data_collection_period` (STRING)
- `country` (STRING)
- `region` (STRING)
- `sector` (STRING)
- `insulin_out_of_pocket` (STRING) - Values: "Yes", "No", "Both", "Some people pay out of pocket"
- `insulin_free_reason` (STRING) - Reason why insulin is free
- `insulin_subsidised_reason` (STRING) - Reason for not charging full price

---

## 16. Expected Data Values

**insulin_out_of_pocket values:**
- "Yes" - People pay out of pocket
- "No" - Insulin is free
- "Both" - Some free, some paid
- "Some people pay out of pocket" - Partially subsidized
- (Other variations possible)

**insulin_free_reason values:**
- Dynamic based on data (e.g., "Government program", "Insurance", "Donation", etc.)

**insulin_subsidised_reason values:**
- Dynamic based on data (e.g., "Insurance scheme", "Government subsidy", "Partial coverage", etc.)
- "---" (excluded from results)
- "NULL" (excluded from results)

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-17 | AI Assistant | Initial refined plan from Price_Analysis_plan7.md |

---

**End of Refined Implementation Plan - Phase 7**
