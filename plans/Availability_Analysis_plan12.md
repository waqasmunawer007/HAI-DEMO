create a similar plan to @Availability_Analysis_plan11_refined refined plan # 12.

To solve this plan use Serena MCP.


Here is a Task Overview:
Creata new section called Insulin availability -Availability of comparator medicine a subheading of Insulin availability section.
**Location:** Add after "Insulin availability - By originator brands VS biosimilars" component in app.py 

-Add two dropdowns: Region and Sector (multi-select with checkboxes and excluded item count). Give them name Region and Sector.

-Add a table with three columns
1. Name
2. Strength(mg)
3. Facilities with Availability (%)
-Add pagination to the table.10 rows per page.
-Add sorting to the table bsased on name column.

#Query configuration:
1.For Region dropdown:
- Table: adl_surveys
- Metric: COUNT_DISTINCT(form_case__case_id)
-Filter: EXCLUDE region EQUALS "NULL"
- Sort: ORDER BY region DESC

1.For Sector dropdown:
- Table: adl_surveys
- Metric: COUNT_DISTINCT(form_case__case_id)
- Sort: ORDER BY sector DESC

2. For Table showing Facilities with Availability (%) 

- Table: adl_comparators
- Metric: 
sum(available_num)/COUNT_DISTINCT(survey_id) x 100 

-Filter:INCLUDE "insulin_originator_biosimilar" EQUALS "Originator Brand" AND  INCLUDE insulin_type CONTAINS "Human"

-Sort: ORDER BY name DESC
-Group by name, strength
