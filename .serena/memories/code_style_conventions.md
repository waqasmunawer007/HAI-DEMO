# Code Style and Conventions

## Python Style
- Standard Python conventions (PEP 8)
- Type hints: Not heavily used in current codebase
- Docstrings: Minimal, mostly inline comments

## Naming Conventions
- Variables: snake_case (e.g., `filtered_df`, `selected_country`)
- Functions: snake_case (e.g., `calc_availability`, `get_bigquery_client`)
- Constants: UPPER_CASE (e.g., `GCP_PROJECT_ID`, `BQ_DATASET`)

## Streamlit Patterns
- Session state keys: `st.session_state.df`, `st.session_state.selected_table`
- All BigQuery functions use `@st.cache_data(ttl=600)` for 10-minute cache
- Client creation uses `@st.cache_resource` (persists across reruns)
- Always use `.copy()` when creating filtered DataFrames
- Check `if not df.empty:` before processing

## HTML/CSS in Streamlit
- Custom HTML uses `st.markdown(html, unsafe_allow_html=True)`
- Reusable CSS classes: `.main-header`, `.metric-card`, `.section-header`, `.info-box`, `.warning-box`
- Color palette: Primary `#1f77b4`, Secondary `#ff7f0e`, Background `#f8f9fa`

## Data Processing Patterns
- Always check if columns exist before using them
- Handle multiple data types for availability: String ("Yes"/"No"), Boolean, Integer (1/0)
- Use `.lower()` when searching column names for case-insensitivity

## Visualization Standards
- Use Plotly for all charts
- Standard layout: `plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'`
- Use `st.plotly_chart(fig, use_container_width=True)` for responsiveness