create a similar plan to @Availability_Analysis_plan6_refined refined plan # 07.

For Barchart, use plotly.
To solve this plan use Serena MCP.


Here is a Task Overview:
Creata new section called Insulin availability - Public sector - By level of care , a subheading of Insulin availability section.
-Add single dropdowns: Region (multi-select with checkboxes and excluded item count). Give a name Region to this dropdown
-Add two Bar Charts  with heading Human and Analogue and their titles are same and that is  Facilities with Availability (%) 
-- Bar y-axis should be in percentage.name is Facilities with Availability(%)
-- Bar x-axis should represent different Level of Care(Primary, Seconday and Tertiary) 
-- Each bar shaded area should be in percentage, show percentage value as lable and on hover on the bar.
-- X-axis title is Level of Care.



#Query configuration:
1.For Region dropdown:
- Table: adl_surveys
- Metric: COUNT_DISTINCT(form_case__case_id)
-Filter: EXCLUDE region EQUALS "NULL"
- Sort: ORDER BY region DESC


2. For Human bar chat
- Table: adl_repeat_repivot
- Metric: 
COUNT_DISTINCT(Available Facilities)/COUNT_DISTINCT(form_case__case_id)
Where "Available Facilities" equal:
CASE WHEN is_unavailable = 0 THEN form_case__case_id END
- Sort: ORDER BY level_of_care ASC
-GROUP BY level_of_care
-Filter:INCLUDE sector CONTAINS "Public"
AND
INCLUDE insulin_type CONTAINS "Human"
AND
((EXCLUDE level_of_care EQUALS "NULL") AND EXCLUDE 
level_of_care EQUALS "---") )

3. For Analogue bar chat
- Table: adl_repeat_repivot
- Metric: 
COUNT_DISTINCT(Available Facilities)/COUNT_DISTINCT(form_case__case_id)
Where "Available Facilities" equal:
CASE WHEN is_unavailable = 0 THEN form_case__case_id END
- Sort: ORDER BY level_of_care ASC
-GROUP BY level_of_care
-Filter:INCLUDE sector CONTAINS "Public"
AND
INCLUDE insulin_type CONTAINS "Analogue"
AND
((EXCLUDE level_of_care EQUALS "NULL") AND EXCLUDE 
level_of_care EQUALS "---") )
