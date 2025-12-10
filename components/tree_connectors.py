"""
Tree Connectors Generator
Generates SVG connector lines between parent and child nodes
"""

def generate_connector_lines(parent_pos, children_positions):
    """
    Generate SVG path for connector lines

    Args:
        parent_pos (dict): Parent node position {'x': x, 'y': y}
        children_positions (list): List of child positions

    Returns:
        str: SVG path string
    """
    if not children_positions or not parent_pos:
        return ""

    from components.tree_layout import get_connector_coordinates

    lines = get_connector_coordinates(parent_pos, children_positions)
    svg_paths = []

    for line in lines:
        path = f'<line x1="{line["x1"]}" y1="{line["y1"]}" x2="{line["x2"]}" y2="{line["y2"]}" class="connector-line" />'
        svg_paths.append(path)

    return '\n'.join(svg_paths)


def generate_all_connectors(positions):
    """
    Generate all connector lines for the entire tree

    Args:
        positions (dict): All node positions from calculate_tree_layout

    Returns:
        str: Complete SVG markup with all connector lines
    """
    all_lines = []

    # Get all nodes by level
    level0_nodes = {k: v for k, v in positions.items() if v['level'] == 0}
    level1_nodes = {k: v for k, v in positions.items() if v['level'] == 1}
    level2_nodes = {k: v for k, v in positions.items() if v['level'] == 2}

    # Connect root to level 1
    if level0_nodes and level1_nodes:
        root_id = list(level0_nodes.keys())[0]
        root_pos = level0_nodes[root_id]
        children = list(level1_nodes.values())

        lines = generate_connector_lines(root_pos, children)
        all_lines.append(lines)

    # Connect public facilities to its children (level 2)
    if level2_nodes:
        # Find public facilities node
        public_node = None
        for node_id, node_data in level1_nodes.items():
            if node_data.get('has_children', False):
                public_node = node_data
                break

        if public_node:
            # Get all level 2 children
            children = list(level2_nodes.values())
            lines = generate_connector_lines(public_node, children)
            all_lines.append(lines)

    return '\n'.join(all_lines)


def create_svg_container(width, height, content):
    """
    Create SVG container with connector lines

    Args:
        width (int): SVG width
        height (int): SVG height
        content (str): SVG path content

    Returns:
        str: Complete SVG markup
    """
    return f"""
    <svg class="connector-svg" width="{width}" height="{height}"
         viewBox="0 0 {width} {height}"
         xmlns="http://www.w3.org/2000/svg">
        {content}
    </svg>
    """
