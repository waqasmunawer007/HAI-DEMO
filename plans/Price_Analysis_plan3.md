Price Analysis Tab
Plan #03

Create a similar plan to @Price_Analysis_Phase2_Refined.md refined plan # 03.

**Use Serena MCP:** Define todo items list and solve them one by one according to this detailed plan.
Use Pltory to draw chart.

Task Overview:
1. Add a new section called Price - By INN below to Median price - By insulin type and level of care (public sector only) clustered bar chart.
2. ADD  two mutliselect dropdowns Region and Sector.
- Expandable dropdown (st.expander) containing checkbox list
3. Add a line chart called "Price - By INN"
- Y-axis range from 0 to 5k
- x- axis contains 5 main categories
  1. Regular
  2. NPH
  3. Pre-mixed regular/NPH
  4. Glargine
  5. Detemir 

 -  Legend - Add three legend called "Min Price-Local", "Median Price-Local" and "Max Price-Local" 

 4. Add a message below to line chart "<div style="text-align: left;" align="left">NOTE: label shown for median price only. Hover over points on the chart to see all values.
</div><div style="text-align: left;" align="left"></div>"

#Query Configurations:
For Line chart
-Table name: adl_surveys_repeat
-Metrics: Min(insulin_standard_price_local)
max(insulin_standard_price_local),
insulin_standard_price_local_median
-Group by insulin_inn
-Filters: EXCLUDE insulin_inn EQUALS  "---"
AND INCLUDE insulin_out_of_pocket EQUALS "Yes"
OR
INCLUDE insulin_out_of_pocket EQUALS "Some people pay out of pocket"
-sort: ORDER BY insulin_inn ASC