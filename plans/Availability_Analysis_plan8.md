create a similar plan to @Availability_Analysis_plan7_refined refined plan # 08.

For Barchart, use plotly.
To solve this plan use Serena MCP.


Here is a Task Overview:
Creata new section called Insulin availability - By INN , a subheading of Insulin availability section.
-Add two dropdowns: Region and Sector (multi-select with checkboxes and excluded item count). Give them name Region and Sector.
-Add One Bar Chart  with heading Facilities with Availability (%) 
-- Bar y-axis should be in percentage.name is Facilities with Availability(%)
-- Bar x-axis should represent different insulines.
-- Each bar shaded area should be in percentage, show percentage value as lable and on hover on the bar.
-- X-axis title is Insulines.


#Query configuration:
1.For Region dropdown:
- Table: adl_surveys
- Metric: COUNT_DISTINCT(form_case__case_id)
-Filter: EXCLUDE region EQUALS "NULL"
- Sort: ORDER BY region DESC

1.For Sector dropdown:
- Table: adl_surveys
- Metric: COUNT_DISTINCT(form_case__case_id)
-Filter: EXCLUDE sector EQUALS "NULL"
- Sort: ORDER BY sector DESC

2. For Insulin bar chat
- Table: adl_repeat_repivot
- Metric: 
COUNT_DISTINCT(Available Facilities)/COUNT_DISTINCT(form_case__case_id)
Where "Available Facilities" equal:
CASE WHEN is_unavailable = 0 THEN form_case__case_id END

- Sort: ORDER BY "Facilities with Available(%) " DESC
WHERE  "Facilities with Available(%) " EQUAL  COUNT_DISTINCT(Available Facilities)/COUNT_DISTINCT(form_case__case_id)
WHERE "Available Facilities" EQUAL:
CASE WHEN is_unavailable = 0 THEN form_case__case_id END

-GROUP BY insulin_inn

-Filter:INCLUDE "Facilities with Availability (%)" GREATER THAN 0
 Where "Facilities with Availability (%)" equal:
COUNT_DISTINCT(Available Facilities)/COUNT_DISTINCT(form_case__case_id) 
Where "Available Facilities" equal:
CASE WHEN is_unavailable = 0 THEN form_case__case_id END


