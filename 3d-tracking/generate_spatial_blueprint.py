import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def generate_spatial_blueprint(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    room = config['room']
    nodes = config['nodes']
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 1. DRAW ROOM BOX (SKELETON)
    L, W, H = room['length_m'], room['width_m'], room['height_m']
    
    # Define edges of the room
    rect_points = np.array([
        [0,0,0], [L,0,0], [L,W,0], [0,W,0], [0,0,0], # Bottom
        [0,0,H], [L,0,H], [L,W,H], [0,W,H], [0,0,H], # Top
    ])
    
    # Vertical pillars
    ax.plot([0,0],[0,0],[0,H], color='black', alpha=0.3)
    ax.plot([L,L],[0,0],[0,H], color='black', alpha=0.3)
    ax.plot([L,L],[W,W],[0,H], color='black', alpha=0.3)
    ax.plot([0,0],[W,W],[0,H], color='black', alpha=0.3)
    
    # Floor and Ceiling
    ax.plot(rect_points[:5,0], rect_points[:5,1], rect_points[:5,2], color='black', alpha=0.5)
    ax.plot(rect_points[5:,0], rect_points[5:,1], rect_points[5:,2], color='black', alpha=0.5)
    
    # 2. PLOT NODES
    colors = ['#ff4d4d', '#4d94ff', '#4d94ff', '#ff4d4d'] # Red for high, Blue for low
    for i, node in enumerate(nodes):
        pos = node['pos']
        ax.scatter(pos[0], pos[1], pos[2], color=colors[i], s=100, edgecolors='black', label=f"Node {node['id']} ({'High' if pos[2]>1 else 'Low'})")
        ax.text(pos[0], pos[1], pos[2]+0.1, f" Node {node['id']}", fontsize=10, fontweight='bold')

    # 3. DRAW TETRAHEDRON SENSING LINES
    node_coords = np.array([n['pos'] for n in nodes])
    for i in range(len(node_coords)):
        for j in range(i + 1, len(node_coords)):
            ax.plot([node_coords[i,0], node_coords[j,0]], 
                    [node_coords[i,1], node_coords[j,1]], 
                    [node_coords[i,2], node_coords[j,2]], 
                    color='cyan', alpha=0.4, linestyle='--')

    # Final Styling
    ax.set_title("Figure 3.3b: Engineering Coordinate Mapping (Tetrahedron)", fontsize=14, pad=20)
    ax.set_xlabel('Length (X) meters')
    ax.set_ylabel('Width (Y) meters')
    ax.set_zlabel('Height (Z) meters')
    ax.view_init(elev=20, azim=45)
    
    save_path = "3d-tracking/Figure_3_3_Engineering_Blueprint.png"
    plt.savefig(save_path, dpi=300)
    print(f"✅ Engineering Blueprint saved to: {save_path}")
    plt.show()

if __name__ == "__main__":
    config = Path(__file__).parent / "geometry_config.json"
    generate_spatial_blueprint(config)
