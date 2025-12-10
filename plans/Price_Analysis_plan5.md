Price Analysis Tab
Plan #05

Create a similar plan to @Price_Analysis_plan4_refined.md refined plan # 05.

**Use Serena MCP:** Define todo items list and solve them one by one according to this detailed plan.
Use Pltory to draw chart.
Use Serena MCP to define todo items list and solve them one by one according to this detailed plan.

Task Overview:
1. Add a new section called  Median price - By presentation after Price - By brand section.


2. ADD  two mutliselect dropdowns Region and Sector.
- Expandable dropdown (st.expander) containing checkbox list
3. Add two tables one for Human and the other for Analogue in two columns.
Each table has following columns.
- Insulin Brand
- Facility with Availablity (n)
- Min Price-Local
- Median Price-Local
- Max Price-Local

3. Display a clustered barchart for Median Price - Local.
For  Clustered barchart:
-- Y axis title is Median price - Local .
-- Y axis price range is dynamic based on max price value 
-- Each bar is shaded with price value.
- Values: Dynamic  main categories: for example Vial, Pre-filled Pen, Catridge etc.  
 - Rotation: Angle labels (-45°) for readability if needed
 -Legend - Add one legend called "Median Price-Local" in (Teal/Dark Blue)


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

3. Median price - By presentation clustered bar chart
- Table: adl_surveys_repeat
- Metric: 
for insulin_standard_price_local_median use:
CASE
	WHEN MOD(COUNT(insulin_standard_price_local), 2) = 1 THEN MEDIAN(insulin_standard_price_local)
    WHEN MOD(COUNT(insulin_standard_price_local), 2) = 0 AND COUNT(insulin_standard_price_local) >= 100 THEN MEDIAN(insulin_standard_price_local)
    ELSE (PERCENTILE(insulin_standard_price_local, 49) + PERCENTILE(insulin_standard_price_local, 51)) / 2
END
-optional metrics:
for insulin_standard_price_usd_median use:
CASE
	WHEN MOD(COUNT(insulin_standard_price_usd), 2) = 1 THEN MEDIAN(insulin_standard_price_usd)
    WHEN MOD(COUNT(insulin_standard_price_usd), 2) = 0 AND COUNT(insulin_standard_price_usd) >= 100 THEN MEDIAN(insulin_standard_price_usd)
    ELSE (PERCENTILE(insulin_standard_price_usd, 49) + PERCENTILE(insulin_standard_price_usd, 51)) / 2
END

-count(1)


- Sort: ORDER BY insulin_presentation DESC
- Group by insulin_presentation
