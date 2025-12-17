"""
BigQuery client connection and query functions.
"""
import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import config
import traceback


@st.cache_resource
def get_bigquery_client():
    """
    Create and cache a BigQuery client connection.
    Priority order:
    1. Streamlit secrets (for cloud deployment)
    2. Service account key file (for local development)
    3. Application default credentials (gcloud auth)
    """
    print("Starting BigQuery client initialization...", flush=True)

    # Try to get credentials from Streamlit secrets (for cloud deployment)
    try:
        print("Checking for Streamlit secrets...", flush=True)
        if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
            print("✓ gcp_service_account found in secrets", flush=True)
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
            project_id = st.secrets.get("GCP_PROJECT_ID", config.GCP_PROJECT_ID)
            print(f"✓ Creating client with project_id: {project_id}", flush=True)
            client = bigquery.Client(credentials=credentials, project=project_id)
            print("✓ BigQuery client created from Streamlit secrets!", flush=True)
            return client
    except Exception as e:
        print(f"⚠ Streamlit secrets method failed: {str(e)}", flush=True)
        print(f"⚠ Traceback: {traceback.format_exc()}", flush=True)

    # Fallback to service account file (for local development)
    try:
        print("Trying service account file method...", flush=True)
        if config.GOOGLE_APPLICATION_CREDENTIALS:
            print(f"✓ GOOGLE_APPLICATION_CREDENTIALS: {config.GOOGLE_APPLICATION_CREDENTIALS}", flush=True)
            credentials = service_account.Credentials.from_service_account_file(
                config.GOOGLE_APPLICATION_CREDENTIALS
            )
            client = bigquery.Client(
                credentials=credentials,
                project=config.GCP_PROJECT_ID
            )
            print("✓ BigQuery client created from service account file!", flush=True)
            return client
    except Exception as e:
        print(f"⚠ Service account file method failed: {str(e)}", flush=True)

    # Final fallback to application default credentials (gcloud auth)
    try:
        print("Trying application default credentials...", flush=True)
        from google.auth import default
        credentials, project = default()
        print(f"✓ Got default credentials for project: {project}", flush=True)
        client = bigquery.Client(credentials=credentials, project=project or config.GCP_PROJECT_ID)
        print("✓ BigQuery client created from default credentials!", flush=True)
        return client
    except Exception as e:
        print(f"✗ Application default credentials failed: {str(e)}", flush=True)
        print("✗ ALL AUTHENTICATION METHODS FAILED", flush=True)
        st.error("⚠️ Failed to connect to BigQuery. Please check your credentials and configuration.")
        return None


@st.cache_data(ttl=600)
def query_table(_client, table_name, limit=100):
    """
    Query a BigQuery table and return results as a pandas DataFrame.

    Args:
        _client: BigQuery client instance
        table_name: Name of the table to query
        limit: Maximum number of rows to return (default: 100)

    Returns:
        pandas DataFrame with query results
    """
    query = f"""
        SELECT *
        FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
        LIMIT {limit}
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error querying table {table_name}: {str(e)}")
        return None


@st.cache_data(ttl=600)
def run_custom_query(_client, query):
    """
    Execute a custom SQL query and return results as a pandas DataFrame.

    Args:
        _client: BigQuery client instance
        query: SQL query string

    Returns:
        pandas DataFrame with query results
    """
    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_table_schema(_client, table_name):
    """
    Get the schema of a BigQuery table.

    Args:
        _client: BigQuery client instance
        table_name: Name of the table

    Returns:
        List of field information dictionaries
    """
    try:
        table_ref = f"{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}"
        table = _client.get_table(table_ref)

        schema_info = []
        for field in table.schema:
            schema_info.append({
                "name": field.name,
                "type": field.field_type,
                "mode": field.mode,
                "description": field.description or ""
            })

        return schema_info
    except Exception as e:
        st.error(f"Error getting schema for {table_name}: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_row_count(_client, table_name):
    """
    Get the total row count for a table.

    Args:
        _client: BigQuery client instance
        table_name: Name of the table

    Returns:
        Integer row count
    """
    query = f"""
        SELECT COUNT(*) as row_count
        FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    """

    try:
        result = _client.query(query).to_dataframe()
        return result['row_count'].iloc[0]
    except Exception as e:
        st.error(f"Error getting row count for {table_name}: {str(e)}")
        return 0



@st.cache_data(ttl=600)
def get_grouped_counts(_client, table_name, group_by_column, sort_desc=True):
    """
    Get grouped counts for a specific column.
    
    Args:
        _client: BigQuery client instance
        table_name: Name of the table
        group_by_column: Column name to group by
        sort_desc: Sort in descending order (default: True)
    
    Returns:
        pandas DataFrame with grouped counts
    """
    order_clause = "DESC" if sort_desc else "ASC"
    query = f"""
        SELECT 
            {group_by_column},
            COUNT(DISTINCT form_case__case_id) as survey_count
        FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
        GROUP BY {group_by_column}
        ORDER BY survey_count {order_clause}
    """
    
    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting grouped counts for {group_by_column}: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_data_collection_periods(_client, table_name):
    """
    Get data collection periods with survey counts.

    Args:
        _client: BigQuery client instance
        table_name: Name of the table

    Returns:
        pandas DataFrame with data collection periods and counts
    """
    query = f"""
        SELECT
            data_collection_period,
            COUNT(DISTINCT form_case__case_id) as survey_count
        FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
        WHERE data_collection_period IS NOT NULL
            AND data_collection_period NOT LIKE '%Click here%'
            AND data_collection_period NOT LIKE '%select%'
            AND TRIM(data_collection_period) != ''
            AND LENGTH(data_collection_period) > 1
        GROUP BY data_collection_period
        ORDER BY data_collection_period DESC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting data collection periods: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_selected_periods_summary(_client, table_name, selected_periods):
    """
    Get summary table for selected data collection periods.
    
    Args:
        _client: BigQuery client instance
        table_name: Name of the table
        selected_periods: List of selected data collection periods
    
    Returns:
        pandas DataFrame with period summaries
    """
    if not selected_periods:
        return None
    
    # Build the WHERE clause for selected periods
    periods_str = "', '".join(selected_periods)
    
    query = f"""
        SELECT 
            data_collection_period,
            MIN(survey_date) as first_survey_date,
            MAX(survey_date) as last_survey_date,
            COUNT(DISTINCT form_case__case_id) as survey_count
        FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
        WHERE data_collection_period IN ('{periods_str}')
            AND data_collection_period != 'Click here to select...'
        GROUP BY data_collection_period
        ORDER BY data_collection_period DESC
    """
    
    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting selected periods summary: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_facility_data(_client, table_name, selected_periods, selected_countries=None, selected_regions=None):
    """
    Get facility data for the selected filters.
    
    Args:
        _client: BigQuery client instance
        table_name: Name of the table
        selected_periods: List of selected data collection periods
        selected_countries: List of selected countries (optional)
        selected_regions: List of selected regions (optional)
    
    Returns:
        pandas DataFrame with facility data
    """
    if not selected_periods:
        return None
    
    # Build the WHERE clause
    periods_str = "', '".join(selected_periods)
    where_clauses = [f"data_collection_period IN ('{periods_str}')"]
    
    if selected_countries:
        countries_str = "', '".join(selected_countries)
        where_clauses.append(f"country IN ('{countries_str}')")
    
    if selected_regions:
        regions_str = "', '".join(selected_regions)
        where_clauses.append(f"region IN ('{regions_str}')")
    
    where_clause = " AND ".join(where_clauses)
    
    query = f"""
        SELECT 
            form_case__case_id,
            sector,
            level_of_care,
            country,
            region,
            data_collection_period
        FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
        WHERE {where_clause}
    """
    
    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting facility data: {str(e)}")
        return None


@st.cache_data(ttl=600)
def fetch_facility_statistics(_client, table_name, filters):
    """
    Fetch facility statistics from database using optimized single query.
    
    Args:
        _client: BigQuery client instance
        table_name: Name of the table
        filters (dict): Filter selections from Data Selectors
            {
                'country': ['Tanzania', 'Kenya'],
                'region': ['Dar es Salaam'],
                'data_collection_period': ['Y3/P1']
            }
    
    Returns:
        dict: Formatted facility statistics with hierarchical structure
    """
    if not filters.get('data_collection_period'):
        return None
    
    # Build the WHERE clause with filters
    where_clauses = ["1=1"]
    
    # Add data collection period filter (required)
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
    
    where_clause = " AND ".join(where_clauses)
    
    # Optimized single query with conditional aggregation
    # Using COALESCE to handle NULL values
    query = f"""
    SELECT
        COUNT(DISTINCT form_case__case_id) as total_facilities,
        COUNT(DISTINCT CASE WHEN COALESCE(sector, '') LIKE '%Public%' THEN form_case__case_id END) as public_facilities,
        COUNT(DISTINCT CASE WHEN COALESCE(sector, '') LIKE '%Public%' AND COALESCE(level_of_care, '') = 'Primary' THEN form_case__case_id END) as primary_facilities,
        COUNT(DISTINCT CASE WHEN COALESCE(sector, '') LIKE '%Public%' AND COALESCE(level_of_care, '') = 'Secondary' THEN form_case__case_id END) as secondary_facilities,
        COUNT(DISTINCT CASE WHEN COALESCE(sector, '') LIKE '%Public%' AND COALESCE(level_of_care, '') = 'Tertiary' THEN form_case__case_id END) as tertiary_facilities,
        COUNT(DISTINCT CASE WHEN COALESCE(sector, '') LIKE '%Private Pharmacy%' THEN form_case__case_id END) as private_pharmacies,
        COUNT(DISTINCT CASE WHEN COALESCE(sector, '') LIKE '%NGO%' THEN form_case__case_id END) as ngo_facilities,
        COUNT(DISTINCT CASE WHEN COALESCE(sector, '') LIKE '%Private Hospital or Clinic%' THEN form_case__case_id END) as private_hospitals,
        COUNT(DISTINCT CASE WHEN COALESCE(sector, '') LIKE '%Other%' AND COALESCE(sector, '') NOT LIKE '%Public%' AND COALESCE(sector, '') NOT LIKE '%Private Pharmacy%' AND COALESCE(sector, '') NOT LIKE '%NGO%' AND COALESCE(sector, '') NOT LIKE '%Private Hospital or Clinic%' THEN form_case__case_id END) as other_facilities
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    """
    
    try:
        result = _client.query(query).to_dataframe()
        
        if result.empty:
            return None
        
        # Extract the single row of results
        row = result.iloc[0]
        
        # Transform to expected format
        stats = {
            "total": int(row['total_facilities']),
            "categories": {
                "public": {
                    "total": int(row['public_facilities']),
                    "subcategories": {
                        "primary": int(row['primary_facilities']),
                        "secondary": int(row['secondary_facilities']),
                        "tertiary": int(row['tertiary_facilities'])
                    }
                },
                "private_pharmacies": int(row['private_pharmacies']),
                "ngo_faith": int(row['ngo_facilities']),
                "private_hospitals": int(row['private_hospitals']),
                "other": int(row['other_facilities'])
            }
        }
        
        return stats
        
    except Exception as e:
        st.error(f"Error fetching facility statistics: {str(e)}")
        return None


def validate_facility_stats(stats):
    """
    Validate facility statistics data integrity.
    
    Args:
        stats (dict): Facility statistics dictionary
    
    Returns:
        tuple: (is_valid: bool, errors: list of str)
    """
    if not stats:
        return False, ["No statistics data provided"]
    
    errors = []
    
    try:
        # Rule 1: All values should be non-negative
        total = stats.get('total', 0)
        if total < 0:
            errors.append("Total facilities count is negative")
        
        # Rule 2: Sum of Level 1 categories should not exceed total
        categories = stats.get('categories', {})
        level1_sum = (
            categories.get('public', {}).get('total', 0) +
            categories.get('private_pharmacies', 0) +
            categories.get('ngo_faith', 0) +
            categories.get('private_hospitals', 0) +
            categories.get('other', 0)
        )
        
        if level1_sum > total:
            errors.append(f"Level 1 sum ({level1_sum}) exceeds total ({total})")
        
        # Rule 3: Sum of Level 2 (public subcategories) should not exceed public total
        public_total = categories.get('public', {}).get('total', 0)
        subcats = categories.get('public', {}).get('subcategories', {})
        level2_sum = (
            subcats.get('primary', 0) +
            subcats.get('secondary', 0) +
            subcats.get('tertiary', 0)
        )
        
        if level2_sum > public_total:
            errors.append(f"Public subcategories sum ({level2_sum}) exceeds public total ({public_total})")
        
        # Rule 4: Check for negative values in all categories
        if public_total < 0:
            errors.append("Public facilities count is negative")
        if categories.get('private_pharmacies', 0) < 0:
            errors.append("Private pharmacies count is negative")
        if categories.get('ngo_faith', 0) < 0:
            errors.append("NGO/Faith count is negative")
        if categories.get('private_hospitals', 0) < 0:
            errors.append("Private hospitals count is negative")
        if categories.get('other', 0) < 0:
            errors.append("Other facilities count is negative")
        
        # Check subcategories
        if subcats.get('primary', 0) < 0:
            errors.append("Primary care count is negative")
        if subcats.get('secondary', 0) < 0:
            errors.append("Secondary care count is negative")
        if subcats.get('tertiary', 0) < 0:
            errors.append("Tertiary care count is negative")
        
        return len(errors) == 0, errors
        
    except Exception as e:
        return False, [f"Validation error: {str(e)}"]



@st.cache_data(ttl=600)
def get_sector_values(_client, table_name, filters):
    """
    Get actual distinct sector values to help debug query issues.
    
    Args:
        _client: BigQuery client instance
        table_name: Name of the table
        filters (dict): Filter selections
    
    Returns:
        pandas DataFrame with sector values and counts
    """
    if not filters.get('data_collection_period'):
        return None
    
    # Build the WHERE clause with filters
    where_clauses = ["1=1"]
    
    # Add data collection period filter (required)
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
    
    where_clause = " AND ".join(where_clauses)
    
    # Enhanced debug query with NULL checking
    query = f"""
    SELECT
        CASE 
            WHEN sector IS NULL THEN '[NULL]'
            WHEN TRIM(sector) = '' THEN '[EMPTY]'
            ELSE sector 
        END as sector,
        CASE 
            WHEN level_of_care IS NULL THEN '[NULL]'
            WHEN TRIM(level_of_care) = '' THEN '[EMPTY]'
            ELSE level_of_care 
        END as level_of_care,
        region,
        COUNT(DISTINCT form_case__case_id) as count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY sector, level_of_care, region
    ORDER BY region, count DESC
    """
    
    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting sector values: {str(e)}")
        return None



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
    if not global_filters.get('data_collection_period'):
        return None
    
    # Build WHERE clause with global filters
    where_clauses = ["1=1"]
    
    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")
    
    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")
    
    # Add region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")
    
    # Exclude NULL regions
    where_clauses.append("region IS NOT NULL")
    where_clauses.append("TRIM(region) != ''")
    
    where_clause = " AND ".join(where_clauses)
    
    query = f"""
    SELECT
        region,
        COUNT(DISTINCT form_case__case_id) as facility_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY region
    ORDER BY region ASC
    """
    
    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting insulin regions: {str(e)}")
        return None


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
    if not global_filters.get('data_collection_period'):
        return None
    
    # Build WHERE clause with global filters
    where_clauses = ["1=1"]
    
    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")
    
    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")
    
    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")
    
    # Add local region filter (optional)
    if local_regions:
        local_regions_str = "', '".join(local_regions)
        where_clauses.append(f"region IN ('{local_regions_str}')")
    
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
    ORDER BY sector ASC
    """
    
    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting insulin sectors: {str(e)}")
        return None


@st.cache_data(ttl=600, show_spinner=False)
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
    if not global_filters.get('data_collection_period'):
        return None
    
    # Build WHERE clause with all filters
    where_clauses = ["1=1"]
    
    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")
    
    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")
    
    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")
    
    # Add local region filter (optional)
    if local_regions:
        local_regions_str = "', '".join(local_regions)
        where_clauses.append(f"region IN ('{local_regions_str}')")
    
    # Add local sector filter (optional)
    if local_sectors:
        local_sectors_str = "', '".join(local_sectors)
        where_clauses.append(f"sector IN ('{local_sectors_str}')")
    
    where_clause = " AND ".join(where_clauses)
    
    query = f"""
    SELECT
        COALESCE(SUM(COALESCE(insulin_available_num, 0)), 0) as facilities_with_availability,
        COUNT(DISTINCT form_case__case_id) as total_facilities,
        CASE
            WHEN COUNT(DISTINCT form_case__case_id) > 0
            THEN ROUND(100 - ((COALESCE(SUM(COALESCE(insulin_available_num, 0)), 0) * 100.0) / COUNT(DISTINCT form_case__case_id)), 1)
            ELSE 0
        END as unavailability_percentage
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    """
    
    try:
        result = _client.query(query).to_dataframe()
        
        if result.empty:
            return None
        
        row = result.iloc[0]
        
        # Handle potential NULL/NA values with safe conversion
        facilities_available = row['facilities_with_availability']
        total_fac = row['total_facilities']
        unavail_pct = row['unavailability_percentage']
        
        # Convert to Python types, handling NA/NULL
        metrics = {
            'facilities_with_availability': int(facilities_available) if pd.notna(facilities_available) else 0,
            'total_facilities': int(total_fac) if pd.notna(total_fac) else 0,
            'unavailability_percentage': float(unavail_pct) if pd.notna(unavail_pct) else 0.0
        }
        
        return metrics
        
    except Exception as e:
        st.error(f"Error getting insulin availability metrics: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_insulin_by_sector_regions(_client, table_name, global_filters):
    """
    Get regions for local Region dropdown in Insulin Availability - By Sector component.
    
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
    if not global_filters.get('data_collection_period'):
        return None
    
    # Build WHERE clause with global filters
    where_clauses = ["1=1"]
    
    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")
    
    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")
    
    # Add region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")
    
    # Exclude NULL/empty regions
    where_clauses.append("region IS NOT NULL")
    where_clauses.append("TRIM(region) != ''")
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
        st.error(f"Error getting insulin by sector regions: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_insulin_by_sector_chart_data(_client, table_name, global_filters, local_regions):
    """
    Get insulin availability percentages by sector for bar chart.
    
    Args:
        _client: BigQuery client
        table_name: Table name
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown
    
    Returns:
        pandas DataFrame with columns:
            - sector (str)
            - sector_order (int)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)
    """
    if not global_filters.get('data_collection_period'):
        return None
    
    # Build WHERE clause with global + local region filters
    where_clauses = ["1=1"]
    
    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")
    
    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")
    
    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")
    
    # Add local region filter (optional)
    if local_regions:
        local_regions_str = "', '".join(local_regions)
        where_clauses.append(f"region IN ('{local_regions_str}')")
    
    # Exclude NULL/empty sectors
    where_clauses.append("sector IS NOT NULL")
    where_clauses.append("TRIM(sector) != ''")
    
    where_clause = " AND ".join(where_clauses)
    
    query = f"""
    SELECT
        sector,
        SAFE_CAST(sector_order AS INT64) as sector_order,
        COUNT(DISTINCT form_case__case_id) as total_facilities,
        SUM(COALESCE(insulin_available_num, 0)) as facilities_with_insulin,
        CASE
            WHEN COUNT(DISTINCT form_case__case_id) > 0
            THEN ROUND((SUM(COALESCE(insulin_available_num, 0)) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
            ELSE 0
        END as availability_percentage
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY sector, sector_order
    ORDER BY SAFE_CAST(sector_order AS INT64) ASC NULLS LAST, sector ASC
    """
    
    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting insulin by sector chart data: {str(e)}")
        return None


# ============================================================================
# Plan 5: Insulin Availability - By Insulin Type Functions
# ============================================================================

@st.cache_data(ttl=600)
def get_insulin_by_type_regions(_client, table_name, global_filters):
    """
    Get regions for local Region dropdown in Insulin Availability - By Insulin Type component.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
            {
                'data_collection_period': ['Y1/P1'],
                'country': ['Tanzania'],
                'region': ['Eastern']
            }

    Returns:
        pandas DataFrame with columns: region, facility_count
    """
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Exclude NULL/empty regions
    where_clauses.append("region IS NOT NULL")
    where_clauses.append("TRIM(region) != ''")
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
        st.error(f"Error getting insulin by type regions: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_insulin_by_type_sectors(_client, table_name, global_filters):
    """
    Get sectors for local Sector dropdown in Insulin Availability - By Insulin Type component.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors

    Returns:
        pandas DataFrame with columns: sector, facility_count
    """
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Exclude NULL/empty sectors
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
        st.error(f"Error getting insulin by type sectors: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_insulin_by_type_human_chart_data(_client, table_name, global_filters, local_regions, local_sectors):
    """
    Get insulin availability percentages by insulin type for Human insulin bar chart.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        pandas DataFrame with columns:
            - insulin_type (str)
            - insulin_type_order (int)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)
    """
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global + local filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add local region filter (optional)
    if local_regions:
        local_regions_str = "', '".join(local_regions)
        where_clauses.append(f"region IN ('{local_regions_str}')")

    # Add local sector filter (optional)
    if local_sectors:
        local_sectors_str = "', '".join(local_sectors)
        where_clauses.append(f"sector IN ('{local_sectors_str}')")

    # Exclude NULL/empty insulin types and filter for Human
    where_clauses.append("insulin_type IS NOT NULL")
    where_clauses.append("TRIM(insulin_type) != ''")
    where_clauses.append("insulin_type LIKE '%Human%'")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        insulin_type,
        insulin_type_order,
        COUNT(DISTINCT form_case__case_id) as total_facilities,
        COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) as facilities_with_insulin,
        CASE
            WHEN COUNT(DISTINCT form_case__case_id) > 0
            THEN ROUND((COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
            ELSE 0
        END as availability_percentage
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_type, insulin_type_order
    ORDER BY insulin_type_order ASC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting insulin by type (Human) chart data: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_insulin_by_type_analogue_chart_data(_client, table_name, global_filters, local_regions, local_sectors):
    """
    Get insulin availability percentages by insulin type for Analogue insulin bar chart.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        pandas DataFrame with columns:
            - insulin_type (str)
            - insulin_type_order (int)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)
    """
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global + local filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add local region filter (optional)
    if local_regions:
        local_regions_str = "', '".join(local_regions)
        where_clauses.append(f"region IN ('{local_regions_str}')")

    # Add local sector filter (optional)
    if local_sectors:
        local_sectors_str = "', '".join(local_sectors)
        where_clauses.append(f"sector IN ('{local_sectors_str}')")

    # Exclude NULL/empty insulin types and filter for Analogue
    where_clauses.append("insulin_type IS NOT NULL")
    where_clauses.append("TRIM(insulin_type) != ''")
    where_clauses.append("insulin_type LIKE '%Analogue%'")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        insulin_type,
        insulin_type_order,
        COUNT(DISTINCT form_case__case_id) as total_facilities,
        COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) as facilities_with_insulin,
        CASE
            WHEN COUNT(DISTINCT form_case__case_id) > 0
            THEN ROUND((COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
            ELSE 0
        END as availability_percentage
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_type, insulin_type_order
    ORDER BY insulin_type_order ASC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting insulin by type (Analogue) chart data: {str(e)}")
        return None


# Plan 6: Insulin Availability - By Region functions

@st.cache_data(ttl=600)
def get_insulin_by_region_sectors(_client, table_name, global_filters):
    """
    Get sectors for local Sector dropdown in Insulin Availability - By Region component.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys)
        global_filters (dict): Global filters from Data Selectors

    Returns:
        pandas DataFrame with columns: sector, facility_count
    """
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Exclude NULL/empty sectors
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
        st.error(f"Error getting insulin by region sectors: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_insulin_by_region_human_chart_data(_client, table_name, global_filters, local_sectors):
    """
    Get insulin availability percentages by region for Human insulin bar chart.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        pandas DataFrame with columns:
            - region (str)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)
    """
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global + local sector filter
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add local sector filter (optional)
    if local_sectors:
        local_sectors_str = "', '".join(local_sectors)
        where_clauses.append(f"sector IN ('{local_sectors_str}')")

    # Exclude NULL/empty regions and filter for Human insulin
    where_clauses.append("region IS NOT NULL")
    where_clauses.append("TRIM(region) != ''")
    where_clauses.append("insulin_type IS NOT NULL")
    where_clauses.append("insulin_type LIKE '%Human%'")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        region,
        COUNT(DISTINCT form_case__case_id) as total_facilities,
        COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) as facilities_with_insulin,
        CASE
            WHEN COUNT(DISTINCT form_case__case_id) > 0
            THEN ROUND((COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
            ELSE 0
        END as availability_percentage
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY region
    ORDER BY region ASC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting insulin by region (Human) chart data: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_insulin_by_region_analogue_chart_data(_client, table_name, global_filters, local_sectors):
    """
    Get insulin availability percentages by region for Analogue insulin bar chart.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        pandas DataFrame with columns:
            - region (str)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)
    """
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global + local sector filter
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add local sector filter (optional)
    if local_sectors:
        local_sectors_str = "', '".join(local_sectors)
        where_clauses.append(f"sector IN ('{local_sectors_str}')")

    # Exclude NULL/empty regions and filter for Analogue insulin
    where_clauses.append("region IS NOT NULL")
    where_clauses.append("TRIM(region) != ''")
    where_clauses.append("insulin_type IS NOT NULL")
    where_clauses.append("insulin_type LIKE '%Analogue%'")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        region,
        COUNT(DISTINCT form_case__case_id) as total_facilities,
        COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) as facilities_with_insulin,
        CASE
            WHEN COUNT(DISTINCT form_case__case_id) > 0
            THEN ROUND((COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
            ELSE 0
        END as availability_percentage
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY region
    ORDER BY region ASC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting insulin by region (Analogue) chart data: {str(e)}")
        return None


# ============================================================================
# Plan 7: Insulin Availability - Public Sector - By Level of Care Functions
# ============================================================================

@st.cache_data(ttl=600)
def get_insulin_public_levelcare_regions(_client, table_name, global_filters):
    """
    Get regions for local Region dropdown in Insulin Availability - Public Sector - By Level of Care component.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
            {
                'data_collection_period': ['Y1/P1'],
                'country': ['Peru'],
                'region': ['Arequipa']
            }

    Returns:
        pandas DataFrame with columns: region, facility_count
    """
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add implicit Public sector filter (ALWAYS)
    where_clauses.append("sector LIKE '%Public%'")

    # Exclude NULL/empty regions
    where_clauses.append("region IS NOT NULL")
    where_clauses.append("TRIM(region) != ''")
    where_clauses.append("region != 'NULL'")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        region,
        COUNT(DISTINCT form_case__case_id) as facility_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY region
    ORDER BY region ASC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting insulin public levelcare regions: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_insulin_public_levelcare_human_chart_data(_client, table_name, global_filters, local_regions):
    """
    Get insulin availability percentages by level of care for Human insulin in Public sector.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown

    Returns:
        pandas DataFrame with columns:
            - level_of_care (str)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)
    """
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global + local region filter
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add local region filter (optional)
    if local_regions:
        local_regions_str = "', '".join(local_regions)
        where_clauses.append(f"region IN ('{local_regions_str}')")

    # Add implicit Public sector filter (ALWAYS)
    where_clauses.append("sector LIKE '%Public%'")

    # Filter for Human insulin and exclude NULL/empty level_of_care
    where_clauses.append("insulin_type IS NOT NULL")
    where_clauses.append("insulin_type LIKE '%Human%'")
    where_clauses.append("level_of_care IS NOT NULL")
    where_clauses.append("TRIM(level_of_care) != ''")
    where_clauses.append("level_of_care NOT IN ('NULL', '---')")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        level_of_care,
        COUNT(DISTINCT form_case__case_id) as total_facilities,
        COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) as facilities_with_insulin,
        CASE
            WHEN COUNT(DISTINCT form_case__case_id) > 0
            THEN ROUND((COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
            ELSE 0
        END as availability_percentage
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY level_of_care
    ORDER BY level_of_care ASC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting insulin public levelcare (Human) chart data: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_insulin_public_levelcare_analogue_chart_data(_client, table_name, global_filters, local_regions):
    """
    Get insulin availability percentages by level of care for Analogue insulin in Public sector.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown

    Returns:
        pandas DataFrame with columns:
            - level_of_care (str)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)
    """
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global + local region filter
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add local region filter (optional)
    if local_regions:
        local_regions_str = "', '".join(local_regions)
        where_clauses.append(f"region IN ('{local_regions_str}')")

    # Add implicit Public sector filter (ALWAYS)
    where_clauses.append("sector LIKE '%Public%'")

    # Filter for Analogue insulin and exclude NULL/empty level_of_care
    where_clauses.append("insulin_type IS NOT NULL")
    where_clauses.append("insulin_type LIKE '%Analogue%'")
    where_clauses.append("level_of_care IS NOT NULL")
    where_clauses.append("TRIM(level_of_care) != ''")
    where_clauses.append("level_of_care NOT IN ('NULL', '---')")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        level_of_care,
        COUNT(DISTINCT form_case__case_id) as total_facilities,
        COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) as facilities_with_insulin,
        CASE
            WHEN COUNT(DISTINCT form_case__case_id) > 0
            THEN ROUND((COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
            ELSE 0
        END as availability_percentage
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY level_of_care
    ORDER BY level_of_care ASC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting insulin public levelcare (Analogue) chart data: {str(e)}")
        return None


# ============================================================================
# Plan 8: Insulin Availability - By INN Functions
# ============================================================================

@st.cache_data(ttl=600)
def get_insulin_by_inn_regions(_client, table_name, global_filters):
    """
    Get regions for local Region dropdown in Insulin Availability - By INN component.

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
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Exclude NULL/empty regions
    where_clauses.append("region IS NOT NULL")
    where_clauses.append("TRIM(region) != ''")
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
        st.error(f"Error getting insulin by INN regions: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_insulin_by_inn_sectors(_client, table_name, global_filters):
    """
    Get sectors for local Sector dropdown in Insulin Availability - By INN component.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys)
        global_filters (dict): Global filters from Data Selectors

    Returns:
        pandas DataFrame with columns: sector, facility_count
    """
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Exclude NULL/empty sectors
    where_clauses.append("sector IS NOT NULL")
    where_clauses.append("TRIM(sector) != ''")
    where_clauses.append("sector != 'NULL'")

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
        st.error(f"Error getting insulin by INN sectors: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_insulin_by_inn_chart_data(_client, table_name, global_filters, local_regions, local_sectors):
    """
    Get insulin availability percentages by insulin INN, ONLY showing insulins with availability > 0%.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_repeat_repivot)
        global_filters (dict): Global filters from Data Selectors
        local_regions (list): Selected regions from local Region dropdown
        local_sectors (list): Selected sectors from local Sector dropdown

    Returns:
        pandas DataFrame with columns:
            - insulin_inn (str)
            - total_facilities (int)
            - facilities_with_insulin (int)
            - availability_percentage (float)

        Only returns rows where availability_percentage > 0
    """
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global + local region + local sector filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add local region filter (optional)
    if local_regions:
        local_regions_str = "', '".join(local_regions)
        where_clauses.append(f"region IN ('{local_regions_str}')")

    # Add local sector filter (optional)
    if local_sectors:
        local_sectors_str = "', '".join(local_sectors)
        where_clauses.append(f"sector IN ('{local_sectors_str}')")

    # Exclude NULL/empty insulin_inn
    where_clauses.append("insulin_inn IS NOT NULL")
    where_clauses.append("TRIM(insulin_inn) != ''")
    where_clauses.append("insulin_inn != 'NULL'")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        insulin_inn,
        COUNT(DISTINCT form_case__case_id) as total_facilities,
        COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) as facilities_with_insulin,
        CASE
            WHEN COUNT(DISTINCT form_case__case_id) > 0
            THEN ROUND((COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
            ELSE 0
        END as availability_percentage
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_inn
    HAVING
        CASE
            WHEN COUNT(DISTINCT form_case__case_id) > 0
            THEN ROUND((COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
            ELSE 0
        END > 0
    ORDER BY availability_percentage DESC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting insulin by INN chart data: {str(e)}")
        return None


# ============================================================================
# Plan 9: Insulin - Top 10 Brands Functions
# ============================================================================

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
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Exclude NULL/empty sectors
    where_clauses.append("sector IS NOT NULL")
    where_clauses.append("TRIM(sector) != ''")
    where_clauses.append("sector != 'NULL'")

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
        st.error(f"Error getting insulin top brands sectors: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_insulin_top_brands_chart_data(_client, table_name, global_filters, local_sectors):
    """
    Get record counts for all insulin brands, processed for top 10 + "Other" display.

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
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global + local sector filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add local sector filter (optional)
    if local_sectors:
        local_sectors_str = "', '".join(local_sectors)
        where_clauses.append(f"sector IN ('{local_sectors_str}')")

    # Exclude NULL/empty insulin_brand and "---" placeholder
    where_clauses.append("insulin_brand IS NOT NULL")
    where_clauses.append("TRIM(insulin_brand) != ''")
    where_clauses.append("insulin_brand != 'NULL'")
    where_clauses.append("insulin_brand != '---'")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        insulin_brand,
        COUNT(*) as record_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_brand
    ORDER BY record_count DESC
    """

    try:
        df = _client.query(query).to_dataframe()

        if df is None or df.empty:
            return None

        # Post-processing: Calculate top 10 + "Other"
        total_count = df['record_count'].sum()

        if total_count == 0:
            return None

        # Take top 10 brands
        top_10 = df.head(10).copy()

        # Calculate percentages for top 10
        top_10['percentage'] = (top_10['record_count'] / total_count) * 100

        # If more than 10 brands, sum remaining into "Other"
        if len(df) > 10:
            other_count = df.iloc[10:]['record_count'].sum()
            other_percentage = (other_count / total_count) * 100

            # Create "Other" row
            other_row = pd.DataFrame([{
                'insulin_brand': 'Other',
                'record_count': other_count,
                'percentage': other_percentage
            }])

            # Concatenate top 10 + "Other"
            result = pd.concat([top_10, other_row], ignore_index=True)
        else:
            result = top_10

        return result

    except Exception as e:
        st.error(f"Error getting insulin top brands chart data: {str(e)}")
        return None


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
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Exclude NULL/empty regions
    where_clauses.append("region IS NOT NULL")
    where_clauses.append("TRIM(region) != ''")
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
        st.error(f"Error getting insulin by presentation regions: {str(e)}")
        return None


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
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Exclude NULL/empty sectors
    where_clauses.append("sector IS NOT NULL")
    where_clauses.append("TRIM(sector) != ''")
    where_clauses.append("sector != 'NULL'")

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
        st.error(f"Error getting insulin by presentation sectors: {str(e)}")
        return None


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
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global + local region + local sector filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add local region filter (optional)
    if local_regions:
        local_regions_str = "', '".join(local_regions)
        where_clauses.append(f"region IN ('{local_regions_str}')")

    # Add local sector filter (optional)
    if local_sectors:
        local_sectors_str = "', '".join(local_sectors)
        where_clauses.append(f"sector IN ('{local_sectors_str}')")

    # Exclude NULL/empty insulin_presentation and insulin_type
    where_clauses.append("insulin_presentation IS NOT NULL")
    where_clauses.append("TRIM(insulin_presentation) != ''")
    where_clauses.append("insulin_presentation != 'NULL'")
    where_clauses.append("insulin_type IS NOT NULL")
    where_clauses.append("TRIM(insulin_type) != ''")
    where_clauses.append("insulin_type != 'NULL'")

    where_clause = " AND ".join(where_clauses)

    query = f"""
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
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_presentation, insulin_type
    HAVING
        CASE
            WHEN COUNT(DISTINCT form_case__case_id) > 0
            THEN ROUND((COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
            ELSE 0
        END > 0
    ORDER BY availability_percentage DESC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting insulin by presentation chart data: {str(e)}")
        return None


# ============================================================================
# Plan 11: Insulin Availability - By Originator Brands VS Biosimilars Functions
# ============================================================================

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
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Exclude NULL/empty regions
    where_clauses.append("region IS NOT NULL")
    where_clauses.append("TRIM(region) != ''")
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
        st.error(f"Error getting insulin originator/biosimilar regions: {str(e)}")
        return None


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
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Exclude NULL/empty sectors
    where_clauses.append("sector IS NOT NULL")
    where_clauses.append("TRIM(sector) != ''")
    where_clauses.append("sector != 'NULL'")

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
        st.error(f"Error getting insulin originator/biosimilar sectors: {str(e)}")
        return None


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
    if not global_filters.get('data_collection_period'):
        return 0.0

    # Build WHERE clause with global + local filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add local region filter (optional)
    if local_regions:
        local_regions_str = "', '".join(local_regions)
        where_clauses.append(f"region IN ('{local_regions_str}')")

    # Add local sector filter (optional)
    if local_sectors:
        local_sectors_str = "', '".join(local_sectors)
        where_clauses.append(f"sector IN ('{local_sectors_str}')")

    # Filter by Originator Brand and Human insulin type
    where_clauses.append("insulin_originator_biosimilar = 'Originator Brand'")
    where_clauses.append("insulin_type LIKE '%Human%'")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        COUNT(DISTINCT form_case__case_id) as total_facilities,
        COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) as facilities_with_insulin,
        CASE
            WHEN COUNT(DISTINCT form_case__case_id) > 0
            THEN ROUND((COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
            ELSE 0
        END as availability_percentage
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    """

    try:
        result = _client.query(query).to_dataframe()

        if result.empty:
            return 0.0

        row = result.iloc[0]
        percentage = row['availability_percentage']

        return float(percentage) if pd.notna(percentage) else 0.0

    except Exception as e:
        st.error(f"Error getting Human Originator metric: {str(e)}")
        return 0.0


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
    if not global_filters.get('data_collection_period'):
        return 0.0

    # Build WHERE clause with global + local filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add local region filter (optional)
    if local_regions:
        local_regions_str = "', '".join(local_regions)
        where_clauses.append(f"region IN ('{local_regions_str}')")

    # Add local sector filter (optional)
    if local_sectors:
        local_sectors_str = "', '".join(local_sectors)
        where_clauses.append(f"sector IN ('{local_sectors_str}')")

    # Filter by Originator Brand and Analogue insulin type
    where_clauses.append("insulin_originator_biosimilar = 'Originator Brand'")
    where_clauses.append("insulin_type LIKE '%Analogue%'")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        COUNT(DISTINCT form_case__case_id) as total_facilities,
        COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) as facilities_with_insulin,
        CASE
            WHEN COUNT(DISTINCT form_case__case_id) > 0
            THEN ROUND((COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
            ELSE 0
        END as availability_percentage
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    """

    try:
        result = _client.query(query).to_dataframe()

        if result.empty:
            return 0.0

        row = result.iloc[0]
        percentage = row['availability_percentage']

        return float(percentage) if pd.notna(percentage) else 0.0

    except Exception as e:
        st.error(f"Error getting Analogue Originator metric: {str(e)}")
        return 0.0


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
    if not global_filters.get('data_collection_period'):
        return 0.0

    # Build WHERE clause with global + local filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add local region filter (optional)
    if local_regions:
        local_regions_str = "', '".join(local_regions)
        where_clauses.append(f"region IN ('{local_regions_str}')")

    # Add local sector filter (optional)
    if local_sectors:
        local_sectors_str = "', '".join(local_sectors)
        where_clauses.append(f"sector IN ('{local_sectors_str}')")

    # Filter by Biosimilar and Human insulin type
    where_clauses.append("insulin_originator_biosimilar = 'Biosimilar'")
    where_clauses.append("insulin_type LIKE '%Human%'")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        COUNT(DISTINCT form_case__case_id) as total_facilities,
        COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) as facilities_with_insulin,
        CASE
            WHEN COUNT(DISTINCT form_case__case_id) > 0
            THEN ROUND((COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
            ELSE 0
        END as availability_percentage
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    """

    try:
        result = _client.query(query).to_dataframe()

        if result.empty:
            return 0.0

        row = result.iloc[0]
        percentage = row['availability_percentage']

        return float(percentage) if pd.notna(percentage) else 0.0

    except Exception as e:
        st.error(f"Error getting Human Biosimilar metric: {str(e)}")
        return 0.0


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
    if not global_filters.get('data_collection_period'):
        return 0.0

    # Build WHERE clause with global + local filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add local region filter (optional)
    if local_regions:
        local_regions_str = "', '".join(local_regions)
        where_clauses.append(f"region IN ('{local_regions_str}')")

    # Add local sector filter (optional)
    if local_sectors:
        local_sectors_str = "', '".join(local_sectors)
        where_clauses.append(f"sector IN ('{local_sectors_str}')")

    # Filter by Biosimilar and Analogue insulin type
    where_clauses.append("insulin_originator_biosimilar = 'Biosimilar'")
    where_clauses.append("insulin_type LIKE '%Analogue%'")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
        COUNT(DISTINCT form_case__case_id) as total_facilities,
        COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) as facilities_with_insulin,
        CASE
            WHEN COUNT(DISTINCT form_case__case_id) > 0
            THEN ROUND((COUNT(DISTINCT CASE WHEN is_unavailable = 0 THEN form_case__case_id END) * 100.0) / COUNT(DISTINCT form_case__case_id), 1)
            ELSE 0
        END as availability_percentage
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    """

    try:
        result = _client.query(query).to_dataframe()

        if result.empty:
            return 0.0

        row = result.iloc[0]
        percentage = row['availability_percentage']

        return float(percentage) if pd.notna(percentage) else 0.0

    except Exception as e:
        st.error(f"Error getting Analogue Biosimilar metric: {str(e)}")
        return 0.0


# ============================================================
# Plan 12: Comparator Medicine Availability Functions
# ============================================================

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
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Exclude NULL/empty regions
    where_clauses.append("region IS NOT NULL")
    where_clauses.append("TRIM(region) != ''")
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
        st.error(f"Error getting comparator medicine regions: {str(e)}")
        return None


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
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Exclude NULL/empty sectors
    where_clauses.append("sector IS NOT NULL")
    where_clauses.append("TRIM(sector) != ''")
    where_clauses.append("sector != 'NULL'")

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
        st.error(f"Error getting comparator medicine sectors: {str(e)}")
        return None


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
        pandas DataFrame with columns: name, strength, total_surveys, surveys_with_medicine, availability_percentage
    """
    if not global_filters.get('data_collection_period'):
        return None

    # Build WHERE clause with global + local filters
    where_clauses = ["1=1"]

    # Add data collection period filter (required)
    periods = global_filters['data_collection_period']
    periods_str = "', '".join(periods)
    where_clauses.append(f"data_collection_period IN ('{periods_str}')")

    # Add country filter (optional)
    if global_filters.get('country'):
        countries_str = "', '".join(global_filters['country'])
        where_clauses.append(f"country IN ('{countries_str}')")

    # Add global region filter (optional)
    if global_filters.get('region'):
        regions_str = "', '".join(global_filters['region'])
        where_clauses.append(f"region IN ('{regions_str}')")

    # Add local region filter (optional)
    if local_regions:
        local_regions_str = "', '".join(local_regions)
        where_clauses.append(f"region IN ('{local_regions_str}')")

    # Add local sector filter (optional)
    if local_sectors:
        local_sectors_str = "', '".join(local_sectors)
        where_clauses.append(f"sector IN ('{local_sectors_str}')")

    # Exclude NULL/empty names and strengths
    where_clauses.append("name IS NOT NULL")
    where_clauses.append("TRIM(name) != ''")
    where_clauses.append("strength IS NOT NULL")

    where_clause = " AND ".join(where_clauses)

    query = f"""
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
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY name, strength
    ORDER BY name DESC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting comparator medicine table data: {str(e)}")
        return None


# ============================================================================
# PRICE ANALYSIS FUNCTIONS (Phase 2)
# ============================================================================

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


@st.cache_data(ttl=600)
def get_price_by_inn(_client, table_name, filters):
    """
    Get min, median, and max insulin prices by INN category.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        filters (dict): Filters (data_collection_period, country, region, sector)

    Returns:
        pandas DataFrame with columns:
            - insulin_inn (str)
            - min_price_local (float)
            - median_price_local (float)
            - max_price_local (float)
            - min_price_usd (float)
            - median_price_usd (float)
            - max_price_usd (float)
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

    # Insulin INN filters
    where_clauses.append("insulin_inn IS NOT NULL")
    where_clauses.append("insulin_inn != '---'")

    # Out-of-pocket payment filter
    where_clauses.append("(insulin_out_of_pocket = 'Yes' OR insulin_out_of_pocket = 'Some people pay out of pocket')")

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT
      insulin_inn,
      MIN(insulin_standard_price_local) as min_price_local,
      APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(50)] as median_price_local,
      MAX(insulin_standard_price_local) as max_price_local,
      MIN(insulin_standard_price_usd) as min_price_usd,
      APPROX_QUANTILES(insulin_standard_price_usd, 100)[OFFSET(50)] as median_price_usd,
      MAX(insulin_standard_price_usd) as max_price_usd,
      COUNT(1) as product_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_inn
    ORDER BY insulin_inn ASC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting price by INN: {str(e)}")
        return None


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


@st.cache_data(ttl=600)
def get_median_price_by_presentation(_client, table_name, filters):
    """
    Get median insulin prices by presentation type.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        filters (dict): Filters (data_collection_period, country, region, sector)

    Returns:
        pandas DataFrame with columns:
            - insulin_presentation (str)
            - median_price_local (float)
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

    # Presentation filters
    where_clauses.append("insulin_presentation IS NOT NULL")

    # Out-of-pocket payment filter
    where_clauses.append("(insulin_out_of_pocket = 'Yes' OR insulin_out_of_pocket = 'Some people pay out of pocket')")

    where_clause = " AND ".join(where_clauses)

    # Use the complex median calculation from the plan
    query = f"""
    SELECT
      insulin_presentation,
      CASE
        WHEN MOD(COUNT(insulin_standard_price_local), 2) = 1 THEN APPROX_QUANTILES(insulin_standard_price_local, 2)[OFFSET(1)]
        WHEN MOD(COUNT(insulin_standard_price_local), 2) = 0 AND COUNT(insulin_standard_price_local) >= 100 THEN APPROX_QUANTILES(insulin_standard_price_local, 2)[OFFSET(1)]
        ELSE (APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(49)] + APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(51)]) / 2
      END as median_price_local,
      COUNT(1) as product_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_presentation
    ORDER BY insulin_presentation DESC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting median price by presentation: {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_median_price_by_originator_human(_client, table_name, filters):
    """
    Get median insulin prices by originator/biosimilar for human insulin.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        filters (dict): Filters (data_collection_period, country, region, sector)

    Returns:
        pandas DataFrame with columns:
            - insulin_originator_biosimilar (str)
            - median_price_local (float)
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

    # Human insulin type filter
    where_clauses.append("insulin_type LIKE '%Human%'")

    # Originator/biosimilar filters
    where_clauses.append("insulin_originator_biosimilar IS NOT NULL")
    where_clauses.append("insulin_originator_biosimilar != '---'")

    # Out-of-pocket payment filter
    where_clauses.append("(insulin_out_of_pocket = 'Yes' OR insulin_out_of_pocket = 'Some people pay out of pocket')")

    where_clause = " AND ".join(where_clauses)

    # Use the complex median calculation from the plan
    query = f"""
    SELECT
      insulin_originator_biosimilar,
      CASE
        WHEN MOD(COUNT(insulin_standard_price_local), 2) = 1 THEN APPROX_QUANTILES(insulin_standard_price_local, 2)[OFFSET(1)]
        WHEN MOD(COUNT(insulin_standard_price_local), 2) = 0 AND COUNT(insulin_standard_price_local) >= 100 THEN APPROX_QUANTILES(insulin_standard_price_local, 2)[OFFSET(1)]
        ELSE (APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(49)] + APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(51)]) / 2
      END as median_price_local,
      COUNT(1) as product_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_originator_biosimilar
    ORDER BY insulin_originator_biosimilar DESC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting median price by originator (human): {str(e)}")
        return None


@st.cache_data(ttl=600)
def get_median_price_by_originator_analogue(_client, table_name, filters):
    """
    Get median insulin prices by originator/biosimilar for analogue insulin.

    Args:
        _client: BigQuery client
        table_name: Table name (adl_surveys_repeat)
        filters (dict): Filters (data_collection_period, country, region, sector)

    Returns:
        pandas DataFrame with columns:
            - insulin_originator_biosimilar (str)
            - median_price_local (float)
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

    # Analogue insulin type filter
    where_clauses.append("insulin_type LIKE '%Analogue%'")

    # Originator/biosimilar filters
    where_clauses.append("insulin_originator_biosimilar IS NOT NULL")
    where_clauses.append("insulin_originator_biosimilar != '---'")

    # Out-of-pocket payment filter
    where_clauses.append("(insulin_out_of_pocket = 'Yes' OR insulin_out_of_pocket = 'Some people pay out of pocket')")

    where_clause = " AND ".join(where_clauses)

    # Use the complex median calculation from the plan
    query = f"""
    SELECT
      insulin_originator_biosimilar,
      CASE
        WHEN MOD(COUNT(insulin_standard_price_local), 2) = 1 THEN APPROX_QUANTILES(insulin_standard_price_local, 2)[OFFSET(1)]
        WHEN MOD(COUNT(insulin_standard_price_local), 2) = 0 AND COUNT(insulin_standard_price_local) >= 100 THEN APPROX_QUANTILES(insulin_standard_price_local, 2)[OFFSET(1)]
        ELSE (APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(49)] + APPROX_QUANTILES(insulin_standard_price_local, 100)[OFFSET(51)]) / 2
      END as median_price_local,
      COUNT(1) as product_count
    FROM `{config.GCP_PROJECT_ID}.{config.BQ_DATASET}.{table_name}`
    WHERE {where_clause}
    GROUP BY insulin_originator_biosimilar
    ORDER BY insulin_originator_biosimilar DESC
    """

    try:
        df = _client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error getting median price by originator (analogue): {str(e)}")
        return None


# ============================
# Phase 7: Free Insulin Functions
# ============================

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
