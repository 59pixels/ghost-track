import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def generate_report_figure(file_path):
    if not Path(file_path).exists():
        print(f"❌ Record file not found: {file_path}")
        return

    data = np.load(file_path)
    # Use Node 1 as the representative example for the report
    csi = data['node_1_csi']
    ts = data['node_1_ts']
    rel_ts = ts - ts[0]
    
    # CALCULATE THE STAT: Variance
    mvs = np.var(csi, axis=1)
    
    # Apply Smoothing for 'Report-Ready' quality
    window = 8
    mvs_smooth = np.convolve(mvs, np.ones(window)/window, mode='same')

    # Create the Plot
    plt.figure(figsize=(10, 5))
    plt.plot(rel_ts, mvs_smooth, color='#007acc', linewidth=2, label='CSI Disturbance (MVS)')
    
    # Styling for Figure 4.1
    plt.fill_between(rel_ts, mvs_smooth, color='#007acc', alpha=0.1)
    plt.title('Figure 4.1: MVS Variance Output (Human Entry Detection)', fontsize=14, fontweight='bold')
    plt.xlabel('Time (Seconds)', fontsize=12)
    plt.ylabel('Variance Magnitude ($\sigma^2$)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    # Save the file
    save_path = "3d-tracking/Figure_4_1_MVS.png"
    plt.savefig(save_path, dpi=300)
    print(f"✅ Figure 4.1 generated and saved to: {save_path}")
    plt.show()

if __name__ == "__main__":
    # Check for synthetic or real data
    npz = "3d-tracking/synthetic_movement.npz"
    if not Path(npz).exists():
        npz = "3d-tracking/test_stream.npz"
        
    generate_report_figure(npz)
