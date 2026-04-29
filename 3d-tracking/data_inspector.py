import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def inspect_data(file_path):
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return

    print(f"📂 Loading {file_path}...")
    data = np.load(file_path)
    
    # Detect how many nodes are in the file
    node_keys = [k for k in data.keys() if k.endswith('_csi')]
    num_nodes = len(node_keys)
    
    if num_nodes == 0:
        print("❌ No node data found in file.")
        return

    print(f"✅ Found data for {num_nodes} nodes.")
    
    fig, axes = plt.subplots(num_nodes, 1, figsize=(12, 3 * num_nodes), sharex=True)
    if num_nodes == 1:
        axes = [axes]

    for i in range(num_nodes):
        node_id = i + 1
        csi_key = f"node_{node_id}_csi"
        ts_key = f"node_{node_id}_ts"
        
        if csi_key not in data or ts_key not in data:
            continue
            
        csi = data[csi_key]
        ts = data[ts_key]
        
        # Calculate relative time
        rel_ts = ts - ts[0]
        
        # Calculate Magnitude Variance (Motion Metric)
        # We calculate the variance across subcarriers for each packet
        # Higher variance = more disturbance in the radio environment
        mvs = np.var(csi, axis=1)
        
        # Smoothing (simple moving average for better visualization)
        window = 10
        mvs_smooth = np.convolve(mvs, np.ones(window)/window, mode='same')
        
        ax = axes[i]
        ax.plot(rel_ts, mvs_smooth, label=f'Node {node_id} Motion Score', color=plt.cm.viridis(i/num_nodes))
        ax.set_ylabel('Variance')
        ax.set_title(f"Node {node_id} ({len(csi)} packets)")
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')

    axes[-1].set_xlabel('Time (seconds)')
    plt.tight_layout()
    
    output_img = "3d-tracking/data_inspection.png"
    plt.savefig(output_img)
    print(f"📊 Visualization saved to {output_img}")
    plt.show()

if __name__ == "__main__":
    inspect_data("3d-tracking/test_stream.npz")
