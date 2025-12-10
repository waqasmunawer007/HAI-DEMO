create a similar plan to @Availability_Analysis_plan5_refined refined plan # 06.

For Barchart, use plotly.
To solve this plan use Serena MCP.


Here is a Task Overview:
Creata new section called Insulin availability - By region, a subheading of Insulin availability section.
-Add single dropdowns: Sector (multi-select with checkboxes and excluded item count). Give a name sector to this dropdown
-Add two Bar Charts  with heading Human and Analogue and their titles are same and that is  Facilities with Availability (%) 
-- Bar y-axis should be in percentage.name is Facilities with Availability(%)
-- Bar x-axis should represent different Regions with their name . for example Public sector: Arequipa, Ayacucho etc.
-- Each bar shaded area should be in percentage, show percentage value as lable and on hover on the bar.



#Query configuration:
1.For Sector dropdown:
- Table: adl_surveys
- Metric: COUNT_DISTINCT(form_case__case_id)
- Sort: ORDER BY sector DESC


2. For Human bar chat
- Table: adl_repeat_repivot
- Metric: 
COUNT_DISTINCT(Available Facilities)/COUNT_DISTINCT(form_case__case_id)
Where "Available Facilities" equal:
CASE WHEN is_unavailable = 0 THEN form_case__case_id END
- Sort: ORDER BY region ASC
-GROUP BY region
-Filter: INCLUDE insulin_type CONTAINS "Human"

3. For Analogue bar chat
- Table: adl_repeat_repivot
- Metric:
COUNT_DISTINCT(Available Facilities)/COUNT_DISTINCT(form_case__case_id)
Where "Available Facilities" equal:
CASE WHEN is_unavailable = 0 THEN form_case__case_id END
- Sort: ORDER BY region ASC
-GROUP BY region
-Filter: INCLUDE insulin_type CONTAINS "Analogue"
