import numpy as np
import json
from pathlib import Path

def generate_synthetic_human_movement(config_path, output_path, duration_sec=45, fs=30):
    """
    Simulates realistic human 'Biometric' movement in a 3D volume.
    """
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    room = config['room']
    nodes = config['nodes']
    num_packets = duration_sec * fs
    
    # Define Waypoints (Tightened to the center 'Safe Zone')
    L, W, H = room['length_m'], room['width_m'], room['height_m']
    waypoints = [
        [L*0.4, W*0.4, 0.0], # Start near center
        [L*0.6, W*0.4, 0.0], # Shift Right
        [L*0.6, W*0.6, 0.0], # Shift Up
        [L*0.4, W*0.6, 0.0], # Shift Left
        [L*0.4, W*0.4, 0.0]  # Back to center
    ]
    
    # 1. Generate Smooth Interpolated Path
    path_points = []
    points_per_seg = num_packets // (len(waypoints) - 1)
    
    for i in range(len(waypoints) - 1):
        start_wp = np.array(waypoints[i])
        end_wp = np.array(waypoints[i+1])
        
        for p in range(points_per_seg):
            # Sigmoid-style smoothing for velocity (starts slow, speeds up, ends slow)
            t = p / points_per_seg
            v_smooth = 3 * t**2 - 2 * t**3 
            pos = start_wp + (end_wp - start_wp) * v_smooth
            
            # --- HUMAN BIOMETRICS ---
            # A. Natural Sway (Random Noise)
            pos[0] += np.random.normal(0, 0.02)
            pos[1] += np.random.normal(0, 0.02)
            
            # B. Walking Cadence (Z-axis bobbing)
            # 2Hz oscillation for steps
            cadence_t = (len(path_points) / fs) * 2 * np.pi * 1.8 
            pos[2] = 1.0 + 0.05 * np.sin(cadence_t) 
            
            path_points.append(pos)
            
    target_path = np.array(path_points[:num_packets])
    
    # 2. Generate CSI Data with Distance-Based Variance
    save_data = {}
    print(f"🧬 Modeling Biometric signals...")
    
    for node in nodes:
        node_id = node['id']
        node_pos = np.array(node['pos'])
        
        # Calculate distance
        distances = np.linalg.norm(target_path - node_pos, axis=1)
        
        # Base Amplitudes
        base_csi = np.full((len(target_path), 64), 30.0)
        
        # Apply Inverse-Square Law Disturbance
        for p in range(len(target_path)):
            dist = distances[p]
            # Variance spikes when person is close
            # Scaled for human body mass (cross-section)
            variance_intensity = 18.0 / (dist + 0.4)**2 
            
            # Add dynamic jitter to simulate breathing/motion
            noise = np.random.normal(0, variance_intensity, 64)
            base_csi[p] += noise
            
        save_data[f"node_{node_id}_csi"] = base_csi.astype(np.float32)
        save_data[f"node_{node_id}_ts"] = np.linspace(0, duration_sec, len(target_path)) + 1600000000.0

    # SAVE GROUND TRUTH FOR ACCURACY CALCULATIONS
    save_data["ground_truth"] = target_path.astype(np.float32)

    np.savez_compressed(output_path, **save_data)
    print(f"✅ Synthetic data saved to {output_path}")
    print(f"📊 Simulated a {duration_sec}s figure-8 walk in a {room['length_m']}x{room['width_m']}m room.")

if __name__ == "__main__":
    config = Path(__file__).parent / "geometry_config.json"
    output = Path(__file__).parent / "synthetic_movement.npz"
    generate_synthetic_human_movement(config, output)
