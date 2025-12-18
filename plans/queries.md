Table : adl_surveys_repeat
Dimension X-axis
 insulin_type and  insulin_typea and level of care.
Metric Y-axis
CASE
	WHEN MOD(COUNT(insulin_standard_price_local), 2) = 1 THEN MEDIAN(insulin_standard_price_local)
    WHEN MOD(COUNT(insulin_standard_price_local), 2) = 0 AND COUNT(insulin_standard_price_local) >= 100 THEN MEDIAN(insulin_standard_price_local)
    ELSE (PERCENTILE(insulin_standard_price_local, 49) + PERCENTILE(insulin_standard_price_local, 51)) / 2
END

Filters:
1.EXCLUDE insulin_type EQUALS  "---"
2.INCLUDE Sector CONTAINS "Public"
3.EXCLUDE level_of_care EQUALS "NULL"
OR
EXCLUDE level_of_care EQUALS  "---"
4.INCLUDE insulin_out_of_pocket EQUALS "Yes"
OR
INCLUDE insulin_out_of_pocket EQUALS "Some people pay out of pocket"
Sort:ORDER BY insulin_type_order ASC
Secondry Sort:
ORDER BY level_of_care ASC