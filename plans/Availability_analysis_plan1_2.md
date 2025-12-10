# Dashboard UI Revamp - Availability Analysis Header Content Implementation

## Content Structure and Layout

### Main Page Heading
**Title:** Insulin Availability Analysis

**Styling:**
- Large, bold header font
- Primary color scheme
- Positioned at top of page content area

---

## Two-Column Layout Section
(Position: Below main heading, above Data Selectors)

### Column 1: Instructions and Optional Metrics

#### Instructions Section

**Heading:** Instructions:

**Content:**

**Primary Alert (Red text):**
```html
<font color="#d32f2f">To begin select a Data Collection Period (data not shown by default)</font>
```

**Selecting a region:**
```html
<div style="text-align: left;" align="left">
  <i>Selecting a region: </i>By default, all regions are displayed. You can select more or more regions by using the Region selection box, this will apply for all graphs under the same heading.
</div>
```

**Currency:**
```html
<div style="text-align: left;" align="left">
  <i>Currency:</i> By default, results are displayed in local currency. To select USD, see below.
</div>
```

**User Guide Link:**
```html
For more see the <a class="b157502361" target="_blank" href="https://accisstoolkit.haiweb.org/user-guide/"><u>User Guide</u></a>
```

---

#### Optional Metrics Info Box

**Layout:** Icon + Text horizontal layout

**Content:**
```html
[icon: chart/graph icon representing metrics] Optional metrics - many graphs and scorecards have optional metrics, such as the number of facilities or the price in USD. If available the button is shown in the top right corner of the graph. Click on this to choose which metric to show, or show multiple for comparison.
```

**Styling Notes:**
- Use appropriate chart/analytics icon on the left
- Icon should be vertically aligned with first line of text
- Light background box with subtle border
- Left accent border (optional)
- Adequate padding around content

**Recommended Icon Options:**
- Bar chart icon
- Line graph icon
- Analytics/dashboard icon
- Settings/options icon with graph

---

### Column 2: Definitions

**Heading:**
```html
<div style="text-align: left;" align="left">
  <font style="font-size: 16px;"><b>Definitions:</b></font>
</div>
```

**Content:**

**Facilities with Availability (%):**
```html
<div style="text-align: left;" align="left">
  <font style="font-size: 14px;">
    <i>Facilities with Availability (%)</i> - Percentage of facilities out of the total in a given data collection period with insulin (or comparator NCD medicine) in stock on the day of data collection.
  </font>
</div>
<div style="text-align: left;" align="left"><font style="font-size: 14px;"><br></font></div>
```

**Facilities with Availability (n):**
```html
<div style="text-align: left;" align="left">
  <font style="font-size: 14px;">
    <i>Facilities with Availability (n)</i> - Number of facilities in a given data collection period with insulin (or comparator NCD medicine) in stock on the day of data collection.
  </font>
</div>
<div style="text-align: left;" align="left"><font style="font-size: 14px;"><br></font></div>
```

**INN Definition:**
```html
<div style="text-align: left;" align="left">
  <font style="font-size: 14px;">
    <i>INN</i>: International Nonproprietary Name
  </font>
</div>
<div style="text-align: left;" align="left"><font style="font-size: 14px;"><br></font></div>
```

**Note:**
```html
<div style="text-align: left;" align="left">
  <font style="font-size: 14px;">
    Note: data on all pages of the dashboard relate to the supply of outpatients (not inpatients)
  </font>
</div>
```

---

## Layout Specifications

### Column Configuration
- **Layout Type:** Two-column grid
- **Column 1 (Instructions):** 50-55% width
- **Column 2 (Definitions):** 45-50% width
- **Gap between columns:** 20-30px
- **Responsive behavior:** Stack vertically on mobile/tablet

### Spacing and Padding
- **Top margin from main heading:** 24px
- **Bottom margin to Data Selectors:** 32px
- **Internal padding within columns:** 16px
- **Space between instruction items:** 16px
- **Space between definition items:** 12px

### Typography
- **Main heading (Insulin Availability Analysis):** 28-32px, bold
- **Section headings (Instructions, Definitions):** 16-18px, bold
- **Body text:** 14px, regular
- **Italic labels:** 14px, italic
- **Red alert text:** 14px, color: #d32f2f

### Color Scheme
- **Alert text:** #d32f2f (red)
- **Headings:** Primary dark color (#1a237e or similar)
- **Body text:** Dark gray (#424242)
- **Links:** Primary blue with underline
- **Background (Optional metrics box):** Light gray (#f5f5f5)

### Border and Box Styling
- **Optional metrics box:**
  - Background: #f5f5f5 or #e3f2fd
  - Border: 1px solid #e0e0e0
  - Border-radius: 4px
  - Padding: 16px
  - Optional left accent: 4px solid primary color

---

## Implementation Structure

### HTML Structure Template
```html
<!-- Main Heading -->
<h1>Insulin Availability Analysis</h1>

<!-- Two Column Layout Container -->
<div class="content-header-section">
  
  <!-- Column 1: Instructions -->
  <div class="column-instructions">
    <h3>Instructions:</h3>
    
    <!-- Alert Message -->
    <p class="alert-text">To begin select a Data Collection Period (data not shown by default)</p>
    
    <!-- Instruction Items -->
    <p><em>Selecting a region:</em> By default, all regions are displayed...</p>
    <p><em>Currency:</em> By default, results are displayed in local currency...</p>
    <p>For more see the <a href="https://accisstoolkit.haiweb.org/user-guide/" target="_blank">User Guide</a></p>
    
    <!-- Optional Metrics Box -->
    <div class="info-box">
      <span class="icon">[chart icon]</span>
      <span class="text">Optional metrics - many graphs and scorecards...</span>
    </div>
  </div>
  
  <!-- Column 2: Definitions -->
  <div class="column-definitions">
    <h3>Definitions:</h3>
    
    <p><em>Facilities with Availability (%):</em> - Percentage of facilities...</p>
    <p><em>Facilities with Availability (n):</em> - Number of facilities...</p>
    <p><em>INN:</em> International Nonproprietary Name</p>
    <p class="note">Note: data on all pages of the dashboard relate to the supply of outpatients (not inpatients)</p>
  </div>
  
</div>

<!-- Data Selectors Section Begins Below -->
<h2>Data Selectors</h2>
```

---

## Implementation Checklist

### Content Elements
- [ ] Main page heading: "Insulin Availability Analysis"
- [ ] Instructions section with heading
- [ ] Red alert text for data collection period
- [ ] Selecting a region instructions (italic label)
- [ ] Currency instructions (italic label)
- [ ] User Guide hyperlink (opens in new tab)
- [ ] Optional metrics info box with icon
- [ ] Definitions section with heading
- [ ] Facilities with Availability (%) definition
- [ ] Facilities with Availability (n) definition
- [ ] INN definition
- [ ] Note about outpatient data

### Styling and Layout
- [ ] Two-column grid layout implemented
- [ ] Proper column width distribution (50/50 or 55/45)
- [ ] Responsive stacking for mobile devices
- [ ] Red color (#d32f2f) applied to alert text
- [ ] Italic formatting on instruction labels
- [ ] Font sizes: 16px headings, 14px body text
- [ ] Proper spacing between sections
- [ ] Info box background and border styling
- [ ] Icon integrated in optional metrics box

### Functionality
- [ ] User Guide link opens in new tab
- [ ] User Guide URL correct: https://accisstoolkit.haiweb.org/user-guide/
- [ ] All text properly formatted and readable
- [ ] Responsive layout tested on multiple screen sizes

### Positioning
- [ ] Content positioned above "Data Selectors" heading
- [ ] Content positioned below main page title
- [ ] Proper vertical spacing maintained
- [ ] Alignment consistent across columns

---

## Visual Layout Reference
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│              Insulin Availability Analysis                       │
│                                                                  │
├──────────────────────────────┬──────────────────────────────────┤
│ Instructions:                │ Definitions:                     │
│                              │                                  │
│ [RED] To begin select a Data │ Facilities with Availability (%) │
│ Collection Period...         │ - Percentage of facilities...    │
│                              │                                  │
│ Selecting a region: By       │ Facilities with Availability (n) │
│ default, all regions...      │ - Number of facilities...        │
│                              │                                  │
│ Currency: By default...      │ INN: International...            │
│                              │                                  │
│ For more see the User Guide  │ Note: data on all pages...       │
│                              │                                  │
│ ┌────────────────────────┐   │                                  │
│ │[📊] Optional metrics - │   │                                  │
│ │many graphs and score-  │   │                                  │
│ │cards have optional...  │   │                                  │
│ └────────────────────────┘   │                                  │
└──────────────────────────────┴──────────────────────────────────┘
│                                                                  │
│ Data Selectors                                                   │
│ (continues below...)                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Notes for Developers

1. **Icon Selection:** Choose an icon that clearly represents analytics/metrics functionality. Material Design Icons or Font Awesome provide suitable options.

2. **Accessibility:** Ensure all text has sufficient contrast ratios. The red alert text (#d32f2f on white) meets WCAG AA standards.

3. **Link Behavior:** The User Guide link should open in a new tab (target="_blank") and include rel="noopener noreferrer" for security.

4. **HTML Cleanup:** The provided HTML includes inline styles. Consider extracting these to CSS classes for better maintainability.

5. **Responsive Breakpoint:** Recommended breakpoint for column stacking: 768px (tablet width).

6. **Content Updates:** All text content should be stored in a way that allows easy updates without code changes (consider CMS or config file).