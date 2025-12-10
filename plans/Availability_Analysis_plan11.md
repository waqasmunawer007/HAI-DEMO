create a similar plan to @Availability_Analysis_plan7_refined refined plan # 11.

To solve this plan use Serena MCP.


Here is a Task Overview:
Creata new section called Insulin availability - By originator brands VS biosimilars , a subheading of Insulin availability section.
**Location:** Add after "Insulin availability - By presentation and insulin type" component in app.py 

-Add two dropdowns: Region and Sector (multi-select with checkboxes and excluded item count). Give them name Region and Sector.

-Add two columns side by side. 
1.First column should have   Insulin type - Human.
2.Second column should have   Insulin type - Analogue.
3-Each column should have  one score card with lable Facilities with Originator Brands (%) and display value with percentage below it.
4-Each column should have  2nd score card with lable Facilities with Biosimilars (%) and display value with percentage below it.
-Both score cards should have be in two rowa, one above the other.

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

2. Insulin Type Human- Facilities with
 Originator Brands (%)

- Table: adl_repeat_repivot
- Metric: 
COUNT_DISTINCT(Available Facilities)/COUNT_DISTINCT(form_case__case_id)
Where "Available Facilities" equal:
CASE WHEN is_unavailable = 0 THEN form_case__case_id END

-Filter:INCLUDE "insulin_originator_biosimilar" EQUALS "Originator Brand" AND  INCLUDE insulin_type CONTAINS "Human"


3. Insulin Type Analogue- Facilities with
 Originator Brands (%)

- Table: adl_repeat_repivot
- Metric: 
COUNT_DISTINCT(Available Facilities)/COUNT_DISTINCT(form_case__case_id)
Where "Available Facilities" equal:
CASE WHEN is_unavailable = 0 THEN form_case__case_id END

-Filter:INCLUDE "insulin_originator_biosimilar" EQUALS "Originator Brand" AND  INCLUDE insulin_type CONTAINS "Analogue"

4.Insulin Type Human- Facilities with Biosimilars (%)

- Table: adl_repeat_repivot
- Metric: 
COUNT_DISTINCT(Available Facilities)/COUNT_DISTINCT(form_case__case_id)
Where "Available Facilities" equal:
CASE WHEN is_unavailable = 0 THEN form_case__case_id END

-Filter:INCLUDE "insulin_originator_biosimilar" EQUALS "Biosimilar" AND INCLUDE insulin_type CONTAINS "Human"

5.Insulin Type Analogue- Facilities with Biosimilars (%)

- Table: adl_repeat_repivot
- Metric: 
COUNT_DISTINCT(Available Facilities)/COUNT_DISTINCT(form_case__case_id)
Where "Available Facilities" equal:
CASE WHEN is_unavailable = 0 THEN form_case__case_id END

-Filter:INCLUDE "insulin_originator_biosimilar" EQUALS "Biosimilar" AND INCLUDE insulin_type CONTAINS "Analogue"