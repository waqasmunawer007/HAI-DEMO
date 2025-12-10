Price Analysis Tab
Plan #04

Create a similar plan to @Price_Analysis_plan3_refined.md refined plan # 04.

**Use Serena MCP:** Define todo items list and solve them one by one according to this detailed plan.
Use Pltory to draw chart.
Use Serena MCP to define todo items list and solve them one by one according to this detailed plan.

Task Overview:
1. Add a new section called  Price - By brand after Price By INN section.


2. ADD  two mutliselect dropdowns Region and Sector.
- Expandable dropdown (st.expander) containing checkbox list
3. Add two tables one for Human and the other for Analogue in two columns.
Each table has following columns.
- Insulin Brand
- Facility with Availablity (n)
- Min Price-Local
- Median Price-Local
- Max Price-Local

-Add paginations to tables.


#Query Configurations:

1.For Region dropdown:
- Table: adl_surveys
- Metric: COUNT_DISTINCT(form_case__case_id)
-Filter: EXCLUDE region EQUALS "NULL"
- Sort: ORDER BY region DESC

2.For Sector dropdown:
- Table: adl_surveys
- Metric: COUNT_DISTINCT(form_case__case_id)
- Sort: ORDER BY sector DESC

3. For Human - Insulin Brand
- Table: adl_surveys_repeat
- Metric: 
COUNT_DISTINCT(form_case__case_id),
Min(insulin_standard_price_local),
max(insulin_standard_price_local),
for median price use 
CASE
        WHEN MOD(COUNT(insulin_price_local), 2) = 1 THEN MEDIAN(insulin_price_local)
    WHEN MOD(COUNT(insulin_price_local), 2) = 0 AND COUNT(insulin_price_local) >= 100 THEN MEDIAN(insulin_price_local)
    ELSE (PERCENTILE(insulin_price_local, 49) + PERCENTILE(insulin_price_local, 51)) / 2
END
Optional metrics:
- For insulin_standard_price_usd_median:
CASE
	WHEN MOD(COUNT(insulin_standard_price_usd), 2) = 1 THEN MEDIAN(insulin_standard_price_usd)
    WHEN MOD(COUNT(insulin_standard_price_usd), 2) = 0 AND COUNT(insulin_standard_price_usd) >= 100 THEN MEDIAN(insulin_standard_price_usd)
    ELSE (PERCENTILE(insulin_standard_price_usd, 49) + PERCENTILE(insulin_standard_price_usd, 51)) / 2
END
- Min(insulin_standard_price_usd)
- Max(insulin_standard_price_usd)


-Filter: 
INCLUDE insulin_type CONTAINS "Human",
EXCLUDE insulin_standard_price_local EQUALS  "NULL",
EXCLUDE insulin_brand EQUALS  "0" OR
EXCLUDE insulin_brand EQUALS  "---"
INCLUDE insulin_out_of_pocket EQUALS "Yes"
OR
INCLUDE insulin_out_of_pocket EQUALS "Some people pay out of pocket"
- Sort: Order by COUNT_DISTINCT(form_case__case_id) DESC
- Group by  insulin_brand



- For Analogue - Insulin Brand

- Table: adl_surveys_repeat
- Metric: 
COUNT_DISTINCT(form_case__case_id),
Min(insulin_standard_price_local),
max(insulin_standard_price_local),
for median price use 
CASE
        WHEN MOD(COUNT(insulin_price_local), 2) = 1 THEN MEDIAN(insulin_price_local)
    WHEN MOD(COUNT(insulin_price_local), 2) = 0 AND COUNT(insulin_price_local) >= 100 THEN MEDIAN(insulin_price_local)
    ELSE (PERCENTILE(insulin_price_local, 49) + PERCENTILE(insulin_price_local, 51)) / 2
END
Optional metrics:
- For insulin_standard_price_usd_median:
CASE
	WHEN MOD(COUNT(insulin_standard_price_usd), 2) = 1 THEN MEDIAN(insulin_standard_price_usd)
    WHEN MOD(COUNT(insulin_standard_price_usd), 2) = 0 AND COUNT(insulin_standard_price_usd) >= 100 THEN MEDIAN(insulin_standard_price_usd)
    ELSE (PERCENTILE(insulin_standard_price_usd, 49) + PERCENTILE(insulin_standard_price_usd, 51)) / 2
END
- Min(insulin_standard_price_usd)
- Max(insulin_standard_price_usd)


-Filter: 
INCLUDE insulin_type CONTAINS "Analogue",
EXCLUDE insulin_standard_price_local EQUALS  "NULL",
EXCLUDE insulin_brand EQUALS  "0" OR
EXCLUDE insulin_brand EQUALS  "---"
INCLUDE insulin_out_of_pocket EQUALS "Yes"
OR
INCLUDE insulin_out_of_pocket EQUALS "Some people pay out of pocket"
- Sort: Order by COUNT_DISTINCT(form_case__case_id) DESC
- Group by  insulin_brand