# HAI Facilities Data Dashboard - Project Overview

## Purpose
Modern Streamlit application for analyzing healthcare facilities data from Google BigQuery. Focuses on insulin availability, pricing, medical device access, and facility distribution across multiple regions.

## Tech Stack
- **Frontend**: Streamlit (single-file app.py ~1050 lines)
- **Database**: Google BigQuery
- **Visualization**: Plotly (Express and Graph Objects)
- **Data Processing**: Pandas
- **Authentication**: Google Cloud (gcloud auth or service account)
- **Python Version**: Python 3.x

## BigQuery Configuration
- **Project**: hai-dev
- **Dataset**: facilities
- **Tables**: adl_surveys, adl_comparators, adl_repeat_repivot, adl_surveys_repeat, adl_surveys_repeat_cgm

## Key Features
- 6 main tabs: Availability Analysis, Price Analysis, Trends & Insights, Data Explorer, Custom Query, About
- Session state management for data persistence
- Filter system: Country, Region, Sector dropdowns
- 10 specialized insulin filters in Availability Analysis tab
- Custom CSS styling with gradient headers and metric cards