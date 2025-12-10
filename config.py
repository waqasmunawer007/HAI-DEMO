"""
Configuration settings for the Streamlit BigQuery application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# BigQuery Configuration
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "hai-dev")
BQ_DATASET = os.getenv("BQ_DATASET", "facilities")

# BigQuery Tables
TABLES = {
    "comparators": "adl_comparators",
    "repeat_repivot": "adl_repeat_repivot",
    "surveys": "adl_surveys",
    "surveys_repeat": "adl_surveys_repeat",
    "surveys_repeat_cgm": "adl_surveys_repeat_cgm"
}

# Optional: Service Account Credentials Path
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", None)

# App Configuration
APP_TITLE = "HAI Facilities Data Dashboard"
APP_ICON = "📊"