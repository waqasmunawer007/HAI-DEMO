# Price Analysis Tab - Phase 1 Implementation Plan (Refined)

## Overview
This document provides a detailed implementation plan for Phase 1 of the Price Analysis tab. The implementation follows the existing architecture patterns established in the Availability Analysis tab, ensuring consistency in UI/UX, data handling, and code structure.

## Phase 1 Scope
Phase 1 focuses on building the foundational structure of the Price Analysis tab:
- Page header and title
- Instructions and Definitions sections
- Data Selectors (Country, Region, Data Collection Period filters)
- Filter integration with session state
- No data visualizations in Phase 1 (reserved for Phase 2+)

---

## 1. Page Structure

### 1.1 Tab Title
**Location:** `app.py` line ~2511 (inside `with tab2:` block)

**Implementation:**
```python
with tab2:
    # Page title
    st.markdown("""
        <div class="main-header">
            <h1>💰 Insulin Price Analysis</h1>
            <p>Comprehensive analysis of insulin pricing across facilities and regions</p>
        </div>
    """, unsafe_allow_html=True)
```

**CSS:** Uses existing `.main-header` class (already defined in app.py lines 72-91)

---

### 1.2 Two-Column Layout: Instructions & Definitions

**Location:** Immediately after page title

**Implementation:**
Create a two-column layout using Streamlit's column structure:

```python
# Instructions and Definitions Section
st.markdown("<br>", unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    # Instructions column

with col_right:
    # Definitions column
```

#### Column 1: Instructions

**Content Structure:**
```html
<div class="info-box">
    <span style="font-size: 16px;">
        <b>Instructions:
            <font color="#d32f2f">To begin select a Data Collection Period (data not shown by default)</font>
        </b>
    </span>
    <br><br>
    <span style="font-size: 16px;">
        <i>Selecting a region:</i> By default, all regions are displayed.
        You can select one or more regions by using the Region selection box,
        this will apply for all graphs under the same heading.
    </span>
    <br><br>
    <span style="font-size: 16px;">
        <i>Currency:</i> By default, results are displayed in local currency.
        To select USD, see below.
    </span>
    <br><br>
    <span style="font-size: 16px;">
        For more see the
        <a href="https://accisstoolkit.haiweb.org/user-guide/" target="_blank">
            <u>User Guide</u>
        </a>
    </span>
    <br><br>
    <div style="display: flex; align-items: center;">
        <span style="margin-right: 8px;">⚙️</span>
        <span>
            <b>Optional metrics</b> - many graphs and scorecards have optional metrics,
            such as the number of facilities or the price in USD. If available,
            the button is shown in the top right corner of the graph.
            Click on this to choose which metric to show, or show multiple for comparison.
        </span>
    </div>
</div>
```

**Icon:** Use `⚙️` emoji for optional metrics (as suggested in plan)

**CSS:** Uses existing `.info-box` class (already defined in app.py lines 162-168)

#### Column 2: Definitions

**Content Structure:**
```html
<div class="info-box">
    <font style="font-size: 16px;"><b>Definitions:</b></font>
    <br><br>
    <i>Insulin Price</i> - Standardised in all cases to 1000IU.
    <br><br>
    <i>Facilities (n)</i> - Number of facilities within a certain category.
    <br><br>
    <i>Reported Responses (%)</i> - Percentage out of all reported responses
    (products, places, etc.) in a certain category.
    <br><br>
    <i>Reported Responses (n)</i> - Number of responses (products, places, etc.)
    reported in a certain category.
    <br><br>
    <i>INN</i>: International Nonproprietary Name
</div>
```

**CSS:** Uses existing `.info-box` class

---

## 2. Data Selectors Section

### 2.1 Section Header

**Implementation:**
```python
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header"><h3>Data Selectors</h3></div>', unsafe_allow_html=True)
```

### 2.2 Three-Column Filter Layout

**Layout Structure:**
```python
# Create three columns for the filter dropdowns
col1, col2, col3 = st.columns(3)
```

### 2.3 Filter 1: Country Dropdown

**Location:** `col1`

**Database Query:**
- **Table:** `adl_surveys`
- **Function:** `get_grouped_counts(client, table_name, "country")`
- **Group By:** `country`
- **Metric:** `COUNT(DISTINCT form_case__case_id)`
- **Sort:** `ORDER BY COUNT(DISTINCT form_case__case_id) DESC`

**Implementation Pattern:**
```python
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
```

**Session State Key:** `selected_countries_price` (separate from availability tab to avoid conflicts)

### 2.4 Filter 2: Region Dropdown

**Location:** `col2`

**Database Query:**
- **Table:** `adl_surveys`
- **Function:** `get_grouped_counts(client, table_name, "region")`
- **Group By:** `region`
- **Metric:** `COUNT(DISTINCT form_case__case_id)`
- **Sort:** `ORDER BY COUNT(DISTINCT form_case__case_id) DESC`

**Implementation Pattern:**
```python
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
```

**Session State Key:** `selected_regions_price`

### 2.5 Filter 3: Data Collection Period Dropdown

**Location:** `col3`

**Database Query:**
- **Table:** `adl_surveys`
- **Function:** `get_data_collection_periods(client, table_name)` (already exists in bigquery_client.py)
- **Group By:** `data_collection_period`
- **Metric:** `MIN(survey_date)` (for ordering)
- **Sort:** `ORDER BY data_collection_period DESC`

**Implementation Pattern:**
```python
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
```

**Session State Key:** `selected_periods_price`

---

## 3. Default State Message

### 3.1 "Data Not Shown" Message

**Location:** After Data Selectors section

**Condition:** Display when no Data Collection Period is selected

**Implementation:**
```python
st.markdown("<br>", unsafe_allow_html=True)

if not st.session_state.selected_periods_price:
    st.markdown("""
        <div class="info-box">
            <strong>💡 Data is not shown by default.</strong><br>
            Use the dropdown menu above to select a Data Collection Period and see the data.
        </div>
    """, unsafe_allow_html=True)
else:
    # Future Phase 2: Price visualizations will go here
    st.markdown("""
        <div class="info-box">
            <strong>📊 Price Visualizations</strong><br>
            Price analysis charts and metrics will be displayed here in Phase 2.
        </div>
    """, unsafe_allow_html=True)
```

---

## 4. Session State Management

### 4.1 Initialize Session State Variables

**Location:** `app.py` - Before the tab definitions (around line 210-217)

**Implementation:**
```python
# Initialize session state for Price Analysis tab
if 'selected_countries_price' not in st.session_state:
    st.session_state.selected_countries_price = []
if 'selected_regions_price' not in st.session_state:
    st.session_state.selected_regions_price = []
if 'selected_periods_price' not in st.session_state:
    st.session_state.selected_periods_price = []
```

### 4.2 Session State Keys Summary

| Filter | Session State Key | Data Type | Purpose |
|--------|------------------|-----------|---------|
| Country | `selected_countries_price` | List[str] | Store selected country names |
| Region | `selected_regions_price` | List[str] | Store selected region names |
| Data Collection Period | `selected_periods_price` | List[str] | Store selected period names |

**Note:** Using separate session state keys (with `_price` suffix) prevents conflicts with the Availability Analysis tab filters.

---

## 5. Database Functions Required

### 5.1 Existing Functions (No Changes Needed)

The following functions already exist in `database/bigquery_client.py` and can be reused:

1. **`get_bigquery_client()`** - Creates cached BigQuery client connection
2. **`get_grouped_counts(_client, table_name, group_by_column, sort_desc=True)`** - Generic grouped counting
3. **`get_data_collection_periods(_client, table_name)`** - Fetches data collection periods with counts

### 5.2 Table Configuration

**Primary Table:** `adl_surveys`

**Table Constant:** Use existing `TABLE_NAME` constant:
```python
TABLE_NAME = "adl_surveys"
```

This table is already used in Availability Analysis tab and contains the required columns:
- `country`
- `region`
- `data_collection_period`
- `form_case__case_id` (for counting surveys)

---

## 6. Code Organization

### 6.1 File Structure

```
/Users/waqas/HAI_demo/
├── app.py                          # Main application file
│   └── [Line ~2511] Tab 2: Price Analysis
│       ├── Page header & title
│       ├── Instructions & Definitions (2 columns)
│       ├── Data Selectors section (3 columns)
│       └── Default state message
├── database/
│   └── bigquery_client.py         # No changes needed in Phase 1
├── plans/
│   ├── Price_Analysis_plan1.md    # Original plan
│   └── Price_Analysis_Phase1_Refined.md  # This document
```

### 6.2 Code Sections in app.py

**Tab 2 Structure (after implementation):**

```python
# Tab 2: Price Analysis - Phase 1
with tab2:
    # Section 1: Page Header (Lines ~2512-2520)
    # - Title: "Insulin Price Analysis"
    # - Subtitle/description

    # Section 2: Instructions & Definitions (Lines ~2521-2600)
    # - Two-column layout
    # - Left: Instructions with icon
    # - Right: Definitions list

    # Section 3: Data Selectors (Lines ~2601-2750)
    # - Section header
    # - Three-column layout (Country, Region, Period)
    # - Multi-select dropdowns with counts
    # - Session state updates

    # Section 4: Default State Message (Lines ~2751-2770)
    # - Show info box when no period selected
    # - Placeholder for future visualizations
```

---

## 7. Testing Strategy

### 7.1 Manual Testing Checklist

**Filter Functionality:**
- [ ] Country dropdown loads with survey counts
- [ ] Region dropdown loads with survey counts
- [ ] Data Collection Period dropdown loads with survey counts
- [ ] Multi-select works for all three filters
- [ ] Selection summary shows correct count
- [ ] Session state persists when switching tabs
- [ ] Filters are independent from Availability Analysis tab filters

**UI/UX Testing:**
- [ ] Page title displays correctly with gradient styling
- [ ] Two-column layout renders properly on desktop
- [ ] Instructions text is formatted correctly (bold, italic, colors)
- [ ] Definitions text displays all items
- [ ] Optional metrics icon (⚙️) appears correctly
- [ ] Info boxes use correct background colors
- [ ] Default message appears when no period selected
- [ ] Responsive layout works on different screen sizes

**Data Integrity:**
- [ ] BigQuery queries execute successfully
- [ ] Country counts match expected values
- [ ] Region counts match expected values
- [ ] Period counts match expected values
- [ ] Spinner shows during data loading
- [ ] Error messages display for query failures

### 7.2 Test Execution Commands

**Syntax Check:**
```bash
python3 -m py_compile app.py
```

**Run Application:**
```bash
streamlit run app.py
```

**Test Navigation:**
1. Open app at `http://localhost:8501`
2. Click "💰 Price Analysis" tab
3. Verify page loads without errors
4. Test each filter dropdown
5. Select combinations of filters
6. Switch to Availability Analysis tab and back
7. Verify filter selections persist

### 7.3 Expected BigQuery Queries

**Country Filter Query:**
```sql
SELECT
    country,
    COUNT(DISTINCT form_case__case_id) as survey_count
FROM `hai-dev.facilities.adl_surveys`
GROUP BY country
ORDER BY survey_count DESC
```

**Region Filter Query:**
```sql
SELECT
    region,
    COUNT(DISTINCT form_case__case_id) as survey_count
FROM `hai-dev.facilities.adl_surveys`
GROUP BY region
ORDER BY survey_count DESC
```

**Data Collection Period Query:**
```sql
SELECT
    data_collection_period,
    COUNT(DISTINCT form_case__case_id) as survey_count
FROM `hai-dev.facilities.adl_surveys`
GROUP BY data_collection_period
ORDER BY data_collection_period DESC
```

---

## 8. Implementation Steps

### Step 1: Initialize Session State (5 minutes)
- Add session state initialization for three filter variables
- Location: Before tab definitions in app.py

### Step 2: Replace Tab 2 Placeholder (5 minutes)
- Remove existing placeholder content (lines 2512-2519)
- Add page header with title

### Step 3: Build Instructions & Definitions Layout (15 minutes)
- Create two-column layout
- Add Instructions content with HTML formatting
- Add Definitions content with HTML formatting
- Test responsive layout

### Step 4: Build Data Selectors Section (30 minutes)
- Add section header
- Create three-column layout
- Implement Country filter dropdown
- Implement Region filter dropdown
- Implement Data Collection Period filter dropdown
- Test all filters with BigQuery

### Step 5: Add Default State Message (5 minutes)
- Add conditional info box
- Test display when no period selected

### Step 6: Testing & Validation (20 minutes)
- Run syntax check
- Manual testing of all filters
- Cross-tab navigation testing
- Responsive layout testing

**Total Estimated Time:** ~80 minutes

---

## 9. Future Phases Preview

### Phase 2: Price Visualizations
- Overall price metrics (average, median, range)
- Price by sector (bar chart)
- Price by insulin type (comparison chart)
- Price by region (geographic visualization)
- Price trends over time

### Phase 3: Advanced Analytics
- Currency conversion toggle (Local ↔ USD)
- Originator vs biosimilar price comparison
- Price by presentation type (vial, pen, cartridge)
- Price distribution histograms
- Outlier detection and highlighting

### Phase 4: Export & Reporting
- Download price data as CSV/Excel
- Generate price analysis reports
- Custom price comparison tools
- Alert thresholds for price anomalies

---

## 10. Key Design Decisions

### 10.1 Session State Separation
**Decision:** Use separate session state keys for Price Analysis filters (`_price` suffix)

**Rationale:**
- Prevents conflicts with Availability Analysis tab
- Allows independent filter selections between tabs
- Enables future cross-tab comparisons if needed

### 10.2 Reuse Existing Database Functions
**Decision:** Use existing `get_grouped_counts()` and `get_data_collection_periods()` functions

**Rationale:**
- Reduces code duplication
- Maintains consistency in query patterns
- Leverages existing caching mechanisms
- Simplifies maintenance

### 10.3 Same Table as Availability Analysis
**Decision:** Use `adl_surveys` table for Phase 1 filters

**Rationale:**
- Same table contains both availability and price data
- Ensures filter consistency across tabs
- Simplifies initial implementation
- Future phases may join with price-specific tables

### 10.4 HTML-Based Layout for Instructions
**Decision:** Use HTML markup for Instructions and Definitions sections

**Rationale:**
- Matches existing styling patterns in app.py
- Provides fine-grained control over formatting
- Enables exact color specifications (`#d32f2f`)
- Consistent with Looker Studio design reference

---

## 11. Potential Issues & Solutions

### Issue 1: Filter State Not Persisting
**Symptom:** Filters reset when switching tabs
**Solution:** Ensure session state variables are initialized before tab definitions

### Issue 2: Query Performance
**Symptom:** Slow dropdown loading
**Solution:** Existing `@st.cache_data(ttl=600)` decorator on query functions handles this

### Issue 3: Empty Dropdowns
**Symptom:** No options appear in dropdowns
**Solution:**
- Verify BigQuery authentication
- Check table name constant is correct
- Verify `adl_surveys` table has data
- Check error messages in UI

### Issue 4: Layout Breaking on Mobile
**Symptom:** Columns stack incorrectly
**Solution:** Existing responsive CSS handles this (lines 179+ in app.py)

---

## 12. Dependencies

### Required Packages (Already Installed)
- `streamlit` - UI framework
- `pandas` - Data manipulation
- `google-cloud-bigquery` - BigQuery client
- `plotly` - For future visualizations (Phase 2+)

### Required Files
- `app.py` - Main application
- `database/bigquery_client.py` - Database functions
- `config.py` - Configuration settings
- `.env` - Environment variables (BigQuery project ID, credentials)

### BigQuery Requirements
- Project: `hai-dev`
- Dataset: `facilities`
- Table: `adl_surveys`
- Columns needed:
  - `country` (STRING)
  - `region` (STRING)
  - `data_collection_period` (STRING)
  - `form_case__case_id` (STRING)

---

## 13. Acceptance Criteria

Phase 1 implementation is complete when:

- [x] **AC1:** Page displays "Insulin Price Analysis" title with gradient header
- [x] **AC2:** Instructions and Definitions appear in two-column layout
- [x] **AC3:** All HTML text formatting matches the specification (bold, italic, colors)
- [x] **AC4:** Optional metrics icon (⚙️) displays in Instructions
- [x] **AC5:** User Guide link is clickable and opens in new tab
- [x] **AC6:** Data Selectors section header is visible
- [x] **AC7:** Country dropdown loads with survey counts in format "Country (N)"
- [x] **AC8:** Region dropdown loads with survey counts in format "Region (N)"
- [x] **AC9:** Data Collection Period dropdown loads with survey counts
- [x] **AC10:** All dropdowns support multi-select
- [x] **AC11:** Selection summaries show "✓ N item(s) selected"
- [x] **AC12:** Default message appears when no period is selected
- [x] **AC13:** Filters persist when switching between tabs
- [x] **AC14:** No console errors or query failures
- [x] **AC15:** Page passes syntax check (`python3 -m py_compile app.py`)

---

## Appendix A: HTML/CSS Reference

### Existing CSS Classes Used
```css
.main-header         /* Lines 72-91: Gradient header */
.info-box           /* Lines 162-168: Blue info boxes */
.section-header     /* Lines 94-99: Section dividers */
```

### Color Palette
- **Primary Blue:** `#1f77b4`
- **Red Accent:** `#d32f2f` (for important instructions)
- **Info Box Background:** `#e3f2fd`
- **Info Box Border:** `#2196f3`
- **Gradient Start:** `#667eea`
- **Gradient End:** `#764ba2`

### Typography
- **Body Text:** 16px
- **Headers:** Default Streamlit sizing
- **Bold:** `<b>` tag
- **Italic:** `<i>` tag

---

## Appendix B: Session State Architecture

```python
# Availability Analysis Tab (Tab 1) - Existing
st.session_state.selected_countries     # List[str]
st.session_state.selected_regions       # List[str]
st.session_state.selected_periods       # List[str]

# Price Analysis Tab (Tab 2) - New in Phase 1
st.session_state.selected_countries_price  # List[str]
st.session_state.selected_regions_price    # List[str]
st.session_state.selected_periods_price    # List[str]
```

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-07 | AI Assistant | Initial refined plan from Price_Analysis_plan1.md |

---

**End of Refined Implementation Plan**
