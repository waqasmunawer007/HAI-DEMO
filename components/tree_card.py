"""
Tree Card Component
Generates HTML for individual facility statistic cards in the tree visualization
"""

def create_facility_card(label, value, card_id, level=0):
    """
    Generate HTML for a single facility statistic card

    Args:
        label (str): Category name (e.g., "Public Facilities")
        value (int): Facility count
        card_id (str): Unique identifier for positioning
        level (int): Tree level (0=root, 1=level1, 2=level2) for styling

    Returns:
        str: HTML string for the card
    """
    # Adjust font sizes based on level
    if level == 0:
        label_size = "13px"
        value_size = "32px"
        min_width = "200px"
        max_width = "220px"
    elif level == 1:
        label_size = "11px"
        value_size = "28px"
        min_width = "140px"
        max_width = "180px"
    else:  # level 2
        label_size = "10px"
        value_size = "24px"
        min_width = "120px"
        max_width = "160px"

    card_html = f"""
    <div class="facility-card" id="{card_id}" data-level="{level}">
        <div class="facility-card-label" style="font-size: {label_size};">{label}</div>
        <div class="facility-card-value" style="font-size: {value_size};">{value}</div>
    </div>
    """

    return card_html


def get_card_styles():
    """
    Returns CSS styles for facility cards

    Returns:
        str: CSS styling rules
    """
    return """
    <style>
    .facility-card {
        background: #FFFFFF;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        padding: 16px 20px;
        text-align: center;
        display: inline-block;
        position: relative;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .facility-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .facility-card[data-level="0"] {
        min-width: 200px;
        max-width: 220px;
    }

    .facility-card[data-level="1"] {
        min-width: 140px;
        max-width: 180px;
    }

    .facility-card[data-level="2"] {
        min-width: 120px;
        max-width: 160px;
    }

    .facility-card-label {
        text-transform: uppercase;
        color: #757575;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
        line-height: 1.3;
    }

    .facility-card-value {
        font-weight: 700;
        color: #1A237E;
        line-height: 1.2;
    }

    /* Tree container styles */
    .tree-container {
        width: 100%;
        overflow-x: auto;
        overflow-y: visible;
        padding: 30px 20px;
        min-width: 900px;
        position: relative;
    }

    .tree-level {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 50px;
        margin-bottom: 100px;
        position: relative;
    }

    .tree-level[data-level="0"] {
        margin-bottom: 100px;
    }

    .tree-level[data-level="1"] {
        margin-bottom: 100px;
    }

    .tree-level[data-level="2"] {
        margin-bottom: 20px;
    }

    /* Connector line styles */
    .connector-svg {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
    }

    .connector-line {
        stroke: #BDBDBD;
        stroke-width: 2;
        fill: none;
    }

    /* Responsive adjustments */
    @media (max-width: 1200px) {
        .tree-level {
            gap: 30px;
        }
    }

    @media (max-width: 768px) {
        .facility-card {
            padding: 12px 16px;
        }

        .tree-level {
            gap: 20px;
        }
    }
    </style>
    """
