import numpy as np
import json
import matplotlib.pyplot as plt
from pathlib import Path
from tracker_3d import TrackerEngine3D, PlaybackSimulator

def calculate_accuracy(config_path, npz_path):
    if not npz_path.exists():
        print(f"❌ Record file not found: {npz_path}")
        return

    # Load Data
    data = np.load(npz_path)
    if 'ground_truth' not in data:
        print("❌ Ground truth not found. Please regenerate synthetic data first.")
        return
        
    ground_truth = data['ground_truth']
    
    # Initialize Engine
    engine = TrackerEngine3D(config_path)
    simulator = PlaybackSimulator(npz_path)
    
    estimates = []
    
    print("🧠 Processing algorithm estimates...")
    # Generate estimates for the entire recording
    for _ in range(len(ground_truth)):
        variances = simulator.get_next_frame()
        pos = engine.calculate_position(variances)
        estimates.append(pos)
        
    estimates = np.array(estimates)
    
    # CALCULATE ERROR STATS
    # Distance formula for each point
    errors = np.linalg.norm(ground_truth - estimates, axis=1)
    rmse = np.sqrt(np.mean(errors**2))
    mae = np.mean(errors)
    
    print(f"📈 --- ACCURACY REPORT ---")
    print(f"📏 Mean Absolute Error (MAE): {mae:.3f} meters")
    print(f"🎯 Root Mean Square Error (RMSE): {rmse:.3f} meters")
    
    # Generate Figure 4.3
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot Ground Truth (Green Path)
    ax.plot(ground_truth[:,0], ground_truth[:,1], ground_truth[:,2], 
            'g-', linewidth=2, label='Ground Truth (Actual Path)', alpha=0.6)
    
    # Plot Algorithm Estimates (Blue Dots)
    ax.scatter(estimates[:,0], estimates[:,1], estimates[:,2], 
               c='#007acc', s=10, label='Algorithm Estimate (CSI)', alpha=0.3)
    
    ax.set_title(f'Figure 4.3: Digital Twin Validation (RMSE: {rmse:.2f}m)', fontsize=14, fontweight='bold')
    ax.set_xlabel('X (Meters)')
    ax.set_ylabel('Y (Meters)')
    ax.set_zlabel('Z (Meters)')
    ax.legend()
    
    save_path = "3d-tracking/Figure_4_3_Accuracy.png"
    plt.savefig(save_path, dpi=300)
    print(f"✅ Accuracy Figure saved to: {save_path}")
    plt.show()

if __name__ == "__main__":
    config = Path(__file__).parent / "geometry_config.json"
    npz = Path(__file__).parent / "synthetic_movement.npz"
    calculate_accuracy(config, npz)
