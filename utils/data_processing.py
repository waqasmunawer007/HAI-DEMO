"""
Data transformation and processing utility functions.
"""
import pandas as pd


def format_currency(value, currency="USD"):
    """
    Format numeric values as currency.

    Args:
        value: Numeric value to format
        currency: Currency symbol (default: USD)

    Returns:
        Formatted currency string
    """
    if pd.isna(value):
        return "N/A"

    if currency == "USD":
        return f"${value:,.2f}"
    else:
        return f"{value:,.2f}"


def calculate_summary_stats(df, column):
    """
    Calculate summary statistics for a numeric column.

    Args:
        df: pandas DataFrame
        column: Column name to analyze

    Returns:
        Dictionary with summary statistics
    """
    if column not in df.columns:
        return None

    stats = {
        "count": df[column].count(),
        "mean": df[column].mean(),
        "median": df[column].median(),
        "min": df[column].min(),
        "max": df[column].max(),
        "std": df[column].std()
    }

    return stats


def filter_by_country(df, countries):
    """
    Filter DataFrame by country selection.

    Args:
        df: pandas DataFrame
        countries: List of country names

    Returns:
        Filtered DataFrame
    """
    if not countries or "country" not in df.columns:
        return df

    return df[df["country"].isin(countries)]


def filter_by_date_range(df, date_column, start_date, end_date):
    """
    Filter DataFrame by date range.

    Args:
        df: pandas DataFrame
        date_column: Name of the date column
        start_date: Start date
        end_date: End date

    Returns:
        Filtered DataFrame
    """
    if date_column not in df.columns:
        return df

    df[date_column] = pd.to_datetime(df[date_column])

    mask = (df[date_column] >= pd.to_datetime(start_date)) & \
           (df[date_column] <= pd.to_datetime(end_date))

    return df[mask]


def aggregate_by_region(df, value_column):
    """
    Aggregate data by region.

    Args:
        df: pandas DataFrame
        value_column: Column to aggregate

    Returns:
        Aggregated DataFrame
    """
    if "region" not in df.columns or value_column not in df.columns:
        return None

    return df.groupby("region")[value_column].agg(['count', 'mean', 'sum']).reset_index()


def get_availability_summary(df):
    """
    Calculate availability statistics for products.

    Args:
        df: pandas DataFrame with availability columns

    Returns:
        Dictionary with availability statistics
    """
    availability_cols = [col for col in df.columns if 'available' in col.lower()]

    summary = {}
    for col in availability_cols:
        if col.endswith('_num'):
            continue

        available_count = (df[col] == 'Yes').sum() if df[col].dtype == 'object' else df[col].sum()
        total_count = df[col].count()

        summary[col] = {
            "available": available_count,
            "total": total_count,
            "percentage": (available_count / total_count * 100) if total_count > 0 else 0
        }

    return summary


def clean_price_data(df, price_columns):
    """
    Clean and standardize price data.

    Args:
        df: pandas DataFrame
        price_columns: List of price column names

    Returns:
        DataFrame with cleaned price columns
    """
    df_clean = df.copy()

    for col in price_columns:
        if col in df_clean.columns:
            # Convert to numeric, handling errors
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

            # Remove negative prices
            df_clean.loc[df_clean[col] < 0, col] = None

    return df_clean