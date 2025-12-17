Price Analysis Tab
Plan #07

Create a similar plan to @Price_Analysis_plan6_refined.md refined plan # 07.

**Use Serena MCP:** Define todo items list and solve them one by one according to this detailed plan.
Use Pltory to draw chart.
Use Serena MCP to define todo items list and solve them one by one according to this detailed plan.

Task Overview:
1. Add a new section called  "Where insulin is free" below to Median price - By originator brands and biosimilars section.


2. ADD  two mutliselect dropdowns Region and Sector.
- Expandable dropdown (st.expander) containing checkbox list
3. Add one score card lable and one pie chart in 2 colums
-Score Card Heading is *Facilities providing for free * and inside scorecard the lable should be Facilities(n) and  its value as number.
-Pie chart heading is "Reasons insulin provided for free"  and below a small text guiding : Hover over a slice to see the Reported Products(n) making up the percentage. Pie chart display percentage of occurrence of each reason. display legends in different colors.

4. Add 2nd score card lable and 2nd pie chart in 2 colums below to 1st score card and 1st pie chart.
-Score Card Heading is *Facilities not charging full price * and inside scorecard the lable should be Facilities(n) and  its value as number.
-Pie chart heading is "Reasons for not charging full price  "  and below a small text guiding : Hover over a slice to see the Reported Products(n) making up the percentage. Pie chart display percentage of occurrence of each reason. display legends in different colors.

5. Add a note message after 2nd score card and 2nd pie chart.
Note: 
This inlcudes facilties that report providing insulin for free at least some people, depending on the national policies, for example insurance or donation schemes.

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

3. Facilities providing for free score card:
- Table: adl_surveys_repeat
- Metric: COUNT_DISTINCT(form_case__case_id)
- Filter:INCLUDE insulin_out_of_pocket IN (No, Both)

4.Reasons insulin provided for free pie chart:
- Table: adl_surveys_repeat
- Metric: COUNT_DISTINCT(form_case__case_id)
(Reported products(n) making up the percentage)
- Filter:INCLUDE insulin_out_of_pocket IN (No, Both) AND
EXCLUDE  insulin_free_reason EQUALS  "---" 
- Group by insulin_free_reason
- Sort:ORDER BY COUNT_DISTINCT(form_case__case_id) DESC


5. Facilities not charging full price score card:
- Table: adl_surveys_repeat
- Metric: COUNT_DISTINCT(form_case__case_id)
- Filter:
EXCLUDE  insulin_subsidised_reason  EQUALS  "---"  OR
EXCLUDE  insulin_subsidised_reason  EQUALS  "NULL" 

6.Reasons insulin provided for free pie chart:
- Table: adl_surveys_repeat
- Metric: COUNT_DISTINCT(form_case__case_id)
(Reported products(n) making up the percentage)
- Filter:
EXCLUDE  insulin_subsidised_reason  EQUALS  "---"  OR
EXCLUDE  insulin_subsidised_reason  EQUALS  "NULL" 
- Group by insulin_subsidised_reason
- Sort:ORDER BY COUNT_DISTINCT(form_case__case_id) DESC
