import numpy as np
import json
from pathlib import Path

class TrackerEngine3D:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.nodes = self.config['nodes']
        self.node_positions = np.array([n['pos'] for n in self.nodes])
        self.num_nodes = len(self.nodes)
        
        # Smoothing state (Low-pass filter)
        self.current_pos = np.array([self.config['room']['length_m']/2, 
                                    self.config['room']['width_m']/2, 
                                    self.config['room']['height_m']/2])
        self.alpha = 0.2  # Original smoothing

    def calculate_position(self, variances):
        """
        Triangulate position based on original weighted centroid.
        """
        v = np.array(variances)
        
        # Avoid division by zero
        if np.sum(v) < 1e-6:
            return self.current_pos
            
        # Original Power Weighting (v^2)
        weights = (v ** 2) / (np.sum(v ** 2) + 1e-6)
        
        # Target position is the weighted average of node positions
        target_pos = np.zeros(3)
        for i in range(self.num_nodes):
            target_pos += weights[i] * self.node_positions[i]
            
        # Apply smoothing (EMA filter)
        self.current_pos = (self.alpha * target_pos) + ((1 - self.alpha) * self.current_pos)
        
        return self.current_pos

class PlaybackSimulator:
    def __init__(self, npz_path):
        self.data = np.load(npz_path)
        self.num_nodes = 4
        
        # Load and align indices
        self.csi_data = []
        for i in range(1, 5):
            self.csi_data.append(self.data[f'node_{i}_csi'])
            
        # Find minimum length to keep them synced
        self.max_idx = min([len(d) for d in self.csi_data])
        self.current_idx = 0

    def get_next_frame(self):
        if self.current_idx >= self.max_idx:
            self.current_idx = 0 # Loop indefinitely
            
        variances = []
        for i in range(4):
            # Calculate variance of the current packet's subcarriers
            packet_csi = self.csi_data[i][self.current_idx]
            variances.append(np.var(packet_csi))
            
        self.current_idx += 1
        return variances

if __name__ == "__main__":
    # Test block
    config = Path(__file__).parent / "geometry_config.json"
    engine = TrackerEngine3D(config)
    print("✅ Tracker Engine Initialized.")
    print(f"Nodes loaded at positions:\n{engine.node_positions}")
