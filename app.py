"""
HAI Facilities Data Dashboard - Streamlit Application
Dashboard UI Revamp - Phase 1: Filter Controls for Availability Analysis
"""
# Print to stdout IMMEDIATELY before any imports
print("="*80, flush=True)
print("APP.PY STARTING - BEFORE ANY IMPORTS", flush=True)
print("="*80, flush=True)

import sys
import traceback

print("✓ sys and traceback imported", flush=True)

# Import basic dependencies one by one with diagnostics
try:
    print("Importing streamlit...", flush=True)
    import streamlit as st
    print("✓ streamlit imported", flush=True)

    print("Importing pandas...", flush=True)
    import pandas as pd
    print("✓ pandas imported", flush=True)

    print("Importing plotly...", flush=True)
    import plotly.express as px
    import plotly.graph_objects as go
    print("✓ plotly imported", flush=True)

    print("Importing config...", flush=True)
    import config
    print("✓ config imported", flush=True)

    print("Importing database.bigquery_client...", flush=True)
    from database.bigquery_client import (
        get_bigquery_client,
        get_grouped_counts,
        get_data_collection_periods,
        get_selected_periods_summary,
        fetch_facility_statistics,
        validate_facility_stats,
        get_insulin_regions,
        get_insulin_sectors,
        get_insulin_availability_metrics,
        get_insulin_by_sector_regions,
        get_insulin_by_sector_chart_data,
        get_insulin_by_type_regions,
        get_insulin_by_type_sectors,
        get_insulin_by_type_human_chart_data,
        get_insulin_by_type_analogue_chart_data,
        get_insulin_by_region_sectors,
        get_insulin_by_region_human_chart_data,
        get_insulin_by_region_analogue_chart_data,
        get_insulin_public_levelcare_regions,
        get_insulin_public_levelcare_human_chart_data,
        get_insulin_public_levelcare_analogue_chart_data,
        get_insulin_by_inn_regions,
        get_insulin_by_inn_sectors,
        get_insulin_by_inn_chart_data,
        get_insulin_top_brands_sectors,
        get_insulin_top_brands_chart_data,
        get_insulin_by_presentation_regions,
        get_insulin_by_presentation_sectors,
        get_insulin_by_presentation_chart_data,
        get_insulin_originator_biosimilar_regions,
        get_insulin_originator_biosimilar_sectors,
        get_insulin_human_originator_metric,
        get_insulin_analogue_originator_metric,
        get_insulin_human_biosimilar_metric,
        get_insulin_analogue_biosimilar_metric,
        get_comparator_medicine_regions,
        get_comparator_medicine_sectors,
        get_comparator_medicine_table_data,
        get_price_regions,
        get_price_sectors,
        get_median_price_by_type,
        get_median_price_by_type_levelcare,
        get_price_by_inn,
        get_price_by_brand_human,
        get_price_by_brand_analogue,
        get_median_price_by_presentation,
        get_median_price_by_originator_human,
        get_median_price_by_originator_analogue
    )
    print("✓ database.bigquery_client imported", flush=True)

    print("Importing components.statistics_tree...", flush=True)
    from components.statistics_tree import render_statistics_tree
    print("✓ components.statistics_tree imported", flush=True)

except Exception as e:
    # Critical import error - print to both stdout and stderr
    print(f"\n{'='*80}", flush=True)
    print(f"CRITICAL IMPORT ERROR: {e}", flush=True)
    print(f"Traceback: {traceback.format_exc()}", flush=True)
    print(f"{'='*80}\n", flush=True)
    print(f"CRITICAL IMPORT ERROR: {e}", file=sys.stderr, flush=True)
    print(f"Traceback: {traceback.format_exc()}", file=sys.stderr, flush=True)
    # Try to use streamlit if it imported
    try:
        st.error(f"❌ CRITICAL IMPORT ERROR: {e}")
        st.error(f"Traceback: {traceback.format_exc()}")
    except:
        pass
    raise

print("\n" + "="*80, flush=True)
print("ALL IMPORTS SUCCESSFUL - Setting up Streamlit page config", flush=True)
print("="*80 + "\n", flush=True)

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

print("✓ st.set_page_config() called successfully", flush=True)

# Custom CSS for modern styling
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --background-light: #f8f9fa;
        --card-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: var(--card-shadow);
    }

    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.5rem;
    }

    .main-header p {
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
        font-size: 1.1rem;
    }

    /* Section headers */
    .section-header {
        background: var(--background-light);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border-left: 4px solid var(--primary-color);
        margin: 1.5rem 0 1rem 0;
    }

    .section-header h3 {
        margin: 0;
        color: #333;
    }

    /* Filter cards */
    .filter-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: var(--card-shadow);
        margin-bottom: 1rem;
    }

    /* Count badge */
    .count-badge {
        display: inline-block;
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: white;
        border-radius: 8px 8px 0 0;
        border: 1px solid #e0e0e0;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    /* Data table styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }

    /* Center align table cells */
    .dataframe td {
        text-align: center !important;
    }

    .dataframe th {
        text-align: center !important;
    }

    /* Info boxes */
    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    .warning-box {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    /* Responsive adjustments for mobile */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }

        /* Force column stacking on mobile */
        [data-testid="column"] {
            width: 100% !important;
            flex: 100% !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="main-header">
        <h1>📊 ACCISS Facilities Dashboard</h1>
        <p>Comprehensive analysis of healthcare facilities data - Insulin availability and pricing</p>
    </div>
""", unsafe_allow_html=True)

# Initialize BigQuery client
print("Initializing BigQuery client...", flush=True)
client = get_bigquery_client()

if not client:
    st.error("⚠️ Failed to connect to BigQuery. Please check your credentials and configuration.")
    st.stop()

print(f"✓ BigQuery client created successfully for project: {client.project}", flush=True)

# Main table for Phase 1 - adl_surveys
TABLE_NAME = config.TABLES["surveys"]

# Initialize session state for Availability Analysis tab
if 'selected_countries' not in st.session_state:
    st.session_state.selected_countries = []
if 'selected_regions' not in st.session_state:
    st.session_state.selected_regions = []
if 'selected_periods' not in st.session_state:
    st.session_state.selected_periods = []

# Initialize session state for Price Analysis tab
if 'selected_countries_price' not in st.session_state:
    st.session_state.selected_countries_price = []
if 'selected_regions_price' not in st.session_state:
    st.session_state.selected_regions_price = []
if 'selected_periods_price' not in st.session_state:
    st.session_state.selected_periods_price = []

# Main content tabs - Two tabs only as per plan
tab1, tab2 = st.tabs([
    "📊 Availability Analysis",
    "💰 Price Analysis"
])

# Tab 1: Availability Analysis - Phase 1 Implementation
with tab1:
    # Main Page Heading
    st.title("Insulin Availability Analysis")
    st.markdown("<br>", unsafe_allow_html=True)

    # Two-Column Layout: Instructions and Definitions
    col_left, col_right = st.columns([1.1, 1])

    with col_left:
        # Instructions Section
        st.markdown("### Instructions:")

        # Red alert text
        st.error("**To begin select a Data Collection Period (data not shown by default)**")

        # Region selection instruction
        st.markdown("""
        *Selecting a region:* By default, all regions are displayed. You can select one or more regions by using the Region selection box, this will apply for all graphs under the same heading.
        """)

        # Currency instruction
        st.markdown("""
        *Currency:* By default, results are displayed in local currency. To select USD, see below.
        """)

        # User Guide link
        st.markdown("""
        For more see the [User Guide](https://accisstoolkit.haiweb.org/user-guide/)
        """)

        # Optional Metrics Info Box
        st.info("""
        📊 **Optional metrics** - many graphs and scorecards have optional metrics, such as the number of facilities or the price in USD. If available the button is shown in the top right corner of the graph. Click on this to choose which metric to show, or show multiple for comparison.
        """)

    with col_right:
        # Definitions Section
        st.markdown("### Definitions:")

        st.markdown("""
        *Facilities with Availability (%)* - Percentage of facilities out of the total in a given data collection period with insulin (or comparator NCD medicine) in stock on the day of data collection.
        """)

        st.markdown("""
        *Facilities with Availability (n)* - Number of facilities in a given data collection period with insulin (or comparator NCD medicine) in stock on the day of data collection.
        """)

        st.markdown("""
        *INN*: International Nonproprietary Name
        """)

        st.markdown("""
        **Note:** data on all pages of the dashboard relate to the supply of outpatients (not inpatients)
        """)

    # Spacing before Data Selectors
    st.markdown("<br>", unsafe_allow_html=True)

    # Data Selectors Section
    st.markdown('<div class="section-header"><h3>Data Selectors</h3></div>', unsafe_allow_html=True)

    # Create three columns for the filter dropdowns
    col1, col2, col3 = st.columns(3)

    # Filter 1: Country Dropdown
    with col1:
        st.markdown("#### Country")
        with st.spinner("Loading countries..."):
            try:
                country_df = get_grouped_counts(client, TABLE_NAME, "country")

                if country_df is not None and not country_df.empty:
                    # Create options with count badges
                    country_options = []
                    for _, row in country_df.iterrows():
                        country = row['country']
                        count = row['survey_count']
                        country_options.append(f"{country} ({count:,})")

                    selected_countries_display = st.multiselect(
                        "Select countries",
                        options=country_options,
                        default=[],
                        help="Filter by country - showing survey count per country",
                        label_visibility="collapsed"
                    )

                    # Extract actual country names from display format
                    st.session_state.selected_countries = [
                        opt.split(' (')[0] for opt in selected_countries_display
                    ]

                    # Show selection summary
                    if st.session_state.selected_countries:
                        st.success(f"✓ {len(st.session_state.selected_countries)} country(ies) selected")
                else:
                    st.warning("No country data available")
            except Exception as e:
                st.error(f"Error loading countries: {str(e)}")

    # Filter 2: Region Dropdown
    with col2:
        st.markdown("#### Region")
        with st.spinner("Loading regions..."):
            try:
                region_df = get_grouped_counts(client, TABLE_NAME, "region")

                if region_df is not None and not region_df.empty:
                    # Create options with count badges
                    region_options = []
                    for _, row in region_df.iterrows():
                        region = row['region']
                        count = row['survey_count']
                        region_options.append(f"{region} ({count:,})")

                    selected_regions_display = st.multiselect(
                        "Select regions",
                        options=region_options,
                        default=[],
                        help="Filter by region - showing survey count per region",
                        label_visibility="collapsed"
                    )

                    # Extract actual region names from display format
                    st.session_state.selected_regions = [
                        opt.split(' (')[0] for opt in selected_regions_display
                    ]

                    # Show selection summary
                    if st.session_state.selected_regions:
                        st.success(f"✓ {len(st.session_state.selected_regions)} region(s) selected")
                else:
                    st.warning("No region data available")
            except Exception as e:
                st.error(f"Error loading regions: {str(e)}")

    # Filter 3: Data Collection Period Dropdown (Searchable)
    with col3:
        st.markdown("#### Data Collection Period")
        with st.spinner("Loading data collection periods..."):
            try:
                period_df = get_data_collection_periods(client, TABLE_NAME)

                if period_df is not None and not period_df.empty:
                    # Create options with count badges
                    period_options = []
                    for _, row in period_df.iterrows():
                        period = row['data_collection_period']
                        count = row['survey_count']
                        period_options.append(f"{period} ({count:,})")

                    selected_periods_display = st.multiselect(
                        "Select data collection periods",
                        options=period_options,
                        default=[],
                        help="🔍 Searchable dropdown - Type to filter periods by name. Shows survey count for each period.",
                        label_visibility="collapsed",
                        placeholder="🔍 Search and select periods..."
                    )

                    # Extract actual period names from display format
                    st.session_state.selected_periods = [
                        opt.split(' (')[0] for opt in selected_periods_display
                    ]

                    # Show selection summary
                    if st.session_state.selected_periods:
                        st.success(f"✓ {len(st.session_state.selected_periods)} period(s) selected")
                else:
                    st.warning("No data collection period data available")
            except Exception as e:
                st.error(f"Error loading data collection periods: {str(e)}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Selected Data Collection Period Summary Table
    st.markdown('<div class="section-header"><h3>Selected Data Collection Period Summary</h3></div>', unsafe_allow_html=True)

    if st.session_state.selected_periods:
        with st.spinner("Loading summary data..."):
            try:
                summary_df = get_selected_periods_summary(
                    client,
                    TABLE_NAME,
                    st.session_state.selected_periods
                )

                if summary_df is not None and not summary_df.empty:
                    # Format the dataframe for display
                    summary_df = summary_df.rename(columns={
                        'data_collection_period': 'Data Collection Period',
                        'first_survey_date': 'First Survey Date',
                        'last_survey_date': 'Last Survey Date',
                        'survey_count': 'Survey Count'
                    })

                    # Format dates if they exist
                    if 'First Survey Date' in summary_df.columns:
                        summary_df['First Survey Date'] = pd.to_datetime(
                            summary_df['First Survey Date']
                        ).dt.strftime('%Y-%m-%d')
                    if 'Last Survey Date' in summary_df.columns:
                        summary_df['Last Survey Date'] = pd.to_datetime(
                            summary_df['Last Survey Date']
                        ).dt.strftime('%Y-%m-%d')

                    # Display the table
                    st.dataframe(
                        summary_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Survey Count": st.column_config.NumberColumn(
                                "Survey Count",
                                format="%d"
                            )
                        }
                    )

                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Periods Selected", len(summary_df))
                    with col2:
                        st.metric("Total Surveys", summary_df['Survey Count'].sum())
                    with col3:
                        if 'First Survey Date' in summary_df.columns:
                            earliest = summary_df['First Survey Date'].min()
                            st.metric("Earliest Survey", earliest)
                    with col4:
                        if 'Last Survey Date' in summary_df.columns:
                            latest = summary_df['Last Survey Date'].max()
                            st.metric("Latest Survey", latest)
                else:
                    st.info("No summary data available for selected periods")
            except Exception as e:
                st.error(f"Error loading summary data: {str(e)}")
    else:
        st.markdown("""
            <div class="info-box">
                <strong>💡 Tip:</strong> Select one or more data collection periods above to view the summary table.
            </div>
        """, unsafe_allow_html=True)

    # Summary of Facilities Surveyed Component
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>Summary of facilities surveyed</h3></div>', unsafe_allow_html=True)

    if st.session_state.selected_periods:
        with st.spinner("Loading facility statistics..."):
            try:
                # Build filters dict for database query
                filters = {
                    'data_collection_period': st.session_state.selected_periods,
                    'country': st.session_state.selected_countries if st.session_state.selected_countries else None,
                    'region': st.session_state.selected_regions if st.session_state.selected_regions else None
                }

                # Fetch facility statistics using optimized database query
                facility_stats = fetch_facility_statistics(client, TABLE_NAME, filters)

                if facility_stats is not None:
                    # Validate data integrity
                    is_valid, errors = validate_facility_stats(facility_stats)

                    if not is_valid:
                        st.warning("Data validation warnings detected:")
                        for error in errors:
                            st.warning(f"⚠️ {error}")

                    # Render the statistics tree with validated data
                    render_statistics_tree(facility_stats)

                    # Optional: Add a note below the tree
                    st.markdown("""
                        <div class="info-box" style="margin-top: 2rem;">
                            <strong>ℹ️ About this visualization:</strong><br>
                            This hierarchical tree shows the distribution of surveyed facilities across different sectors and levels of care.
                            The counts reflect the filters you've selected above (Country, Region, and Data Collection Period).
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No facility data available for the selected filters.")
            except Exception as e:
                st.error(f"Error loading facility statistics: {str(e)}")
    else:
        st.markdown("""
            <div class="info-box">
                <strong>💡 Tip:</strong> Select one or more data collection periods above to view the facility statistics tree.
            </div>
        """, unsafe_allow_html=True)

    # Insulin Availability - Overall Component
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>Insulin availability</h3></div>', unsafe_allow_html=True)
    st.markdown("#### Insulin availability - Overall")

    if st.session_state.selected_periods:
        # Build global filters dict
        global_filters = {
            'data_collection_period': st.session_state.selected_periods,
            'country': st.session_state.selected_countries if st.session_state.selected_countries else None,
            'region': st.session_state.selected_regions if st.session_state.selected_regions else None
        }

        # Two-column layout for local filters
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Region**")
            with st.spinner("Loading regions..."):
                region_df = get_insulin_regions(client, TABLE_NAME, global_filters)

                if region_df is not None and not region_df.empty:
                    # Build region options
                    region_data = []
                    for _, row in region_df.iterrows():
                        region = row['region']
                        count = row['facility_count']
                        region_data.append((region, count))

                    total_regions = len(region_data)

                    # Initialize checkboxes in session state (first time only)
                    # Streamlit's st.checkbox with key parameter handles session state automatically
                    for region, count in region_data:
                        checkbox_key = f"insulin_region_{region}"
                        if checkbox_key not in st.session_state:
                            st.session_state[checkbox_key] = True

                    # Count CURRENT selected items from session state (before rendering)
                    selected_count = sum(
                        1 for region, _ in region_data
                        if st.session_state.get(f"insulin_region_{region}", True)
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
                            checkbox_key = f"insulin_region_{region}"

                            # Display checkbox (uses Streamlit's automatic session state handling)
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

        with col2:
            st.markdown("**Sector**")
            with st.spinner("Loading sectors..."):
                sector_df = get_insulin_sectors(client, TABLE_NAME, global_filters, local_regions)

                if sector_df is not None and not sector_df.empty:
                    # Build sector options
                    sector_data = []
                    for _, row in sector_df.iterrows():
                        sector = row['sector']
                        count = row['facility_count']
                        sector_data.append((sector, count))

                    total_sectors = len(sector_data)

                    # Initialize checkboxes in session state (first time only)
                    # Streamlit's st.checkbox with key parameter handles session state automatically
                    for sector, count in sector_data:
                        checkbox_key = f"insulin_sector_{sector}"
                        if checkbox_key not in st.session_state:
                            st.session_state[checkbox_key] = True

                    # Count CURRENT selected items from session state (before rendering)
                    selected_count = sum(
                        1 for sector, _ in sector_data
                        if st.session_state.get(f"insulin_sector_{sector}", True)
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
                            checkbox_key = f"insulin_sector_{sector}"

                            # Display checkbox (uses Streamlit's automatic session state handling)
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

        # Fetch and display metrics
        st.markdown("<br>", unsafe_allow_html=True)

        with st.spinner("Loading insulin availability metrics..."):
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

    # Insulin Availability - By Sector Component
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("#### Insulin availability - By sector")

    if st.session_state.selected_periods:
        # Build global filters dict (reuse from Plan 3)
        global_filters = {
            'data_collection_period': st.session_state.selected_periods,
            'country': st.session_state.selected_countries if st.session_state.selected_countries else None,
            'region': st.session_state.selected_regions if st.session_state.selected_regions else None
        }

        # Single-column layout for Region filter
        st.markdown("**Region**")
        with st.spinner("Loading regions..."):
            region_df = get_insulin_by_sector_regions(client, TABLE_NAME, global_filters)

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
                    checkbox_key = f"insulin_by_sector_region_{region}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count CURRENT selected items from session state (before rendering)
                selected_count = sum(
                    1 for region, _ in region_data
                    if st.session_state.get(f"insulin_by_sector_region_{region}", True)
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
                        checkbox_key = f"insulin_by_sector_region_{region}"

                        # Display checkbox (uses Streamlit's automatic session state handling)
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

        # Fetch and display bar chart
        st.markdown("<br>", unsafe_allow_html=True)

        with st.spinner("Loading availability by sector data..."):
            chart_df = get_insulin_by_sector_chart_data(
                client,
                TABLE_NAME,
                global_filters,
                local_regions
            )

            if chart_df is not None and not chart_df.empty:
                # Ensure data types are correct
                chart_df['availability_percentage'] = pd.to_numeric(chart_df['availability_percentage'], errors='coerce')
                chart_df['total_facilities'] = pd.to_numeric(chart_df['total_facilities'], errors='coerce')
                chart_df['facilities_with_insulin'] = pd.to_numeric(chart_df['facilities_with_insulin'], errors='coerce')

                # Create bar chart using graph_objects for more control
                fig = go.Figure()

                fig.add_trace(go.Bar(
                    x=chart_df['sector'].tolist(),
                    y=chart_df['availability_percentage'].tolist(),
                    text=[f'{val:.1f}%' for val in chart_df['availability_percentage'].tolist()],
                    textposition='outside',
                    marker_color='#1f77b4',
                    hovertemplate='<b>%{x}</b><br>' +
                                  'Availability: %{y:.1f}%<br>' +
                                  'Facilities with Insulin: %{customdata[0]:,}<br>' +
                                  'Total Facilities: %{customdata[1]:,}<extra></extra>',
                    customdata=chart_df[['facilities_with_insulin', 'total_facilities']].values
                ))

                # Update layout
                fig.update_layout(
                    title='Facilities with Availability (%)',
                    xaxis_title='Sector',
                    yaxis_title='Availability (%)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=450,
                    yaxis=dict(
                        range=[0, 110],  # Slightly higher to accommodate text labels
                        ticksuffix='%'
                    ),
                    xaxis_tickangle=-45 if len(chart_df) > 5 else 0,  # Rotate labels if many sectors
                    showlegend=False,
                    margin=dict(t=50, b=100, l=50, r=50)
                )

                # Display chart
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available for the selected filters")

    else:
        st.markdown("""
            <div class="info-box">
                <strong>💡 Tip:</strong> Select one or more data collection periods above to view insulin availability by sector.
            </div>
        """, unsafe_allow_html=True)

    # Insulin Availability - By Insulin Type Component (Plan 5)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("#### Insulin availability - By insulin type")

    # Note: Plan 5 uses different table (adl_repeat_repivot)
    PLAN5_TABLE_NAME = config.TABLES["repeat_repivot"]

    if st.session_state.selected_periods:
        # Build global filters dict (reuse from Plan 3 & 4)
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
                region_df = get_insulin_by_type_regions(client, PLAN5_TABLE_NAME, global_filters)

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
                        checkbox_key = f"insulin_by_type_region_{region}"
                        if checkbox_key not in st.session_state:
                            st.session_state[checkbox_key] = True

                    # Count selected items from session state
                    selected_count = sum(
                        1 for region, _ in region_data
                        if st.session_state.get(f"insulin_by_type_region_{region}", True)
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
                            checkbox_key = f"insulin_by_type_region_{region}"

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
                sector_df = get_insulin_by_type_sectors(client, PLAN5_TABLE_NAME, global_filters)

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
                        checkbox_key = f"insulin_by_type_sector_{sector}"
                        if checkbox_key not in st.session_state:
                            st.session_state[checkbox_key] = True

                    # Count selected items from session state
                    selected_count = sum(
                        1 for sector, _ in sector_data
                        if st.session_state.get(f"insulin_by_type_sector_{sector}", True)
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
                            checkbox_key = f"insulin_by_type_sector_{sector}"

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

        # Two-column layout for charts
        st.markdown("<br>", unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns(2)

        # Chart 1: Human Insulin Types
        with chart_col1:
            st.markdown("**Human**")

            with st.spinner("Loading Human insulin data..."):
                # Fetch chart data
                human_df = get_insulin_by_type_human_chart_data(
                    client,
                    PLAN5_TABLE_NAME,
                    global_filters,
                    local_regions,
                    local_sectors
                )

                if human_df is not None and not human_df.empty:
                    # Ensure data types are correct
                    human_df['availability_percentage'] = pd.to_numeric(human_df['availability_percentage'], errors='coerce')
                    human_df['total_facilities'] = pd.to_numeric(human_df['total_facilities'], errors='coerce')
                    human_df['facilities_with_insulin'] = pd.to_numeric(human_df['facilities_with_insulin'], errors='coerce')

                    # Create bar chart using graph_objects
                    fig_human = go.Figure()

                    fig_human.add_trace(go.Bar(
                        x=human_df['insulin_type'].tolist(),
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
                        xaxis_title='Insulin Type',
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

        # Chart 2: Analogue Insulin Types
        with chart_col2:
            st.markdown("**Analogue**")

            with st.spinner("Loading Analogue insulin data..."):
                # Fetch chart data
                analogue_df = get_insulin_by_type_analogue_chart_data(
                    client,
                    PLAN5_TABLE_NAME,
                    global_filters,
                    local_regions,
                    local_sectors
                )

                if analogue_df is not None and not analogue_df.empty:
                    # Ensure data types are correct
                    analogue_df['availability_percentage'] = pd.to_numeric(analogue_df['availability_percentage'], errors='coerce')
                    analogue_df['total_facilities'] = pd.to_numeric(analogue_df['total_facilities'], errors='coerce')
                    analogue_df['facilities_with_insulin'] = pd.to_numeric(analogue_df['facilities_with_insulin'], errors='coerce')

                    # Create bar chart using graph_objects
                    fig_analogue = go.Figure()

                    fig_analogue.add_trace(go.Bar(
                        x=analogue_df['insulin_type'].tolist(),
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
                        xaxis_title='Insulin Type',
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
                <strong>💡 Tip:</strong> Select one or more data collection periods above to view insulin availability by insulin type.
            </div>
        """, unsafe_allow_html=True)

    # Insulin Availability - By Region Component (Plan 6)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("#### Insulin availability - By region")

    # Note: Plan 6 uses adl_surveys for sector dropdown and adl_repeat_repivot for charts
    PLAN6_SURVEYS_TABLE = config.TABLES["surveys"]
    PLAN6_REPIVOT_TABLE = config.TABLES["repeat_repivot"]

    if st.session_state.selected_periods:
        # Build global filters dict
        global_filters = {
            'data_collection_period': st.session_state.selected_periods,
            'country': st.session_state.selected_countries if st.session_state.selected_countries else None,
            'region': st.session_state.selected_regions if st.session_state.selected_regions else None
        }

        # Single-column layout for Sector filter
        st.markdown("**Sector**")
        with st.spinner("Loading sectors..."):
            sector_df = get_insulin_by_region_sectors(client, PLAN6_SURVEYS_TABLE, global_filters)

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
                    checkbox_key = f"insulin_by_region_sector_{sector}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items from session state
                selected_count = sum(
                    1 for sector, _ in sector_data
                    if st.session_state.get(f"insulin_by_region_sector_{sector}", True)
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
                        checkbox_key = f"insulin_by_region_sector_{sector}"

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

        # Two-column layout for charts
        st.markdown("<br>", unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns(2)

        # Chart 1: Human Insulin by Region
        with chart_col1:
            st.markdown("**Human**")

            with st.spinner("Loading Human insulin data by region..."):
                # Fetch chart data
                human_df = get_insulin_by_region_human_chart_data(
                    client,
                    PLAN6_REPIVOT_TABLE,
                    global_filters,
                    local_sectors
                )

                if human_df is not None and not human_df.empty:
                    # Ensure data types are correct
                    human_df['availability_percentage'] = pd.to_numeric(human_df['availability_percentage'], errors='coerce')
                    human_df['total_facilities'] = pd.to_numeric(human_df['total_facilities'], errors='coerce')
                    human_df['facilities_with_insulin'] = pd.to_numeric(human_df['facilities_with_insulin'], errors='coerce')

                    # Create bar chart using graph_objects
                    fig_human = go.Figure()

                    fig_human.add_trace(go.Bar(
                        x=human_df['region'].tolist(),
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
                        xaxis_title='Region',
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

        # Chart 2: Analogue Insulin by Region
        with chart_col2:
            st.markdown("**Analogue**")

            with st.spinner("Loading Analogue insulin data by region..."):
                # Fetch chart data
                analogue_df = get_insulin_by_region_analogue_chart_data(
                    client,
                    PLAN6_REPIVOT_TABLE,
                    global_filters,
                    local_sectors
                )

                if analogue_df is not None and not analogue_df.empty:
                    # Ensure data types are correct
                    analogue_df['availability_percentage'] = pd.to_numeric(analogue_df['availability_percentage'], errors='coerce')
                    analogue_df['total_facilities'] = pd.to_numeric(analogue_df['total_facilities'], errors='coerce')
                    analogue_df['facilities_with_insulin'] = pd.to_numeric(analogue_df['facilities_with_insulin'], errors='coerce')

                    # Create bar chart using graph_objects
                    fig_analogue = go.Figure()

                    fig_analogue.add_trace(go.Bar(
                        x=analogue_df['region'].tolist(),
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
                        xaxis_title='Region',
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
                <strong>💡 Tip:</strong> Select one or more data collection periods above to view insulin availability by region.
            </div>
        """, unsafe_allow_html=True)

    # Insulin Availability - Public Sector - By Level of Care Component (Plan 7)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("#### Insulin availability - Public sector - By level of care")

    # Note: Plan 7 uses adl_repeat_repivot table and implicitly filters for Public sector
    PLAN7_TABLE_NAME = config.TABLES["repeat_repivot"]

    if st.session_state.selected_periods:
        # Build global filters dict
        global_filters = {
            'data_collection_period': st.session_state.selected_periods,
            'country': st.session_state.selected_countries if st.session_state.selected_countries else None,
            'region': st.session_state.selected_regions if st.session_state.selected_regions else None
        }

        # Single-column layout for Region filter
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

        # Two-column layout for charts
        st.markdown("<br>", unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns(2)

        # Chart 1: Human Insulin by Level of Care
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
                    st.info("No data available for Human insulin types in Public sector")

        # Chart 2: Analogue Insulin by Level of Care
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
                    st.info("No data available for Analogue insulin types in Public sector")

    else:
        st.markdown("""
            <div class="info-box">
                <strong>💡 Tip:</strong> Select one or more data collection periods above to view insulin availability by level of care in the public sector.
            </div>
        """, unsafe_allow_html=True)

    # Insulin Availability - By INN Component (Plan 8)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("#### Insulin availability - By INN")

    # Note: Plan 8 uses adl_surveys for dropdowns, adl_repeat_repivot for chart
    PLAN8_SURVEYS_TABLE = config.TABLES["surveys"]
    PLAN8_REPIVOT_TABLE = config.TABLES["repeat_repivot"]

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
                region_df = get_insulin_by_inn_regions(client, PLAN8_SURVEYS_TABLE, global_filters)

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
                        checkbox_key = f"insulin_by_inn_region_{region}"
                        if checkbox_key not in st.session_state:
                            st.session_state[checkbox_key] = True

                    # Count selected items from session state
                    selected_count = sum(
                        1 for region, _ in region_data
                        if st.session_state.get(f"insulin_by_inn_region_{region}", True)
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
                            checkbox_key = f"insulin_by_inn_region_{region}"

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
                sector_df = get_insulin_by_inn_sectors(client, PLAN8_SURVEYS_TABLE, global_filters)

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
                        checkbox_key = f"insulin_by_inn_sector_{sector}"
                        if checkbox_key not in st.session_state:
                            st.session_state[checkbox_key] = True

                    # Count selected items from session state
                    selected_count = sum(
                        1 for sector, _ in sector_data
                        if st.session_state.get(f"insulin_by_inn_sector_{sector}", True)
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
                            checkbox_key = f"insulin_by_inn_sector_{sector}"

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

        # Fetch and display bar chart
        st.markdown("<br>", unsafe_allow_html=True)

        with st.spinner("Loading insulin availability by INN..."):
            chart_df = get_insulin_by_inn_chart_data(
                client,
                PLAN8_REPIVOT_TABLE,
                global_filters,
                local_regions,
                local_sectors
            )

            if chart_df is not None and not chart_df.empty:
                # Ensure data types are correct
                chart_df['availability_percentage'] = pd.to_numeric(chart_df['availability_percentage'], errors='coerce')
                chart_df['total_facilities'] = pd.to_numeric(chart_df['total_facilities'], errors='coerce')
                chart_df['facilities_with_insulin'] = pd.to_numeric(chart_df['facilities_with_insulin'], errors='coerce')

                # Create bar chart using graph_objects
                fig = go.Figure()

                fig.add_trace(go.Bar(
                    x=chart_df['insulin_inn'].tolist(),
                    y=chart_df['availability_percentage'].tolist(),
                    text=[f'{val:.1f}%' for val in chart_df['availability_percentage'].tolist()],
                    textposition='outside',
                    marker_color='#1f77b4',
                    hovertemplate='<b>%{x}</b><br>' +
                                  'Availability: %{y:.1f}%<br>' +
                                  'Available Facilities: %{customdata[0]:,}<br>' +
                                  'Total Facilities: %{customdata[1]:,}<extra></extra>',
                    customdata=chart_df[['facilities_with_insulin', 'total_facilities']].values
                ))

                # Update layout
                fig.update_layout(
                    title='Facilities with Availability (%)',
                    xaxis_title='Insulin INN',
                    yaxis_title='Facilities with Availability (%)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=450,
                    yaxis=dict(
                        range=[0, 110],
                        ticksuffix='%'
                    ),
                    xaxis_tickangle=-45,  # Always angle labels for readability
                    showlegend=False,
                    margin=dict(t=50, b=100, l=50, r=50)
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
                <strong>💡 Tip:</strong> Select one or more data collection periods above to view insulin availability by INN.
            </div>
        """, unsafe_allow_html=True)

    # Insulin - Top 10 Brands Component (Plan 9)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("#### Insulin - Top 10 brands")

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

    # Insulin Availability - By Presentation and Insulin Type Component (Plan 10)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("#### Insulin availability - By presentation and insulin type")

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

    # Insulin Availability - By Originator Brands VS Biosimilars Component (Plan 11)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("#### Insulin availability - By originator brands VS biosimilars")

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
                        f"Select Regions ({selected_count}/{total_regions} selected)",
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
                        f"Select Sectors ({selected_count}/{total_sectors} selected)",
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

        # Fetch metrics
        st.markdown("<br>", unsafe_allow_html=True)

        # Two-column layout for scorecards
        scorecard_col1, scorecard_col2 = st.columns(2)

        # Column 1: Human Insulin
        with scorecard_col1:
            st.markdown('<div style="text-align: center; padding: 0.5rem; background: #e3f2fd; border-radius: 5px; margin-bottom: 1rem;"><strong>Insulin Type - Human</strong></div>', unsafe_allow_html=True)

            # Metric 1: Originator Brands
            with st.spinner("Loading Human Originator data..."):
                human_originator_metric = get_insulin_human_originator_metric(
                    client,
                    PLAN11_REPIVOT_TABLE,
                    global_filters,
                    local_regions,
                    local_sectors
                )

                if human_originator_metric is not None:
                    st.markdown(f"""
                        <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1rem; border-left: 4px solid #1f77b4;">
                            <div style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;">Facilities with Originator Brands (%)</div>
                            <div style="color: #1f77b4; font-size: 2rem; font-weight: bold;">{human_originator_metric:.1f}%</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No data available")

            # Metric 2: Biosimilars
            with st.spinner("Loading Human Biosimilar data..."):
                human_biosimilar_metric = get_insulin_human_biosimilar_metric(
                    client,
                    PLAN11_REPIVOT_TABLE,
                    global_filters,
                    local_regions,
                    local_sectors
                )

                if human_biosimilar_metric is not None:
                    st.markdown(f"""
                        <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #1f77b4;">
                            <div style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;">Facilities with Biosimilars (%)</div>
                            <div style="color: #1f77b4; font-size: 2rem; font-weight: bold;">{human_biosimilar_metric:.1f}%</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No data available")

        # Column 2: Analogue Insulin
        with scorecard_col2:
            st.markdown('<div style="text-align: center; padding: 0.5rem; background: #fff3e0; border-radius: 5px; margin-bottom: 1rem;"><strong>Insulin Type - Analogue</strong></div>', unsafe_allow_html=True)

            # Metric 3: Originator Brands
            with st.spinner("Loading Analogue Originator data..."):
                analogue_originator_metric = get_insulin_analogue_originator_metric(
                    client,
                    PLAN11_REPIVOT_TABLE,
                    global_filters,
                    local_regions,
                    local_sectors
                )

                if analogue_originator_metric is not None:
                    st.markdown(f"""
                        <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1rem; border-left: 4px solid #ff7f0e;">
                            <div style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;">Facilities with Originator Brands (%)</div>
                            <div style="color: #ff7f0e; font-size: 2rem; font-weight: bold;">{analogue_originator_metric:.1f}%</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No data available")

            # Metric 4: Biosimilars
            with st.spinner("Loading Analogue Biosimilar data..."):
                analogue_biosimilar_metric = get_insulin_analogue_biosimilar_metric(
                    client,
                    PLAN11_REPIVOT_TABLE,
                    global_filters,
                    local_regions,
                    local_sectors
                )

                if analogue_biosimilar_metric is not None:
                    st.markdown(f"""
                        <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #ff7f0e;">
                            <div style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;">Facilities with Biosimilars (%)</div>
                            <div style="color: #ff7f0e; font-size: 2rem; font-weight: bold;">{analogue_biosimilar_metric:.1f}%</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No data available")

    else:
        st.markdown("""
            <div class="info-box">
                <strong>💡 Tip:</strong> Select one or more data collection periods above to view insulin availability by originator brands and biosimilars.
            </div>
        """, unsafe_allow_html=True)

    # Insulin Availability - Availability of Comparator Medicine Component (Plan 12)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("#### Insulin availability - Availability of comparator medicine")

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

                # Display table with centered alignment
                st.dataframe(
                    paginated_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Name": st.column_config.TextColumn(
                            "Name",
                            width="medium",
                        ),
                        "Strength (mg)": st.column_config.TextColumn(
                            "Strength (mg)",
                            width="medium",
                        ),
                        "Facilities with Availability (%)": st.column_config.TextColumn(
                            "Facilities with Availability (%)",
                            width="medium",
                        )
                    }
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

# Tab 2: Price Analysis - Phase 1 Implementation
with tab2:
    # Main Page Heading
    st.title("Insulin Price Analysis")
    st.markdown("<br>", unsafe_allow_html=True)

    # Two-Column Layout: Instructions and Definitions
    col_left, col_right = st.columns([1.1, 1])

    with col_left:
        # Instructions Section
        st.markdown("### Instructions:")

        # Red alert text
        st.error("**To begin select a Data Collection Period (data not shown by default)**")

        # Region selection instruction
        st.markdown("""
        *Selecting a region:* By default, all regions are displayed. You can select one or more regions by using the Region selection box, this will apply for all graphs under the same heading.
        """)

        # Currency instruction
        st.markdown("""
        *Currency:* By default, results are displayed in local currency. To select USD, see below.
        """)

        # User Guide link
        st.markdown("""
        For more see the [User Guide](https://accisstoolkit.haiweb.org/user-guide/)
        """)

        # Optional Metrics Info Box
        st.info("""
        ⚙️ **Optional metrics** - many graphs and scorecards have optional metrics, such as the number of facilities or the price in USD. If available the button is shown in the top right corner of the graph. Click on this to choose which metric to show, or show multiple for comparison.
        """)

    with col_right:
        # Definitions Section
        st.markdown("### Definitions:")

        st.markdown("""
        *Insulin Price* - Standardised in all cases to 1000IU.
        """)

        st.markdown("""
        *Facilities (n)* - Number of facilities within a certain category.
        """)

        st.markdown("""
        *Reported Responses (%)* - Percentage out of all reported responses (products, places, etc.) in a certain category.
        """)

        st.markdown("""
        *Reported Responses (n)* - Number of responses (products, places, etc.) reported in a certain category.
        """)

        st.markdown("""
        *INN*: International Nonproprietary Name
        """)

    # Data Selectors Section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>Data Selectors</h3></div>', unsafe_allow_html=True)

    # Create three columns for the filter dropdowns
    col1, col2, col3 = st.columns(3)

    # Filter 1: Country Dropdown
    with col1:
        st.markdown("#### Country")
        with st.spinner("Loading countries..."):
            try:
                country_df = get_grouped_counts(client, TABLE_NAME, "country")

                if country_df is not None and not country_df.empty:
                    # Create options with count badges
                    country_options = []
                    for _, row in country_df.iterrows():
                        country = row['country']
                        count = row['survey_count']
                        country_options.append(f"{country} ({count:,})")

                    selected_countries_display = st.multiselect(
                        "Select countries",
                        options=country_options,
                        default=[],
                        help="Filter by country - showing survey count per country",
                        label_visibility="collapsed",
                        key="price_country_filter"
                    )

                    # Extract actual country names from display format
                    st.session_state.selected_countries_price = [
                        opt.split(' (')[0] for opt in selected_countries_display
                    ]

                    # Show selection summary
                    if st.session_state.selected_countries_price:
                        st.success(f"✓ {len(st.session_state.selected_countries_price)} country(ies) selected")
                else:
                    st.warning("No country data available")
            except Exception as e:
                st.error(f"Error loading countries: {str(e)}")

    # Filter 2: Region Dropdown
    with col2:
        st.markdown("#### Region")
        with st.spinner("Loading regions..."):
            try:
                region_df = get_grouped_counts(client, TABLE_NAME, "region")

                if region_df is not None and not region_df.empty:
                    # Create options with count badges
                    region_options = []
                    for _, row in region_df.iterrows():
                        region = row['region']
                        count = row['survey_count']
                        region_options.append(f"{region} ({count:,})")

                    selected_regions_display = st.multiselect(
                        "Select regions",
                        options=region_options,
                        default=[],
                        help="Filter by region - showing survey count per region",
                        label_visibility="collapsed",
                        key="price_region_filter"
                    )

                    # Extract actual region names from display format
                    st.session_state.selected_regions_price = [
                        opt.split(' (')[0] for opt in selected_regions_display
                    ]

                    # Show selection summary
                    if st.session_state.selected_regions_price:
                        st.success(f"✓ {len(st.session_state.selected_regions_price)} region(s) selected")
                else:
                    st.warning("No region data available")
            except Exception as e:
                st.error(f"Error loading regions: {str(e)}")

    # Filter 3: Data Collection Period Dropdown
    with col3:
        st.markdown("#### Data Collection Period")
        with st.spinner("Loading data collection periods..."):
            try:
                period_df = get_data_collection_periods(client, TABLE_NAME)

                if period_df is not None and not period_df.empty:
                    # Create options with count badges
                    period_options = []
                    for _, row in period_df.iterrows():
                        period = row['data_collection_period']
                        count = row['survey_count']
                        period_options.append(f"{period} ({count:,})")

                    selected_periods_display = st.multiselect(
                        "Select data collection periods",
                        options=period_options,
                        default=[],
                        help="🔍 Searchable dropdown - Type to filter periods by name. Shows survey count for each period.",
                        label_visibility="collapsed",
                        placeholder="🔍 Search and select periods...",
                        key="price_period_filter"
                    )

                    # Extract actual period names from display format
                    st.session_state.selected_periods_price = [
                        opt.split(' (')[0] for opt in selected_periods_display
                    ]

                    # Show selection summary
                    if st.session_state.selected_periods_price:
                        st.success(f"✓ {len(st.session_state.selected_periods_price)} period(s) selected")
                else:
                    st.warning("No data collection period data available")
            except Exception as e:
                st.error(f"Error loading data collection periods: {str(e)}")

    # Default State Message
    st.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.selected_periods_price:
        st.markdown("""
            <div class="info-box">
                <strong>💡 Data is not shown by default.</strong><br>
                Use the dropdown menu above to select a Data Collection Period and see the data.
            </div>
        """, unsafe_allow_html=True)
    else:
        # Phase 2: Price Visualizations Section
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header"><h3>Where patients were charged the full price</h3></div>', unsafe_allow_html=True)

        # Information paragraph
        st.markdown("""
        Insulin price is standardised in all cases to 1000IU. Click on the optional metrics button
        to see the number of products that make up the median price.
        """)

        # Local filters for price analysis
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

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

        # Chart 1: Median price by insulin type
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Median price - By insulin type")

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

                # Calculate dynamic y-axis range based on max value
                max_price = chart_df['median_price_local'].max()
                y_axis_max = max_price * 1.15  # Add 15% padding for text labels

                # Update layout
                fig.update_layout(
                    title='Median Price by Insulin Type',
                    xaxis_title='Insulin Type',
                    yaxis_title='Median Price - Local',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=500,
                    yaxis=dict(
                        range=[0, y_axis_max],
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

        # Chart 2: Median price by insulin type and level of care
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Median price - By insulin type and level of care (public sector only)")

        with st.spinner("Loading median price by level of care data..."):
            chart_df = get_median_price_by_type_levelcare(client, config.TABLES["surveys_repeat"], price_filters)

            if chart_df is not None and not chart_df.empty:
                # Get unique levels of care dynamically from the data
                unique_levels = sorted(chart_df['level_of_care'].unique())

                # Define color palette for different levels
                color_palette = {
                    'Primary': '#2ca02c',
                    'Secondary': '#1f77b4',
                    'Tertiary': '#ff7f0e'
                }

                # Create Plotly grouped bar chart
                fig = go.Figure()

                # Add bar traces dynamically for each level of care
                for level in unique_levels:
                    level_df = chart_df[chart_df['level_of_care'] == level]

                    if not level_df.empty:
                        # Use predefined color or default to a fallback color
                        bar_color = color_palette.get(level, '#d62728')

                        fig.add_trace(go.Bar(
                            x=level_df['insulin_type'].tolist(),
                            y=level_df['median_price_local'].tolist(),
                            name=level,
                            marker_color=bar_color,
                            text=[f'{val:,.0f}' for val in level_df['median_price_local'].tolist()],
                            textposition='outside',
                            hovertemplate='<b>%{x}</b><br>' +
                                          f'Level: {level}<br>' +
                                          'Median Price: %{y:,.2f}<br>' +
                                          'Products: %{customdata}<extra></extra>',
                            customdata=level_df['product_count'].tolist()
                        ))

                # Calculate dynamic y-axis range based on max value
                max_price = chart_df['median_price_local'].max()
                y_axis_max = max_price * 1.15  # Add 15% padding for text labels

                # Update layout
                fig.update_layout(
                    title='Median Price by Insulin Type and Level of Care (Public Sector)',
                    xaxis_title='Insulin Type',
                    yaxis_title='Median Price - Local',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=500,
                    yaxis=dict(
                        range=[0, y_axis_max],
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

    # ====================================
    # Phase 3: Price - By INN Section
    # ====================================

    # Section Header
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>Price - By INN</h3></div>', unsafe_allow_html=True)

    # Local Filters: Region and Sector
    st.markdown("<br>", unsafe_allow_html=True)
    col1_inn, col2_inn = st.columns(2)

    with col1_inn:
        st.markdown("**Region**")
        with st.spinner("Loading regions..."):
            # Build global filters dict from session state
            global_filters_inn = {
                'data_collection_period': st.session_state.selected_periods_price,
                'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None
            }

            region_df_inn = get_price_regions(client, config.TABLES["surveys_repeat"], global_filters_inn)

            if region_df_inn is not None and not region_df_inn.empty:
                # Build region options with counts
                region_data_inn = []
                for _, row in region_df_inn.iterrows():
                    region = row['region']
                    count = row['facility_count']
                    region_data_inn.append((region, count))

                total_regions_inn = len(region_data_inn)

                # Initialize checkboxes in session state
                for region, count in region_data_inn:
                    checkbox_key = f"price_inn_region_{region}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items
                selected_count_inn = sum(
                    1 for region, _ in region_data_inn
                    if st.session_state.get(f"price_inn_region_{region}", True)
                )
                excluded_count_inn = total_regions_inn - selected_count_inn

                # Create expander with selection summary
                with st.expander(
                    f"Select Regions ({selected_count_inn}/{total_regions_inn} selected)",
                    expanded=False
                ):
                    if excluded_count_inn > 0:
                        st.caption(f"🚫 {excluded_count_inn} item{'s' if excluded_count_inn != 1 else ''} excluded")

                    # Create checkboxes
                    local_regions_inn = []
                    for region, count in region_data_inn:
                        checkbox_key = f"price_inn_region_{region}"
                        is_checked = st.checkbox(
                            f"{region} ({count:,})",
                            value=st.session_state.get(checkbox_key, True),
                            key=checkbox_key
                        )
                        if is_checked:
                            local_regions_inn.append(region)
            else:
                local_regions_inn = []
                st.info("No region data available")

    with col2_inn:
        st.markdown("**Sector**")
        with st.spinner("Loading sectors..."):
            sector_df_inn = get_price_sectors(client, config.TABLES["surveys_repeat"], global_filters_inn, local_regions_inn)

            if sector_df_inn is not None and not sector_df_inn.empty:
                # Build sector options with counts
                sector_data_inn = []
                for _, row in sector_df_inn.iterrows():
                    sector = row['sector']
                    count = row['facility_count']
                    sector_data_inn.append((sector, count))

                total_sectors_inn = len(sector_data_inn)

                # Initialize checkboxes in session state
                for sector, count in sector_data_inn:
                    checkbox_key = f"price_inn_sector_{sector}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items
                selected_count_inn_sec = sum(
                    1 for sector, _ in sector_data_inn
                    if st.session_state.get(f"price_inn_sector_{sector}", True)
                )
                excluded_count_inn_sec = total_sectors_inn - selected_count_inn_sec

                # Create expander with selection summary
                with st.expander(
                    f"Select Sectors ({selected_count_inn_sec}/{total_sectors_inn} selected)",
                    expanded=False
                ):
                    if excluded_count_inn_sec > 0:
                        st.caption(f"🚫 {excluded_count_inn_sec} item{'s' if excluded_count_inn_sec != 1 else ''} excluded")

                    # Create checkboxes
                    local_sectors_inn = []
                    for sector, count in sector_data_inn:
                        checkbox_key = f"price_inn_sector_{sector}"
                        is_checked = st.checkbox(
                            f"{sector} ({count:,})",
                            value=st.session_state.get(checkbox_key, True),
                            key=checkbox_key
                        )
                        if is_checked:
                            local_sectors_inn.append(sector)
            else:
                local_sectors_inn = []
                st.info("No sector data available")

    # Chart: Price - By INN (Line Chart)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Price - By INN")

    with st.spinner("Loading price by INN data..."):
        # Prepare filters
        inn_price_filters = {
            'data_collection_period': st.session_state.selected_periods_price,
            'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None,
            'region': local_regions_inn if local_regions_inn else None,
            'sector': local_sectors_inn if local_sectors_inn else None
        }

        chart_df_inn = get_price_by_inn(client, config.TABLES["surveys_repeat"], inn_price_filters)

        if chart_df_inn is not None and not chart_df_inn.empty:
            # Create Plotly scatter chart (dots only)
            fig_inn = go.Figure()

            # Calculate dynamic Y-axis range
            max_price = chart_df_inn['max_price_local'].max()
            y_axis_max = max_price * 1.15  # Add 15% padding at top

            # Add Min Price dots
            fig_inn.add_trace(go.Scatter(
                x=chart_df_inn['insulin_inn'].tolist(),
                y=chart_df_inn['min_price_local'].tolist(),
                name='Min Price-Local',
                mode='markers',
                marker=dict(size=10, symbol='circle', color='#2ca02c'),
                hovertemplate='<b>%{x}</b><br>' +
                              'Min Price: %{y:,.2f}<br>' +
                              '<extra></extra>'
            ))

            # Add Median Price dots with text labels
            fig_inn.add_trace(go.Scatter(
                x=chart_df_inn['insulin_inn'].tolist(),
                y=chart_df_inn['median_price_local'].tolist(),
                name='Median Price-Local',
                mode='markers+text',
                marker=dict(size=10, symbol='circle', color='#1f77b4'),
                text=[f'{val:,.0f}' for val in chart_df_inn['median_price_local'].tolist()],
                textposition='top center',
                hovertemplate='<b>%{x}</b><br>' +
                              'Median Price: %{y:,.2f}<br>' +
                              '<extra></extra>'
            ))

            # Add Max Price dots
            fig_inn.add_trace(go.Scatter(
                x=chart_df_inn['insulin_inn'].tolist(),
                y=chart_df_inn['max_price_local'].tolist(),
                name='Max Price-Local',
                mode='markers',
                marker=dict(size=10, symbol='circle', color='#d62728'),
                hovertemplate='<b>%{x}</b><br>' +
                              'Max Price: %{y:,.2f}<br>' +
                              '<extra></extra>'
            ))

            # Update layout
            fig_inn.update_layout(
                title='Price by INN Category',
                xaxis_title='INN Category',
                yaxis_title='Price - Local',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=500,
                yaxis=dict(
                    range=[0, y_axis_max],
                    tickformat=',.0f'
                ),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(t=80, b=80, l=60, r=40),
                hovermode='closest'
            )

            # Display chart
            st.plotly_chart(fig_inn, use_container_width=True)

            # Add informational note below chart
            st.markdown("""
            <div style="text-align: left;" align="left">
                <strong>NOTE:</strong> Label shown for median price only. Hover over points on the chart to see all values.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No price by INN data available for the selected filters")

    # ====================================
    # Phase 4: Price - By Brand Section
    # ====================================

    # Section Header
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>Price - By Brand</h3></div>', unsafe_allow_html=True)

    # Local Filters: Region and Sector
    st.markdown("<br>", unsafe_allow_html=True)
    col1_brand, col2_brand = st.columns(2)

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

    # Tables: Human and Analogue side by side
    st.markdown("<br>", unsafe_allow_html=True)
    col_human, col_analogue = st.columns(2)

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

    # ====================================
    # Phase 5: Median price - By presentation Section
    # ====================================

    # Section Header
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>Median price - By presentation</h3></div>', unsafe_allow_html=True)

    # Local Filters: Region and Sector
    st.markdown("<br>", unsafe_allow_html=True)
    col1_pres, col2_pres = st.columns(2)

    with col1_pres:
        st.markdown("**Region**")
        with st.spinner("Loading regions..."):
            # Build global filters dict from session state
            global_filters_pres = {
                'data_collection_period': st.session_state.selected_periods_price,
                'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None
            }

            region_df_pres = get_price_regions(client, config.TABLES["surveys_repeat"], global_filters_pres)

            if region_df_pres is not None and not region_df_pres.empty:
                # Build region options with counts
                region_data_pres = []
                for _, row in region_df_pres.iterrows():
                    region = row['region']
                    count = row['facility_count']
                    region_data_pres.append((region, count))

                total_regions_pres = len(region_data_pres)

                # Initialize checkboxes in session state
                for region, count in region_data_pres:
                    checkbox_key = f"price_pres_region_{region}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items
                selected_count_pres = sum(
                    1 for region, _ in region_data_pres
                    if st.session_state.get(f"price_pres_region_{region}", True)
                )
                excluded_count_pres = total_regions_pres - selected_count_pres

                # Create expander with selection summary
                with st.expander(
                    f"Select Regions ({selected_count_pres}/{total_regions_pres} selected)",
                    expanded=False
                ):
                    if excluded_count_pres > 0:
                        st.caption(f"🚫 {excluded_count_pres} item{'s' if excluded_count_pres != 1 else ''} excluded")

                    # Create checkboxes
                    local_regions_pres = []
                    for region, count in region_data_pres:
                        checkbox_key = f"price_pres_region_{region}"
                        is_checked = st.checkbox(
                            f"{region} ({count:,})",
                            value=st.session_state.get(checkbox_key, True),
                            key=checkbox_key
                        )
                        if is_checked:
                            local_regions_pres.append(region)
            else:
                local_regions_pres = []
                st.info("No region data available")

    with col2_pres:
        st.markdown("**Sector**")
        with st.spinner("Loading sectors..."):
            sector_df_pres = get_price_sectors(client, config.TABLES["surveys_repeat"], global_filters_pres, local_regions_pres)

            if sector_df_pres is not None and not sector_df_pres.empty:
                # Build sector options with counts
                sector_data_pres = []
                for _, row in sector_df_pres.iterrows():
                    sector = row['sector']
                    count = row['facility_count']
                    sector_data_pres.append((sector, count))

                total_sectors_pres = len(sector_data_pres)

                # Initialize checkboxes in session state
                for sector, count in sector_data_pres:
                    checkbox_key = f"price_pres_sector_{sector}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items
                selected_count_pres_sec = sum(
                    1 for sector, _ in sector_data_pres
                    if st.session_state.get(f"price_pres_sector_{sector}", True)
                )
                excluded_count_pres_sec = total_sectors_pres - selected_count_pres_sec

                # Create expander with selection summary
                with st.expander(
                    f"Select Sectors ({selected_count_pres_sec}/{total_sectors_pres} selected)",
                    expanded=False
                ):
                    if excluded_count_pres_sec > 0:
                        st.caption(f"🚫 {excluded_count_pres_sec} item{'s' if excluded_count_pres_sec != 1 else ''} excluded")

                    # Create checkboxes
                    local_sectors_pres = []
                    for sector, count in sector_data_pres:
                        checkbox_key = f"price_pres_sector_{sector}"
                        is_checked = st.checkbox(
                            f"{sector} ({count:,})",
                            value=st.session_state.get(checkbox_key, True),
                            key=checkbox_key
                        )
                        if is_checked:
                            local_sectors_pres.append(sector)
            else:
                local_sectors_pres = []
                st.info("No sector data available")

    # Chart: Median price - By presentation (Clustered Bar Chart)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Median price - By presentation")

    with st.spinner("Loading median price by presentation data..."):
        # Prepare filters
        pres_price_filters = {
            'data_collection_period': st.session_state.selected_periods_price,
            'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None,
            'region': local_regions_pres if local_regions_pres else None,
            'sector': local_sectors_pres if local_sectors_pres else None
        }

        chart_df_pres = get_median_price_by_presentation(client, config.TABLES["surveys_repeat"], pres_price_filters)

        if chart_df_pres is not None and not chart_df_pres.empty:
            # Create Plotly bar chart
            fig_pres = go.Figure()

            # Calculate dynamic Y-axis range
            max_price = chart_df_pres['median_price_local'].max()
            y_axis_max = max_price * 1.15  # Add 15% padding at top

            # Add bar trace
            fig_pres.add_trace(go.Bar(
                x=chart_df_pres['insulin_presentation'].tolist(),
                y=chart_df_pres['median_price_local'].tolist(),
                name='Median Price-Local',
                marker=dict(
                    color='#17becf',  # Teal color
                    line=dict(color='#0e7c8f', width=1)
                ),
                text=[f'{val:,.0f}' for val in chart_df_pres['median_price_local'].tolist()],
                textposition='outside',
                textfont=dict(size=11),
                hovertemplate='<b>%{x}</b><br>' +
                              'Median Price: %{y:,.2f}<br>' +
                              '<extra></extra>'
            ))

            # Update layout
            fig_pres.update_layout(
                title='Median Price by Insulin Presentation',
                xaxis_title='Insulin Presentation',
                yaxis_title='Median price - Local',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=500,
                xaxis=dict(
                    tickangle=-45,  # Angle labels for readability
                    tickfont=dict(size=11)
                ),
                yaxis=dict(
                    range=[0, y_axis_max],
                    tickformat=',.0f'
                ),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(t=80, b=120, l=60, r=40),
                hovermode='closest'
            )

            # Display chart
            st.plotly_chart(fig_pres, use_container_width=True)
        else:
            st.info("No median price by presentation data available for the selected filters")

    # Phase 6: Median price - By originator brands and biosimilars Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3>Median price - By originator brands and biosimilars</h3></div>', unsafe_allow_html=True)

    # Local filters for Originator/Biosimilar price analysis
    st.markdown("<br>", unsafe_allow_html=True)
    col1_orig, col2_orig = st.columns(2)

    # Region Checkbox Filter (Column 1)
    with col1_orig:
        st.markdown("**Region**")
        with st.spinner("Loading regions..."):
            # Build global filters dict from session state
            global_filters_orig = {
                'data_collection_period': st.session_state.selected_periods_price,
                'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None
            }

            region_df_orig = get_price_regions(client, config.TABLES["surveys_repeat"], global_filters_orig)

            if region_df_orig is not None and not region_df_orig.empty:
                # Build region options with counts
                region_data_orig = []
                for _, row in region_df_orig.iterrows():
                    region = row['region']
                    count = row['facility_count']
                    region_data_orig.append((region, count))

                total_regions_orig = len(region_data_orig)

                # Initialize checkboxes in session state
                for region, count in region_data_orig:
                    checkbox_key = f"price_orig_region_{region}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items
                selected_count_orig = sum(
                    1 for region, _ in region_data_orig
                    if st.session_state.get(f"price_orig_region_{region}", True)
                )
                excluded_count_orig = total_regions_orig - selected_count_orig

                # Create expander with selection summary
                with st.expander(
                    f"Select Regions ({selected_count_orig}/{total_regions_orig} selected)",
                    expanded=False
                ):
                    if excluded_count_orig > 0:
                        st.caption(f"🚫 {excluded_count_orig} item{'s' if excluded_count_orig != 1 else ''} excluded")

                    # Create checkboxes
                    local_regions_orig = []
                    for region, count in region_data_orig:
                        checkbox_key = f"price_orig_region_{region}"
                        is_checked = st.checkbox(
                            f"{region} ({count:,})",
                            value=st.session_state.get(checkbox_key, True),
                            key=checkbox_key
                        )
                        if is_checked:
                            local_regions_orig.append(region)
            else:
                local_regions_orig = []
                st.info("No region data available")

    # Sector Checkbox Filter (Column 2)
    with col2_orig:
        st.markdown("**Sector**")
        with st.spinner("Loading sectors..."):
            sector_df_orig = get_price_sectors(client, config.TABLES["surveys_repeat"], global_filters_orig, local_regions_orig)

            if sector_df_orig is not None and not sector_df_orig.empty:
                # Build sector options with counts
                sector_data_orig = []
                for _, row in sector_df_orig.iterrows():
                    sector = row['sector']
                    count = row['facility_count']
                    sector_data_orig.append((sector, count))

                total_sectors_orig = len(sector_data_orig)

                # Initialize checkboxes in session state
                for sector, count in sector_data_orig:
                    checkbox_key = f"price_orig_sector_{sector}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = True

                # Count selected items
                selected_count_orig_sec = sum(
                    1 for sector, _ in sector_data_orig
                    if st.session_state.get(f"price_orig_sector_{sector}", True)
                )
                excluded_count_orig_sec = total_sectors_orig - selected_count_orig_sec

                # Create expander with selection summary
                with st.expander(
                    f"Select Sectors ({selected_count_orig_sec}/{total_sectors_orig} selected)",
                    expanded=False
                ):
                    if excluded_count_orig_sec > 0:
                        st.caption(f"🚫 {excluded_count_orig_sec} item{'s' if excluded_count_orig_sec != 1 else ''} excluded")

                    # Create checkboxes
                    local_sectors_orig = []
                    for sector, count in sector_data_orig:
                        checkbox_key = f"price_orig_sector_{sector}"
                        is_checked = st.checkbox(
                            f"{sector} ({count:,})",
                            value=st.session_state.get(checkbox_key, True),
                            key=checkbox_key
                        )
                        if is_checked:
                            local_sectors_orig.append(sector)
            else:
                local_sectors_orig = []
                st.info("No sector data available")

    # Charts: Human and Analogue side by side
    st.markdown("<br>", unsafe_allow_html=True)
    col_human_orig, col_analogue_orig = st.columns(2)

    # Human Insulin Chart (Left Column)
    with col_human_orig:
        st.markdown("#### Human Insulin - Originator vs Biosimilar")

        with st.spinner("Loading human insulin originator/biosimilar data..."):
            # Prepare filters
            orig_filters_human = {
                'data_collection_period': st.session_state.selected_periods_price,
                'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None,
                'region': local_regions_orig if local_regions_orig else None,
                'sector': local_sectors_orig if local_sectors_orig else None
            }

            chart_df_human_orig = get_median_price_by_originator_human(client, config.TABLES["surveys_repeat"], orig_filters_human)

            if chart_df_human_orig is not None and not chart_df_human_orig.empty:
                # Create Plotly bar chart
                fig_human_orig = go.Figure()

                # Calculate dynamic Y-axis range
                max_price = chart_df_human_orig['median_price_local'].max()
                y_axis_max = max_price * 1.15  # Add 15% padding at top

                # Add bar trace
                fig_human_orig.add_trace(go.Bar(
                    x=chart_df_human_orig['insulin_originator_biosimilar'].tolist(),
                    y=chart_df_human_orig['median_price_local'].tolist(),
                    name='Median Price-Local',
                    marker=dict(
                        color='#17becf',  # Teal color
                        line=dict(color='#0e7c8f', width=1)
                    ),
                    text=[f'{val:,.0f}' for val in chart_df_human_orig['median_price_local'].tolist()],
                    textposition='outside',
                    textfont=dict(size=11),
                    hovertemplate='<b>%{x}</b><br>' +
                                  'Median Price: %{y:,.2f}<br>' +
                                  '<extra></extra>'
                ))

                # Update layout
                fig_human_orig.update_layout(
                    xaxis_title='Type',
                    yaxis_title='Median price - Local',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=450,
                    yaxis=dict(
                        range=[0, y_axis_max],
                        tickformat=',.0f'
                    ),
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    margin=dict(t=40, b=60, l=60, r=20),
                    hovermode='closest'
                )

                # Display chart
                st.plotly_chart(fig_human_orig, use_container_width=True)
            else:
                st.info("No human insulin originator/biosimilar data available for the selected filters")

    # Analogue Insulin Chart (Right Column)
    with col_analogue_orig:
        st.markdown("#### Analogue Insulin - Originator vs Biosimilar")

        with st.spinner("Loading analogue insulin originator/biosimilar data..."):
            # Prepare filters
            orig_filters_analogue = {
                'data_collection_period': st.session_state.selected_periods_price,
                'country': st.session_state.selected_countries_price if st.session_state.selected_countries_price else None,
                'region': local_regions_orig if local_regions_orig else None,
                'sector': local_sectors_orig if local_sectors_orig else None
            }

            chart_df_analogue_orig = get_median_price_by_originator_analogue(client, config.TABLES["surveys_repeat"], orig_filters_analogue)

            if chart_df_analogue_orig is not None and not chart_df_analogue_orig.empty:
                # Create Plotly bar chart
                fig_analogue_orig = go.Figure()

                # Calculate dynamic Y-axis range
                max_price = chart_df_analogue_orig['median_price_local'].max()
                y_axis_max = max_price * 1.15  # Add 15% padding at top

                # Add bar trace
                fig_analogue_orig.add_trace(go.Bar(
                    x=chart_df_analogue_orig['insulin_originator_biosimilar'].tolist(),
                    y=chart_df_analogue_orig['median_price_local'].tolist(),
                    name='Median Price-Local',
                    marker=dict(
                        color='#17becf',  # Teal color
                        line=dict(color='#0e7c8f', width=1)
                    ),
                    text=[f'{val:,.0f}' for val in chart_df_analogue_orig['median_price_local'].tolist()],
                    textposition='outside',
                    textfont=dict(size=11),
                    hovertemplate='<b>%{x}</b><br>' +
                                  'Median Price: %{y:,.2f}<br>' +
                                  '<extra></extra>'
                ))

                # Update layout
                fig_analogue_orig.update_layout(
                    xaxis_title='Type',
                    yaxis_title='Median price - Local',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=450,
                    yaxis=dict(
                        range=[0, y_axis_max],
                        tickformat=',.0f'
                    ),
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    margin=dict(t=40, b=60, l=60, r=20),
                    hovermode='closest'
                )

                # Display chart
                st.plotly_chart(fig_analogue_orig, use_container_width=True)
            else:
                st.info("No analogue insulin originator/biosimilar data available for the selected filters")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>ACCISS Facilities Dashboard © 2025 - Phase 1: Filter Controls</p>
    </div>
""", unsafe_allow_html=True)
