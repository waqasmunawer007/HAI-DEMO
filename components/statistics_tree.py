"""
Summary Statistics Tree Component
Main component for rendering the hierarchical facility statistics tree
"""

import streamlit as st


def get_facility_statistics(df):
    """
    DEPRECATED: This function is no longer used.
    Facility statistics are now fetched directly from BigQuery using 
    database.bigquery_client.fetch_facility_statistics()
    
    This function is kept for backwards compatibility but should not be called.
    """
    raise NotImplementedError(
        "This function has been replaced by fetch_facility_statistics() in database.bigquery_client"
    )


def build_tree_data(facility_stats):
    """
    Convert facility statistics to tree node structure

    Args:
        facility_stats (dict): Facility statistics from get_facility_statistics

    Returns:
        dict: Tree configuration with node data
    """
    tree_config = {
        'root': {
            'id': 'total',
            'label': 'Total Facilities Surveyed',
            'value': facility_stats['total']
        },
        'level1': [
            {
                'id': 'public',
                'label': 'Public Facilities',
                'value': facility_stats['categories']['public']['total'],
                'has_children': True
            },
            {
                'id': 'private_pharm',
                'label': 'Private Pharmacies',
                'value': facility_stats['categories']['private_pharmacies']
            },
            {
                'id': 'ngo',
                'label': 'NGO/Faith',
                'value': facility_stats['categories']['ngo_faith']
            },
            {
                'id': 'private_hosp',
                'label': 'Private Hospitals',
                'value': facility_stats['categories']['private_hospitals']
            },
            {
                'id': 'other',
                'label': 'Other',
                'value': facility_stats['categories']['other']
            }
        ],
        'level2': [
            {
                'id': 'primary',
                'label': 'Primary',
                'value': facility_stats['categories']['public']['subcategories']['primary'],
                'parent': 'public'
            },
            {
                'id': 'secondary',
                'label': 'Secondary',
                'value': facility_stats['categories']['public']['subcategories']['secondary'],
                'parent': 'public'
            },
            {
                'id': 'tertiary',
                'label': 'Tertiary',
                'value': facility_stats['categories']['public']['subcategories']['tertiary'],
                'parent': 'public'
            }
        ]
    }

    return tree_config


def render_statistics_tree(facility_stats):
    """
    Main function to render the complete tree component using Streamlit native components

    Args:
        facility_stats (dict): Facility statistics dictionary from fetch_facility_statistics

    Returns:
        None (renders to Streamlit)
    """
    # Validate input
    if not facility_stats:
        import streamlit as st
        st.warning("No facility statistics data available.")
        return

    # Build tree data structure
    tree_data = build_tree_data(facility_stats)

    # Use Streamlit components instead of raw HTML
    import streamlit.components.v1 as components

    # Build HTML as a complete self-contained component
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }}
        .stats-tree-container {{
            width: 100%;
            padding: 20px;
            background: transparent;
        }}
        .tree-node {{
            background: #FFFFFF;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            padding: 16px 20px;
            text-align: center;
            display: inline-block;
            margin: 10px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .tree-node:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        .tree-node-label {{
            font-size: 11px;
            text-transform: uppercase;
            color: #757575;
            font-weight: 600;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
            line-height: 1.3;
        }}
        .tree-node-value {{
            font-size: 28px;
            font-weight: 700;
            color: #1A237E;
            line-height: 1.2;
        }}
        .tree-level {{
            display: flex;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
            margin: 20px 0;
        }}
        .tree-level-0 .tree-node {{
            min-width: 200px;
        }}
        .tree-level-0 .tree-node-label {{
            font-size: 13px;
        }}
        .tree-level-0 .tree-node-value {{
            font-size: 32px;
        }}
        .tree-level-1 {{
            border-top: 2px solid #BDBDBD;
            padding-top: 40px;
        }}
        .tree-level-1 .tree-node {{
            min-width: 140px;
            max-width: 180px;
        }}
        .tree-level-2 {{
            margin-left: auto;
            margin-right: auto;
            max-width: 600px;
            border-top: 2px solid #BDBDBD;
            padding-top: 40px;
        }}
        .tree-level-2 .tree-node {{
            min-width: 120px;
            max-width: 160px;
        }}
        .tree-level-2 .tree-node-label {{
            font-size: 10px;
        }}
        .tree-level-2 .tree-node-value {{
            font-size: 24px;
        }}
        .tree-connector {{
            text-align: center;
            color: #BDBDBD;
            font-size: 24px;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="stats-tree-container">
        <!-- Level 0: Root -->
        <div class="tree-level tree-level-0">
            <div class="tree-node">
                <div class="tree-node-label">{tree_data['root']['label']}</div>
                <div class="tree-node-value">{tree_data['root']['value']:,}</div>
            </div>
        </div>

        <div class="tree-connector">│</div>

        <!-- Level 1: Main Categories -->
        <div class="tree-level tree-level-1">
"""

    # Add level 1 nodes
    for node in tree_data['level1']:
        html_content += f"""
            <div class="tree-node">
                <div class="tree-node-label">{node['label']}</div>
                <div class="tree-node-value">{node['value']:,}</div>
            </div>
"""

    html_content += """
        </div>
"""

    # Add level 2 (public facilities breakdown) if data exists
    if tree_data.get('level2'):
        html_content += """
        <div class="tree-connector">│</div>
        <div style="text-align: center; color: #757575; font-size: 12px; margin: 10px 0;">
            <em>Public Facilities by Level of Care</em>
        </div>

        <!-- Level 2: Public Facilities Breakdown -->
        <div class="tree-level tree-level-2">
"""

        for node in tree_data['level2']:
            html_content += f"""
            <div class="tree-node">
                <div class="tree-node-label">{node['label']}</div>
                <div class="tree-node-value">{node['value']:,}</div>
            </div>
"""

        html_content += """
        </div>
"""

    html_content += """
    </div>
</body>
</html>
"""

    # Render using components.html which properly renders HTML
    components.html(html_content, height=600, scrolling=True)
