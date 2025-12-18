```markdown
# Dashboard UI Revamp - Availability Analysis Implementation Plan

## Project Overview
Complete redesign of the main dashboard UI with a focus on streamlined data analysis capabilities.

## Phase 1: Core Structure Implementation

### 1. Remove Existing UI
- Clear all current elements from the main dashboard
- Reset base styles and layout structure
- Prepare clean slate for new design

### 2. Implement Tab Navigation
Create a two-tab navigation system:
- **Tab 1:** Availability Analysis
- **Tab 2:** Price Analysis

### 3. Initial Focus: Availability Analysis Tab
Build the first tab using a phased approach. This plan covers Phase 1 of the Availability Analysis page.

## Phase 1 Components: Filter Controls

### 4. UI Design Reference
- Follow the design patterns from provided screenshots @Availability_Analysis_1.png and @Availability_Analysis_2.png  
- Focus on the first two tab options only
- Implement Data Collection Period with searchable dropdown functionality
- Ignore any additional tabs shown in reference images

### 5. Country Dropdown Filter

**Query Configuration:**
- **Table:** `adl_surveys`
- **Group By:** `country`
- **Metric:** `COUNT_DISTINCT(form_case__case_id)`
- **Sort:** `COUNT(DISTINCT form_case__case_id)`
- **Order:** `DESC`
`Date Range dimension`: `survey_date`


**Implementation Notes:**
- Display countries ranked by survey volume
- Include count badge/label showing number of surveys per country

### 6. Region Dropdown Filter

**Query Configuration:**
- **Table:** `adl_surveys`
- **Group By:** `region`
- **Metric:** `COUNT_DISTINCT(form_case__case_id)`
- **Sort:** `COUNT(DISTINCT form_case__case_id)`
- **Order:** `DESC`

**Implementation Notes:**
- Display regions ranked by survey volume
- Include count badge/label showing number of surveys per region

### 7. Data Collection Period Dropdown

**Query Configuration:**
- **Table:** `adl_surveys`
- **Group By:** `data_collection_period`
- **Metric:** `COUNT_DISTINCT(form_case__case_id)`
- **Sort:** `data_collection_period DESC`

**Implementation Notes:**
- Implement searchable dropdown functionality
- Display periods in reverse chronological order
- Include count of surveys per period

### 8. Selected Data Collection Summary Table

**Query Configuration:**
- **Table:** `adl_surveys`
- **Group By:** `data_collection_period`
- **Metrics:**
  - First Survey Date: `MIN(survey_date)`
  - Last Survey Date: `MAX(survey_date)`
- **Sort:** `data_collection_period DESC`
- **Filter:** `EXCLUDE data_collection_period EQUALS "Click here to select..."`

**Table Columns:**
1. Data Collection Period
2. First Survey Date
3. Last Survey Date
4. Survey Count (implicit from grouping)

**Implementation Notes:**
- Display only selected/active data collection periods
- Exclude placeholder values from results
- Format dates consistently (suggest: YYYY-MM-DD or regional format)
- Enable sorting on all columns

## Next Steps
- Complete Phase 1 implementation
- Await approval before proceeding to Phase 2
- Phase 2 will add additional UI elements to the Availability Analysis page

## Technical Considerations
- Ensure all dropdowns have proper loading states
- Implement error handling for failed queries
- Add responsive design for mobile/tablet views
- Consider caching strategy for dropdown data
- Implement proper SQL injection prevention
- Add accessibility features (ARIA labels, keyboard navigation)
```

***Use serena tool to implement this plan***