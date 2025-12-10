```markdown
# Dashboard UI Revamp - Plan 2: Summary Statistics Tree Component

## Task Overview
Create a hierarchical "Summary Statistics Tree" dashboard component that visually resembles an organization chart, positioned below the Selected Data Collection Period Summary Table.

**Current Phase:** UI Design and Structure
**Next Phase:** Logic implementation and data integration

**Serena MCP:** Use Serena MCP to implement this component, define todo items list and solve them one by one according to the given details plan.
---

## Component Specifications

### Position and Context
- **Location:** Directly below the "Selected Data Collection Period Summary Table"
- **Component Type:** Interactive hierarchical tree visualization
- **Alternative Names:** Summary Statistics Tree, Facility Organization Chart, Hierarchical Facility Overview

---

## Tree Structure Definition

### Hierarchy Levels

**Root Node (Level 0):**
```
Total Facilities Surveyed (0)
```

**Level 1 Children (5 nodes):**
```
├── Public Facilities (0)
├── Private Pharmacies (0)
├── NGO/Faith (0)
├── Private Hospitals (0)
└── Other (0)
```

**Level 2 Children (Under Public Facilities only - 3 nodes):**
```
Public Facilities (0)
    ├── Primary (0)
    ├── Secondary (0)
    └── Tertiary (0)
```

### Complete Tree Structure
```
                    Total Facilities Surveyed (0)
                                |
        ┌───────────────┬───────┴───────┬───────────────┬───────────────┐
        │               │               │               │               │
  Public Facilities  Private      NGO/Faith      Private         Other
       (0)         Pharmacies        (0)        Hospitals         (0)
                      (0)                          (0)
        │
    ┌───┴───┬────────┐
    │       │        │
 Primary Secondary Tertiary
   (0)      (0)      (0)
```

---

## Visual Design Requirements

### Card Style Specifications

**Card Container:**
- Background: White (#FFFFFF)
- Border: None or 1px solid #E0E0E0
- Border-radius: 8px
- Box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1)
- Padding: 16px 20px
- Min-width: 140px
- Max-width: 180px
- Text-align: center

**Label Text (Category Name):**
- Font-size: 11px or 12px
- Text-transform: uppercase
- Color: #757575 or #9E9E9E (gray)
- Font-weight: 500 or 600
- Letter-spacing: 0.5px
- Margin-bottom: 4px

**Value Text (Count):**
- Font-size: 24px or 28px
- Font-weight: bold (700)
- Color: #1A237E or #263238 (dark blue/black)
- Line-height: 1.2

### Connector Line Specifications

**Line Style:**
- Color: #BDBDBD or #E0E0E0 (light gray)
- Width: 2px
- Type: Solid lines
- Style: Orthogonal (right angles, not diagonal)

**Line Drawing Pattern:**
- Vertical line from parent to horizontal distribution line
- Horizontal line connecting all children at same level
- Vertical lines dropping from horizontal line to each child card

**Connection Points:**
- Lines connect to center-top of child cards
- Lines connect from center-bottom of parent cards

---

## Technical Implementation Strategy

### Technology Stack Options

**Option 1: Plotly (Recommended)**
```python
import plotly.graph_objects as go
# Use plotly.graph_objects to create custom shapes and annotations
# Benefits: Interactive, built-in Streamlit support, easier line drawing
```

**Option 2: HTML/CSS via st.markdown()**
```python
import streamlit as st
# Generate HTML with CSS for layout and SVG for connector lines
# Benefits: Full control over styling, lighter weight
```

**Option 3: Hybrid Approach**
```python
# Use HTML/CSS for cards, SVG overlays for connector lines
# Benefits: Best of both worlds
```

**Recommended Approach:** Use **Plotly** for easier connector line implementation and built-in interactivity, OR use **HTML/CSS with SVG** for maximum control and lighter rendering.

---

## Implementation Components

### Component 1: Card Generator Function
```python
def create_facility_card(label, value, card_id):
    """
    Generate HTML for a single facility statistic card
    
    Args:
        label (str): Category name (e.g., "Public Facilities")
        value (int): Facility count
        card_id (str): Unique identifier for positioning
    
    Returns:
        str: HTML string for the card
    """
    pass
```

### Component 2: Tree Layout Calculator
```python
def calculate_tree_layout(tree_data):
    """
    Calculate x,y positions for each node in the tree
    
    Args:
        tree_data (dict): Hierarchical data structure
    
    Returns:
        dict: Node positions {node_id: (x, y)}
    """
    pass
```

### Component 3: Connector Line Generator
```python
def generate_connector_lines(parent_pos, children_positions):
    """
    Generate SVG path or Plotly shapes for connector lines
    
    Args:
        parent_pos (tuple): (x, y) position of parent node
        children_positions (list): List of (x, y) positions for children
    
    Returns:
        str/object: SVG path string or Plotly shapes
    """
    pass
```

### Component 4: Tree Renderer
```python
def render_statistics_tree(facility_data):
    """
    Main function to render the complete tree component
    
    Args:
        facility_data (dict): Facility statistics by category
    
    Returns:
        None (renders to Streamlit)
    """
    pass
```

---

## Layout and Positioning Logic

### Horizontal Spacing
- **Level 0 (Root):** Centered horizontally
- **Level 1 (5 nodes):** Evenly distributed across width
  - Spacing between cards: 40-60px
  - Total width calculation: `(card_width × 5) + (spacing × 4)`
- **Level 2 (3 nodes under Public):** Positioned under Public Facilities card
  - Spacing between cards: 30-40px
  - Aligned to center of parent card

### Vertical Spacing
- **Level 0 to Level 1:** 80-100px vertical gap
- **Level 1 to Level 2:** 80-100px vertical gap
- **Line segments:** 
  - Vertical from parent: 40-50px
  - Horizontal distribution line: At midpoint between levels
  - Vertical to children: 40-50px

### Container Specifications
- **Min-width:** 900px (to accommodate 5 cards + spacing)
- **Overflow-x:** auto (horizontal scroll on small screens)
- **Overflow-y:** visible
- **Padding:** 20px
- **Background:** Transparent or light gray (#F5F5F5)

---

## Responsive Design Requirements

### Desktop (>1200px)
- Display full tree without scrolling
- All cards visible simultaneously
- Optimal spacing between elements

### Tablet (768px - 1200px)
- Enable horizontal scrolling
- Maintain card sizes
- Preserve connector line relationships

### Mobile (<768px)
- Horizontal scroll required
- Consider reducing card padding slightly
- Maintain minimum card width for readability
- Keep connector lines visible during scroll

---

## Data Structure for Tree

### Input Data Format
```python
facility_stats = {
    "total": 0,
    "categories": {
        "public": {
            "total": 0,
            "subcategories": {
                "primary": 0,
                "secondary": 0,
                "tertiary": 0
            }
        },
        "private_pharmacies": 0,
        "ngo_faith": 0,
        "private_hospitals": 0,
        "other": 0
    }
}
```

### Node Configuration
```python
tree_config = {
    "root": {
        "id": "total",
        "label": "Total Facilities Surveyed",
        "value": 0,
        "level": 0
    },
    "level1": [
        {"id": "public", "label": "Public Facilities", "value": 0, "has_children": True},
        {"id": "private_pharm", "label": "Private Pharmacies", "value": 0},
        {"id": "ngo", "label": "NGO/Faith", "value": 0},
        {"id": "private_hosp", "label": "Private Hospitals", "value": 0},
        {"id": "other", "label": "Other", "value": 0}
    ],
    "level2": [
        {"id": "primary", "label": "Primary", "value": 0, "parent": "public"},
        {"id": "secondary", "label": "Secondary", "value": 0, "parent": "public"},
        {"id": "tertiary", "label": "Tertiary", "value": 0, "parent": "public"}
    ]
}
```

---

## CSS Styling Template

### Card Styles
```css
.facility-card {
    background: #FFFFFF;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 16px 20px;
    min-width: 140px;
    max-width: 180px;
    text-align: center;
    display: inline-block;
    position: relative;
}

.facility-card-label {
    font-size: 11px;
    text-transform: uppercase;
    color: #757575;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.facility-card-value {
    font-size: 28px;
    font-weight: 700;
    color: #1A237E;
    line-height: 1.2;
}
```

### Container Styles
```css
.tree-container {
    width: 100%;
    overflow-x: auto;
    overflow-y: visible;
    padding: 20px;
    min-width: 900px;
}

.tree-level {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 50px;
    margin-bottom: 80px;
    position: relative;
}
```

### Connector Line Styles (SVG)
```css
.connector-line {
    stroke: #BDBDBD;
    stroke-width: 2;
    fill: none;
}
```

---

## Implementation Approach Decision Matrix

| Approach | Pros | Cons | Recommended For |
|----------|------|------|-----------------|
| **Plotly** | Built-in shapes, interactive, easy positioning | Larger file size, limited styling control | Quick implementation, need interactivity |
| **HTML/CSS + SVG** | Full control, lightweight, precise styling | More complex code, manual positioning | Production-ready, custom styling needs |
| **Third-party Library** | Pre-built functionality | External dependency, learning curve | Rapid prototyping |

**Recommended:** HTML/CSS + SVG for maximum control and performance

---

## Component Structure Outline

### File Organization
```
├── components/
│   ├── statistics_tree.py          # Main tree component
│   ├── tree_card.py                # Individual card component
│   ├── tree_connectors.py          # Line drawing utilities
│   └── tree_layout.py              # Position calculation logic
└── styles/
    └── tree_styles.css             # CSS styling definitions
```

### Function Hierarchy
```
render_statistics_tree()
├── calculate_tree_layout()
├── generate_tree_html()
│   ├── create_facility_card() [multiple calls]
│   └── generate_connector_lines()
└── st.markdown() or plotly.graph_objects.Figure()
```

---

## Design Phase Deliverables

### Phase 2 Deliverables (Current)
- [ ] Complete component structure definition
- [ ] Visual design specifications documented
- [ ] CSS/styling rules defined
- [ ] Tree layout logic outlined
- [ ] Data structure format defined
- [ ] Technology stack decision made
- [ ] Responsive design requirements specified
- [ ] SVG connector line pattern defined

### Phase 3 Deliverables (Next)
- [ ] Implement tree layout calculation algorithm
- [ ] Build card generation function
- [ ] Create connector line drawing logic
- [ ] Integrate with database queries
- [ ] Add data population logic
- [ ] Implement responsive behavior
- [ ] Add loading states
- [ ] Test with various data scenarios

---

## Technical Notes

### Streamlit Considerations
1. **Component must work without external dependencies** (beyond plotly if chosen)
2. **Use st.markdown(unsafe_allow_html=True)** for HTML/CSS rendering
3. **Avoid using st.components.v1** unless absolutely necessary
4. **Ensure component renders properly on Streamlit Cloud**

### Browser Compatibility
- Target modern browsers (Chrome, Firefox, Safari, Edge)
- Ensure SVG rendering works consistently
- Test horizontal scroll on mobile devices

### Performance Considerations
- Minimize DOM elements
- Use CSS transforms for positioning where possible
- Lazy load or virtualize if tree becomes very large (future consideration)

---

## Visual Reference ASCII

```
                          ┌─────────────────────────┐
                          │  TOTAL FACILITIES       │
                          │     SURVEYED            │
                          │         0               │
                          └───────────┬─────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
    ┌─────────┴─────────┐   ┌────────┴────────┐   ┌─────────┴─────────┐
    │  PUBLIC           │   │  PRIVATE        │   │  NGO/FAITH        │
    │  FACILITIES       │   │  PHARMACIES     │   │                   │
    │       0           │   │       0         │   │       0           │
    └─────────┬─────────┘   └─────────────────┘   └───────────────────┘
              │
      ┌───────┼───────┐
      │       │       │
┌─────┴─┐ ┌──┴──┐ ┌──┴────┐
│PRIMARY│ │SECOND│ │TERTIARY│
│   0   │ │ARY  │ │   0    │
│       │ │  0   │ │        │
└───────┘ └──────┘ └────────┘

         ┌─────────────────┐   ┌─────────────────┐
         │  PRIVATE        │   │  OTHER          │
         │  HOSPITALS      │   │                 │
         │       0         │   │       0         │
         └─────────────────┘   └─────────────────┘
```

---

## Success Criteria for Phase 2

1. **Visual Accuracy:** Component matches the organization chart aesthetic
2. **Responsive:** Works on screens from 320px to 2560px width
3. **Clean Code:** Modular, reusable functions
4. **Styling:** Professional appearance with proper shadows, spacing, colors
5. **Connector Lines:** Orthogonal lines properly connecting all nodes
6. **Flexibility:** Easy to modify node count or hierarchy in future

---

## Next Steps After Phase 2 Completion

1. Review and approve UI design
2. Proceed to Phase 3: Logic Implementation
3. Define database queries for each node
4. Implement data fetching and aggregation
5. Add dynamic value updates based on filter selections
6. Implement loading states and error handling
7. Add interactivity (click to filter, hover tooltips, etc.)
```