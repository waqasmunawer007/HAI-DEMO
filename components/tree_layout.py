"""
Tree Layout Calculator
Calculates x,y positions for each node in the hierarchical tree
"""

def calculate_tree_layout(tree_data):
    """
    Calculate x,y positions for each node in the tree

    Args:
        tree_data (dict): Hierarchical data structure with format:
            {
                'root': {...},
                'level1': [...],
                'level2': [...]
            }

    Returns:
        dict: Node positions {node_id: {'x': x_pos, 'y': y_pos, 'level': level}}
    """
    positions = {}

    # Layout constants
    CARD_WIDTH = 160  # Average card width
    HORIZONTAL_GAP_L1 = 50  # Gap between level 1 cards
    HORIZONTAL_GAP_L2 = 35  # Gap between level 2 cards
    VERTICAL_GAP = 100  # Vertical gap between levels

    # Level 0 (Root) - centered at top
    root = tree_data.get('root', {})
    if root:
        positions[root['id']] = {
            'x': 0,  # Will be centered relative to container
            'y': 0,
            'level': 0,
            'label': root['label'],
            'value': root['value']
        }

    # Level 1 - 5 nodes evenly distributed
    level1_nodes = tree_data.get('level1', [])
    if level1_nodes:
        # Calculate total width needed for level 1
        total_width_l1 = (len(level1_nodes) * CARD_WIDTH) + ((len(level1_nodes) - 1) * HORIZONTAL_GAP_L1)
        start_x_l1 = -total_width_l1 / 2  # Center around x=0

        for idx, node in enumerate(level1_nodes):
            x_pos = start_x_l1 + (idx * (CARD_WIDTH + HORIZONTAL_GAP_L1)) + (CARD_WIDTH / 2)
            positions[node['id']] = {
                'x': x_pos,
                'y': VERTICAL_GAP,
                'level': 1,
                'label': node['label'],
                'value': node['value'],
                'has_children': node.get('has_children', False)
            }

    # Level 2 - 3 nodes under "Public Facilities" only
    level2_nodes = tree_data.get('level2', [])
    if level2_nodes:
        # Find parent node (public facilities)
        parent_id = level2_nodes[0].get('parent', 'public')
        parent_pos = positions.get(parent_id, {'x': 0})
        parent_x = parent_pos['x']

        # Calculate total width needed for level 2
        total_width_l2 = (len(level2_nodes) * CARD_WIDTH) + ((len(level2_nodes) - 1) * HORIZONTAL_GAP_L2)
        start_x_l2 = parent_x - (total_width_l2 / 2)

        for idx, node in enumerate(level2_nodes):
            x_pos = start_x_l2 + (idx * (CARD_WIDTH + HORIZONTAL_GAP_L2)) + (CARD_WIDTH / 2)
            positions[node['id']] = {
                'x': x_pos,
                'y': VERTICAL_GAP * 2,
                'level': 2,
                'label': node['label'],
                'value': node['value'],
                'parent': parent_id
            }

    return positions


def get_connector_coordinates(parent_pos, children_positions):
    """
    Calculate connector line coordinates between parent and children

    Args:
        parent_pos (dict): Parent node position {'x': x, 'y': y}
        children_positions (list): List of child positions [{'x': x, 'y': y}, ...]

    Returns:
        list: List of line segments for SVG path
            Each segment: {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
    """
    if not children_positions or not parent_pos:
        return []

    lines = []
    CARD_HEIGHT = 70  # Approximate card height
    VERTICAL_GAP = 100

    # Parent bottom center point
    parent_x = parent_pos['x']
    parent_bottom = parent_pos['y'] + CARD_HEIGHT

    # Horizontal line Y position (midpoint between parent and children)
    horizontal_y = parent_bottom + (VERTICAL_GAP - CARD_HEIGHT) / 2

    # Children top center points
    children_top = children_positions[0]['y']

    # 1. Vertical line from parent to horizontal distribution line
    lines.append({
        'x1': parent_x,
        'y1': parent_bottom,
        'x2': parent_x,
        'y2': horizontal_y,
        'type': 'vertical'
    })

    # 2. Horizontal distribution line connecting all children
    if len(children_positions) > 1:
        leftmost_x = min(child['x'] for child in children_positions)
        rightmost_x = max(child['x'] for child in children_positions)

        lines.append({
            'x1': leftmost_x,
            'y1': horizontal_y,
            'x2': rightmost_x,
            'y2': horizontal_y,
            'type': 'horizontal'
        })

    # 3. Vertical lines from horizontal line to each child
    for child in children_positions:
        lines.append({
            'x1': child['x'],
            'y1': horizontal_y,
            'x2': child['x'],
            'y2': children_top,
            'type': 'vertical'
        })

    return lines
