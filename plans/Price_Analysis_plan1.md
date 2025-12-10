
Price Analysis Tab
Build this second tab using a phased approach. This plan covers Phase 1 of the Price Analysis page.
1. Give a titlle to the Price Analysis tab as "Insulin Price Analysis"

2.After heading, need to divide the page into two columns

Column 1: Instructions 
Column 2: Definitions

Column 1: Instructions:
<div style="text-align: left;" align="left"><span style="font-size: 16px;"><b>Instructions: <font color="#d32f2f">To begin select a Data Collection Period (data not shown by default)
</font></b></span></div><div style="text-align: left;" align="left"><span style="font-size: 16px;"><b><font color="#d32f2f"><br></font></b></span></div><div style="text-align: left;" align="left"><span style="font-size: 16px;"><i>Selecting a region:</i> By default, all regions are displayed. You can select more or more regions by using the Region selction box, this will apply for all graphs under the same heading.
</span></div><div style="text-align: left;" align="left"><span style="font-size: 16px;"><br></span></div><div style="text-align: left;" align="left"><span style="font-size: 16px;"><i>Currency</i>: By default, results are displayed in local currency. To select USD, see below.
</span></div><div style="text-align: left;" align="left"><span style="font-size: 16px;">For more see the <a class="b157502361" target="_blank" href="https://accisstoolkit.haiweb.org/user-guide/"><u>User Guide</u></a></span></div>

<div style="text-align: left;" align="left">Optional metrics - many graphs and scorecards have optional metrics, such as the number of facilities or the price in USD. If available the button is shown in the top right corner of the graph. Click on this to choose which metric to show, or show multiple for comparison.<br></div><div style="text-align: left;" align="left"></div>. 
There should be an appropriate small icon for the optional metrics box, left side of this text.

Column 2: Definitions
<div style="text-align: left;" align="left"><font style="font-size: 16px;"><b>Definitions:</b></font></div><div style="text-align: left;" align="left"><i>Insulin Price</i> - Standardised in all cases to 1000IU.</div><div style="text-align: left;" align="left"><br></div><div style="text-align: left;" align="left"><i>Facilities (n) - </i>Number of facilities within a certain category.</div><div style="text-align: left;" align="left"><br></div><div style="text-align: left;" align="left"><i>Reported Responses (%)</i> - Percentage out of all reported responses (products, places, etc.) in a certain category.</div><div style="text-align: left;" align="left"><br></div><div style="text-align: left;" align="left"><i>Reported Responses (n</i>) - Number of responses (products, places, etc.) reported in a certain category.</div><div style="text-align: left;" align="left"><br></div><div style="text-align: left;" align="left"><i>INN</i>: International Nonproprietary Name</div>

3. Add new section called Data Selectors after the instructions and definitions section.

4. there are three dropdwons in the data selectors section: 

-Country Dropdown Filter
-Region Dropdown Filter
-Data Collection Period Dropdown

Filters are multi-selectable similar to the availability analysis page.

5. There is a message "Data is not shown by default. Use the dropdown menu below to select a Data Collecti<span style="background-color: transparent;">on Period and see the data.</span>" Need to display it.

6.Query Configuration:
For Country
- **Table:** `adl_surveys`
- **Group By:** `country`
- **Metric:** `COUNT_DISTINCT(form_case__case_id)`
- **Sort:** `ORDER BY COUNT_DISTINCT(form_case__case_id) DESC`

For Region
- **Table:** `adl_surveys`
- **Group By:** `region`
- **Metric:** `COUNT_DISTINCT(form_case__case_id)`
- **Sort:** `ORDER BY COUNT_DISTINCT(form_case__case_id) DESC`

For Data Collection Period
- **Table:** `adl_surveys`
- **Group By:** `data_collection_period`
- **Metric:** `MIN(survey_date)`
- **Sort:** `ORDER BY data_collection_period DESC`

