Price Analysis Tab
Plan #02

Create a similar plan to @Price_Analysis_Phase1_Refined.md refined plan # 02.

**Use Serena MCP:** Define todo items list and solve them one by one according to this detailed plan.
Use Pltory to draw chart.

Task Overview:

1. Creata a new section below to  Data Selectors dropdowns.
2. Heading is "Where patients were charged the full price"
3. A paragraph below to this heading: "Insulin price is standardised in all cases to 1000IU. Click on the optional metrics button to see the number of products that make up the median price."
4.ADD  two mutliselect dropdowns Region and Sector.
- Expandable dropdown (st.expander) containing checkbox list
5. Then add another heading "Median price - By insulin type" for Clustered bar chart.
6. Display a clustered barchart for Median price - By insulin type.
For 1st Clustered barchart:
-- Y axis title is Median price - Local .
-- Y axis range is 0 to 6k.
-- X axis title is Insulin Type.
-- Each bar is shaded with price value.
- Values: Seven main categories: Short-Acting Human, Intermediate-Acting Human, Mixed Human, Long-Acting Analogue, Rapid-Acting Analogue, Mixed Analogue and Intermediate-Acting Anima
 - Rotation: Angle labels (-45°) for readability if needed
 -Legend - Add one legend called "Median Price-Local" in (Teal/Dark Blue)
 

7.and new heading below to Median Price-Local clustered barchar called " Median price - By insulin type and level of care (public sector only)"

8- Add similar clustered bar chart as Legend - Median Price-Local with two legends Secondary and Tertiary. and it has same seven categories.

#Query configuration:
1.For Region dropdown:
- Table: adl_surveys
- Metric: COUNT_DISTINCT(form_case__case_id)
-Filter: EXCLUDE region EQUALS "NULL"
- Sort: ORDER BY region DESC

2.For Sector dropdown:
- Table: adl_surveys
- Metric: COUNT_DISTINCT(form_case__case_id)
- Sort: ORDER BY sector DESC

3. For Median price - By insulin type clustered bar chart: 
- Table: adl_surveys_repeat
- Metric: insulin_standard_price_local_median, insulin_standard_price_usd_median(Optional Metric), 
count(1)(optional metric)
- Filter: EXCLUDE insulin_type EQUALS  "---" AND INCLUDE insulin_out_of_pocket EQUALS "Yes"
OR
INCLUDE insulin_out_of_pocket EQUALS "Some people pay out of pocket"
- Sort: ORDER BY insulin_type_order ASC
- Group by insulin_type

4. For Median price - By insulin type and level of care (public sector only): 
- Table: adl_surveys_repeat
- Metric: insulin_standard_price_local_median, insulin_standard_price_usd_median(Optional Metric), 
count(1)(optional metric)

- Filter: EXCLUDE insulin_type EQUALS  "---" AND INCLUDE Sector CONTAINS "Public" AND
(EXCLUDE level_of_care EQUALS "NULL"
OR
EXCLUDE level_of_care EQUALS  "---") AND

(INCLUDE insulin_out_of_pocket EQUALS "Yes"
OR
INCLUDE insulin_out_of_pocket EQUALS "Some people pay out of pocket")


- Sort: ORDER BY insulin_type_order ASC
 Secondry Sort: ORDER BY level_of_care ASC
- Group by insulin_type and level_of_care