import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from pathlib import Path

# Import our custom Signal Engine
try:
    from tracker_3d import TrackerEngine3D, PlaybackSimulator
except ImportError:
    TrackerEngine3D, PlaybackSimulator = None, None

# Set Sleek Dark Theme
plt.style.use('dark_background')

class TrackerVisualizer3D:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self.room = self.config['room']
        self.nodes = self.config['nodes']
        
        # Initialize the Signal Engine
        self.engine = TrackerEngine3D(config_path) if TrackerEngine3D else None
        
        # Check for Playback Data (Prioritize Synthetic if it exists)
        synth_path = Path(__file__).parent / "synthetic_movement.npz"
        real_path = Path(__file__).parent / "test_stream.npz"
        
        npz_path = synth_path if synth_path.exists() else real_path
        
        if npz_path.exists() and PlaybackSimulator:
            self.simulator = PlaybackSimulator(npz_path)
            self.mode = f"PLAYBACK ({npz_path.name})"
        else:
            self.simulator = None
            self.mode = "ORBIT_SIM"

        # Setup Figure with no borders
        self.fig = plt.figure(figsize=(12, 9), facecolor='#0a0a0a')
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#0a0a0a')
        
        # Initialize plotting elements with Neon colors
        self.user_dot, = self.ax.plot([], [], [], 'wo', markersize=12, 
                                     markeredgecolor='#00ffcc', markeredgewidth=2, 
                                     label='Target Signal', zorder=10)
        self.user_glow, = self.ax.plot([], [], [], 'o', markersize=25, 
                                      color='#00ffcc', alpha=0.3, zorder=5)
        
        self.trail, = self.ax.plot([], [], [], color='#00ffcc', linewidth=2, alpha=0.6)
        self.history = []
        
        # Real-time HUD Text
        self.hud = self.ax.text2D(0.02, 0.98, "", transform=self.ax.transAxes, 
                                 color='#00ffcc', fontsize=11, fontweight='bold',
                                 verticalalignment='top',
                                 bbox=dict(facecolor='black', alpha=0.6, edgecolor='#00ffcc'))
        
        self.setup_room()
        
    def setup_room(self):
        """Draw the modern room boundaries and place nodes"""
        L = self.room['length_m']
        W = self.room['width_m']
        H = self.room['height_m']
        
        # Draw Neon Grid Floor
        xx, yy = np.meshgrid(np.linspace(0, L, 10), np.linspace(0, W, 10))
        self.ax.plot_wireframe(xx, yy, np.zeros_like(xx), color='#333333', alpha=0.5, linewidth=0.5)
        
        # Drawing Room edges as before ...
        edges = [
            ([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]),
            ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]),
            ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
            ([0, 0], [0, W], [H, H]), ([L, L], [0, W], [H, H]),
            ([0, 0], [0, 0], [0, H]), ([L, L], [0, 0], [0, H]),
            ([0, 0], [W, W], [0, H]), ([L, L], [W, W], [0, H])
        ]
        for x, y, z in edges:
            self.ax.plot(x, y, z, color='#0066ff', alpha=0.4, linewidth=1.5)

        for node in self.nodes:
            x, y, z = node['pos']
            color = '#ff3300' if node['role'] == 'anchor_high' else '#ff9900'
            self.ax.scatter(x, y, z, color=color, s=150, marker='H', edgecolors='white', linewidth=1)
            self.ax.text(x, y, z, f" NODE-{node['id']}", color='white', fontsize=8, alpha=0.8)

        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        self.ax.xaxis.pane.set_edgecolor('#0a0a0a')
        self.ax.yaxis.pane.set_edgecolor('#0a0a0a')
        self.ax.zaxis.pane.set_edgecolor('#0a0a0a')

        self.ax.set_xlim(0, L)
        self.ax.set_ylim(0, W)
        self.ax.set_zlim(0, H)
        
        self.ax.set_title('ESPECTRE 3D RADAR SYSTEM [LOCAL HOST]', color='#00ffcc', fontsize=14, pad=40)
        self.ax.legend(facecolor='black', edgecolor='#00ffcc', loc='lower right', fontsize=9)

    def update(self, frame):
        """Update loop supporting Playback or Simulation"""
        if self.simulator and self.engine:
            # PLAYBACK MODE: Process real recording data
            variances = self.simulator.get_next_frame()
            pos = self.engine.calculate_position(variances)
            x, y, z = pos
            status = "SIGNAL: RE-PLAY"
        else:
            # SIMULATION MODE: Smooth walking simulation
            t = frame / 15.0
            x = (self.room['length_m'] / 2) + 1.0 * np.sin(t * 0.8)
            y = (self.room['width_m'] / 2) + 1.4 * np.cos(t * 0.6)
            z = 1.4 + 0.3 * np.sin(t * 1.5)
            status = "SIGNAL: ORBIT_SIM"
        
        # Update Main Target
        self.user_dot.set_data([x], [y])
        self.user_dot.set_3d_properties([z])
        self.user_glow.set_data([x], [y])
        self.user_glow.set_3d_properties([z])
        
        # Update Trail
        self.history.append([x, y, z])
        if len(self.history) > 30: self.history.pop(0)
        h = np.array(self.history)
        self.trail.set_data(h[:, 0], h[:, 1])
        self.trail.set_3d_properties(h[:, 2])
        
        # Update HUD
        self.hud.set_text(f"TARGET ACQUIRED\nX: {x:.2f}m\nY: {y:.2f}m\nZ: {z:.2f}m\nSTATUS: {status}")
        
        return self.user_dot, self.user_glow, self.trail, self.hud

    def run(self):
        ani = FuncAnimation(self.fig, self.update, frames=600, interval=33, blit=False)
        plt.show()

if __name__ == "__main__":
    config_file = Path(__file__).parent / "geometry_config.json"
    vis = TrackerVisualizer3D(config_file)
    print(f"\n[SYSTEM] Booting 3D RADAR [Mode: {vis.mode}]")
    print(f"[SYSTEM] Environment: {vis.room['length_m']}m x {vis.room['width_m']}m x {vis.room['height_m']}m")
    vis.run()
